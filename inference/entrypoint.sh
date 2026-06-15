#!/bin/bash

if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading model from $MODEL_URL..."
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
fi

python3 -m llama_cpp.server --model "$MODEL_PATH" --host 0.0.0.0 --port 8000
