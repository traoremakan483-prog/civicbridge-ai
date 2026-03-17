# CivicBridge

**CivicBridge** is a multilingual public service navigator grounded in official documents. It helps citizens, migrants, and low-digital-literacy users understand healthcare and social-aid services in a simple, actionable, and trustworthy way — in English, Malay, and Indonesian.

> All answers are grounded only in uploaded official documents. CivicBridge never fabricates information.

---

## MVP Features

- **Two bundled demo documents** ready to use out of the box:
  - National Healthcare Assistance Program (NHAP)
  - Community Social Support Grant (CSSG)
- **Upload any official PDF** to query your own document instead
- **Ask a question** about a public service in plain language
- **Receive a structured response** with five clear sections:
  - Official Answer — grounded directly in the document
  - Simple Explanation — plain-language rewrite for any reading level
  - Action Steps — 3 to 5 concrete things to do
  - What Should I Do Next? — who can apply, documents needed, step-by-step process, estimated time, and important warnings
  - Source / Evidence — the exact excerpt used to generate the answer
- **Translate** any output to English, Malay, or Indonesian with one click
- **Trust indicator** on every response confirming the answer is document-grounded

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/civicbridge.git
cd civicbridge
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Open `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key. Get one at https://platform.openai.com/api-keys |

---

## Project Structure

```
civicbridge/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── settings.py         # App constants, model names, language config
│   └── prompts.py          # All LLM prompt templates
├── core/
│   ├── document_loader.py  # PDF parsing and text chunking
│   ├── vector_store.py     # FAISS index build and search
│   ├── rag_pipeline.py     # Retrieval and grounded answer generation
│   ├── simplifier.py       # Plain-language simplification
│   ├── action_steps.py     # 3–5 actionable steps extraction
│   ├── next_steps.py       # "What Should I Do Next?" feature
│   └── translator.py       # EN / Malay / Indonesian translation
├── ui/
│   └── components.py       # Reusable Streamlit response card blocks
└── docs/
    └── sample_document.pdf # Bundled official healthcare/social-aid document
```

---

## Important Note on Grounding

CivicBridge answers questions strictly from the content of uploaded official documents. It will not speculate, fill in gaps, or use external knowledge. If information is not found in the document, the app will say so clearly. This design minimises hallucination risk and ensures every answer can be traced to a verified source.

---

## Tech Stack

- **UI:** Streamlit
- **LLM + Embeddings:** OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)
- **RAG:** LangChain + FAISS (in-memory)
- **PDF Parsing:** PyMuPDF
- **Secrets:** python-dotenv
