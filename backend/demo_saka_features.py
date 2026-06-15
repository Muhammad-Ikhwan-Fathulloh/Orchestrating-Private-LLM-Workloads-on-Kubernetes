"""
Demo: Saka-NLP Features untuk Sovereign AI
Jalankan file ini secara standalone untuk melihat fitur Saka-NLP in action.
"""

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from saka.core.prompt import build_prompt, PromptTemplate, parse_llm_output
from saka.core.agent import get_react_prompt, MultiAgentManager
from saka import OutputFormatter, Agent


# ============================================================
# DEMO 1: Structured Prompt untuk Asisten Akademik
# ============================================================
def demo_edu_structured():
    print("=" * 60)
    print("  DEMO 1: Education Structured Prompt (build_prompt)")
    print("=" * 60)
    prompt = build_prompt(
        role="Asisten Akademik Virtual",
        task="Menganalisis kebutuhan belajar siswa dan memberikan rencana studi.",
        constraint=(
            "1. Fokus pada materi kurikulum nasional.\n"
            "2. Jika subjek tidak jelas, minta klarifikasi."
        ),
        output_contract={
            "subjek": "...",
            "rencana": ["...", "..."],
            "durasi": "2 jam",
        },
        fallback_rule="Jika siswa cuma bilang 'halo' tanpa subjek, minta dia pilih pelajaran.",
        input_data="Gw bingung nih mau belajar fisika bagian mekanika, gimana ya?",
    )
    print(prompt)


# ============================================================
# DEMO 2: PromptTemplate untuk Konteks Pelajaran
# ============================================================
def demo_edu_template():
    print("\n" + "=" * 60)
    print("  DEMO 2: Education PromptTemplate")
    print("=" * 60)
    t = PromptTemplate("Pelajaran: {{mapel}} | Topik: {{topik}} | Level: {{level}}")
    print(t.render(mapel="Matematika", topik="Aljabar", level="SMA"))


# ============================================================
# DEMO 3: ReAct Agent Prompt
# ============================================================
def demo_edu_agent():
    print("\n" + "=" * 60)
    print("  DEMO 3: Education ReAct Agent Prompt")
    print("=" * 60)
    tools = [
        {
            "name": "get_exam_schedule",
            "description": "Cek jadwal ujian",
            "parameters": {
                "type": "object",
                "properties": {"kelas": {"type": "string"}},
            },
        }
    ]
    print(get_react_prompt("Kapan jadwal ujian kelas 12?", tools))


# ============================================================
# DEMO 4: OutputFormatter (Markdown, HTML, CSV, Table)
# ============================================================
def demo_output_formatter():
    print("\n" + "=" * 60)
    print("  DEMO 4: OutputFormatter")
    print("=" * 60)

    llm_data = [
        {"Word": "mangga", "Lang": "Indonesian/Javanese", "Pos": "Noun"},
        {"Word": "daharan", "Lang": "Javanese (Krama)", "Pos": "Verb"},
        {"Word": "abdi", "Lang": "Sundanese", "Pos": "Pronoun"},
    ]

    print("--- Markdown Table ---")
    print(OutputFormatter.format(llm_data, "markdown"))

    print("\n--- HTML Table ---")
    print(OutputFormatter.format(llm_data, "html"))

    print("\n--- CSV Output ---")
    print(OutputFormatter.format(llm_data, "csv"))

    print("\n--- Plain Text Table ---")
    print(OutputFormatter.format(llm_data, "table"))

    # Format via Agent instance
    agent = Agent(role="Linguistic Assistant", task="Analyze words")
    result = agent.format_output(llm_data, "markdown")
    print("\n--- Formatted via Agent ---")
    print(result)


# ============================================================
# DEMO 5: MultiAgentManager untuk Spesialisasi Akademik
# ============================================================
def demo_multi_agent():
    print("\n" + "=" * 60)
    print("  DEMO 5: MultiAgent Academic Specialization")
    print("=" * 60)

    mgr = MultiAgentManager()

    # Tambah Agent Spesialis
    mgr.add_agent(
        "math_expert",
        "Guru Matematika SMA",
        "Bantu jawab soal aljabar dan kalkulus.",
    )
    mgr.add_agent(
        "science_expert",
        "Guru Fisika & Kimia",
        "Bantu jawab soal mekanika, optik, dan reaksi kimia.",
    )

    # Case: Siswa bertanya tentang Fisika
    query = "Gimana cara ngitung gaya gravitasi antara dua benda?"

    # Route Query
    router_prompt = mgr.route_prompt(query)
    print("--- Router Prompt ---")
    print(router_prompt)

    # Simulasi route ke science_expert
    selected_agent_name = "science_expert"
    specialist_agent = mgr.agents[selected_agent_name]
    specialist_prompt = specialist_agent.prompt(query)

    print("\n--- Specialist Prompt ---")
    print(specialist_prompt)


# ============================================================
# DEMO 6: Parse LLM Output
# ============================================================
def demo_parse_output():
    print("\n" + "=" * 60)
    print("  DEMO 6: Parse LLM JSON Output")
    print("=" * 60)
    raw = '```json\n{"subjek": "Fisika", "rencana": ["Bab Mekanika", "Latihan Soal"], "durasi": "2 jam"}\n```'
    parsed = parse_llm_output(raw)
    print(f"Raw: {raw}")
    print(f"Parsed: {parsed}")


# ============================================================
# RUN ALL DEMOS
# ============================================================
if __name__ == "__main__":
    demo_edu_structured()
    demo_edu_template()
    demo_edu_agent()
    demo_output_formatter()
    demo_multi_agent()
    demo_parse_output()
