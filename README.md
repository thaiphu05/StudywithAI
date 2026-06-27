# IELTS Evaluation System

FastAPI backend for evaluating IELTS Writing Task 2 and Speaking responses. Supports two scoring engines — a ModernBERT-base regression model (default) or Google Gemini LLM — plus account management, token budgeting, and evaluation history.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload          # dev server on :8000
pytest                                 # health-check test
```

Requires a `.env` file — see [Configuration](#configuration).

## Features

- **Writing Evaluation** — Upload a prompt + essay (.docx or image). Scored per the 4 IELTS criteria (Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range and Accuracy) plus overall band. Two modes:
  - **Default**: ModernBERT-base regression model → predicts band scores directly
  - **LLM** (`?MLmodel_type=true`): Google Gemini → detailed feedback with comments, examples, and band scores
- **Speaking Evaluation** — Upload audio (mp3/wav/webm/m4a). Speech-to-text via faster-whisper, then LLM evaluation for Lexical Resource and Grammatical Range and Accuracy.
- **Account System** — JWT auth with bcrypt. Three tiers (normal, plus, pro) with token budgets (5K / 50K / 200K) that reset every 30 days.
- **History** — Per-account evaluation history with plan-based retention limits.

## API

All routes under `/api/v1/`. Most require JWT authentication (Bearer token).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | — | Login (email or phone + password) → JWT |
| POST | `/auth/logout` | — | Logout |
| POST | `/accounts` | — | Create account |
| GET | `/accounts/{id}` | user/admin | Get account details |
| POST | `/results/writing/{account_id}` | user/admin | Evaluate writing submission |
| POST | `/results/speaking/{account_id}` | user/admin | Evaluate speaking submission |
| GET | `/history` | user/admin | List evaluation history |
| GET | `/history/{id}` | user/admin | Get history entry |
| POST | `/history` | user/admin | Create history entry |
| DELETE | `/history/{id}` | user/admin | Delete history entry |
| GET | `/health` | admin | Health check |
| POST | `/uploads` | — | Upload prompt + essay (stub — does not score) |

### Writing Evaluation

Submit a prompt and essay as `multipart/form-data`:

```
POST /api/v1/results/writing/{account_id}
Fields: problem_file, essay_file
Query:  ?MLmodel_type=true   (uses Gemini instead of model)
```

Returns `EvaluationResult` with `overall_band`, `summary`, `criteria[]`, and `estimated_tokens_used`.

### Speaking Evaluation

```
POST /api/v1/results/speaking/{account_id}
Fields: audio_file
Query:  ?topic=...
```

## Project Structure

```
src/
├── main.py                      # FastAPI app, CORS, router registration
├── api/
│   ├── dependencies.py          # DI singletons, JWT validation
│   └── routes/                  # auth, accounts, health, history, results, uploads
├── core/config.py               # Settings from .env
├── db/
│   ├── base.py                  # SQLAlchemy declarative base
│   ├── models.py                # ORM: AccountDB, StudyHistoryDB
│   └── session.py               # Engine, session factory, init_db()
├── domain/models.py             # Domain dataclasses
├── models/
│   ├── WR_model.py              # ModernBERT + regression head (PyTorch)
│   ├── LLM_model.py             # Google Gemini wrapper
│   ├── OCR_model.py             # PaddleOCR wrapper
│   └── STT_model.py             # faster-whisper wrapper
├── schemas/                     # Pydantic models for request/response
├── services/
│   ├── account_service.py       # Account CRUD, token reservation/release
│   ├── auth_service.py          # Login, JWT generation
│   ├── history_service.py       # History CRUD with plan-based trimming
│   ├── ocr_service.py           # Image → text
│   ├── parser_service.py        # .docx → text
│   ├── scoring_writing_service.py   # Model-based + LLM-based writing scoring
│   ├── scoring_speaking_service.py  # STT + LLM speaking scoring
│   ├── stt_service.py           # Audio → text
│   └── orchestration_service.py # Main coordinator for evaluations
├── utils/
│   ├── image.py                 # Image pre/post processing
│   ├── llm.py                   # LLM output parser
│   └── writing.py               # Model output formatter
tests/
└── test_health.py
```

## Configuration

Set these in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | JWT signing key (**required**) |
| `WRITING_MODEL_PATH` | `./modernbert_best_model.pth` | Writing model checkpoint |
| `LLM_API_KEY` | — | Google Gemini API key |
| `OCR_API_KEY` | — | API key for cloud OCR |
| `OCR_SELF_HOST` | `false` | Use local PaddleOCR instead of API |
| `DATABASE_URL` | `sqlite:///./app.db` | PostgreSQL or SQLite |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `720` | JWT token expiry |

## Account Types

| Type | Token Budget | History Limit | Plan |
|------|-------------|---------------|------|
| normal | 5,000 | 3 entries | indefinite |
| plus | 50,000 | 10 entries | 30 days |
| pro | 200,000 | 100 entries | 30 days |

Tokens reset every 30 days. Expired plus/pro accounts downgrade to normal.

## Known Issues

- **OpenSSL 3.5+**: `SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED` when downloading ModernBERT-base. Fix: `pip install urllib3==1.26.18`.
- **Model checkpoint required**: The server crashes on startup if `WRITING_MODEL_PATH` is missing.
- **Upload route** (`POST /uploads`) extracts text but does not trigger scoring. Use `/results/writing/{account_id}` for full evaluation.
- **Frontend**: Not yet wired — `write-genius-20/` directory is a placeholder.
- **Speaking**: LLM-only evaluation (no model-based path yet).

## Production

Set `DATABASE_URL` to a PostgreSQL connection string (Neon recommended). Configure `SECRET_KEY`, `LLM_API_KEY`, and `WRITING_MODEL_PATH` in the environment.
