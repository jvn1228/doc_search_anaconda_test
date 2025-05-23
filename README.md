# doc_search

Hello Anaconda

This is the repo for the technical assessment. It implements the required in-memory search service using FastAPI.

## Design and Assumptions
A very basic index is created that separates words based on whitespace only. A keyword search must exactly match for a document to be returned. Punctuation is not removed and so must be included at this stage as well. It is assumed characters will be in the latin alphabet, although it probably works with any UTF-8 characters. It is also assumed we only care that the word exists in the document and have no concerns about where or how often it occurs, so search returns are weighed equally in that regard, and are likely arranged in order of insertion.

The index contains all unique words across all documents. It does not distinguish on size at this moment (eg "a" is considered a valid keyword although realistically it is not). If many, many documents are uploaded and unique words balloon, the index may not be as efficient as desired, especially for deleting documents, where the index must be scanned for the document's tokens.

The API is simple and, because it's for fun, does not factor in security (a proxy server can be used to handle that). In a similar vein, for prod deployment, an entry point to run uvicorn directly without hot-reloading may be preferred. And pod health monitoring would be added.

## Setup
[uv](https://docs.astral.sh/uv/) is used to manage the environment and dependencies.

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
  "content": "I'm just a simple document\nI don't know where I went"
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
