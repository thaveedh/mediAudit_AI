import os
import json
import re
import urllib.request
import urllib.error

try:
    import ollama
except ImportError:
    ollama = None


def format_plain_english_synthesis(context: str, question: str) -> str:
    """
    Synthesize a clean, natural-language, human-friendly response
    grounded in the retrieved FDA section data without raw dump headers.
    """
    if not context or not context.strip():
        return f"I couldn't find an official FDA DailyMed record matching: *{question}*."

    # Parse medicine and section if present
    medicine = "this medication"
    med_match = re.search(r"Medicine:\s*([^\n]+)", context, re.IGNORECASE)
    if med_match:
        medicine = med_match.group(1).strip()

    section_match = re.search(r"Section:\s*([^\n]+)", context, re.IGNORECASE)
    section_name = section_match.group(1).strip() if section_match else ""

    # Strip meta headers
    clean_text = context
    clean_text = re.sub(r"Medicine:\s*[^\n]+\n*", "", clean_text)
    clean_text = re.sub(r"Section:\s*[^\n]+\n*", "", clean_text)
    clean_text = re.sub(r"Content:\s*", "", clean_text)
    clean_text = clean_text.strip()

    q_lower = question.lower()

    # 1. Ingredients inquiry
    if any(k in q_lower for k in ["ingredient", "ingredients", "contain", "composition", "made of", "what is in"]):
        # Extract active and inactive ingredients
        active_match = re.search(r"Active Ingredient[s]?:\s*([^\n\•]+)", clean_text, re.IGNORECASE)
        inactive_match = re.search(r"Inactive [I|i]ngredient[s]?:\s*([^\n]+)", clean_text, re.IGNORECASE)

        lines = [f"Based on the official FDA DailyMed labeling for **{medicine}**:\n"]

        if active_match:
            lines.append("### Active Ingredient")
            lines.append(f"• **{active_match.group(1).strip()}**\n")
        elif "active ingredient" in clean_text.lower():
            # Extract sentence with active ingredient
            for s in clean_text.split("."):
                if "active ingredient" in s.lower():
                    lines.append("### Active Ingredient")
                    lines.append(f"• {s.strip()}.\n")
                    break

        if inactive_match:
            lines.append("### Inactive Ingredients")
            inactives = [item.strip() for item in inactive_match.group(1).split(",") if item.strip()]
            for item in inactives:
                clean_item = item.strip().rstrip(".").capitalize()
                lines.append(f"• {clean_item}")
            lines.append("")
        elif not active_match:
            # Fallback to presenting the cleaned description
            lines.append(clean_text)

        lines.append("---\n> **FDA Prescribing Label Data Grounded**.")
        return "\n".join(lines)

    # 2. Side effects / adverse reactions inquiry
    if any(k in q_lower for k in ["side effect", "side effects", "adverse", "reaction", "reactions", "danger", "harm"]):
        return (
            f"Based on the official FDA DailyMed labeling for **{medicine}**:\n\n"
            f"### Side Effects & Adverse Reactions\n\n"
            f"{clean_text}\n\n"
            f"---\n> **FDA Prescribing Label Data Grounded**."
        )

    # 3. Dosage inquiry
    if any(k in q_lower for k in ["dose", "dosage", "how much", "how often", "frequency", "mg"]):
        return (
            f"Based on the official FDA DailyMed labeling for **{medicine}**:\n\n"
            f"### Recommended Dosage & Administration\n\n"
            f"{clean_text}\n\n"
            f"---\n> **FDA Prescribing Label Data Grounded**."
        )

    # 4. Food & dietary inquiry
    if any(k in q_lower for k in ["food", "diet", "eat", "drink", "alcohol", "avoid"]):
        return (
            f"Based on the official FDA DailyMed labeling for **{medicine}**:\n\n"
            f"### Food, Drink & Dietary Guidance\n\n"
            f"{clean_text}\n\n"
            f"---\n> **FDA Prescribing Label Data Grounded**."
        )

    # 5. Indications / General query
    header = f"### {section_name}" if section_name else "### FDA DailyMed Guidance"
    return (
        f"Based on the official FDA DailyMed labeling for **{medicine}**:\n\n"
        f"{header}\n\n"
        f"{clean_text}\n\n"
        f"---\n> **FDA Prescribing Label Data Grounded**."
    )


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

    # 1. Try Groq API (High priority: Qwen models supported!)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        models_to_try = [
            os.getenv("GROQ_MODEL", "qwen-qwq-32b"),
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        for model in models_to_try:
            try:
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
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    answer = data["choices"][0]["message"]["content"]
                    print(f"Generated response via Groq model ({model})")
                    return answer
            except Exception as e:
                print(f"Groq ({model}) failed: {e}")
                continue

    # 2. Try OpenRouter API (Qwen free tier)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps({
                    "model": os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-7b-instruct:free"),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://medi-audit-ai-seven.vercel.app",
                    "X-Title": "MediAudit AI"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter API error: {e}")

    # 3. Try Ollama (Local or remote via OLLAMA_HOST, e.g. ngrok tunnel)
    ollama_host = os.getenv("OLLAMA_HOST")
    is_cloud = os.getenv("RENDER") or os.getenv("PORT")

    # In cloud without OLLAMA_HOST, skip waiting for local daemon to respond instantly
    if not ollama_host and is_cloud:
        return format_plain_english_synthesis(context, question)

    if ollama:
        ollama_host = ollama_host or "http://127.0.0.1:11434"
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        try:
            client = ollama.Client(host=ollama_host, timeout=3.0)
            response = client.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Ollama connection error at {ollama_host}: {e}")

    # 4. Fallback: Synthesize plain English answer from grounded FDA context
    return format_plain_english_synthesis(context, question)
