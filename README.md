# AI Knowledge API

A Flask API for storing knowledge documents, splitting them into chunks, and answering questions against a selected document with OpenAI.

## Features

- Health check endpoint
- Document ingestion with `title` and full `content`
- Automatic document chunking on create
- SQLAlchemy-backed persistence for documents and chunks (SQLite for local dev, PostgreSQL for production)
- Question answering endpoint that retrieves relevant chunks and sends them to OpenAI via the Responses API

## Tech Stack

- Python 3.13
- Flask 3
- Flask-SQLAlchemy / SQLAlchemy
- psycopg2 (PostgreSQL driver)
- boto3 (AWS S3 integration)
- python-dotenv
- OpenAI Python SDK v2 (Responses API)
- pytest

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   │   ├── chunk.py
│   │   └── document.py
│   ├── routes/
│   │   ├── documents.py
│   │   ├── health.py
│   │   └── questions.py
│   ├── services/
│   │   └── retrieval_service.py
│   └── utils/
│       └── text_splitter.py
├── scripts/
│   └── init_db.py
├── terraform/              # AWS infrastructure (EC2, S3, security groups)
├── requirements.txt
└── run.py                  # Entry point
```

## How It Works

1. A document is created through `POST /documents` with a title and raw content.
2. The API splits the content into word-based chunks (120 words each by default).
3. Both the document and its chunks are stored in the database.
4. `POST /ask` scores stored chunks by keyword overlap with the question, selects the top 3, and sends them as context to OpenAI (`gpt-5.4-mini` via the Responses API).
5. The response returns an answer plus the source chunks used to generate it.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create a .env file in the project root (see Environment Variables below)

# Initialize the database (creates tables)
python scripts/init_db.py

# Start the API
python run.py
```

The server starts at `http://localhost:5000`.

## Docker

```bash
# Build the image
docker build -t ai-knowledge .

# Run the container
docker run --env-file .env -p 5000:5000 ai-knowledge
```

## Environment Variables

`run.py` loads environment variables from a `.env` file in the project root.

| Variable        | Default         | Required          |
|-----------------|-----------------|-------------------|
| `SECRET_KEY`    | `dev-secret-key`| No                |
| `FLASK_DEBUG`   | `false`         | No                |
| `DATABASE_URL`  | `sqlite:///app.db` | No (SQLite is used when unset) |
| `OPENAI_API_KEY`| —               | Yes, for `POST /ask` |

Example `.env`:

```bash
SECRET_KEY=local-dev-secret
FLASK_DEBUG=true
DATABASE_URL=sqlite:///app.db
OPENAI_API_KEY=your-openai-api-key
```

For PostgreSQL set `DATABASE_URL` to a `postgresql://` connection string; `psycopg2-binary` is included in the dependencies.

## Data Model

### `Document`

| Column | Type |
|--------|------|
| `id` | Integer PK |
| `title` | String(255) |
| `content` | Text |
| `s3_key` | String(500), nullable |
| `created_at` | DateTime (UTC) |

### `DocumentChunk`

| Column | Type |
|--------|------|
| `id` | Integer PK |
| `document_id` | Integer FK → documents.id |
| `chunk_index` | Integer |
| `content` | Text |
| `created_at` | DateTime (UTC) |

## API Reference

Base URL: `http://127.0.0.1:5000`

---

### `GET /health`

```bash
curl http://127.0.0.1:5000/health
```

Response `200`:
```json
{"status": "ok"}
```

---

### `POST /documents`

Creates a document and its chunks.

```bash
curl -X POST http://127.0.0.1:5000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Password reset guide",
    "content": "Step 1: Go to the sign-in page. Step 2: Click Forgot Password. Step 3: Follow the email instructions."
  }'
```

Response `201`:
```json
{
  "id": 1,
  "title": "Password reset guide",
  "chunk_count": 1,
  "s3_key": null,
  "created_at": "2026-04-28T20:00:00+00:00"
}
```

---

### `GET /documents`

Returns all documents ordered by newest first.

```bash
curl http://127.0.0.1:5000/documents
```

Response `200`:
```json
[
  {
    "id": 1,
    "title": "Password reset guide",
    "content": "Step 1: Go to the sign-in page...",
    "s3_key": null,
    "created_at": "2026-04-28T20:00:00+00:00"
  }
]
```

---

### `PATCH /documents/<document_id>`

Updates only the document title.

```bash
curl -X PATCH http://127.0.0.1:5000/documents/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated password reset guide"}'
```

Response `200`:
```json
{
  "id": 1,
  "title": "Updated password reset guide",
  "s3_key": null,
  "created_at": "2026-04-28T20:00:00+00:00"
}
```

---

### `DELETE /documents/<document_id>`

Deletes a document and all its chunks.

```bash
curl -X DELETE http://127.0.0.1:5000/documents/1
```

Response `204` — no body.

---

### `POST /ask`

Answers a question using the most relevant chunks from a document.

Request body:

| Field | Type | Required |
|-------|------|----------|
| `document_id` | integer | Yes |
| `question` | string | Yes |

```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "question": "How does a user reset their password?"
  }'
```

Response `200`:
```json
{
  "answer": "The user should go to the sign-in page, click Forgot Password, and follow the email instructions.",
  "sources": [
    {
      "chunk_index": 0,
      "content": "Step 1: Go to the sign-in page. Step 2: Click Forgot Password. Step 3: Follow the email instructions."
    }
  ]
}
```

---

## Notes

- `POST /ask` uses the OpenAI Responses API (`client.responses.create`) with model `gpt-5.4-mini` and a cap of 300 output tokens.
- `POST /ask` returns `500` if `OPENAI_API_KEY` is not configured.
- Chunking is word-count based; defaults to 120 words per chunk.
- Chunk retrieval scores chunks by keyword overlap with the question and returns up to 3 results, falling back to the first 3 chunks if no overlap is found.
