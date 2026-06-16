import os
import requests
from .saka_utils import build_rag_prompt, build_agent_prompt, safe_parse_llm_output

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://inference:8000/v1")


def _call_llm(prompt: str, model: str = "qwen2.5-1.5b-instruct") -> str:
    """Kirim prompt ke llama-cpp-python server (OpenAI-compatible) dengan model tertentu."""
    payload = {
        "model": model,
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


def generate_response(query: str, context: str, model: str = "qwen2.5-1.5b-instruct") -> str:
    """Generate RAG response menggunakan Saka build_prompt dengan model tertentu."""
    prompt = build_rag_prompt(query, context)
    raw = _call_llm(prompt, model)
    parsed = safe_parse_llm_output(raw)
    if isinstance(parsed, dict) and "jawaban" in parsed:
        return parsed["jawaban"]
    return raw


def generate_response_with_agent(query: str, mgr, selected_agent_name: str, model: str = None) -> str:
    """Generate response via multi-agent specialist using agent-specific knowledge base and model."""
    from .vector_store import search_similar_documents, get_agent_by_name
    from .saka_utils import preprocess_text

    processed = preprocess_text(query)
    context_list = search_similar_documents(processed, agent_name=selected_agent_name)
    context_text = "\n".join([doc["content"] for doc in context_list])

    agent = mgr.agents[selected_agent_name]
    agent_data = get_agent_by_name(selected_agent_name)
    
    # Use agent's model if not specified
    use_model = model if model is not None else agent_data["model_name"] if agent_data else "qwen2.5-1.5b-instruct"

    # Gunakan Saka build_prompt dengan role/task dari agent
    prompt = build_agent_prompt(query, context_text, agent.role, agent.task)
    raw = _call_llm(prompt, use_model)
    parsed = safe_parse_llm_output(raw)
    if isinstance(parsed, dict) and "jawaban" in parsed:
        return parsed["jawaban"]
    return raw


def compare_models(query: str, context: str = None) -> dict:
    """Generate comparison between both Qwen models for a given query."""
    from .saka_utils import preprocess_text
    from .vector_store import search_similar_documents

    processed = preprocess_text(query)
    context_list = search_similar_documents(processed) if context is None else [{"content": context}]
    context_text = "\n".join([doc["content"] for doc in context_list])

    response_15b = generate_response(query, context_text, "qwen2.5-1.5b-instruct")
    response_3b = generate_response(query, context_text, "qwen2.5-3b-instruct")
    
    return {
        "qwen2.5-1.5b-instruct": response_15b,
        "qwen2.5-3b-instruct": response_3b
    }
