FROM python:3.11-slim

WORKDIR /app

COPY src/ /app/src/

ENV PYTHONPATH="/app/src"

ENTRYPOINT ["python", "/app/src/orchestrator.py", "/app/target"]