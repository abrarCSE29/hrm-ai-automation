FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir uv && uv sync --frozen 2>/dev/null || uv sync
ENV PYTHONPATH=/app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
