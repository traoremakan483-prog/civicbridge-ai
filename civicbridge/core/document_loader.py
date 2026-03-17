import fitz
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def load_pdf(file_path: str) -> list[Document]:
    """
    Load a PDF file and extract its text page by page using PyMuPDF.

    Each page that contains text becomes a LangChain Document with metadata
    recording the source file and page number. Empty pages are skipped.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        A list of LangChain Document objects, one per non-empty page.

    Raises:
        FileNotFoundError: If the PDF path does not exist.
        ValueError: If the PDF contains no extractable text.
    """
    try:
        pdf = fitz.open(file_path)
    except Exception as e:
        raise FileNotFoundError(f"Could not open PDF at '{file_path}': {e}")

    pages: list[Document] = []
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text().strip()
        if not text:
            continue
        pages.append(
            Document(
                page_content=text,
                metadata={"source": str(file_path), "page": page_num + 1},
            )
        )

    pdf.close()

    if not pages:
        raise ValueError(
            f"No extractable text found in '{file_path}'. "
            "The PDF may be scanned or image-only."
        )

    return pages


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split a list of Documents into smaller chunks suitable for retrieval.

    Uses RecursiveCharacterTextSplitter with chunk size and overlap values
    from config/settings.py. Source and page metadata are preserved on every
    chunk.

    Args:
        documents: List of LangChain Document objects (e.g. from load_pdf).

    Returns:
        A list of smaller Document chunks ready for embedding and indexing.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_split(file_path: str) -> list[Document]:
    """
    Convenience function: load a PDF and return split chunks in one call.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        A list of Document chunks ready for vector store ingestion.
    """
    pages = load_pdf(file_path)
    return split_documents(pages)
