import os
import json
import gzip
from pathlib import Path
from utils.query_normalizer import normalize_query

_dataset = None


def get_fda_dataset():
    """Load the complete 8,118 FDA DailyMed records (4.7MB gzipped) into memory."""
    global _dataset
    if _dataset is None:
        try:
            gz_path = Path(__file__).resolve().parent.parent / "fda_dataset.json.gz"
            if gz_path.exists():
                with gzip.open(gz_path, "rt", encoding="utf-8") as f:
                    _dataset = json.load(f)
                    print(f"Loaded {len(_dataset)} FDA DailyMed documents into index.")
            else:
                _dataset = []
        except Exception as e:
            print(f"Error loading fda_dataset.json.gz: {e}")
            _dataset = []
    return _dataset


# Curated FDA records for core medicines not present in the Part 6 dump (e.g. Warfarin)
CURATED_FDA_DATA = {
    "warfarin": {
        "INGREDIENTS": (
            "Warfarin",
            "INGREDIENTS & COMPOSITION",
            "• Active Ingredient: Warfarin Sodium (1 mg, 2 mg, 2.5 mg, 3 mg, 4 mg, 5 mg, 6 mg, 7.5 mg, 10 mg scored tablets) — a vitamin K antagonist anticoagulant.\n"
            "• Inactive Ingredients: Lactose monohydrate, magnesium stearate, povidone, corn starch, and color additives (D&C Yellow No. 10, FD&C Blue No. 1, FD&C Red No. 40)."
        ),
        "INDICATIONS": (
            "Warfarin",
            "INDICATIONS AND USAGE",
            "• Prophylaxis and treatment of venous thrombosis (DVT) and pulmonary embolism (PE).\n"
            "• Prophylaxis and treatment of thromboembolic complications associated with atrial fibrillation or cardiac valve replacement.\n"
            "• Reduction in the risk of recurrent myocardial infarction and stroke."
        ),
        "FOOD": (
            "Warfarin",
            "FOOD AND DIETARY INTERACTIONS",
            "• Vitamin K Consistency: Foods high in Vitamin K (spinach, kale, broccoli, Brussels sprouts, collard greens, green cabbage) decrease warfarin's effectiveness. Maintain a consistent dietary intake; do not suddenly increase or reduce leafy green vegetables.\n"
            "• Cranberry products: Cranberry juice or extracts may enhance warfarin's anticoagulant action and elevate bleeding risk.\n"
            "• Alcohol: Avoid heavy or binge alcohol consumption, which can alter metabolism and drastically increase bleeding danger."
        ),
        "INTERACTIONS": (
            "Warfarin",
            "DRUG INTERACTIONS",
            "• NSAIDs (Ibuprofen, Naproxen, Aspirin): Markedly increase risk of severe gastrointestinal bleeding.\n"
            "• Antibiotics (Ciprofloxacin, Metronidazole, Bactrim, Erythromycin): Dangerously elevate INR.\n"
            "• Herbal supplements: St. John's Wort decreases warfarin levels; Ginkgo and Garlic increase bleeding."
        ),
        "ADVERSE": (
            "Warfarin",
            "ADVERSE REACTIONS & SIDE EFFECTS",
            "• Major or Fatal Hemorrhage: Uncontrolled bleeding (nosebleeds, bleeding gums, dark/red urine, tarry stools, unusual bruising, coughing up blood).\n"
            "• Tissue Necrosis & Gangrene of skin, systemic atheroemboli / purple toes syndrome."
        ),
        "WARNINGS": (
            "Warfarin",
            "WARNINGS & PRECAUTIONS",
            "• Boxed Warning: Can cause major or fatal bleeding. Regular monitoring of the International Normalized Ratio (INR) is mandatory.\n"
            "• Contraindicated in pregnancy (causes fetal hemorrhage and congenital malformations)."
        ),
        "DOSAGE": (
            "Warfarin",
            "DOSAGE AND ADMINISTRATION",
            "• Individualized based on the patient's target INR range (usually 2.0 to 3.0 for most indications).\n"
            "• Taken once daily, at the same time each day (typically in the evening), with or without food."
        )
    }
}

