# Sovereign AI: Private RAG on Kubernetes

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Muhammad-Ikhwan-Fathulloh/Orchestrating-Private-LLM-Workloads-on-Kubernetes)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Proyek ini mendemonstrasikan implementasi pipeline RAG (Retrieval-Augmented Generation) privat
untuk **Universitas Teknologi Bandung, Teknik Informatika**, diorkestrasikan menggunakan Kubernetes (K3s).

**Repository**: https://github.com/Muhammad-Ikhwan-Fathulloh/Orchestrating-Private-LLM-Workloads-on-Kubernetes

## Fitur Utama
- **Saka-NLP**: `build_prompt`, `PromptTemplate`, `OutputFormatter`, `MultiAgentManager`, `parse_llm_output`
- **pgvector**: Penyimpanan vektor performa tinggi di dalam PostgreSQL
- **Qwen SLM**: Small Language Model yang efisien dijalankan secara lokal via `llama-cpp-python` (Qwen2.5-1.5B dan Qwen2.5-3B)
- **Multi-Agent Dinamis**: Agen disimpan di pgvector dengan keywords routing dan model spesifik per agent
- **Perbandingan Model**: Bandingkan output dari kedua model Qwen secara langsung
- **Cloud-Native**: Siap dideploy ke K3s dengan manifest Kubernetes

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
│       ├── inference.py      # LLM client (supports multiple models)
│       ├── agents.py         # MultiAgentManager (dinamis dari pgvector)
│       └── vector_store.py   # pgvector + embeddings + Agent model
├── inference/          # Qwen GGUF inference (FastAPI + llama-cpp-python)
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── server.py
├── infrastructure/     # Kubernetes manifests
│   ├── postgres-pgvector.yaml
│   ├── inference.yaml
│   └── backend.yaml
├── presentation/       # Slides
│   └── slides.md
├── docker-compose.yaml
└── README.md
```

---

## Cara Instalasi & Menjalankan (Docker Compose)
Ini adalah cara termudah untuk menjalankan proyek secara lokal!

### Prasyarat
Pastikan Anda sudah menginstall:
- [Docker](https://www.docker.com/) dan [Docker Compose](https://docs.docker.com/compose/)

### Langkah 1: Clone repository
```bash
git clone https://github.com/Muhammad-Ikhwan-Fathulloh/Orchestrating-Private-LLM-Workloads-on-Kubernetes.git
cd Orchestrating-Private-LLM-Workloads-on-Kubernetes
```

### Langkah 2: Jalankan dengan Docker Compose
```bash
docker-compose up --build
```
Perintah ini akan:
1. Build image untuk backend dan inference
2. Pull image postgres-pgvector dan pgweb
3. Download model Qwen2.5-1.5B dan Qwen2.5-3B secara otomatis
4. Menjalankan semua service secara otomatis!

### Langkah 3: Akses Aplikasi
Setelah semua service berjalan, buka browser dan akses:

| Service     | URL                        | Keterangan                  |
| ----------- | -------------------------- | --------------------------- |
| Frontend    | http://localhost:3000      | UI Mahasiswa                |
| Backend API | http://localhost:8080/docs | Swagger Docs (Test API!)    |
| PGWeb       | http://localhost:8081      | Database UI                 |
| Inference   | http://localhost:8000/v1/models | List model yang tersedia |

---

## Cara Instalasi K3s
Berikut adalah langkah-langkah untuk menginstall K3s (Kubernetes Ringkas) di server Anda:

### Instalasi K3s Server (Single Node)
```bash
# Jalankan script instalasi K3s
curl -sfL https://get.k3s.io | sh -

# Verifikasi instalasi
sudo k3s kubectl get nodes
```

### Instalasi K3s Agent (Multi Node - Opsional)
Jika Anda ingin menambah node worker:
```bash
# Di server K3s server, dapatkan token
sudo cat /var/lib/rancher/k3s/server/node-token

# Di node worker, jalankan:
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER_IP>:6443 K3S_TOKEN=<TOKEN> sh -
```

### Konfigurasi Kubectl (Untuk Akses dari Lokal)
Untuk mengakses K3s dari mesin lokal Anda:
```bash
# Salin file kubeconfig dari server K3s
sudo cat /etc/rancher/k3s/k3s.yaml

