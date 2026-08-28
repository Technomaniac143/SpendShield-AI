FROM python:3.11-slim

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./

ENV PYTHONPATH=/app/backend

EXPOSE 8000

# Run startup (migrations + bucket creation), then launch the app
CMD ["sh", "-c", "python scripts/render_startup.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]