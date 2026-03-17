from langchain_openai import ChatOpenAI

from config.prompts import ACTION_STEPS_PROMPT
from config.settings import DEFAULT_LLM_MODEL


def generate_action_steps(answer: str) -> list[str]:
    """
    Extract 3–5 concrete, actionable steps from a grounded answer.

    Only steps that are clearly supported by the answer are returned.
    The function does not fabricate steps when the answer lacks detail.

    Args:
        answer: The grounded answer string produced by the RAG pipeline.

    Returns:
        A list of action step strings (3–5 items when possible, fewer if
        the answer does not support more).

    Raises:
        ValueError: If the answer is empty.
        Exception: Propagates any OpenAI API errors to the caller.
    """
    if not answer or not answer.strip():
        raise ValueError("Cannot generate action steps from an empty answer.")

    prompt = ACTION_STEPS_PROMPT.format(answer=answer)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    raw = response.content.strip()
    steps = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        for prefix in ("1.", "2.", "3.", "4.", "5.", "-", "*", "•"):
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        if line:
            steps.append(line)

    return steps
