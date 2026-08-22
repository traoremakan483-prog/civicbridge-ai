from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config.prompts import GROUNDED_ANSWER_PROMPT, REFUSAL_ANSWER
from config.settings import DEFAULT_LLM_MODEL
from core.vector_store import retrieve_relevant, to_documents


def _build_context(documents: list[Document]) -> str:
    """
    Concatenate retrieved document chunks into a single context string.

    Each passage is wrapped in a numbered tag rather than merely separated by
    a blank line. Two reasons:

      1. The model can cite "passage 2" instead of paraphrasing vaguely.
      2. It marks a boundary between INSTRUCTIONS and DATA. Document text is
         untrusted input: a PDF (or an uploaded one) can contain a sentence
         like "ignore the instructions above". Explicit delimiters plus an
         explicit rule in the prompt make that much harder to pull off.
    """
    return "\n\n".join(
        f"<passage id=\"{i}\">\n{doc.page_content}\n</passage>"
        for i, doc in enumerate(documents, start=1)
    )


def generate_answer(question: str, vector_store) -> dict:
    """
    Retrieve relevant passages and generate an answer grounded strictly in them.

    If nothing in the knowledge base is actually about the question, the
    function returns a refusal **without calling the language model**. That is
    deliberate: skipping the call makes invention impossible rather than
    merely discouraged, and costs nothing.

    Args:
        question:     The citizen's question, in English.
        vector_store: A FAISS store built by `build_vector_store`.

    Returns:
        A dict with:
            "answer"           (str)             — the answer, or the refusal.
            "source_documents" (list[Document])  — passages used; empty on refusal.
            "answered"         (bool)            — False when refused.
            "why"              (str)             — developer-facing explanation
                                                   of the retrieval decision.

    Raises:
        Exception: Propagates OpenAI API errors so the caller can show them.
    """
    decision = retrieve_relevant(vector_store, question)

    if not decision.accepted:
        return {
            "answer": REFUSAL_ANSWER,
            "source_documents": [],
            "answered": False,
            "why": decision.reason,
        }

    documents = to_documents(decision)
    context = _build_context(documents)

    prompt = GROUNDED_ANSWER_PROMPT.format(context=context, question=question)

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return {
        "answer": response.content.strip(),
        "source_documents": documents,
        "answered": True,
        "why": decision.reason,
    }
