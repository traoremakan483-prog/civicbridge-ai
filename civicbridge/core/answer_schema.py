"""
Parse and validate the single structured response that replaces four LLM calls.

WHY THIS FILE EXISTS
────────────────────────────────────────────────────────────────────────────
Answering one question used to cost up to thirteen round-trips to the model:

    translate question         1
    grounded answer            1
    plain-language version     1
    action steps               1
    "what should I do next"    1
    translating the outputs    up to 8
                              ────
                              up to 13

All sequential, all blocking — thirty to sixty seconds of spinner, and a bill
six times larger than it needed to be. Every one of those calls sent the same
passages or the same answer back over the wire again.

The four generation calls are now ONE call returning JSON, and the eight
translation calls are ONE call translating the whole payload. Three round-trips
instead of thirteen; two when the citizen writes in English.

The cost of that choice is a new failure mode: a model can return malformed
JSON, miss a key, or wrap the object in prose or a ``` fence. Parsing it is
therefore treated as untrusted input, and — like the retrieval policy — the
parsing lives here, free of LangChain and network calls, so it can be tested
against every malformed shape a model actually produces.
"""

import json
import re
from dataclasses import dataclass, field

# La chaine que les prompts imposent quand une section est absente du document.
NOT_SPECIFIED = "Not specified in the document."

NEXT_STEPS_KEYS = (
    "who_can_apply",
    "required_documents",
    "step_by_step_process",
    "estimated_processing_time",
    "important_notes",
)


@dataclass
class StructuredAnswer:
    """Everything the UI needs, from a single model response."""

    answer: str
    simple: str
    action_steps: list[str] = field(default_factory=list)
    next_steps: dict = field(default_factory=dict)
    #: Champs que le modele a omis ou mal formes, reconstruits par defaut.
    repaired: list[str] = field(default_factory=list)


def _strip_code_fence(raw: str) -> str:
    """
    Remove a ``` or ```json fence if the model wrapped its JSON in one.

    Asking for "JSON only" works most of the time. Most of the time is not a
    guarantee, and a fence is the single most common way it fails.
    """
    text = raw.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return fence.group(1).strip() if fence else text


def _extract_object(raw: str) -> str:
    """
    Pull the outermost {...} out of a response that carries extra prose.

    Models sometimes prepend "Here is the JSON you asked for:". Slicing from
    the first brace to the last is crude but robust for a single top-level
    object, which is what the prompt asks for.
    """
    text = _strip_code_fence(raw)
    if text.startswith("{") and text.endswith("}"):
        return text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in the model response")
    return text[start : end + 1]


def _as_text(value) -> str:
    """Coerce a field to text, accepting the shapes models actually return."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "\n".join(_as_text(v) for v in value if _as_text(v))
    if isinstance(value, dict):
        return "\n".join(f"{k}: {_as_text(v)}" for k, v in value.items())
    return str(value).strip()


def _as_steps(value) -> list[str]:
    """
    Coerce the action steps to a list of strings.

    Asked for an array, a model may still return a numbered string. Both are
    accepted; leading numbering ("1. ", "- ") is stripped so the UI does not
    render "1. 1. Visit ...".
    """
    if value is None:
        return []
    items = value if isinstance(value, (list, tuple)) else str(value).splitlines()
    steps = []
    for item in items:
        text = _as_text(item)
        text = re.sub(r"^\s*(?:\d+[.)]|[-•*])\s*", "", text).strip()
        if text:
            steps.append(text)
    return steps


def parse_structured_answer(raw: str) -> StructuredAnswer:
    """
    Turn the model's response into a StructuredAnswer, repairing what can be
    repaired and recording what had to be.

    A missing section is filled with NOT_SPECIFIED rather than left absent:
    the UI has a defined slot for each one, and "not specified in the document"
    is both true and useful, where a blank box is neither.

    Args:
        raw: The model's reply, possibly fenced or wrapped in prose.

    Returns:
        A StructuredAnswer. `repaired` lists the fields that were missing or
        malformed — surface it in logs, never to the citizen.

    Raises:
        ValueError: If no JSON object can be recovered at all, or if the
            answer itself is empty. Callers should fall back rather than show
            an empty card.
    """
    try:
        data = json.loads(_extract_object(raw))
    except json.JSONDecodeError as e:
        raise ValueError(f"model returned malformed JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")

    repaired: list[str] = []

    answer = _as_text(data.get("answer"))
    if not answer:
        raise ValueError("the model response contains no answer")

    simple = _as_text(data.get("simple"))
    if not simple:
        # Mieux vaut repeter la reponse officielle que d'afficher une carte
        # vide la ou l'utilisateur attend une explication.
        simple = answer
        repaired.append("simple")

    steps = _as_steps(data.get("action_steps"))
    if not steps:
        repaired.append("action_steps")

    raw_next = data.get("next_steps")
    if not isinstance(raw_next, dict):
        raw_next = {}
        repaired.append("next_steps")

    next_steps = {}
    for key in NEXT_STEPS_KEYS:
        value = _as_text(raw_next.get(key))
        if not value:
            value = NOT_SPECIFIED
            repaired.append(f"next_steps.{key}")
        next_steps[key] = value

    return StructuredAnswer(
        answer=answer,
        simple=simple,
        action_steps=steps,
        next_steps=next_steps,
        repaired=repaired,
    )


def blocks_for_translation(answer: StructuredAnswer) -> dict:
    """
    Flatten a StructuredAnswer into the labelled blocks sent for translation.

    Sections marked "not specified" are left out: translating that sentence
    into eight languages costs money and tells the reader nothing.
    """
    blocks = {
        "Official Answer": answer.answer,
        "Simple Explanation": answer.simple,
    }
    if answer.action_steps:
        blocks["Action Steps"] = "\n".join(
            f"{i}. {s}" for i, s in enumerate(answer.action_steps, start=1)
        )
    labels = {
        "who_can_apply": "Who can apply",
        "required_documents": "Required documents",
        "step_by_step_process": "Step-by-step process",
        "estimated_processing_time": "Estimated processing time",
        "important_notes": "Important notes",
    }
    for key, label in labels.items():
        value = answer.next_steps.get(key, "")
        if value and value != NOT_SPECIFIED:
            blocks[label] = value
    return blocks


def parse_translated_blocks(raw: str, expected: dict) -> dict:
    """
    Parse the batch translation response back into the same labelled blocks.

    Any label the model dropped falls back to its English original — showing
    the source is a visible imperfection; showing an empty section is a silent
    one, and the citizen would never know a paragraph went missing.
    """
    try:
        data = json.loads(_extract_object(raw))
    except (json.JSONDecodeError, ValueError):
        return dict(expected)

    if not isinstance(data, dict):
        return dict(expected)

    return {
        label: _as_text(data.get(label)) or original
        for label, original in expected.items()
    }
