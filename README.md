# doc_search

Hello Anaconda

This is the repo for the technical assessment. It implements the required in-memory search service using FastAPI.

## Setup
uv is used to manage the environment and dependencies.

## Running

### Local Development
```bash
uv run main.py
```

### Using Docker
Build and run using Docker Compose:
```bash
docker-compose build
docker-compose up
```

## Testing
`uv run pytest --cov`

## API
When running for development, see http://localhost:8080/docs.

### Example usage

**Insert doc**
```bash
curl -X 'POST' \
  'http://localhost:8080/documents/a' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "I'\''m just a simple document\nI don'\''t know where I went"
}'
```

Does not return anything

**Search docs**
```bash
curl -X 'GET' \
  'http://localhost:8080/search?keyword=document' \
  -H 'accept: application/json'
```

Returns list of document ids containing keyword
```json
[
    "a"
]
```

**Delete doc**
```bash
curl -X 'DELETE' \
  'http://localhost:8080/documents/a' \
  -H 'accept: application/json'
```

Does not return anything

**Get deleted ids**
```bash
curl -X 'GET' \
  'http://localhost:8080/documents/deleted' \
  -H 'accept: application/json'
```

Returns list of deleted document ids
```json
[
    "a"
]
```
