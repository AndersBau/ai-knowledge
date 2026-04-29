# AI Knowledge API

A Flask API for storing knowledge documents, splitting them into chunks, and answering questions against a selected document with OpenAI.

## Features

- Health check endpoint
- Document ingestion with `title` and full `content`
- Automatic document chunking on create
- SQLAlchemy-backed persistence for documents and chunks
- Question answering endpoint that retrieves relevant chunks and sends them to OpenAI

## Tech Stack

- Python 3.13
- Flask 3
- Flask-SQLAlchemy
- SQLAlchemy
- python-dotenv
- OpenAI Python SDK

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
├── requirements.txt
└── run.py                   # Entry point
```

## How It Works

1. A document is created through `POST /documents` with a title and raw content.
2. The API splits the content into smaller word-based chunks.
3. Both the document and its chunks are stored in the database.
4. `POST /ask` retrieves the most relevant chunks for a document and sends that context to OpenAI.
5. The response returns an answer plus the source chunks used to answer it.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Add a local `.env` file in the project root.
4. Initialize the database.
5. Start the Flask app.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Create a .env file in the project root (see Environment Variables below)

# 5. Initialize the database (creates tables)
python scripts/init_db.py

# 6. Start the API
python run.py
```

The server starts at `http://localhost:5000`.

## Environment Variables

`run.py` loads environment variables from a `.env` file in the repository root.

Supported settings:

- `SECRET_KEY` default: `dev-secret-key`
- `FLASK_DEBUG` default: `false`
- `DATABASE_URL` default: `sqlite:///app.db`
- `OPENAI_API_KEY` required for `POST /ask`

Example `.env`:

```bash
SECRET_KEY=local-dev-secret
FLASK_DEBUG=true
DATABASE_URL=sqlite:///app.db
OPENAI_API_KEY=your-openai-api-key
```

## Initialize the Database

Create the tables for documents and document chunks:

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
