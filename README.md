# 🌏 CivicBridge — Multilingual Public Service Navigator

CivicBridge is a multilingual AI-powered assistant that helps citizens understand
public-service support across healthcare, social aid, emergency relief, and family care.
Built for a 2-day hackathon, it is a fully functional RAG-based prototype with multilingual
input/output support.

---

## What CivicBridge Does

Citizens ask questions in **English, Malay, or Indonesian** and receive:

- A **grounded official answer** based strictly on the selected knowledge base
- A **plain-language explanation** of the official answer
- **Action steps** — numbered, concrete tasks the citizen should take
- A **What Should I Do Next** guide with eligibility, documents, process, and timeline
- **Source excerpts** showing which parts of the document were used
- A **full translation** of all outputs into the user's language

All answers are grounded in the built-in curated source documents.
No external web search or knowledge is used.

---

## Built-In Support Domains

CivicBridge includes four curated official-style prototype source guides:

| Domain | Program |
|--------|---------|
| 🏥 Healthcare Support | National Healthcare Assistance Program (NHAP) |
| 🤝 Social Support | Community Social Support Grant (CSSG) |
| 🚑 Emergency Medical Relief | Emergency Medical Relief Program (EMRP) |
| 👨‍👩‍👧 Family Care Support | Family Care Support Allowance (FCSA) |

> **Note:** These are curated official-style prototype guides created for hackathon
> demonstration purposes. They are not live government web sources.

---

## Optional: Custom Document Upload

Users can upload their own official PDF under the **Advanced: Custom Document** section
in the sidebar. This temporarily overrides the selected built-in domain for that session.

---

## Multilingual Support

| Feature | Languages |
|---------|-----------|
| Question input | English, Malay, Indonesian |
| UI labels / interface | English, Malay, Indonesian |
| Output translation | English, Malay, Indonesian |

Questions typed in Malay or Indonesian are automatically translated to English internally
before retrieval, then translated back to the user's chosen language for output.

---

## Architecture

```
User question (any language)
        │
        ▼
[Input translation → English]  ← skipped if already English
        │
        ▼
[FAISS vector store retrieval]  ← top-K relevant chunks from PDF
        │
        ▼
[Grounded answer generation]  ← GPT-4o-mini, context-only
        │
        ├─► [Plain-language simplification]
        ├─► [Action steps extraction]
        └─► [Next steps guide]
                │
                ▼
        [Output translation]  ← on demand, user's language
```

- **LLM**: OpenAI GPT-4o-mini (via LangChain)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector store**: FAISS (in-memory, no persistence required)
- **PDF parsing**: PyMuPDF
- **UI**: Streamlit

---

## Getting Started

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
│   ├── NHAP_Official_Guide.pdf
│   ├── CSSG_Official_Guide.pdf
│   ├── EMRP_Official_Guide.pdf
│   └── FCSA_Official_Guide.pdf
├── config/
│   ├── settings.py           # Domain map, language config, UI labels
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

## Hackathon Notes

- Built in 2 days as a civic-tech AI prototype
- Fully portable — no database, no login, no external services beyond OpenAI
- Designed for demonstration of grounded, multilingual public-service navigation
- Grounding is enforced at the prompt level — the LLM is instructed to answer
  strictly from retrieved context only