# Simpan ke ~/.kube/config di mesin lokal Anda
# Edit bagian server menjadi https://<SERVER_IP>:6443
```

---

## Cara Menjalankan di Kubernetes (K3s)
Untuk deployment ke Kubernetes K3s:

### Prasyarat
- K3s sudah terinstall (lihat bagian di atas)
- Docker registry untuk menyimpan image

### Langkah 1: Build & Push Image
```bash
# Build image backend
docker build -t your-registry/rag-backend:latest ./backend
docker push your-registry/rag-backend:latest

# Build image inference
docker build -t your-registry/qwen-inference:latest ./inference
docker push your-registry/qwen-inference:latest
```

### Langkah 2: Update Manifest Kubernetes
Edit file di `infrastructure/` untuk mengganti image name sesuai registry Anda!

### Langkah 3: Deploy ke K3s
```bash
kubectl apply -f infrastructure/
```

---

## API Endpoints
Gunakan **Swagger Docs** di http://localhost:8080/docs untuk mencoba semua endpoint secara interaktif!

### Manajemen Agen
- **POST /agents**: Buat agen baru (dengan keywords dan model opsional!)
  ```json
  {
    "name": "biology_expert",
    "role": "Guru Biologi",
    "task": "Membantu menjawab soal biologi",
    "keywords": ["biologi", "sel", "dna", "evolusi"],
    "model_name": "qwen2.5-3b-instruct"
  }
  ```
- **GET /agents**: Lihat semua agen yang tersimpan di database beserta detailnya
- **GET /agents/{agent_name}**: Lihat detail agen tertentu

### Ingest Dokumen
- **POST /ingest**: Tambah dokumen ke knowledge base (bisa spesifik untuk agen tertentu!)
  ```json
  {
    "content": "Materi Matematika: Rumus Luas Lingkaran adalah πr²...",
    "metadata": {"mata_kuliah": "Matematika Dasar", "semester": 1},
    "agent_name": "math_expert" // Opsional: hanya untuk agen math_expert
  }
  ```

### Query RAG
- **POST /query**: Query RAG umum (bisa pilih model yang akan digunakan)
- **POST /agent/query**: Query ke agen spesialis (otomatis routing berdasarkan keywords dan gunakan model agen!)
- **POST /compare**: Bandingkan jawaban dari kedua model Qwen untuk pertanyaan yang sama!
  ```json
  {
    "query": "Jelaskan apa itu algoritma sorting",
    "context": "Opsional: konteks khusus jika ingin bypass pencarian"
  }
  ```

---

## Cara Update Proyek (Jika Ada Perubahan)
Jika Anda mengupdate kode proyek atau menarik perubahan baru dari repository:

### 1. Pull Perubahan Terbaru
```bash
git pull origin main
```

### 2. Restart Docker Compose
Untuk menerapkan perubahan, rebuild dan restart service:
```bash
docker-compose down
docker-compose up --build
```

### 3. Migrasi Database (Opsional)
Jika ada perubahan pada model database (seperti menambah kolom baru):
- Database di Docker Compose akan tetap menyimpan data Anda
- `init_db()` di `main.py` akan otomatis membuat tabel baru jika belum ada
- **Catatan**: Untuk perubahan schema yang kompleks, Anda perlu menjalankan migrasi manual

---

## Demo Saka-NLP (Standalone)
Untuk mencoba fitur Saka-NLP tanpa Docker:
```bash
pip install git+https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP.git
python backend/demo_saka_features.py
```

---

## Kredit
- **Saka-NLP**: [Muhammad-Ikhwan-Fathulloh/Saka-NLP](https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP)
- **pgvector**: [pgvector/pgvector](https://github.com/pgvector/pgvector)
- **pgweb**: [sosedoff/pgweb](https://sosedoff.github.io/pgweb/)
- **K3s**: [k3s.io](https://k3s.io/)
- **Qwen Model**: [Qwen/Qwen2.5-GGUF](https://huggingface.co/Qwen)

---

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE). Lihat file LICENSE untuk informasi lebih detail.

