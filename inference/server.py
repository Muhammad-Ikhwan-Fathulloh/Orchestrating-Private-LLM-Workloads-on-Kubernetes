"""Custom inference server that serves both Qwen models with OpenAI-compatible API."""

from llama_cpp import Llama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="Sovereign AI Inference Server")

# Load both models
print("Loading Qwen2.5-1.5B-Instruct model...")
llm_15b = Llama(
    model_path="/models/qwen2.5-1.5b-instruct-q8_0.gguf",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,
    verbose=True
)

print("Loading Qwen2.5-3B-Instruct model...")
llm_3b = Llama(
    model_path="/models/qwen2.5-3b-instruct-q8_0.gguf",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,
    verbose=True
)

# Model map
MODEL_MAP = {
    "qwen2.5-1.5b-instruct": llm_15b,
    "qwen2.5-3b-instruct": llm_3b,
    # Aliases
    "1.5b": llm_15b,
    "3b": llm_3b
}


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    if request.model not in MODEL_MAP:
        raise HTTPException(status_code=404, detail=f"Model {request.model} not found. Available models: {list(MODEL_MAP.keys())}")
    
    llm = MODEL_MAP[request.model]
    
    # Build prompt
    prompt = ""
    for msg in request.messages:
        if msg.role == "system":
            prompt += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
        elif msg.role == "user":
            prompt += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
        elif msg.role == "assistant":
            prompt += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"
    
    # Generate response
    output = llm(
        prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        stop=["<|im_end|>"],
        echo=False
    )
    
    response_text = output["choices"][0]["text"].strip()
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{id(output)}",
        created=1735689600,
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=Message(role="assistant", content=response_text),
                finish_reason="stop"
            )
        ],
        usage={
            "prompt_tokens": output["usage"]["prompt_tokens"],
            "completion_tokens": output["usage"]["completion_tokens"],
            "total_tokens": output["usage"]["total_tokens"]
        }
    )


@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 1735689600,
                "owned_by": "sovereign-ai"
            }
            for model_name in MODEL_MAP.keys()
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
