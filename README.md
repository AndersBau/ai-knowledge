# AI Knowledge API

A Flask REST API for storing knowledge documents, splitting them into chunks, and answering questions against a selected document using OpenAI.

## Features

- Health check endpoint
- Document ingestion with `title` and full `content`
- Automatic word-based chunking on document create
- Full CRUD for documents (create, list, update title, delete)
- SQLAlchemy-backed persistence for documents and chunks
- Keyword-scored chunk retrieval for question answering
- Question answering endpoint that sends relevant chunks as context to OpenAI
- Docker support

## Tech Stack

- Python 3.13
- Flask 3
- Flask-SQLAlchemy
- python-dotenv
- OpenAI Python SDK
- boto3 (AWS S3 integration)
- pytest

## Project Structure

```text
.
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Config loaded from environment
│   ├── extensions.py        # SQLAlchemy instance
│   ├── models/
│   │   ├── document.py      # Document model
│   │   └── chunk.py         # DocumentChunk model
│   ├── routes/
│   │   ├── health.py        # GET /health
│   │   ├── documents.py     # CRUD /documents
│   │   └── questions.py     # POST /ask
│   ├── services/
│   │   └── retrieval_service.py  # Keyword-scored chunk retrieval
│   └── utils/
│       └── text_splitter.py      # Word-based text chunking
├── scripts/
│   └── init_db.py           # Creates database tables
├── Dockerfile
├── requirements.txt
└── run.py                   # Entry point
```

## How It Works

1. A document is created via `POST /documents` with a `title` and raw `content`.
2. The content is split into smaller word-based chunks and stored alongside the document.
3. `POST /ask` accepts a `document_id` and `question`, scores stored chunks by keyword overlap, and sends the top matches to OpenAI as context.
4. The response returns the generated answer plus the source chunks used.

## Local Setup

### Prerequisites

- Python 3.13+
- An OpenAI API key

### Steps

```bash
# 1. Clone the repo and navigate to the project root
cd ai-knowledge

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the project root (see Environment Variables below)

# 5. Initialize the database (creates tables)
python scripts/init_db.py

# 6. Start the API
python run.py
```

The server starts at `http://localhost:5000`.

## Environment Variables

`run.py` automatically loads a `.env` file from the project root.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `FLASK_DEBUG` | `false` | Enable debug mode |
| `DATABASE_URL` | `sqlite:///app.db` | SQLAlchemy database URL |
| `OPENAI_API_KEY` | — | **Required** for `POST /ask` |

Example `.env`:

```bash
SECRET_KEY=local-dev-secret
FLASK_DEBUG=true
DATABASE_URL=sqlite:///app.db
OPENAI_API_KEY=your-openai-api-key
```

## Running with Docker

```bash
# Build the image
docker build -t ai-knowledge .

# Run the container (pass your .env file)
docker run --env-file .env -p 5000:5000 ai-knowledge
```

## API Reference

### Health

```
GET /health
```

Response: `{"status": "ok"}`

---

### Documents

#### Create a document

```
POST /documents
Content-Type: application/json

{
  "title": "My Document",
  "content": "Full text content of the document..."
}
```

Response `201`:
```json
{
  "id": 1,
  "title": "My Document",
  "chunk_count": 4,
  "s3_key": null,
  "created_at": "2026-04-29T12:00:00"
}
```

#### List all documents

```
GET /documents
```

#### Update document title

```
PATCH /documents/<id>
Content-Type: application/json

{ "title": "Updated Title" }
```

#### Delete a document

```
DELETE /documents/<id>
```

Response: `204 No Content`

---

### Question Answering

```
POST /ask
Content-Type: application/json

{
  "document_id": 1,
  "question": "What is the main topic of this document?"
}
```

Response `200`:
```json
{
  "answer": "Based on the document...",
  "sources": [
    { "chunk_index": 0, "content": "..." },
    { "chunk_index": 2, "content": "..." }
  ]
}
```
```

Default base URL:

- `http://127.0.0.1:5000`

## Data Model

### `Document`

- `id`
- `title`
- `content`
- `s3_key`
- `created_at`

### `DocumentChunk`

- `id`
- `document_id`
- `chunk_index`
- `content`
- `created_at`

## API Endpoints

### `GET /health`

```bash
curl http://127.0.0.1:5000/health
```

### `POST /documents`

Creates a document and stores generated chunks.

```bash
curl -X POST http://127.0.0.1:5000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Password reset guide",
    "content": "Step 1: Go to the sign-in page. Step 2: Click Forgot Password. Step 3: Follow the email instructions."
  }'
```

Example response:

```json
{
  "chunk_count": 1,
  "created_at": "2026-04-28T20:00:00+00:00",
  "id": 1,
  "s3_key": null,
  "title": "Password reset guide"
}
```

### `GET /documents`

Returns all documents ordered by newest first.

```bash
curl http://127.0.0.1:5000/documents
```

### `PATCH /documents/<document_id>`

Updates only the document title.

```bash
curl -X PATCH http://127.0.0.1:5000/documents/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated password reset guide"}'
```

### `DELETE /documents/<document_id>`

Deletes a document and its chunks.

```bash
curl -X DELETE http://127.0.0.1:5000/documents/1
```

### `POST /ask`

Answers a question using chunks from a single document.

Request body:

- `document_id`
- `question`

```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "question": "How does a user reset their password?"
  }'
```

Example response:

```json
{
  "answer": "The document says the user should go to the sign-in page, click Forgot Password, and follow the email instructions.",
  "sources": [
    {
      "chunk_index": 0,
      "content": "Step 1: Go to the sign-in page. Step 2: Click Forgot Password. Step 3: Follow the email instructions."
    }
  ]
}
```

## Notes

- `POST /ask` returns `500` if `OPENAI_API_KEY` is not configured.
- Chunking is currently word-count based and defaults to 120 words per chunk.
- Retrieval is currently a simple keyword overlap match over stored chunks.
