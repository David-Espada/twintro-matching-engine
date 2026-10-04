FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY backend/app /app/backend/app
RUN pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir /app/backend
COPY dataset /app/dataset
COPY scripts /app/scripts
RUN useradd --create-home twintro && mkdir -p /model-cache && chown -R twintro:twintro /app /model-cache
USER twintro
ENV DATASET_PATH=/app/dataset/professional_profiles.json
EXPOSE 8000
CMD ["sh", "-c", "python scripts/seed_database.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
