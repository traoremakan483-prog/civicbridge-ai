from langchain_openai import ChatOpenAI

from config.prompts import SIMPLIFICATION_PROMPT
from config.settings import DEFAULT_LLM_MODEL


def simplify_answer(answer: str) -> str:
    """
    Rewrite a grounded answer in plain, simple language.

    The rewrite preserves the original meaning and does not introduce
    any facts not present in the input. Suitable for citizens with low
    digital or reading literacy.

    Args:
        answer: The grounded answer string produced by the RAG pipeline.

    Returns:
        A simplified version of the answer as a plain string.

    Raises:
        ValueError: If the answer is empty.
        Exception: Propagates any OpenAI API errors to the caller.
    """
    if not answer or not answer.strip():
        raise ValueError("Cannot simplify an empty answer.")

    prompt = SIMPLIFICATION_PROMPT.format(answer=answer)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return response.content.strip()
