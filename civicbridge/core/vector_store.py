from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from config.settings import DEFAULT_EMBEDDING_MODEL, RETRIEVAL_K


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


def get_retriever(vector_store: FAISS):
    """
    Return a LangChain retriever from the given FAISS vector store.

    Uses RETRIEVAL_K from config/settings.py to control how many chunks
    are returned per query.

    Args:
        vector_store: A FAISS vector store built with build_vector_store.

    Returns:
        A LangChain VectorStoreRetriever configured for similarity search.
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K},
    )
