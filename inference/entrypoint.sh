#!/bin/bash

# Create models directory if it doesn't exist
mkdir -p /models

# Download 1.5B model if not exists
MODEL_15B_PATH="/models/qwen2.5-1.5b-instruct-q8_0.gguf"
if [ ! -f "$MODEL_15B_PATH" ]; then
    echo "Downloading Qwen2.5-1.5B-Instruct model..."
    curl -L "$MODEL_15B_URL" -o "$MODEL_15B_PATH"
fi

# Download 3B model if not exists
MODEL_3B_PATH="/models/qwen2.5-3b-instruct-q8_0.gguf"
if [ ! -f "$MODEL_3B_PATH" ]; then
    echo "Downloading Qwen2.5-3B-Instruct model..."
    curl -L "$MODEL_3B_URL" -o "$MODEL_3B_PATH"
fi

# Start custom inference server
python3 /app/server.py
