# PolicyWise AI — Enterprise Policy Q&A (Week 2)

A Python LangChain + Pinecone + LangGraph + Groq RAG demo with a Streamlit interface and a 15-question evaluation harness.

> **Repository status:** This is a reconstructed **reference implementation** created from the user's description and logs, **not an exact export** from the live Replit project. For an exact submission reflecting 75 passing tests and actual execution, export/publish your **original Replit repository** instead. No unverified scores are claimed for this code.

## Architecture

`PDF briefs -> PyPDFLoader -> RecursiveCharacterTextSplitter -> MiniLM embeddings -> Pinecone (policywise-v1) -> retrieve top 5 -> LangGraph evidence gate -> Groq LLM -> citations or abstention -> Streamlit`

## Setup

1. Create Python 3.11/3.12 environment; `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` locally or set **Replit Secrets** (`PINECONE_API_KEY`, `GROQ_API_KEY`). Never commit secrets.
3. Create a **Pinecone dense index**, 384 dimensions, cosine metric, named `policywise-index`. Use your own embeddings (not Pinecone integrated embeddings).
4. Place the eight approved GitLab *policy briefs* in `data/policies/`. They are **independent summaries**, not authoritative GitLab policy copies. If you are using a previously populated index, **be aware that this reconstructed chunk-ID algorithm may produce different IDs**. Do not upload over a valuable existing namespace without confirming IDs or using a new namespace.
5. Run:

```bash
python -m src.ingest
python -m src.upload
python -m src.test_retrieval "What does the GitLab paid time off policy say?"
python -m src.test_rag "What does the GitLab paid time off policy say?"
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 5000 --server.headless true
pytest -q
```

## Evaluation

`evaluation/questions.csv` contains the actual 15 question prompts from the user-provided report, but **ground-truth evidence labels are intentionally blank**; human validation is required. Run `python -m evaluation.run` to capture a **new** live result table, fill the manual review fields, then `python -m evaluation.rescore`. Current scripts do not claim automatic faithfulness measurement. See `docs/RESULTS.md` for historical result provenance.

## Known limitations

- The LangGraph evidence check is LLM-based and can reject answerable questions or consume rate-limited API calls.
- The generated citation ID whitelist ensures only approved source chunks are cited; it does **not** prove that each sentence is semantically supported. Human evaluation is required.
- The scope is small (8 one-page source briefs / 16 historical vectors). Eligibility, location-specific benefits, and employee-specific data are intentionally out of scope.
- This minimal reference implementation does not reproduce the original project's retry/backoff layer, human-ground-truth dataset, or 75 original tests.
- The local HuggingFace embedding model can be slow to initialize on Replit.
- Dependencies use major-version compatibility ranges; for a reproducible submission, commit a lockfile from your working environment.

## Privacy and safe publishing

Never commit `.env`, API keys, employer-private records, or raw PDFs unless you have redistribution rights. Use official GitLab handbook links as attribution and distinguish the briefs from official policies.