SECTION_MAP = {
    "INGREDIENTS": ["DESCRIPTION", "INGREDIENTS", "INGREDIENTS AND APPEARANCE", "ACTIVE INGREDIENT", "INACTIVE INGREDIENT", "COMPOSITION"],
    "ADVERSE": ["ADVERSE REACTIONS"],
    "INDICATIONS": ["INDICATIONS AND USAGE", "CLINICAL PHARMACOLOGY"],
    "WARNINGS": ["WARNINGS", "BOXED WARNING", "CONTRAINDICATIONS", "PRECAUTIONS"],
    "INTERACTIONS": ["DRUG INTERACTIONS", "PRECAUTIONS"],
    "FOOD": ["PRECAUTIONS", "WARNINGS", "DRUG INTERACTIONS", "DOSAGE AND ADMINISTRATION"],
    "DOSAGE": ["DOSAGE AND ADMINISTRATION"]
}


def detect_section_intent(query: str) -> str:
    q = query.lower()

    if any(k in q for k in ["ingredient", "ingredients", "contain", "contains", "composition", "made of", "what is in", "components"]):
        return "INGREDIENTS"

    if any(k in q for k in ["food", "foods", "diet", "dietary", "eat", "drink", "avoid", "alcohol", "grapefruit", "cranberry", "vitamin"]):
        return "FOOD"

    if any(k in q for k in ["side effect", "side effects", "adverse", "reaction", "reactions", "danger", "harm", "problem"]):
        return "ADVERSE"

    if any(k in q for k in ["interaction", "interactions", "interact", "combine", "together", "other drug", "other med", "other medicine"]):
        return "INTERACTIONS"

    if any(k in q for k in ["dose", "dosage", "how much", "how often", "frequency", "how many", "mg", "take how"]):
        return "DOSAGE"

    if any(k in q for k in ["warning", "warnings", "precaution", "precautions", "contraindication", "safe", "safety", "risk"]):
        return "WARNINGS"

    if any(k in q for k in ["why", "prescribe", "prescribed", "use", "used for", "purpose", "treat", "indication", "indications", "what is"]):
        return "INDICATIONS"

    return "ALL"


def retrieve(query: str, medicine: str = None, k: int = 5):
    print("=" * 60)
    print("USER QUERY:", query)

    normalized_query = normalize_query(query).lower()
    print("NORMALIZED QUERY:", normalized_query)

    target_intent = detect_section_intent(query)
    print("DETECTED INTENT:", target_intent)

    documents = []
    metadatas = []

    # 1. Search the full FDA DailyMed dataset (8,118 records)
    dataset = get_fda_dataset()
    if dataset:
        target_sections = SECTION_MAP.get(target_intent, [])

        # Find matching medicine records
        med_matches = [
            d for d in dataset
            if d["medicine"].lower() in normalized_query or any(word in d["medicine"].lower() for word in normalized_query.split() if len(word) > 3)
        ]

        if med_matches:
            # Filter by the section matching the user's intent
            section_matches = [
                d for d in med_matches
                if d["section"] in target_sections
            ]

            # If specific section found, use it!
            selected = section_matches if section_matches else med_matches[:3]

            # Take the best matching document without duplicates
            seen_texts = set()
            for d in selected:
                clean_text = d["text"].strip()
                if clean_text not in seen_texts:
                    seen_texts.add(clean_text)
                    documents.append(clean_text)
                    metadatas.append({"medicine": d["medicine"], "section": d["section"]})
                if len(documents) >= 2:
                    break

    # 2. Check curated FDA knowledge base (e.g. Warfarin) if not in the Part 6 dump
    if not documents:
        for med_key, section_dict in CURATED_FDA_DATA.items():
            if med_key in normalized_query or med_key in query.lower():
                if target_intent != "ALL" and target_intent in section_dict:
                    med_name, section_title, content = section_dict[target_intent]
                    doc_text = f"Medicine: {med_name}\nSection: {section_title}\n\n{content}"
                    documents.append(doc_text)
                    metadatas.append({"medicine": med_name, "section": section_title})
                else:
                    for key in ["INDICATIONS", "ADVERSE", "WARNINGS"]:
                        if key in section_dict:
                            med_name, section_title, content = section_dict[key]
                            doc_text = f"Medicine: {med_name}\nSection: {section_title}\n\n{content}"
                            documents.append(doc_text)
                            metadatas.append({"medicine": med_name, "section": section_title})

    print(f"RESULTS FOUND: {len(documents)}")
    return {"documents": [documents], "metadatas": [metadatas]}
