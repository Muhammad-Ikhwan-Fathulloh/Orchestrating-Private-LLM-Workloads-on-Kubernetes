# Multi-Agent Manager menggunakan Saka-NLP
# Source: https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP

from saka.core.agent import MultiAgentManager
from .vector_store import list_agents

_manager = None


def get_agent_manager() -> MultiAgentManager:
    """Singleton MultiAgentManager dengan agen-agen dinamis dari pgvector."""
    global _manager
    if _manager is None:
        _manager = MultiAgentManager()
        # Load agents from database
        agents = list_agents()
        for agent in agents:
            _manager.add_agent(agent["name"], agent["role"], agent["task"])

    return _manager


def refresh_agent_manager() -> MultiAgentManager:
    """Refresh agent manager from database (useful after adding new agents)."""
    global _manager
    _manager = MultiAgentManager()
    agents = list_agents()
    for agent in agents:
        _manager.add_agent(agent["name"], agent["role"], agent["task"])
    return _manager


def route_query(query: str) -> str:
    """
    Route query ke agent yang paling sesuai berdasarkan keyword matching.
    Di produksi, ini bisa diganti dengan LLM-based routing menggunakan
    mgr.route_prompt(query) lalu kirim ke LLM.
    """
    q = query.lower()
    agents = list_agents()
    agent_names = [agent["name"] for agent in agents]
    if not agent_names:
        return None
    best_agent = "general_academic" if "general_academic" in agent_names else agent_names[0]
    best_score = 0

    for agent in agents:
        agent_name = agent["name"]
        keywords = agent.get("keywords", []) or []
        score = sum(1 for kw in keywords if kw and kw.lower() in q)
        if score > best_score:
            best_score = score
            best_agent = agent_name

    return best_agent
