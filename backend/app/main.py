from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional
from .saka_utils import preprocess_text
from .vector_store import (
    store_document,
    search_similar_documents,
    init_db,
    create_agent,
    list_agents,
    get_agent_by_name,
    init_default_agents,
)
from .inference import generate_response, generate_response_with_agent, compare_models
from .agents import get_agent_manager, route_query, refresh_agent_manager

# Saka-NLP imports
from saka import OutputFormatter

app = FastAPI(title="Sovereign AI RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    init_default_agents()


# --- Request/Response Models ---

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = {}
    agent_name: Optional[str] = None  # Optional: specify which agent's knowledge base to add this to


class QueryRequest(BaseModel):
    query: str
    format: Optional[str] = "markdown"  # markdown, html, csv, table
    model: Optional[str] = "qwen2.5-1.5b-instruct"  # Model to use


class AgentQueryRequest(BaseModel):
    query: str
    format: Optional[str] = "markdown"
    model: Optional[str] = None  # Optional: override agent's default model


class CreateAgentRequest(BaseModel):
    name: str
    role: str
    task: str
    keywords: Optional[List[str]] = None
    model_name: Optional[str] = "qwen2.5-1.5b-instruct"  # Default model for this agent


class CompareRequest(BaseModel):
    query: str
    context: Optional[str] = None


# --- Endpoints ---

@app.post("/ingest")
async def ingest_document(req: DocumentRequest):
    """Ingest dokumen akademik: preprocessing via Saka-NLP -> embedding -> pgvector."""
    processed_content = preprocess_text(req.content)
    doc_id = store_document(processed_content, req.content, req.metadata, req.agent_name)
    return {
        "status": "success",
        "document_id": doc_id,
        "processed_content": processed_content,
        "agent_name": req.agent_name,
    }


@app.post("/query")
async def query_rag(req: QueryRequest):
    """Query RAG pipeline: preprocess -> retrieve -> generate via Saka build_prompt."""
    processed_query = preprocess_text(req.query)

    context_list = search_similar_documents(processed_query)
    context_text = "\n".join([doc["content"] for doc in context_list])

    if not context_list:
        return {"answer": "Maaf, saya tidak menemukan informasi yang relevan di dokumen saya."}

    answer = generate_response(req.query, context_text, req.model)

    # Format context using Saka OutputFormatter
    formatted_context = OutputFormatter.format(context_list, req.format)

    return {
        "query": req.query,
        "processed_query": processed_query,
        "model": req.model,
        "context_formatted": formatted_context,
        "context_raw": context_list,
        "answer": answer,
    }


@app.post("/agent/query")
async def agent_query(req: AgentQueryRequest):
    """Multi-Agent RAG: route query ke agen spesialis via Saka MultiAgentManager."""
    mgr = get_agent_manager()

    # Step 1: Dapatkan router prompt
    router_prompt = mgr.route_prompt(req.query)

    # Step 2: Route ke agent yang tepat (simulasi sederhana berdasarkan keyword)
    selected_agent_name = route_query(req.query)

    # Step 3: Generate specialist prompt & jawaban
    agent_data = get_agent_by_name(selected_agent_name) if selected_agent_name else None
    answer = generate_response_with_agent(req.query, mgr, selected_agent_name, req.model)

    return {
        "query": req.query,
        "routed_to": selected_agent_name,
        "agent": agent_data,
        "router_prompt_preview": router_prompt[:300],
        "answer": answer,
    }


@app.post("/compare")
async def compare_models_endpoint(req: CompareRequest):
    """Compare responses from both Qwen models."""
    return compare_models(req.query, req.context)


@app.post("/agents")
async def create_agent_endpoint(req: CreateAgentRequest):
    """Create a new agent."""
    try:
        agent_id = create_agent(req.name, req.role, req.task, req.keywords, req.model_name)
        # Refresh agent manager to include new agent
        refresh_agent_manager()
        return {"status": "success", "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create agent: {str(e)}")


@app.get("/agents")
async def list_agents_endpoint():
    """List semua agen spesialis yang tersedia."""
    agents = list_agents()
    return {"agents": agents}


@app.get("/agents/{agent_name}")
async def get_agent_endpoint(agent_name: str):
    """Get a specific agent by name."""
    agent = get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.get("/health")
async def health_check():
    return {"status": "ok"}
