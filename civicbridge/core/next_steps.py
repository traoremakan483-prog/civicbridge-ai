import json

from langchain_openai import ChatOpenAI

from config.prompts import NEXT_STEPS_PROMPT
from config.settings import DEFAULT_LLM_MODEL

_FALLBACK = "Not specified in the document."

_EMPTY_RESULT = {
    "who_can_apply": _FALLBACK,
    "required_documents": _FALLBACK,
    "step_by_step_process": _FALLBACK,
    "estimated_processing_time": _FALLBACK,
    "important_notes": _FALLBACK,
}


def _parse_sections(raw: str) -> dict:
    """
    Parse the LLM's free-text response into a structured dictionary.

    Looks for bold section headers produced by NEXT_STEPS_PROMPT and maps
    each section's content to the corresponding dict key. Falls back to
    _FALLBACK for any section the LLM did not populate.

    Args:
        raw: The raw text output from the LLM.

    Returns:
        A dict with the five required keys.
    """
    key_map = {
        "who can apply": "who_can_apply",
        "required documents": "required_documents",
        "step-by-step process": "step_by_step_process",
        "estimated processing time": "estimated_processing_time",
        "important notes": "important_notes",
        "important notes or warnings": "important_notes",
    }

    result = dict(_EMPTY_RESULT)
    current_key = None
    buffer = []

    for line in raw.splitlines():
        stripped = line.strip()

        matched = False
        lower = stripped.lower().lstrip("0123456789. *#").strip("*").strip()
        for header, dict_key in key_map.items():
            if lower.startswith(header):
                if current_key and buffer:
                    result[current_key] = " ".join(buffer).strip()
                current_key = dict_key
                buffer = []
                matched = True
                break

        if not matched and current_key and stripped:
            buffer.append(stripped)

    if current_key and buffer:
        result[current_key] = " ".join(buffer).strip()

    for k, v in result.items():
        if not v or v.lower() == "not specified in the document.":
            result[k] = _FALLBACK

    return result


def generate_next_steps(question: str, context: str) -> dict:
    """
    Produce a structured "What Should I Do Next?" guide.

    The output is built strictly from the retrieved document context and
    the citizen's question. Missing sections are filled with a safe
    fallback string rather than fabricated content.

    Args:
        question: The citizen's original question.
        context:  The combined text of the retrieved document chunks.

    Returns:
        A dict with these exact keys:
            - who_can_apply
            - required_documents
            - step_by_step_process
            - estimated_processing_time
            - important_notes

    Raises:
        ValueError: If both question and context are empty.
        Exception: Propagates any OpenAI API errors to the caller.
    """
    if not question.strip() and not context.strip():
        raise ValueError("Both question and context cannot be empty.")

    prompt = NEXT_STEPS_PROMPT.format(context=context, question=question)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return _parse_sections(response.content)
