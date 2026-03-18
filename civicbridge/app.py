import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config.settings import (
    APP_NAME,
    APP_TAGLINE,
    DOMAIN_DESCRIPTIONS,
    SUPPORT_DOMAINS,
    SUPPORTED_LANGUAGES,
    UI_LABELS,
)
from core.document_loader import load_and_split
from core.vector_store import build_vector_store, get_retriever
from core.rag_pipeline import generate_answer
from core.simplifier import simplify_answer
from core.action_steps import generate_action_steps
from core.next_steps import generate_next_steps
from core.translator import translate_text, translate_to_english
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

/* ── Domain info box ────────────────────────────────────── */
.cb-domain-box {
    background: #f8faff;
    border: 1px solid #dbeafe;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.2rem;
    font-size: 0.88rem;
    color: #1e40af;
    line-height: 1.5;
}
.cb-domain-box strong { color: #1e3a8a; }

/* ── What we support grid ───────────────────────────────── */
.cb-support-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-bottom: 1.2rem;
}
.cb-support-item {
    background: #f8faff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-size: 0.86rem;
    color: #334155;
}
.cb-support-item .cb-item-icon { font-size: 1.1rem; }
.cb-support-item .cb-item-name { font-weight: 600; color: #1e293b; }
.cb-support-item .cb-item-prog { font-size: 0.78rem; color: #64748b; }
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

# ── Session state ──────────────────────────────────────────────────────────────

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "result" not in st.session_state:
    st.session_state.result = None

uploaded_file = None  # default; may be overwritten by the file uploader below

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    # 1. Language selector (drives UI labels + output translation)
    lang_options = list(SUPPORTED_LANGUAGES.keys())
    selected_lang = st.selectbox(
        "🌐 Your Language",
        options=lang_options,
        index=0,
        key="lang_select",
    )
    L = UI_LABELS[selected_lang]

    st.markdown("---")

    # 2. Support domain selector (primary experience)
    st.markdown(f"### {L['domain_header']}")
    st.markdown(
        f"<p style='font-size:0.82rem;color:#94a3b8;margin-top:-0.4rem;margin-bottom:0.6rem;'>"
        f"{L['domain_hint']}</p>",
        unsafe_allow_html=True,
    )
    domain_names = list(SUPPORT_DOMAINS.keys())
    selected_domain = st.selectbox(
        "Support domain",
        options=domain_names,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 3. Advanced: PDF upload (secondary / optional)
    with st.expander(L["advanced_header"], expanded=False):
        st.markdown(
            f"<p style='font-size:0.82rem;color:#64748b;margin-bottom:0.6rem;'>"
            f"{L['advanced_hint']}</p>",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            L["upload_label"],
            type=["pdf"],
            help=L["upload_note"],
        )
        if uploaded_file:
            st.markdown(
                f"<p style='font-size:0.78rem;color:#f59e0b;margin-top:0.3rem;'>"
                f"⚠️ {L['upload_note']}</p>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem;color:#cbd5e1;text-align:center;'>"
        "CivicBridge · Prototype<br>"
        "Curated official-style source guides"
        "</p>",
        unsafe_allow_html=True,
    )

# ── Hero header ────────────────────────────────────────────────────────────────

st.markdown(
    f"""<div class="cb-hero"><div class="cb-hero-title">🌏 {APP_NAME}</div><div class="cb-hero-sub">{APP_TAGLINE}</div><div class="cb-hero-desc">{L['hero_desc']}</div></div><hr class="cb-divider">""",
    unsafe_allow_html=True,
)

if not check_api_key():
    st.stop()

# ── Document loading ───────────────────────────────────────────────────────────

if uploaded_file is not None:
    doc_name = f"upload:{uploaded_file.name}"
    if st.session_state.active_doc_name != doc_name:
        with st.spinner(L["spinner_loading"]):
            chunks = load_document(uploaded_file, filename=uploaded_file.name)
        if chunks:
            try:
                st.session_state.retriever = get_retriever(build_vector_store(chunks))
                st.session_state.active_doc_name = doc_name
                st.session_state.result = None
                st.sidebar.success(f"✅ {uploaded_file.name} loaded ({len(chunks)} chunks)")
            except Exception as e:
                st.sidebar.error(f"Failed to index document: {e}")
        else:
            st.sidebar.error("Could not read the uploaded PDF. Try another file.")
else:
    domain_key = f"domain:{selected_domain}"
    if st.session_state.active_doc_name != domain_key:
        domain_path = SUPPORT_DOMAINS[selected_domain]
        if domain_path.exists():
            with st.spinner(L["spinner_loading"]):
                chunks = load_document(domain_path)
            if chunks:
                try:
                    st.session_state.retriever = get_retriever(build_vector_store(chunks))
                    st.session_state.active_doc_name = domain_key
                    st.session_state.result = None
                except Exception as e:
                    st.sidebar.error(f"Failed to index knowledge base: {e}")
            else:
                st.sidebar.error(f"Could not read {domain_path.name}.")
        else:
            st.sidebar.error(
                f"Knowledge base not found: `docs/{domain_path.name}`. "
                "Please check the `civicbridge/docs/` folder."
            )

# ── What CivicBridge can help with ────────────────────────────────────────────

if st.session_state.retriever is None:
    st.info(L["info_no_doc"])
    st.stop()

# Show active domain info when loaded from a built-in domain
if uploaded_file is None:
    prog_name = DOMAIN_DESCRIPTIONS.get(selected_domain, "")
    st.markdown(
        f'<div class="cb-domain-box">📂 <strong>{selected_domain}</strong>'
        f'<br><span style="color:#3b82f6;">{prog_name}</span>'
        f' &nbsp;·&nbsp; Curated official-style source guide</div>',
        unsafe_allow_html=True,
    )

# ── Question input ─────────────────────────────────────────────────────────────

st.markdown(
    f"<p style='font-size:0.9rem;font-weight:600;color:#334155;margin-bottom:0.3rem;'>"
    f"{L['question_header']}</p>",
    unsafe_allow_html=True,
)
question = st.text_input(
    label="Your question",
    placeholder=L["question_placeholder"],
    label_visibility="collapsed",
)
submit = st.button(L["submit_btn"], type="primary", use_container_width=True)

# ── Pipeline execution ─────────────────────────────────────────────────────────

if submit:
    if not question.strip():
        st.warning(L["warn_empty"])
        st.stop()

    with st.spinner(L["spinner_answering"]):
        try:
            # Translate question to English for retrieval if needed
            question_en = translate_to_english(question, selected_lang)

            rag_result = generate_answer(question_en, st.session_state.retriever)
            answer = rag_result["answer"]
            source_docs = rag_result["source_documents"]
            context = build_context_string(source_docs)

            simple = simplify_answer(answer)
            steps = generate_action_steps(answer)
            next_s = generate_next_steps(question_en, context)

            st.session_state.result = {
                "question": question,
                "question_en": question_en,
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
    translate_label = f"{L['translate_btn_prefix']} {selected_lang} →"
    translate_btn = st.button(translate_label, use_container_width=True)

    if translate_btn:
        if selected_lang == "English":
            st.info(L["already_english"])
        else:
            with st.spinner(L["spinner_translating"]):
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
