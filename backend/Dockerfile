FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Saka-NLP from GitHub
RUN pip install --no-cache-dir git+https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP.git

# Install other dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    pgvector \
    sentence-transformers \
    requests \
    python-multipart

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
