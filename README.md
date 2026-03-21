# 🌏 CivicBridge — Multilingual Public Service Navigator

CivicBridge is a multilingual AI-powered assistant that helps citizens understand
public-service support across healthcare, social aid, emergency relief, and family care.
Built for a 2-day hackathon, it is a fully functional RAG-based prototype with multilingual
input/output support.

The **primary experience** is built around four built-in support domains backed by curated
official-style prototype source guides. Users can also upload their own PDF as an optional
advanced mode.

---

## What CivicBridge Does

Citizens select a support domain, ask a question in English, Malay, or Indonesian, and receive:

- A **grounded official answer** based strictly on the selected knowledge base
- A **plain-language explanation** of the official answer
- **Action steps** — numbered, concrete tasks the citizen should take
- A **What Should I Do Next** guide covering eligibility, documents, process, and timeline
- **Source excerpts** showing exactly which parts of the document were used
- A **full translation** of all outputs into the user's chosen language

All answers are grounded in the built-in curated source documents.
No external web search or live government API is used.

---

## Built-In Support Domains

CivicBridge ships with four curated official-style prototype source guides:

| Domain | Program | Source File |
|--------|---------|-------------|
| 🏥 Healthcare Support | National Healthcare Assistance Program (NHAP) | `NHAP_Official_Guide.pdf` |
| 🤝 Social Support | Community Social Support Grant (CSSG) | `CSSG_Official_Guide.pdf` |
| 🚑 Emergency Medical Relief | Emergency Medical Relief Program (EMRP) | `EMRP_Official_Guide.pdf` |
| 👨‍👩‍👧 Family Care Support | Family Care Support Allowance (FCSA) | `FCSA_Official_Guide.pdf` |

Each guide covers program overview, eligibility criteria, required documents,
application steps, processing time, and important conditions.

> **Honesty note:** These are curated official-style prototype guides created for
> hackathon demonstration purposes. They are **not** live government web sources,
> and CivicBridge does **not** perform live web retrieval or query any government API.
> Answers are strictly grounded in the bundled PDF content.

---

## Optional: Custom Document Upload

Users can upload their own official PDF under the **Advanced: Custom Document** expander
in the sidebar. This temporarily overrides the selected built-in domain for that session.
The upload is optional and secondary to the built-in domain experience.

---

## Multilingual Support

| Feature | Languages |
|---------|-----------|
| Question input | English, Malay, Indonesian |
| Interface labels | English, Malay, Indonesian |
| Output translation | English, Malay, Indonesian |

Questions typed in Malay or Indonesian are automatically translated to English internally
before retrieval, ensuring accurate semantic search. All outputs can then be translated
back into the user's chosen language on demand.

---

## Architecture

```
User question (any language)
        │
        ▼
[Input translation → English]   ← skipped if already English
        │
        ▼
[FAISS vector store retrieval]  ← top-K relevant chunks from selected PDF
        │
        ▼
[Grounded answer generation]    ← GPT-4o-mini, context-only, no hallucination
        │
        ├─► [Plain-language simplification]
        ├─► [Action steps extraction]
        └─► [Next steps guide]
                │
                ▼
        [Output translation]    ← on demand, user's chosen language
```

**Stack:**
- LLM: OpenAI GPT-4o-mini (via LangChain)
- Embeddings: OpenAI text-embedding-3-small
- Vector store: FAISS (in-memory, no persistence required)
- PDF parsing: PyMuPDF
- UI: Streamlit

---

## Getting Started
access with : https://public-service-ai.replit.app/
or

### 1. Clone the repository

```bash
git clone https://github.com/traoremakan483-prog/civicbridge-ai.git
cd civicbridge-ai
```

### 2. Install dependencies

```bash
pip install -r civicbridge/requirements.txt
```

### 3. Set your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the app

```bash
streamlit run civicbridge/app.py --server.port 5000
```

Open `http://localhost:5000` in your browser.

---

## Project Structure

```
civicbridge/
├── app.py                    # Main Streamlit application
├── requirements.txt
├── docs/
│   ├── NHAP_Official_Guide.pdf   # Healthcare Support
│   ├── CSSG_Official_Guide.pdf   # Social Support
│   ├── EMRP_Official_Guide.pdf   # Emergency Medical Relief
│   └── FCSA_Official_Guide.pdf   # Family Care Support
├── config/
│   ├── settings.py           # Domain map, language config, UI labels (i18n)
│   └── prompts.py            # All LLM prompt templates
├── core/
│   ├── document_loader.py    # PDF loading and text splitting
│   ├── vector_store.py       # FAISS index builder and retriever
│   ├── rag_pipeline.py       # Grounded answer generation
│   ├── simplifier.py         # Plain-language simplification
│   ├── action_steps.py       # Action steps extraction
│   ├── next_steps.py         # What Should I Do Next guide
│   └── translator.py         # Output translation + question→English
└── ui/
    └── components.py         # Streamlit rendering components
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |

Do **not** commit `.env` to version control. It is listed in `.gitignore`.

---

## Future Improvements

The following are realistic next steps for a production version of CivicBridge:

- **More support domains** — expand to education, housing, employment, and legal aid
- **More languages and dialects** — add Tamil, Mandarin, and regional dialects
- **Real official-source integrations** — connect to live government portals and APIs
- **Voice input and accessibility** — support speech-to-text for non-literate users
- **Mobile-first version** — lightweight PWA or native mobile app
- **Persistent history** — allow users to revisit past questions across sessions
- **Feedback loop** — let users flag answers as helpful or incorrect to improve quality
- **Multi-document retrieval** — query across all domains simultaneously

---

## Hackathon Notes

- Built in 2 days as a civic-tech AI prototype
- Fully portable — no database, no login, no external services beyond OpenAI
- Designed for demonstration of grounded, multilingual public-service navigation
- Grounding is enforced at the prompt level — the LLM answers strictly from
  retrieved document context only, with no access to external knowledge
- `.env` is excluded from the repository; all secrets are managed locally
