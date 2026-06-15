import os
from sqlalchemy import Column, Integer, Text, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Multilingual embedding model (supports Indonesian)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)  # Agent identifier (e.g., "math_expert")
    role = Column(Text, nullable=False)  # Agent role (e.g., "Guru Matematika")
    task = Column(Text, nullable=False)  # Agent task description
    keywords = Column(JSON, nullable=True)  # List of keywords for routing


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    processed_content = Column(Text)  # Lemmatized/Analyzed text
    content = Column(Text)  # Original text
    metadata = Column(JSON)
    agent_name = Column(Text, nullable=True)  # Agent-specific knowledge base
    embedding = Column(Vector(384))  # MiniLM-L12-v2 = 384 dims


def init_db():
    """Create pgvector extension and tables."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


def store_document(processed_content: str, original_content: str, metadata: dict, agent_name: str = None) -> int:
    embedding = model.encode(processed_content)
    db = SessionLocal()
    try:
        db_doc = Document(
            processed_content=processed_content,
            content=original_content,
            metadata=metadata,
            agent_name=agent_name,
            embedding=embedding.tolist(),
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc.id
    finally:
        db.close()


def search_similar_documents(query: str, limit: int = 3, agent_name: str = None) -> list:
    query_embedding = model.encode(query)
    db = SessionLocal()
    try:
        query_obj = db.query(Document)
        if agent_name:
            query_obj = query_obj.filter(Document.agent_name == agent_name)
        results = (
            query_obj
            .order_by(Document.embedding.cosine_distance(query_embedding.tolist()))
            .limit(limit)
            .all()
        )
        return [
            {"id": r.id, "content": r.content, "metadata": r.metadata, "agent_name": r.agent_name}
            for r in results
        ]
    finally:
        db.close()


def create_agent(name: str, role: str, task: str, keywords: list = None) -> int:
    db = SessionLocal()
    try:
        db_agent = Agent(name=name, role=role, task=task, keywords=keywords)
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent.id
    finally:
        db.close()


def list_agents() -> list:
    db = SessionLocal()
    try:
        agents = db.query(Agent).all()
        return [{"id": a.id, "name": a.name, "role": a.role, "task": a.task, "keywords": a.keywords} for a in agents]
    finally:
        db.close()


def get_agent_by_name(name: str) -> dict:
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.name == name).first()
        if agent:
            return {"id": agent.id, "name": agent.name, "role": agent.role, "task": agent.task, "keywords": agent.keywords}
        return None
    finally:
        db.close()


def init_default_agents():
    """Initialize default agents if they don't exist yet."""
    default_agents = [
        (
            "math_expert",
            "Guru Matematika",
            "Membantu menjawab soal aljabar, kalkulus, statistik, dan geometri.",
            ["matematika", "aljabar", "kalkulus", "statistik", "geometri", "persamaan", "integral", "turunan", "matriks", "hitung"]
        ),
        (
            "science_expert",
            "Guru Fisika & Kimia",
            "Membantu menjawab soal mekanika, optik, termodinamika, dan reaksi kimia.",
            ["fisika", "kimia", "gravitasi", "gaya", "energi", "reaksi", "mekanika", "optik", "termodinamika", "atom", "molekul"]
        ),
        (
            "language_expert",
            "Guru Bahasa Indonesia",
            "Membantu analisis sastra, tata bahasa, dan penulisan akademik.",
            ["bahasa", "sastra", "puisi", "cerpen", "novel", "tata bahasa", "ejaan", "paragraf", "kalimat", "menulis"]
        ),
        (
            "cs_expert",
            "Guru Informatika",
            "Membantu pemrograman, algoritma, struktur data, dan jaringan komputer.",
            ["program", "algoritma", "kode", "python", "javascript", "java", "database", "jaringan", "komputer", "informatika"]
        ),
        (
            "general_academic",
            "Asisten Akademik Umum",
            "Membantu pertanyaan akademik umum yang tidak termasuk kategori di atas.",
            []
        ),
    ]
    db = SessionLocal()
    try:
        for name, role, task, keywords in default_agents:
            existing = db.query(Agent).filter(Agent.name == name).first()
            if not existing:
                db.add(Agent(name=name, role=role, task=task, keywords=keywords))
        db.commit()
    finally:
        db.close()
