import os
import json
import urllib.request
import urllib.error
import ollama

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

6. NEVER tell the patient to change, stop, or increase their prescribed dosage.

7. If the user asks what a medicine is used for, explain its purpose clearly.

8. If the user asks about side effects, explain the side effects simply.

9. If the user asks about drug interactions, explain which medicines interact
   and what problem the interaction can cause.

10. Answer ONLY using information present in the FDA MEDICAL CONTEXT.

11. NEVER use your own medical knowledge to fill missing information.

12. If the FDA context does not contain the answer, say:
    "This information was not found in the retrieved FDA DailyMed data."

13. Do not provide general dietary, lifestyle, or medical advice unless it
    is explicitly supported by the FDA MEDICAL CONTEXT.

14. Do not assume that a medicine interacts with a food, drink, vitamin,
    or another medicine unless the FDA context explicitly supports it.

========================================
RESPONSE STYLE
========================================

Make the answer understandable to someone with NO medical background.

Use short paragraphs and bullet points.

Do not overload the user with unnecessary medical details.

For food questions, prefer this structure:

Medicine:
[Medicine name]

Foods / Drinks to be careful with:
- Food/drink
- Food/drink
- Food/drink

Why?
[Simple explanation]

What can I do?
[Simple practical guidance]

General Dietary Guidance:
[Only when FDA information is insufficient]

Important:
[Short safety note when necessary]

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
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Cloud LLM (Groq) request error: {e}")

    # 2. Try Ollama (Local or remote via OLLAMA_HOST)
    ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    try:
        client = ollama.Client(host=ollama_host)
        response = client.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"Ollama connection error at {ollama_host}: {e}")

        # Graceful fallback when deployed to cloud without Ollama daemon
        if context and context.strip():
            return (
                f"### Retrieved FDA DailyMed Information\n\n"
                f"{context.strip()}\n\n"
                f"---\n"
                f"> **Notice**: The LLM engine is unreachable at `{ollama_host}`. "
                f"Displaying raw retrieved FDA records above. "
                f"To enable AI explanations in cloud deployment, set `OLLAMA_HOST` or `GROQ_API_KEY`."
            )

        return (
            f"The assistant received your question, but could not connect to the LLM backend (`{ollama_host}`) "
            f"and found no matching FDA records for: *{question}*. "
            f"Please verify backend configuration or try another query."
        )
