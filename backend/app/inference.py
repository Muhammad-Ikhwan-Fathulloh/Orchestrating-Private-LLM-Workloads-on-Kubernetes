import os
import requests
from .saka_utils import build_rag_prompt, build_agent_prompt, safe_parse_llm_output

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://inference:8000/v1")


def _call_llm(prompt: str) -> str:
    """Kirim prompt ke llama-cpp-python server (OpenAI-compatible)."""
    payload = {
        "model": "qwen",
        "messages": [
            {
                "role": "system",
                "content": "Anda adalah asisten akademik Sovereign AI.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 512,
    }
    try:
        response = requests.post(f"{INFERENCE_URL}/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error connecting to inference service: {e}")
        return "Maaf, terjadi kesalahan saat menghubungi layanan AI."


def generate_response(query: str, context: str) -> str:
    """Generate RAG response menggunakan Saka build_prompt."""
    prompt = build_rag_prompt(query, context)
    raw = _call_llm(prompt)
    parsed = safe_parse_llm_output(raw)
    if isinstance(parsed, dict) and "jawaban" in parsed:
        return parsed["jawaban"]
    return raw


def generate_response_with_agent(query: str, mgr, selected_agent_name: str) -> str:
    """Generate response via multi-agent specialist using agent-specific knowledge base."""
    from .vector_store import search_similar_documents
    from .saka_utils import preprocess_text

    processed = preprocess_text(query)
    context_list = search_similar_documents(processed, agent_name=selected_agent_name)
    context_text = "\n".join([doc["content"] for doc in context_list])

    agent = mgr.agents[selected_agent_name]

    # Gunakan Saka build_prompt dengan role/task dari agent
    prompt = build_agent_prompt(query, context_text, agent.role, agent.task)
    raw = _call_llm(prompt)
    parsed = safe_parse_llm_output(raw)
    if isinstance(parsed, dict) and "jawaban" in parsed:
        return parsed["jawaban"]
    return raw
