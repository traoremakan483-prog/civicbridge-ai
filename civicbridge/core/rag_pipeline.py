from langchain.schema import Document
from langchain_openai import ChatOpenAI

from config.prompts import GROUNDED_ANSWER_PROMPT
from config.settings import DEFAULT_LLM_MODEL


def _build_context(documents: list[Document]) -> str:
    """
    Concatenate retrieved document chunks into a single context string.

    Each chunk is separated by a blank line so the LLM can distinguish
    between passages from different parts of the document.

    Args:
        documents: List of retrieved LangChain Document objects.

    Returns:
        A single string combining all chunk contents.
    """
    return "\n\n".join(doc.page_content for doc in documents)


def generate_answer(question: str, retriever) -> dict:
    """
    Retrieve relevant document chunks and generate a grounded answer.

    The answer is produced strictly from the retrieved context. If no
    relevant chunks are found, the function returns a safe fallback message
    without calling the LLM.

    Args:
        question:  The citizen's question as a plain string.
        retriever: A LangChain VectorStoreRetriever (from vector_store.py).

    Returns:
        A dict with two keys:
            "answer"           (str)         — the LLM-generated answer.
            "source_documents" (list[Document]) — the chunks used as context.

    Raises:
        Exception: Propagates any OpenAI API errors so the caller can handle
                   them and display a meaningful message in the UI.
    """
    source_documents: list[Document] = retriever.invoke(question)

    if not source_documents:
        return {
            "answer": (
                "No relevant information was found in the uploaded document "
                "for your question. Please try rephrasing, or consult the "
                "relevant authority directly."
            ),
            "source_documents": [],
        }

    context = _build_context(source_documents)

    prompt = GROUNDED_ANSWER_PROMPT.format(
        context=context,
        question=question,
    )

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)

    return {
        "answer": response.content.strip(),
        "source_documents": source_documents,
    }
