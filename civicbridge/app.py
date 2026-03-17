import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config.settings import APP_NAME, APP_TAGLINE, SAMPLE_DOCUMENT_PATH, SUPPORTED_LANGUAGES
from core.document_loader import load_and_split
from core.vector_store import build_vector_store, get_retriever
from core.rag_pipeline import generate_answer
from core.simplifier import simplify_answer
from core.action_steps import generate_action_steps
from core.next_steps import generate_next_steps
from core.translator import translate_text
from ui.components import (
    render_trust_message,
    render_official_answer,
    render_simple_explanation,
    render_action_steps,
    render_next_steps,
    render_source_excerpts,
    render_translation_output,
)


def check_api_key() -> bool:
    """Return True if OPENAI_API_KEY is set, otherwise show an error."""
    if not os.environ.get("OPENAI_API_KEY"):
        st.error(
            "OpenAI API key not found. "
            "Create a `.env` file with `OPENAI_API_KEY=your_key_here` "
            "and restart the app."
        )
        return False
    return True


def load_document(file_path_or_bytes, filename: str = "") -> list:
    """
    Load and split a document from a file path or uploaded bytes.

    Returns a list of document chunks, or an empty list on failure.
    """
    try:
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            return load_and_split(str(file_path_or_bytes))
        tmp_path = f"/tmp/{filename}"
        with open(tmp_path, "wb") as f:
            f.write(file_path_or_bytes.read())
        return load_and_split(tmp_path)
    except FileNotFoundError:
        return []
    except ValueError as e:
        st.warning(str(e))
        return []


def build_context_string(source_documents: list) -> str:
    """Combine retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in source_documents)


st.set_page_config(page_title=APP_NAME, page_icon="🌏", layout="centered")

st.title(f"🌏 {APP_NAME}")
st.caption(APP_TAGLINE)
st.markdown("---")

if not check_api_key():
    st.stop()

with st.sidebar:
    st.header("📂 Document")
    uploaded_file = st.file_uploader(
        "Upload an official PDF",
        type=["pdf"],
        help="Upload any official public-service document to query.",
    )
    st.markdown("---")
    st.caption(
        "No document? The app loads a sample healthcare/social-aid document "
        "automatically on startup."
    )

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "result" not in st.session_state:
    st.session_state.result = None

if uploaded_file is not None:
    doc_name = uploaded_file.name
    if st.session_state.active_doc_name != doc_name:
        with st.spinner(f"Processing **{doc_name}**…"):
            chunks = load_document(uploaded_file, filename=doc_name)
        if chunks:
            st.session_state.retriever = get_retriever(build_vector_store(chunks))
            st.session_state.active_doc_name = doc_name
            st.session_state.result = None
            st.sidebar.success(f"✅ {doc_name} loaded ({len(chunks)} chunks)")
        else:
            st.sidebar.error("Could not read the uploaded PDF. Try another file.")
else:
    if st.session_state.active_doc_name != "sample":
        if SAMPLE_DOCUMENT_PATH.exists():
            with st.spinner("Loading sample document…"):
                chunks = load_document(SAMPLE_DOCUMENT_PATH)
            if chunks:
                st.session_state.retriever = get_retriever(build_vector_store(chunks))
                st.session_state.active_doc_name = "sample"
                st.sidebar.info("📄 Using sample document")
        else:
            st.sidebar.warning(
                "No sample document found at `docs/sample_document.pdf`. "
                "Please upload a PDF to get started."
            )

if st.session_state.retriever is None:
    st.info("👈 Upload a PDF document using the sidebar to get started.")
    st.stop()

st.markdown("#### Ask a question")
question = st.text_input(
    label="Your question",
    placeholder="e.g. Who is eligible for healthcare assistance?",
    label_visibility="collapsed",
)
submit = st.button("Get Answer", type="primary", use_container_width=True)

if submit:
    if not question.strip():
        st.warning("Please enter a question before submitting.")
        st.stop()

    with st.spinner("Searching the document and generating your answer…"):
        try:
            rag_result = generate_answer(question, st.session_state.retriever)
            answer = rag_result["answer"]
            source_docs = rag_result["source_documents"]
            context = build_context_string(source_docs)

            simple = simplify_answer(answer)
            steps = generate_action_steps(answer)
            next_s = generate_next_steps(question, context)

            st.session_state.result = {
                "question": question,
                "answer": answer,
                "simple": simple,
                "steps": steps,
                "next_steps": next_s,
                "source_docs": source_docs,
                "context": context,
            }
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

if st.session_state.result:
    r = st.session_state.result
    st.markdown("---")
    render_trust_message()
    st.markdown("")

    render_official_answer(r["answer"])
    st.markdown("---")

    render_simple_explanation(r["simple"])
    st.markdown("---")

    render_action_steps(r["steps"])
    st.markdown("---")

    render_next_steps(r["next_steps"])
    st.markdown("---")

    render_source_excerpts(r["source_docs"])
    st.markdown("---")

    st.markdown("#### 🌐 Translate outputs")
    lang_options = list(SUPPORTED_LANGUAGES.keys())
    selected_lang = st.selectbox(
        "Select language",
        options=lang_options,
        index=0,
        label_visibility="collapsed",
    )
    translate_btn = st.button("Translate", use_container_width=True)

    if translate_btn:
        if selected_lang == "English":
            st.info("Outputs are already in English.")
        else:
            with st.spinner(f"Translating into {selected_lang}…"):
                try:
                    blocks_to_translate = {
                        "Official Answer": r["answer"],
                        "Simple Explanation": r["simple"],
                        "Action Steps": "\n".join(
                            f"{i+1}. {s}" for i, s in enumerate(r["steps"])
                        ),
                    }
                    next_s = r["next_steps"]
                    for label, key in [
                        ("Who can apply", "who_can_apply"),
                        ("Required documents", "required_documents"),
                        ("Step-by-step process", "step_by_step_process"),
                        ("Estimated processing time", "estimated_processing_time"),
                        ("Important notes", "important_notes"),
                    ]:
                        value = next_s.get(key, "")
                        if value and value != "Not specified in the document.":
                            blocks_to_translate[label] = value

                    translated = {
                        label: translate_text(text, selected_lang)
                        for label, text in blocks_to_translate.items()
                    }
                    st.markdown("---")
                    render_translation_output(translated)
                except Exception as e:
                    st.error(f"Translation failed: {e}")
