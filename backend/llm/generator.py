import os
import json
import urllib.request
import urllib.error

try:
    import ollama
except ImportError:
    ollama = None


def generate_rag_answer(context: str, question: str):

    prompt = f"""
You are a simple and friendly medical assistant.

Your job is to help ordinary people understand medicines and health information.

The retrieved information below comes from FDA medical documents.

========================================
IMPORTANT RULES
========================================

1. Use the FDA context for medicine-specific information.
2. Explain everything in SIMPLE ENGLISH.
3. Avoid complicated doctor terminology.
4. If you use a medical term, explain it immediately in simple words.
5. NEVER invent FDA information.
6. Answer ONLY using information present in the FDA MEDICAL CONTEXT.

========================================
FDA MEDICAL CONTEXT
========================================

{context}

========================================
USER QUESTION
========================================

{question}

========================================
ANSWER
========================================
"""

    # 1. Check if an external cloud LLM (e.g. Groq) is configured
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "PrescriptionAudit/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Cloud LLM (Groq) request error: {e}")

    # 2. Try Ollama (Local or remote via OLLAMA_HOST)
    ollama_host = os.getenv("OLLAMA_HOST")
    is_cloud = os.getenv("RENDER") or os.getenv("PORT")

    # If in cloud deployment without remote OLLAMA_HOST configured,
    # skip attempting localhost connection so it responds instantly
    if not ollama_host and is_cloud:
        if context and context.strip():
            return (
                f"### Retrieved FDA DailyMed Information\n\n"
                f"{context.strip()}\n\n"
                f"---\n"
                f"> **FDA Prescribing Label Data Grounded**."
            )
        return f"No matching FDA DailyMed record was found for: *{question}*."

    # If local or remote OLLAMA_HOST is provided, try Ollama with strict 2.5s timeout
    if ollama:
        ollama_host = ollama_host or "http://127.0.0.1:11434"
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        try:
            client = ollama.Client(host=ollama_host, timeout=2.5)
            response = client.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Ollama connection error at {ollama_host}: {e}")

    # Default fallback when Ollama is unavailable
    if context and context.strip():
        return (
            f"### Retrieved FDA DailyMed Information\n\n"
            f"{context.strip()}\n\n"
            f"---\n"
            f"> **FDA Prescribing Label Data Grounded**."
        )

    return (
        f"The assistant received your question (*{question}*). "
        f"No specific FDA DailyMed record was found for this medicine."
    )
