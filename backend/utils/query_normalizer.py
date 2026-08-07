medicine_aliases = {

    # Generic names
    "paracetamol": "acetaminophen",
    "acetaminophen": "acetaminophen",
    "ibuprofen": "ibuprofen",
    "aspirin": "aspirin",
    "metformin": "metformin",
    "amoxicillin": "amoxicillin",

    # Brand names
    "crocin": "acetaminophen",
    "calpol": "acetaminophen",
    "tylenol": "acetaminophen",
    "advil": "ibuprofen",
    "brufen": "ibuprofen",

    # Common spelling mistakes
    "paracetomal": "acetaminophen",
    "paracitamol": "acetaminophen",
    "paracetmol": "acetaminophen",
    "ibruprofen": "ibuprofen",
    "ibuprofan": "ibuprofen",
    "metphormin": "metformin",
}


def normalize_query(query: str) -> str:

    words = query.lower().split()

    normalized_words = []

    for word in words:
        normalized_words.append(
            medicine_aliases.get(word, word)
        )

    return " ".join(normalized_words)