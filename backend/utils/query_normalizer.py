import re

MEDICINE_ALIASES = {
    # Generic names
    "paracetamol": "acetaminophen",
    "acetaminophen": "acetaminophen",
    "ibuprofen": "ibuprofen",
    "aspirin": "aspirin",
    "metformin": "metformin",
    "amoxicillin": "amoxicillin",
    "warfarin": "warfarin",
    "metronidazole": "metronidazole",
    "diazepam": "diazepam",
    "furosemide": "furosemide",
    "albuterol": "albuterol",
    "lisinopril": "lisinopril",
    "atorvastatin": "atorvastatin",
    "omeprazole": "omeprazole",
    "losartan": "losartan",

    # Brand names & Trade names
    "crocin": "acetaminophen",
    "calpol": "acetaminophen",
    "tylenol": "acetaminophen",
    "panadol": "acetaminophen",
    "advil": "ibuprofen",
    "brufen": "ibuprofen",
    "motrin": "ibuprofen",
    "nurofen": "ibuprofen",
    "aleve": "naproxen",
    "naprosyn": "naproxen",
    "coumadin": "warfarin",
    "jantoven": "warfarin",
    "glucophage": "metformin",
    "flagyl": "metronidazole",
    "valium": "diazepam",
    "lasix": "furosemide",
    "ventolin": "albuterol",
    "proventil": "albuterol",
    "proair": "albuterol",
    "prilosec": "omeprazole",
    "lipitor": "atorvastatin",
    "prinivil": "lisinopril",
    "zestril": "lisinopril",
    "cozaar": "losartan",

    # Common spelling mistakes
    "paracetomal": "acetaminophen",
    "paracitamol": "acetaminophen",
    "paracetmol": "acetaminophen",
    "ibruprofen": "ibuprofen",
    "ibuprofan": "ibuprofen",
    "metphormin": "metformin",
    "warferin": "warfarin",
    "diazepan": "diazepam",
}

STOP_WORDS = {
    "what", "is", "the", "of", "in", "and", "for", "to", "a", "an", "are",
    "can", "i", "take", "with", "on", "by", "at", "from", "does", "how",
    "much", "many", "tell", "me", "about", "side", "effect", "effects",
    "ingredient", "ingredients", "dose", "dosage", "harm", "danger", "food",
    "foods", "eat", "drink", "alcohol", "warning", "warnings", "reaction",
    "reactions", "prescribe", "prescribed", "use", "uses", "used", "treat",
    "treatment", "drug", "drugs", "medicine", "medicines", "contain", "contains"
}


def normalize_query(query: str) -> str:
    """Normalize query tokens using alias dictionary and lowercasing."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", query.lower())
    words = cleaned.split()

    normalized_words = [MEDICINE_ALIASES.get(w, w) for w in words]
    return " ".join(normalized_words)


def extract_medicine(query: str, candidate_medicines: list = None) -> str:
    """
    Intelligently identify the target medicine in the user's query
    without false-positive collisions with question or stop words.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", query.lower())
    words = cleaned.split()

    # 1. Direct alias check
    for w in words:
        if w in MEDICINE_ALIASES:
            return MEDICINE_ALIASES[w]

    if not candidate_medicines:
        return ""

    # 2. Check if any known medicine is a direct substring of the normalized query
    norm_query = normalize_query(query)
    for med in candidate_medicines:
        m_lower = med.lower().strip()
        if m_lower and m_lower in norm_query:
            return m_lower

    # 3. Match candidate non-stopwords against medicine name tokens
    query_tokens = [w for w in words if w not in STOP_WORDS and len(w) >= 3]

    best_match = ""
    best_score = 0

    for med in candidate_medicines:
        m_lower = med.lower().strip()
        med_tokens = [w for w in m_lower.split() if w not in STOP_WORDS and len(w) >= 3]

        score = 0
        for q_tok in query_tokens:
            if q_tok in med_tokens:
                score += 3
            elif any(q_tok in mt or mt in q_tok for mt in med_tokens):
                score += 1

        if score > best_score:
            best_score = score
            best_match = m_lower

    return best_match
