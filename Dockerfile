# Dockerfile - lightweight python image for live-market & dashboard
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements first for caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy code
COPY . /app

# create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# default: run the dashboard app
# (for the live feed service use a different command in compose/k8s)
CMD ["uvicorn", "services.dashboard:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
