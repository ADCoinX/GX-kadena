# Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app /app
EXPOSE 8000
CMD ["uvicorn", "gx_kadena.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]