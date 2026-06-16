FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir llama-cpp-python fastapi uvicorn pydantic

# Copy server script and entrypoint
COPY server.py /app/server.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Model URLs
ENV MODEL_15B_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q8_0.gguf"
ENV MODEL_3B_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q8_0.gguf"

ENTRYPOINT ["/app/entrypoint.sh"]
