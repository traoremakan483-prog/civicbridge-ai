"""
Tests for the retrieval relevance policy.

These run on the standard library alone — no OpenAI key, no embeddings, no
network. That is the point of keeping the decision separate from FAISS: the
rule that decides whether CivicBridge answers or refuses can be checked on
every commit, by anyone, in milliseconds.

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "civicbridge"))

from core.retrieval_policy import (  # noqa: E402
    ScoredPassage,
    decide,
    distance_to_relevance,
)


def passage(relevance: float, text: str = "…") -> ScoredPassage:
    return ScoredPassage(text=text, relevance=relevance)


class RefusingIsTheImportantPart(unittest.TestCase):
    """The behaviour the old code could not produce at all."""

    def test_an_off_topic_question_is_refused(self):
        # What a healthcare index returns for "how do I bake a cake": four
        # passages, all weakly matching on stray shared words.
        decision = decide([passage(0.12), passage(0.09), passage(0.07), passage(0.05)])
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.passages, [])
        self.assertIn("outside this document", decision.reason)

    def test_refusal_hands_back_nothing_to_answer_from(self):
        # The caller must be unable to build a prompt by accident: no passages
        # means no context, which means no invented answer.
        decision = decide([passage(0.30), passage(0.20)], min_relevance=0.35)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.passages, [])

    def test_an_empty_index_is_refused_rather_than_crashing(self):
        decision = decide([])
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.best_relevance, 0.0)


class AcceptingLegitimateQuestions(unittest.TestCase):
    """Refusing everything would be just as broken."""

    def test_a_clearly_relevant_question_is_answered(self):
        decision = decide([passage(0.81), passage(0.74), passage(0.10)])
        self.assertTrue(decision.accepted)
        self.assertEqual(len(decision.passages), 2, "the 0.10 passage must be dropped")

    def test_passages_come_back_best_first(self):
        decision = decide([passage(0.51, "c"), passage(0.92, "a"), passage(0.63, "b")])
        self.assertEqual([p.text for p in decision.passages], ["a", "b", "c"])

    def test_a_single_strong_passage_is_enough_by_default(self):
        decision = decide([passage(0.88), passage(0.04)])
        self.assertTrue(decision.accepted)

    def test_requiring_two_passages_rejects_a_lone_match(self):
        # A single lucky paragraph is often a shared word, not a shared subject.
        decision = decide([passage(0.88), passage(0.04)], min_passages=2)
        self.assertFalse(decision.accepted)


class TheInversionTrap(unittest.TestCase):
    """
    FAISS returns DISTANCE (lower is closer); the policy expects RELEVANCE
    (higher is closer). Getting this backwards does not raise anything by
    itself — it silently makes the assistant answer from the least relevant
    passages. So the conversion is a named function, and out-of-range input
    is rejected loudly.
    """

    def test_identical_vectors_score_one(self):
        self.assertAlmostEqual(distance_to_relevance(0.0), 1.0)

    def test_opposite_vectors_score_zero(self):
        self.assertAlmostEqual(distance_to_relevance(2.0), 0.0)

    def test_conversion_is_monotonic_decreasing(self):
        closer, further = distance_to_relevance(0.4), distance_to_relevance(1.4)
        self.assertGreater(closer, further)

    def test_a_negative_distance_is_rejected(self):
        with self.assertRaises(ValueError):
            distance_to_relevance(-0.1)

    def test_passing_a_raw_distance_as_relevance_is_rejected(self):
        # 1.7 is a plausible L2 distance and an impossible relevance score.
        with self.assertRaises(ValueError) as ctx:
            decide([passage(1.7)])
        self.assertIn("distance", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
