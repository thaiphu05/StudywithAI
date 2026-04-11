# IELTS Writing Task 2 Evaluation System

This repository is scaffolded for 3 main functions:

1. Upload IELTS Writing Task 2 prompt (`.docx` or image)
2. Upload candidate essay (`.docx` or image)
3. Return explanation + estimated band score and detailed feedback

It also includes account orchestration for:

- user/account lifecycle
- token budget and usage tracking
- per-account limits

## Project Structure

```text
src/
  main.py
  api/
    dependencies.py
    routes/
      health.py
      uploads.py
      results.py
      accounts.py
  core/
    config.py
  domain/
    models.py
  schemas/
    upload.py
    result.py
    account.py
  services/
    parser_service.py
    ocr_service.py
    scoring_service.py
    orchestration_service.py
    account_service.py

tests/
  test_health.py

docs/
  architecture.md
```

## Quick Start

1. Create virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run API:

```bash
uvicorn src.main:app --reload
```

4. Open docs:

- http://127.0.0.1:8000/docs

## Notes

- Current implementation is a scaffold with placeholders where external AI scoring/OCR providers should be integrated.
- File upload supports `.docx`, `.png`, `.jpg`, `.jpeg`.

## Connect Neon Database

1. Create a project/database in Neon.
2. Copy the connection string and set `DATABASE_URL` in your `.env`:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start app:

```bash
uvicorn src.main:app --reload
```

On startup, app initializes the `accounts` table automatically.
