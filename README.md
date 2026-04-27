# AI Support Knowledge API

A small Flask API for managing support knowledge documents.

## Features

- Health check endpoint
- Document CRUD endpoints:
  - Create document
  - List documents
  - Update document title
  - Delete document
- SQLAlchemy-backed persistence (SQLite by default)

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Pytest (for testing).

## Project Structure

```text
.
├── app/
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   │   └── document.py
│   └── routes/
│       ├── documents.py
│       └── health.py
├── scripts/
│   └── init_db.py
├── tests/
├── requirements.txt
└── run.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

The app reads configuration from environment variables:

- `SECRET_KEY` (default: `dev-secret-key`)
- `FLASK_DEBUG` (default: `false`)
- `DATABASE_URL` (default: `sqlite:///app.db`)

Example:

```bash
export SECRET_KEY="local-dev-secret"
export FLASK_DEBUG="true"
export DATABASE_URL="sqlite:///app.db"
```

## Initialize the Database

Create database tables:

```bash
python scripts/init_db.py
```

## Run the API

```bash
python run.py
```

By default, the app runs on:

- `http://127.0.0.1:5000`

## API Endpoints

### Health

- `GET /health`

Example:

```bash
curl http://127.0.0.1:5000/health
```

### Documents

- `POST /documents`
- `GET /documents`
- `PATCH /documents/<document_id>`
- `DELETE /documents/<document_id>`

Create document:

```bash
curl -X POST http://127.0.0.1:5000/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "How to reset password"}'
```

List documents:

```bash
curl http://127.0.0.1:5000/documents
```

Update document title:

```bash
curl -X PATCH http://127.0.0.1:5000/documents/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated support article title"}'
```

Delete document:

```bash
curl -X DELETE http://127.0.0.1:5000/documents/1
```

## Run Tests

If tests are added under `tests/`, run:

```bash
pytest
```
