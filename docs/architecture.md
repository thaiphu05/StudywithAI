# Architecture Overview

## Core Flows

1. Prompt Upload (`/uploads/problem`)
- Input: `.docx` or image
- Validation and text extraction via parser/OCR

2. Essay Upload (`/uploads/essay`)
- Input: `.docx` or image
- Validation and text extraction via parser/OCR

3. Evaluation (`/results/evaluate`)
- Input: `account_id`, prompt file, essay file
- Token estimation and account budget check
- Score + explanation output (overall and per criterion)

## Orchestration and Token Management

The `EvaluationOrchestrator` coordinates:

- file persistence (`save_upload`)
- content extraction (`extract_text`)
- token estimation and reservation
- scoring output generation

The `AccountService` manages:

- account creation/retrieval
- token limit enforcement
- running token usage per account

## Future Extensions

- Replace in-memory account store with PostgreSQL/Redis.
- Replace OCR placeholder with Tesseract or cloud OCR.
- Replace scoring placeholder with LLM-based evaluator.
- Add auth (JWT/API key), rate limiting, and audit logs.
