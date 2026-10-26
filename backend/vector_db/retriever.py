import os
import json
import gzip
import re
from pathlib import Path
from utils.query_normalizer import normalize_query, extract_medicine

_dataset = None
_known_medicines = None


def get_fda_dataset():
    """Load the complete 8,118 FDA DailyMed records into memory."""
    global _dataset, _known_medicines
    if _dataset is None:
        try:
            gz_path = Path(__file__).resolve().parent.parent / "fda_dataset.json.gz"
            if gz_path.exists():
                with gzip.open(gz_path, "rt", encoding="utf-8") as f:
                    _dataset = json.load(f)
                    _known_medicines = list({d["medicine"].lower().strip() for d in _dataset if d.get("medicine")})
                    print(f"Loaded {len(_dataset)} FDA DailyMed documents across {len(_known_medicines)} medicines.")
            else:
                _dataset = []
                _known_medicines = []
        except Exception as e:
            print(f"Error loading fda_dataset.json.gz: {e}")
            _dataset = []
            _known_medicines = []
    return _dataset


def get_known_medicines():
    global _known_medicines
    if _known_medicines is None:
        get_fda_dataset()
    return _known_medicines or []


# Baseline FDA records for medicines not in the primary Part 6 dump (e.g. Warfarin)
CURATED_FDA_DATA = {
    "warfarin": {
        "INGREDIENTS": (
            "Warfarin",
            "INGREDIENTS & COMPOSITION",
            "Active Ingredient: Warfarin Sodium (1 mg, 2 mg, 2.5 mg, 3 mg, 4 mg, 5 mg, 6 mg, 7.5 mg, 10 mg scored tablets) — a vitamin K antagonist anticoagulant.\n"
            "Inactive Ingredients: Lactose monohydrate, magnesium stearate, povidone, corn starch, and color additives (D&C Yellow No. 10, FD&C Blue No. 1, FD&C Red No. 40)."
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

    if any(k in q for k in ["food", "foods", "diet", "dietary", "eat", "drink", "avoid", "alcohol", "grapefruit", "cranberry", "vitamin", "vitamins"]):
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


def clean_section_text(raw_text: str) -> str:
    """Strip XML headers and format clean content."""
    text = raw_text.strip()
    if "Content:" in text:
        text = text.split("Content:", 1)[1].strip()
    # Normalize excessive whitespace/newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def retrieve(query: str, medicine: str = None, k: int = 5):
    print("=" * 60)
    print("USER QUERY:", query)

    # 1. Detect target medicine
    known_meds = get_known_medicines()
    detected_medicine = extract_medicine(query, known_meds)
    print("DETECTED MEDICINE:", detected_medicine)

    # 2. Detect section intent
    target_intent = detect_section_intent(query)
    print("DETECTED INTENT:", target_intent)

    documents = []
    metadatas = []

    # 3. DIRECTLY SEARCH THE FULL 8,118 FDA DAILYMED DATASET FIRST
    dataset = get_fda_dataset()
    if dataset and detected_medicine:
        target_sections = SECTION_MAP.get(target_intent, [])

        # Filter strictly for the target medicine
        med_matches = [
            d for d in dataset
            if d["medicine"].lower().strip() == detected_medicine or detected_medicine in d["medicine"].lower()
        ]

        if med_matches:
            print(f"HITTING DATASET: Found {len(med_matches)} FDA documents for {detected_medicine}")
            # Filter by the section matching user intent
            section_matches = [
                d for d in med_matches
                if d["section"] in target_sections
            ]

            selected = section_matches if section_matches else med_matches[:2]

            seen_content = set()
            for d in selected:
                raw_text = d["text"].strip()
                content = clean_section_text(raw_text)
                if content not in seen_content:
                    seen_content.add(content)
                    doc_formatted = (
                        f"Medicine: {d['medicine']}\n"
                        f"Section: {d['section']}\n"
                        f"MatchedRecords: {len(med_matches)}\n"
                        f"SourceFile: fda_dataset.json.gz (8,118 records)\n\n"
                        f"{content}"
                    )
                    documents.append(doc_formatted)
                    metadatas.append({
                        "medicine": d["medicine"],
                        "section": d["section"],
                        "content": content,
                        "source": "FDA DailyMed Database (8,118 records)",
                        "matched_records": len(med_matches)
                    })
                if len(documents) >= 2:
                    break

    # 4. If no documents found in the dataset, check curated baseline reference (e.g. Warfarin)
    if not documents and detected_medicine:
        for med_key, section_dict in CURATED_FDA_DATA.items():
            if med_key in detected_medicine or detected_medicine in med_key:
                if target_intent in section_dict:
                    med_name, sec_name, content = section_dict[target_intent]
                    doc_text = (
                        f"Medicine: {med_name}\n"
                        f"Section: {sec_name}\n"
                        f"MatchedRecords: 1\n"
                        f"SourceFile: Curated DailyMed Reference\n\n"
                        f"{content}"
                    )
                    documents.append(doc_text)
                    metadatas.append({
                        "medicine": med_name,
                        "section": sec_name,
                        "content": content,
                        "source": "Curated DailyMed Reference",
                        "matched_records": 1
                    })
                    break

    print(f"RESULTS RETRIEVED FROM DATASET: {len(documents)}")
    return {"documents": [documents], "metadatas": [metadatas]}
