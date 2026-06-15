# Saka-NLP Prompt & Preprocessing Utilities
# Source: https://github.com/Muhammad-Ikhwan-Fathulloh/Saka-NLP

from saka.core.prompt import build_prompt, PromptTemplate, parse_llm_output


def preprocess_text(text: str) -> str:
    """
    Preprocessing teks Indonesia dengan Saka-NLP PromptTemplate
    untuk normalisasi sebelum embedding.
    """
    t = PromptTemplate(
        "Lakukan analisis morfologi dan lemmatisasi teks berikut: {{teks}}"
    )
    prompt = t.render(teks=text)
    # Untuk preprocessing sederhana, kita kembalikan teks lowercase
    # Di produksi, ini bisa dikirim ke LLM untuk lemmatisasi aktual
    return text.lower().strip()


def build_rag_prompt(query: str, context: str) -> str:
    """
    Gunakan Saka build_prompt untuk membuat prompt terstruktur
    yang dikirim ke LLM untuk RAG generation.
    """
    prompt = build_prompt(
        role="Asisten Akademik Virtual Sovereign AI",
        task="Menjawab pertanyaan pengguna berdasarkan konteks dokumen akademik yang diberikan.",
        constraint=(
            "1. Jawab HANYA berdasarkan konteks yang diberikan.\n"
            "2. Jika jawaban tidak ada dalam konteks, katakan 'Saya tidak menemukan jawabannya dalam dokumen'.\n"
            "3. Gunakan Bahasa Indonesia yang formal dan akademis.\n"
            "4. Sertakan referensi ke bagian konteks yang relevan."
        ),
        output_contract={
            "jawaban": "...",
            "referensi": ["bagian konteks 1", "..."],
            "confidence": "tinggi/sedang/rendah",
        },
        fallback_rule="Jika pertanyaan di luar konteks, minta pengguna untuk mengunggah dokumen yang relevan terlebih dahulu.",
        input_data=f"Konteks:\n{context}\n\nPertanyaan: {query}",
    )
    return prompt


def build_agent_prompt(query: str, context: str, role: str, task: str) -> str:
    """
    Build prompt yang disesuaikan untuk agent spesialis.
    """
    prompt = build_prompt(
        role=role,
        task=task,
        constraint=(
            "1. Jawab berdasarkan konteks yang diberikan.\n"
            "2. Gunakan istilah teknis yang sesuai dengan bidang Anda.\n"
            "3. Berikan penjelasan langkah demi langkah jika diperlukan."
        ),
        output_contract={
            "jawaban": "...",
            "penjelasan_langkah": ["langkah 1", "..."],
        },
        fallback_rule="Jika pertanyaan di luar keahlian Anda, delegasikan ke agen lain.",
        input_data=f"Konteks:\n{context}\n\nPertanyaan: {query}",
    )
    return prompt


def safe_parse_llm_output(raw_output: str) -> dict:
    """
    Parse output LLM yang mungkin berformat JSON menggunakan Saka parse_llm_output.
    """
    try:
        return parse_llm_output(raw_output)
    except Exception:
        return {"jawaban": raw_output}
