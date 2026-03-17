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
    Produce a structured "What Should I Do Next?" guide from raw document context.

    This function intentionally receives the raw retrieved context rather than
    a pre-generated answer. A generated answer may have been condensed during
    the RAG step, losing detail about eligibility, required documents, or
    processing time. Using the full context gives the LLM the best chance of
    populating every section accurately.

    The function must not invent or infer details not present in the context.
    Any section that cannot be answered from the context is filled with the
    safe fallback string "Not specified in the document." rather than
    fabricated content.

    Args:
        question: The citizen's original question. Used to focus the LLM on
                  the most relevant parts of the context.
        context:  The combined text of the retrieved document chunks, as
                  returned by document_loader / vector_store.

    Returns:
        A dict that always contains exactly these five keys:
            - who_can_apply            (str) Eligibility criteria.
            - required_documents       (str) Documents the citizen must prepare.
            - step_by_step_process     (str) Steps to apply or access the service.
            - estimated_processing_time (str) Typical processing duration, if stated.
            - important_notes          (str) Warnings, deadlines, or restrictions.
        Each value is either extracted from the document or falls back to
        "Not specified in the document."

    Raises:
        ValueError: If both question and context are empty strings.
        Exception: Propagates any OpenAI API errors to the caller.
    """
    if not question.strip() and not context.strip():
        raise ValueError("Both question and context cannot be empty.")

    prompt = NEXT_STEPS_PROMPT.format(context=context, question=question)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return _parse_sections(response.content)
