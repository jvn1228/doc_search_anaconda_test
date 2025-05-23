# Build stage
FROM python:3.13-slim AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY doc_search /app/doc_search/

# Install dependencies and build package
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy built package from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY main.py /app/

EXPOSE 8080

# Useful for immediate logging
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
