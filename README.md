# AI-Driven Post-Earthquake Emergency Material Demand Prediction

India-specific RAG + reasoning LLM system for evidence-grounded post-earthquake emergency material and resource demand prediction.

## Scope

- Post-earthquake emergency intelligence only
- India-specific knowledge base (NCS, NIDM, NDMA, MHA, NDRF, etc.)
- Hybrid retrieval (BM25 + dense + reranker)
- WOA-BP affected population estimation (configurable; no fabricated training data)
- Evidence-grounded structured predictions

## Quick start

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn api.main:app --reload
```

## Documentation

- [Data access and source policy](docs/DATA_ACCESS.md)

## Implementation phases

See project specification for phased rollout (source registry → ingestion → RAG → WOA-BP → API → evaluation).
