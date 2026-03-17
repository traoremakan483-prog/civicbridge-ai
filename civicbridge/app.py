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

CSS = """
<style>
/* ── Cards ─────────────────────────────────────────────── */
.cb-card {
    padding: 1.1rem 1.4rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;
    background: #ffffff;
}
.cb-card-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #94a3b8;
    margin-bottom: 0.55rem;
}
.cb-card-body {
    font-size: 0.97rem;
    color: #1e293b;
    line-height: 1.7;
}
.cb-card-body p { margin: 0; }

/* ── Card accent colours ────────────────────────────────── */
.cb-trust   { background: #f0fdf4; border-left: 4px solid #22c55e; border-color: #dcfce7; }
.cb-answer  { border-left: 4px solid #3b82f6; background: #f8faff; }
.cb-simple  { border-left: 4px solid #8b5cf6; background: #faf8ff; }
.cb-steps   { border-left: 4px solid #10b981; background: #f7fffe; }
.cb-next    { border-left: 4px solid #f59e0b; background: #fffdf5; }
.cb-translate { border-left: 4px solid #0ea5e9; background: #f0f9ff; }

/* ── Trust message ──────────────────────────────────────── */
.cb-trust { display: flex; align-items: flex-start; gap: 0.6rem; }
.cb-trust-icon { font-size: 1rem; flex-shrink: 0; padding-top: 0.05rem; }
.cb-trust-text { font-size: 0.9rem; color: #15803d; line-height: 1.55; }

/* ── Action steps ───────────────────────────────────────── */
.cb-step-list { display: flex; flex-direction: column; gap: 0.55rem; }
.cb-step-row  { display: flex; align-items: flex-start; gap: 0.75rem; }
.cb-step-num  {
    min-width: 1.6rem; height: 1.6rem;
    background: #10b981; color: #fff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}
.cb-step-text { font-size: 0.96rem; color: #1e293b; padding-top: 0.15rem; line-height: 1.55; }

/* ── Next-steps fields ──────────────────────────────────── */
.cb-field-row   { margin-bottom: 0.75rem; }
.cb-field-row:last-child { margin-bottom: 0; }
.cb-field-label {
    font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: #92400e; margin-bottom: 0.2rem;
}
.cb-field-value { font-size: 0.95rem; color: #1e293b; line-height: 1.6; }

/* ── Translation fields ─────────────────────────────────── */
.cb-translate .cb-field-label { color: #0369a1; }

/* ── Source / Evidence label ────────────────────────────── */
.cb-section-label {
    font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: #94a3b8; margin-bottom: 0.4rem;
}
.cb-excerpt-text {
    font-size: 0.88rem; color: #475569;
    line-height: 1.65; font-style: italic;
    border-left: 3px solid #cbd5e1;
    padding-left: 0.75rem; margin-top: 0.4rem;
}

/* ── Hero ───────────────────────────────────────────────── */
.cb-hero {
    text-align: center;
    padding: 1.8rem 0 0.5rem 0;
}
.cb-hero-title {
    font-size: 2.2rem; font-weight: 800;
    color: #1e293b; letter-spacing: -0.02em;
}
.cb-hero-sub {
    font-size: 1rem; color: #64748b; margin-top: 0.2rem;
}
.cb-hero-desc {
    font-size: 0.88rem; color: #94a3b8;
    margin-top: 0.5rem; max-width: 520px;
    margin-left: auto; margin-right: auto;
    line-height: 1.55;
}
.cb-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.2rem 0; }
</style>
"""


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


# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(page_title=APP_NAME, page_icon="🌏", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# ── Hero header ────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="cb-hero">
        <div class="cb-hero-title">🌏 {APP_NAME}</div>
        <div class="cb-hero-sub">{APP_TAGLINE}</div>
        <div class="cb-hero-desc">
            Ask questions about public healthcare and social-aid services.
            Get grounded answers, plain explanations, and clear action steps —
            in English, Malay, or Indonesian.
        </div>
    </div>
    <hr class="cb-divider">
    """,
    unsafe_allow_html=True,
)

if not check_api_key():
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📂 Document")
    uploaded_file = st.file_uploader(
        "Upload an official PDF",
        type=["pdf"],
        help="Upload any official public-service document to query.",
    )
    st.markdown(
        "<p style='font-size:0.82rem;color:#94a3b8;margin-top:0.4rem;'>"
        "Supported: any text-based PDF.<br>"
        "If no file is uploaded, a sample healthcare document loads automatically."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🌐 Language")
    lang_options = list(SUPPORTED_LANGUAGES.keys())
    selected_lang = st.selectbox(
        "Translation language",
        options=lang_options,
        index=0,
        label_visibility="collapsed",
    )
    st.markdown(
        "<p style='font-size:0.82rem;color:#94a3b8;margin-top:0.4rem;'>"
        "Select a language, then click <strong>Translate</strong> after getting an answer."
        "</p>",
        unsafe_allow_html=True,
    )

# ── Session state ──────────────────────────────────────────────────────────────

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "result" not in st.session_state:
    st.session_state.result = None

# ── Document loading ───────────────────────────────────────────────────────────

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
                st.sidebar.success("📄 Sample document loaded")
        else:
            st.sidebar.warning(
                "No sample document found at `docs/sample_document.pdf`. "
                "Please upload a PDF to get started."
            )

if st.session_state.retriever is None:
    st.info("👈 Upload a PDF in the sidebar — or add a sample document to `docs/` — to get started.")
    st.stop()

# ── Question input ─────────────────────────────────────────────────────────────

st.markdown(
    "<p style='font-size:0.9rem;font-weight:600;color:#334155;margin-bottom:0.3rem;'>"
    "Ask a question about the document</p>",
    unsafe_allow_html=True,
)
question = st.text_input(
    label="Your question",
    placeholder="e.g. Who is eligible for healthcare assistance?",
    label_visibility="collapsed",
)
submit = st.button("Get Answer →", type="primary", use_container_width=True)

# ── Pipeline execution ─────────────────────────────────────────────────────────

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

# ── Results display ────────────────────────────────────────────────────────────

if st.session_state.result:
    r = st.session_state.result

    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    render_trust_message()

    render_official_answer(r["answer"])
    render_simple_explanation(r["simple"])
    render_action_steps(r["steps"])
    render_next_steps(r["next_steps"])

    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    render_source_excerpts(r["source_docs"])

    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    translate_btn = st.button(
        f"Translate into {selected_lang} →",
        use_container_width=True,
    )

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
                    render_translation_output(translated, language=selected_lang)
                except Exception as e:
                    st.error(f"Translation failed: {e}")
