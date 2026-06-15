# Sovereign AI: Private RAG on Kubernetes

Proyek ini mendemonstrasikan implementasi pipeline RAG (Retrieval-Augmented Generation) privat
untuk **Universitas Teknologi Bandung, Teknik Informatika**, diorkestrasikan menggunakan Kubernetes (K3s).

## Fitur Utama
- **Saka-NLP**: `build_prompt`, `PromptTemplate`, `OutputFormatter`, `MultiAgentManager`, `parse_llm_output`
- **pgvector**: Penyimpanan vektor performa tinggi di dalam PostgreSQL.
- **Qwen SLM**: Small Language Model yang efisien dijalankan secara lokal via `llama-cpp-python`.
- **Multi-Agent**: 5 agen spesialis akademik (Matematika, Sains, Bahasa, Informatika, Umum).
- **Cloud-Native**: Siap dideploy ke K3s dengan manifest Kubernetes.

## Struktur Proyek
```
├── frontend/           # HTML + Bootstrap UI
│   └── index.html
├── backend/            # FastAPI + Saka-NLP
│   ├── Dockerfile
│   ├── demo_saka_features.py
│   └── app/
│       ├── main.py           # API endpoints + CORS
│       ├── saka_utils.py     # build_prompt, PromptTemplate
│       ├── inference.py      # LLM client
│       ├── agents.py         # MultiAgentManager
│       └── vector_store.py   # pgvector + embeddings
├── inference/          # Qwen GGUF inference
│   ├── Dockerfile
│   └── entrypoint.sh
├── infrastructure/     # Kubernetes manifests
│   ├── postgres-pgvector.yaml
│   ├── inference.yaml
│   └── backend.yaml
├── presentation/       # Slides
│   └── slides.md
├── docker-compose.yaml
└── README.md
```

## Cara Menjalankan (Docker Compose)
```bash
docker-compose up --build
```

| Service     | URL                        | Keterangan   |
| ----------- | -------------------------- | ------------ |
| Frontend    | http://localhost:3000      | UI Mahasiswa |
| Backend API | http://localhost:8080/docs | Swagger Docs |
| PGWeb       | http://localhost:8081      | Database UI  |
| Inference   | http://localhost:8000      | Qwen LLM API |

## Cara Menjalankan di Kubernetes (K3s)
```bash
# Build & push image ke registry
docker build -t your-registry/rag-backend:latest ./backend
docker build -t your-registry/qwen-inference:latest ./inference

# Deploy
kubectl apply -f infrastructure/
```

## Demo Saka-NLP (Standalone)
```bash
pip install git+https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP.git
python backend/demo_saka_features.py
```

## Kredit
- **Saka-NLP**: [Muhammad-Ikhwan-Fathulloh/Saka-NLP](https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP)
- **pgvector**: [pgvector/pgvector](https://github.com/pgvector/pgvector)
- **pgweb**: [sosedoff/pgweb](https://sosedoff.github.io/pgweb/)
- **K3s**: [k3s.io](https://k3s.io/)
- **Qwen Model**: [Qwen/Qwen2.5-GGUF](https://huggingface.co/Qwen)
