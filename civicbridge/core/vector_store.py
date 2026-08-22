from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from config.settings import DEFAULT_EMBEDDING_MODEL, RETRIEVAL_K
from core.retrieval_policy import (
    MIN_PASSAGES,
    MIN_RELEVANCE,
    RetrievalDecision,
    ScoredPassage,
    decide,
)


def _get_embeddings() -> OpenAIEmbeddings:
    """
    Create an OpenAIEmbeddings instance using the model defined in settings.

    The OpenAI API key is read automatically from the OPENAI_API_KEY
    environment variable (loaded via python-dotenv in app.py).

    Returns:
        A configured OpenAIEmbeddings object.
    """
    return OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL)


def build_vector_store(documents: list[Document]) -> FAISS:
    """
    Build an in-memory FAISS vector store from a list of Document chunks.

    Embeds all chunks using OpenAI embeddings and indexes them in FAISS.
    The index lives in memory only — no files are written to disk.

    Args:
        documents: List of LangChain Document chunks (from document_loader).

    Returns:
        A FAISS vector store ready for similarity search.

    Raises:
        ValueError: If the documents list is empty.
        Exception: If embedding or indexing fails (e.g. invalid API key).
    """
    if not documents:
        raise ValueError(
            "Cannot build a vector store from an empty document list. "
            "Ensure the PDF was loaded and split successfully."
        )

    embeddings = _get_embeddings()
    return FAISS.from_documents(documents, embeddings)


def retrieve_relevant(
    vector_store: FAISS,
    query: str,
    k: int = RETRIEVAL_K,
    min_relevance: float = MIN_RELEVANCE,
    min_passages: int = MIN_PASSAGES,
) -> RetrievalDecision:
    """
    Retrieve passages for `query` and judge whether any of them is actually
    about the question.

    This replaces the previous `get_retriever()`, which returned a plain
    similarity retriever. A similarity search always hands back its k nearest
    neighbours — it cannot express "nothing in here matches" — so an off-topic
    question came back with k weakly-related paragraphs and the model answered
    from them. See `core/retrieval_policy` for the full reasoning.

    Args:
        vector_store:  A FAISS store built by `build_vector_store`.
        query:         The question, in English (retrieval happens in English).
        k:             How many neighbours to fetch before filtering.
        min_relevance: Bar a passage must clear to be used.
        min_passages:  How many must clear it before we answer at all.

    Returns:
        A RetrievalDecision. When `accepted` is False, callers must not invoke
        the language model — there is nothing to ground an answer in.
    """
    # `with_relevance_scores` returns scores in [0, 1] where HIGHER is closer,
    # already normalised by LangChain. The raw FAISS API returns distances,
    # where LOWER is closer — the two are inverted, and mixing them up is
    # silent. Everything downstream speaks relevance, never distance.
    hits = vector_store.similarity_search_with_relevance_scores(query, k=k)

    scored = [
        ScoredPassage(
            text=doc.page_content,
            relevance=float(score),
            metadata=doc.metadata,
        )
        for doc, score in hits
    ]

    return decide(scored, min_relevance=min_relevance, min_passages=min_passages)


def to_documents(decision: RetrievalDecision) -> list[Document]:
    """
    Turn accepted passages back into LangChain Documents, for the parts of the
    UI that still display source excerpts with their page numbers.
    """
    return [
        Document(page_content=p.text, metadata=p.metadata or {})
        for p in decision.passages
    ]
