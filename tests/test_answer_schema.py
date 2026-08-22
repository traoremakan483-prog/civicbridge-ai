"""
Tests for parsing the single structured model response.

Collapsing thirteen LLM calls into three buys speed and money, and costs one
thing: the response is now JSON produced by a language model, which is to say
untrusted input. These tests cover the malformed shapes models actually return
— fences, prose around the object, a numbered string where an array was asked
for, missing keys — because each of them, unhandled, is a crash or an empty
card in front of someone trying to find out whether they qualify for help.

Standard library only. No key, no network.

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "civicbridge"))

from core.answer_schema import (  # noqa: E402
    NOT_SPECIFIED,
    blocks_for_translation,
    parse_structured_answer,
    parse_translated_blocks,
)

COMPLETE = """{
  "answer": "You qualify if your household income is below RM2,500 [passage 1].",
  "simple": "You can apply if your family earns less than RM2,500 a month.",
  "action_steps": ["Prepare your IC", "Visit the district office", "Submit form NHAP-1"],
  "next_steps": {
    "who_can_apply": "Households under RM2,500 monthly income.",
    "required_documents": "IC, income statement, utility bill.",
    "step_by_step_process": "Fill form NHAP-1, submit at the district office.",
    "estimated_processing_time": "14 working days.",
    "important_notes": "Applications close on 31 December."
  }
}"""


class TheHappyPath(unittest.TestCase):
    def test_a_complete_response_is_parsed_whole(self):
        r = parse_structured_answer(COMPLETE)
        self.assertIn("RM2,500", r.answer)
        self.assertEqual(len(r.action_steps), 3)
        self.assertEqual(r.next_steps["estimated_processing_time"], "14 working days.")
        self.assertEqual(r.repaired, [], "nothing should need repairing")


class ShapesModelsActuallyReturn(unittest.TestCase):
    def test_a_json_code_fence_is_stripped(self):
        r = parse_structured_answer("```json\n" + COMPLETE + "\n```")
        self.assertIn("RM2,500", r.answer)

    def test_a_bare_code_fence_is_stripped(self):
        r = parse_structured_answer("```\n" + COMPLETE + "\n```")
        self.assertIn("RM2,500", r.answer)

    def test_prose_around_the_object_is_ignored(self):
        r = parse_structured_answer(
            "Here is the JSON you asked for:\n" + COMPLETE + "\nHope this helps!"
        )
        self.assertIn("RM2,500", r.answer)

    def test_action_steps_returned_as_a_numbered_string(self):
        r = parse_structured_answer(
            '{"answer": "a", "simple": "b", '
            '"action_steps": "1. Prepare your IC\\n2. Visit the office"}'
        )
        self.assertEqual(r.action_steps, ["Prepare your IC", "Visit the office"])

    def test_existing_numbering_is_not_doubled(self):
        r = parse_structured_answer(
            '{"answer": "a", "simple": "b", "action_steps": ["1. Visit", "- Submit"]}'
        )
        self.assertEqual(r.action_steps, ["Visit", "Submit"])

    def test_a_section_returned_as_a_list_is_joined(self):
        r = parse_structured_answer(
            '{"answer": "a", "simple": "b", '
            '"next_steps": {"required_documents": ["IC", "Payslip"]}}'
        )
        self.assertEqual(r.next_steps["required_documents"], "IC\nPayslip")


class RepairingWhatIsMissing(unittest.TestCase):
    def test_a_missing_simple_explanation_falls_back_to_the_answer(self):
        r = parse_structured_answer('{"answer": "The official answer."}')
        self.assertEqual(r.simple, "The official answer.")
        self.assertIn("simple", r.repaired)

    def test_every_next_steps_section_always_exists(self):
        r = parse_structured_answer('{"answer": "a", "simple": "b"}')
        for key in (
            "who_can_apply",
            "required_documents",
            "step_by_step_process",
            "estimated_processing_time",
            "important_notes",
        ):
            self.assertEqual(r.next_steps[key], NOT_SPECIFIED)

    def test_repairs_are_recorded_so_they_can_be_logged(self):
        r = parse_structured_answer('{"answer": "a"}')
        self.assertIn("simple", r.repaired)
        self.assertIn("action_steps", r.repaired)


class RefusingToShowAnEmptyCard(unittest.TestCase):
    def test_malformed_json_raises(self):
        with self.assertRaises(ValueError):
            parse_structured_answer("{not json at all")

    def test_a_response_with_no_object_raises(self):
        with self.assertRaises(ValueError):
            parse_structured_answer("I'm sorry, I cannot help with that.")

    def test_an_empty_answer_raises(self):
        with self.assertRaises(ValueError):
            parse_structured_answer('{"answer": "", "simple": "something"}')

    def test_a_json_array_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_structured_answer('["answer"]')


class TranslationBatching(unittest.TestCase):
    def test_sections_marked_not_specified_are_not_sent_for_translation(self):
        r = parse_structured_answer(COMPLETE)
        r.next_steps["important_notes"] = NOT_SPECIFIED
        blocks = blocks_for_translation(r)
        self.assertNotIn("Important notes", blocks)
        self.assertIn("Official Answer", blocks)

    def test_a_dropped_label_falls_back_to_english(self):
        expected = {"Official Answer": "English answer", "Action Steps": "1. Go"}
        got = parse_translated_blocks('{"Official Answer": "Jawapan"}', expected)
        self.assertEqual(got["Official Answer"], "Jawapan")
        self.assertEqual(
            got["Action Steps"],
            "1. Go",
            "a missing translation must show the source, never an empty section",
        )

    def test_an_unparseable_translation_falls_back_entirely(self):
        expected = {"Official Answer": "English answer"}
        self.assertEqual(parse_translated_blocks("garbage", expected), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
