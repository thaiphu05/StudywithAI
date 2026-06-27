# AGENTS.md

## Project overview

IELTS Writing Task 2 evaluation system. FastAPI backend (`src/main.py`) + React frontend (`write-genius-20/`). Two scoring paths: ModernBERT-base regression model (default) or Google Gemini LLM (pass `?MLmodel_type=true`).

## Quick start

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload          # dev server on :8000
pytest                                 # single health-check test exists
```

## Architecture

- Routes at `/api/v1/{auth,accounts,health,uploads,results,history}`
- DB auto-initialized on startup (SQLite default, PostgreSQL via `DATABASE_URL`)
- Services are singletons created in `src/api/dependencies.py`
- CORS: localhost:5173, :8080
- Health endpoint requires admin token

## Important gotchas

- **OpenSSL 3.5+ bug with HuggingFace**: `SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED` when downloading ModernBERT-base. Fix: `pip install urllib3==1.26.18`.
- **Model checkpoint required**: `ScoringWritingService` crashes on startup if `WRITING_MODEL_PATH` (default `./modernbert_best_model.pth`) is missing. Set in `.env` or place file at expected path.
- **LLM evaluation** uses Google Gemini (`google-genai`). Set `LLM_API_KEY` in `.env`.
- **OCR** uses PaddleOCR. Set `OCR_API_KEY` for Gemini-based OCR or `OCR_SELF_HOST=true` for local.
- **Auth**: JWT with bcrypt. `SECRET_KEY` must be set. Tokens expire per `ACCESS_TOKEN_EXPIRE_MINUTES` (default 720 min).
- **Upload route** (`POST /api/v1/uploads`) is a stub — extracts text from files but doesn't score them. Use `POST /api/v1/results/writing/{account_id}` for full evaluation.
- **No speaking endpoint** yet; commented out in `src/api/routes/results.py`.
- **FE** (`write-genius-20/`) uses Bun and mock data — not wired to BE.

## Account / token system

- Account types: `normal` (5K tokens), `plus` (50K), `pro` (200K)
- Token budgets reset with plan duration (30 days). Expired `pro`/`plus` downgrade to `normal`.
- History limits per plan: normal=3, plus=10, pro=100 (pro keeps all, others trim oldest)

## Production

Set `DATABASE_URL` to a PostgreSQL connection string (Neon recommended).
