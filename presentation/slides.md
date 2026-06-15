# Sovereign AI: Orchestrating Private LLM Workloads on Kubernetes

---

## 📅 Sesi Teknis: End-to-End Pipeline RAG Privat
**Membangun Asisten Akademik UTB Teknik Informatika**
**Dengan Saka-NLP & K3s**

---

## 1. Tantangan AI di Institusi Pendidikan
- **Privasi Data**: Data riset dan akademik sangat sensitif.
- **Kedaulatan Data**: Mengapa harus bergantung pada API pihak ketiga?
- **Nuansa Bahasa**: LLM global gagal menangkap morfologi Bahasa Indonesia.

---

## 2. Arsitektur "Sovereign AI"

### Diagram Arsitektur Utama
```mermaid
graph TD
    A["👨‍🎓 Mahasiswa UTB"] -->|Pertanyaan| B["🌐 Frontend\n(Bootstrap + JS)"]
    B -->|POST /query| C["⚙️ RAG Backend\n(FastAPI + Saka-NLP)"]
    C -->|1. Preprocess| D["🔤 Saka-NLP\nMorphology & Prompt"]
    C -->|2. Embed & Search| E["🗃️ PostgreSQL\n+ pgvector"]
    C -->|3. Generate| F["🤖 Qwen Inference\n(llama-cpp-python)"]
    F -->|Response| C
    C -->|Jawaban| B
    B -->|Tampilkan| A

    style A fill:#2980b9,color:#fff
    style B fill:#3498db,color:#fff
    style C fill:#1a3a5c,color:#fff
    style D fill:#e74c3c,color:#fff
    style E fill:#27ae60,color:#fff
    style F fill:#8e44ad,color:#fff
```

---

## 3. Pipeline RAG Detail

### Diagram Alur Data
```mermaid
flowchart LR
    subgraph INGESTION["📥 Ingestion Pipeline"]
        I1["Dokumen\nAkademik"] --> I2["Saka-NLP\nPreprocessing"]
        I2 --> I3["Sentence\nTransformer"]
        I3 --> I4["pgvector\nStore"]
    end

    subgraph QUERY["🔍 Query Pipeline"]
        Q1["Pertanyaan\nMahasiswa"] --> Q2["Saka-NLP\nbuild_prompt"]
        Q2 --> Q3["pgvector\nSimilarity Search"]
        Q3 --> Q4["Prompt +\nKonteks"]
        Q4 --> Q5["Qwen LLM\nGeneration"]
        Q5 --> Q6["Saka\nparse_llm_output"]
        Q6 --> Q7["OutputFormatter\nMarkdown/HTML/CSV"]
    end

    I4 -.->|Vektor DB| Q3

    style INGESTION fill:#eaf4e8,stroke:#27ae60
    style QUERY fill:#e8f0fa,stroke:#2980b9
```

---

## 4. Multi-Agent System

### Diagram Routing Multi-Agent
```mermaid
flowchart TD
    Q["Pertanyaan Masuk"] --> R["🧭 Router\n(MultiAgentManager)"]
    R -->|Matematika| M["🔢 Math Expert\nAljabar, Kalkulus"]
    R -->|Sains| S["🔬 Science Expert\nFisika, Kimia"]
    R -->|Bahasa| L["📝 Language Expert\nSastra, Tata Bahasa"]
    R -->|Informatika| C["💻 CS Expert\nAlgoritma, Programming"]
    R -->|Lainnya| G["📚 General Academic"]

    M --> A["Jawaban"]
    S --> A
    L --> A
    C --> A
    G --> A

    style R fill:#f39c12,color:#fff
    style M fill:#3498db,color:#fff
    style S fill:#27ae60,color:#fff
    style L fill:#9b59b6,color:#fff
    style C fill:#e74c3c,color:#fff
    style G fill:#95a5a6,color:#fff
```

---

## 5. Saka-NLP Features

### 5.1 Structured Prompt (`build_prompt`)
```python
prompt = build_prompt(
    role="Asisten Akademik Virtual",
    task="Menjawab pertanyaan berdasarkan konteks dokumen.",
    constraint="Jawab HANYA dari konteks...",
    output_contract={"jawaban": "...", "referensi": ["..."]},
    fallback_rule="Minta upload dokumen jika tidak ada konteks.",
    input_data=f"Konteks:\n{context}\n\nPertanyaan: {query}"
)
```

### 5.2 Template Prompt
```python
t = PromptTemplate("Pelajaran: {{mapel}} | Level: {{level}}")
print(t.render(mapel="Matematika", level="SMA"))
```

### 5.3 Multi-Agent
```python
mgr = MultiAgentManager()
mgr.add_agent("math_expert", "Guru Matematika", "Bantu soal aljabar...")
router_prompt = mgr.route_prompt(query)
```

### 5.4 Output Formatting
```python
OutputFormatter.format(data, "markdown")  # html, csv, table
```

---

## 6. Deployment Stack

### Diagram Kubernetes
```mermaid
graph TB
    subgraph K3S["☸️ K3s Cluster"]
        subgraph NS["Namespace: sovereign-ai"]
            FE["Pod: Frontend\n(nginx)"]
            BE["Pod: Backend\n(FastAPI + Saka)"]
            PG["StatefulSet: PostgreSQL\n(pgvector)"]
            PW["Pod: pgweb\n(DB Admin)"]
            INF["Pod: Inference\n(Qwen + llama-cpp)"]
        end
    end

    U["👨‍🎓 User"] --> FE
    FE --> BE
    BE --> PG
    BE --> INF
    PW --> PG

    style K3S fill:#326ce5,color:#fff
    style NS fill:#e8f0fa,stroke:#326ce5
```

---

## 7. Stack Teknologi

| Komponen      | Teknologi             | Fungsi                          |
| ------------- | --------------------- | ------------------------------- |
| **NLP**       | Saka-NLP              | Prompt, morphology, multi-agent |
| **Database**  | PostgreSQL + pgvector | Vector storage                  |
| **DB Admin**  | pgweb                 | Web UI PostgreSQL               |
| **Inference** | llama-cpp-python      | Serving Qwen GGUF               |
| **Model**     | Qwen 2.5 (1.5B/3B)    | SLM generation                  |
| **Frontend**  | HTML + Bootstrap      | UI Mahasiswa                    |
| **Runtime**   | K3s                   | Lightweight Kubernetes          |
| **Container** | Docker Compose        | Local development               |

---

## 8. Demo Langsung 🎬

```bash
# Jalankan semua service
docker-compose up --build

# Akses:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8080/docs
# PGWeb:     http://localhost:8081
# Inference: http://localhost:8000
```

---

## 9. Kesimpulan
- ✅ **Privat**: Data tidak pernah meninggalkan infrastruktur UTB.
- ✅ **Cerdas**: Multi-Agent + Saka-NLP untuk konteks Indonesia.
- ✅ **Scalable**: Cloud-native, siap K3s/Kubernetes.
- ✅ **Efisien**: SLM Qwen + GGUF = resource rendah.

---

## Tanya Jawab (Q&A)
**Terima Kasih!**

📦 Repository: [github.com/...](https://github.com/...)
📚 Saka-NLP: [github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP](https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP)
