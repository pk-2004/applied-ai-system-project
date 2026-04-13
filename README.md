# DocuBot

DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  This project has been updated in a way such that when users choose the Naive LLM model, its response will be much shorter than before. 

It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.



---
## Architecture Overview
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOCUBOT SYSTEM DIAGRAM                            │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════╗
║   INPUT LAYER        ║
║  ─────────────────   ║
║  • User Query        ║
║  • 8 Sample Queries  ║
║    (dataset.py)      ║
╚══════════╤═══════════╝
           │
           ▼
╔══════════════════════╗        ╔════════════════════════════╗
║   CLI RUNNER         ║        ║   DOCUMENT STORE           ║
║  (main.py)           ║        ║  (docs/ folder)            ║
║  ─────────────────   ║        ║  ──────────────────────    ║
║  Mode selector:      ║        ║  • AUTH.md                 ║
║  [1] Naive LLM       ║        ║  • API_REFERENCE.md        ║
║  [2] Retrieval Only  ║        ║  • DATABASE.md             ║
║  [3] RAG             ║        ║  • SETUP.md                ║
╚══════════╤═══════════╝        ╚═══════════╤════════════════╝
           │                               │
           │          ┌────────────────────┘
           │          │  load_documents()
           ▼          ▼
╔════════════════════════════════════════════════════════════════════╗
║                         DOCUBOT CORE  (docubot.py)                 ║
║  ─────────────────────────────────────────────────────────────     ║
║                                                                    ║
║   build_index()                    retrieve(query, top_k=3)        ║
║   ───────────                      ────────────────────────        ║
║   word → [filenames]               • Split docs by ## headings     ║
║   (inverted index)                 • Score chunks (word overlap)   ║
║                                    • Filter: score ≥ 2             ║
║                                    • Return top-K ranked snippets  ║
╚════════════════════╤═══════════════════════╤═══════════════════════╝
                     │                       │
          ┌──────────┘                       └──────────────┐
          │ MODE 1: Naive LLM                               │ MODES 2 & 3
          │ (full_corpus_text())                            │ (retrieved snippets)
          ▼                                                 ▼
╔═══════════════════════════╗              ╔══════════════════════════════╗
║   NAIVE LLM PATH          ║              ║   RETRIEVAL OUTPUT  (Mode 2) ║
║  ─────────────────────    ║              ║  ────────────────────────    ║
║  Sends generic prompt:    ║              ║  Returns formatted snippets  ║
║  "Answer this developer   ║              ║  with source filenames —     ║
║   question: {query}"      ║              ║  NO LLM involved             ║
║  (docs are ignored)       ║              ╚══════════════════════════════╝
╚════════════╤══════════════╝
             │                                     │ MODE 3: RAG
             │                                     ▼
             │                      ╔══════════════════════════════════╗
             │                      ║   RAG PATH  (llm_client.py)      ║
             │                      ║  ─────────────────────────────   ║
             │                      ║  Prompt includes:                ║
             │                      ║  • Each snippet + filename label ║
             │                      ║  • "Use only these snippets"     ║
             │                      ║  • Refuse if insufficient info   ║
             └──────────┐           ╚═══════════════╤══════════════════╝
                        │                           │
                        ▼                           ▼
              ╔══════════════════════════════════════════════╗
              ║         GEMINI-2.5-FLASH  (GeminiClient)     ║
              ║       Google Generative AI SDK               ║
              ╚═════════════════════╤════════════════════════╝
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             Generic answer   Grounded answer   "I do not know
             (may hallucinate) (from snippets)   based on docs"

═══════════════════════════════════════════════════════════════════
                   EVALUATION & HUMAN REVIEW LAYER
═══════════════════════════════════════════════════════════════════

╔══════════════════════════════════╗   ╔══════════════════════════════════╗
║  AUTOMATED EVALUATOR             ║   ║  HUMAN REVIEW                    ║
║  (evaluation.py)                 ║   ║  (model_card.md + CLI)           ║
║  ─────────────────────────────   ║   ║  ─────────────────────────────   ║
║  Inputs:                         ║   ║  • Side-by-side mode comparison  ║
║  • 8 sample queries              ║   ║  • Manual query testing via CLI  ║
║  • Expected file mappings        ║   ║  • Failure case analysis         ║
║    (human-curated)               ║   ║  • Design tradeoff reflection    ║
║                                  ║   ╚══════════════════════════════════╝
║  Process:                        ║
║  retrieve() → check if expected  ║
║  file appears in results         ║
║                                  ║
║  Output:                         ║
║  hit_rate = hits / 8 queries     ║
╚══════════════════════════════════╝

---


---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Create a `.env` file in the project root:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls

---

## Sample Interactions

**Mode 1 — Naive LLM**

```
Question: Where is the auth token generated?

Answer:
Auth tokens are typically generated server-side using a secret key after
successful credential validation. The token is then returned to the client
and must be included in subsequent request headers.
```

**Mode 2 — Retrieval Only**

```
Question: Which fields are stored in the users table?

[DATABASE.md]
## Users Table
The users table contains:
- user_id
- email
- password_hash
- joined_at
```

**Mode 3 — RAG**

```
Question: How does a client refresh an access token?

Answer:
Based on AUTH.md and API_REFERENCE.md, a client refreshes an access token
by sending a POST request to /api/refresh with the existing token. The server
validates it and returns a new access token if the refresh token is still valid.
```

---

## Design Decisions


**Naive LLM prompt tuning**  
The original prompt had no length constraint, leading to verbose multi-paragraph answers. Adding "in 2-3 sentences maximum" and "do not include preamble" directly to the prompt reduced response length without changing the model or adding any post-processing.

---

## Testing Summary

**What worked:**  
Retrieval evaluation (`evaluation.py`) reliably measures whether the correct document is returned for known queries. The automated pytest suite (`test_naive_llm.py`) confirmed that after updating the Naive LLM prompt, responses stayed under 100 words and 4 sentences across all five test queries. The no-filler test also caught verbose preamble phrases that crept in before the prompt was tightened.

**What didn't work / limitations:**  
The retrieval scorer uses exact word matching, so queries with synonyms or different phrasing (e.g., "generate a token" vs. "create a token") can miss relevant documents. The Naive LLM mode still occasionally produces answers that are technically correct but not grounded in the actual project docs, because it never reads them. In addition, the Naive LLM can take a while to get responses from since it is fethcing the Gemini API and running a search. 
**What I learned:**  
Being specific to the LLM as much as possible will help in getting the desired results. In this case, a prompt was specified to the LLM to shorten its responses which it did. 

---

## Reflection

The Naive LLM mode produces confident-sounding answers that have nothing to do with the actual project docs, while the RAG mode, using the same underlying model, stays accurate and grounded simply because of how the prompt is structured and what context is included.The most surprising lesson was how much a single prompt affects the output significantly. 

A particular limitation with this system is that the prompt fed into the LLM says to restrict the ouput to 2-3 sentences. As a result, it may disregard the details for queries which require more information. Since the output is contracted, users may just trust the LLM's response as it is convinient to understand. However, maybe a disclaimer can be given warning the user that the responses would be relativley short and may lack sufficient detail. 

I was able to use Claude as a helpful resource to aid me in making the necessary changes while also understanding them. It would give me ideas on how to go about certian tasks and implement them with my approval. There were some areas where the AI had to rectify its changes, such as changing the test cases, but on the whole it has been reliable. 

