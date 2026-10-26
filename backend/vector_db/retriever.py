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


# Curated FDA records for key baseline medicines (Warfarin, Ibuprofen, Metformin)
CURATED_FDA_DATA = {
    "ibuprofen": {
        "INGREDIENTS": (
            "Ibuprofen",
            "DESCRIPTION & INGREDIENTS",
            "Active Ingredient: Ibuprofen (200 mg in OTC tablets; 400 mg, 600 mg, 800 mg in prescription formulations) — a nonsteroidal anti-inflammatory drug (NSAID).\n"
            "Inactive Ingredients: Colloidal silicon dioxide, croscarmellose sodium, hypromellose 2910, hydroxypropyl cellulose, magnesium stearate, microcrystalline cellulose, polyethylene glycol 400, pregelatinized starch, povidone K-90, sodium lauryl sulphate, titanium dioxide."
        ),
        "INDICATIONS": (
            "Ibuprofen",
            "INDICATIONS AND USAGE",
            "• Relief of mild to moderate pain (such as headache, toothache, muscular ache, backache, arthritis, and menstrual cramps).\n"
            "• Reduction of fever.\n"
            "• Relief of signs and symptoms of rheumatoid arthritis and osteoarthritis."
        ),
        "ADVERSE": (
            "Ibuprofen",
            "ADVERSE REACTIONS & SIDE EFFECTS",
            "• Common Side Effects: Nausea, epigastric pain, heartburn, indigestion, diarrhea, constipation, dizziness, headache, abdominal distress.\n"
            "• Serious Adverse Events: Stomach bleeding or ulcers (black/tarry stools), fluid retention, worsening high blood pressure, and renal (kidney) impairment."
        ),
        "INTERACTIONS": (
            "Ibuprofen",
            "DRUG INTERACTIONS",
            "• Aspirin & other NSAIDs (Naproxen): Increases gastrointestinal bleeding risks and diminishes aspirin's cardioprotective effect.\n"
            "• Blood Thinners (Warfarin, Apixaban): Substantially increases bleeding danger.\n"
            "• ACE Inhibitors & Diuretics: Ibuprofen may reduce their blood-pressure-lowering effectiveness.\n"
            "• Lithium & Methotrexate: Ibuprofen can decrease their clearance, increasing toxicity risks."
        ),
        "FOOD": (
            "Ibuprofen",
            "FOOD AND DIETARY INTERACTIONS",
            "• Take with food, milk, or a full glass of water to reduce stomach upset and mucosal irritation.\n"
            "• Avoid alcohol: Drinking 3 or more alcoholic drinks every day while taking ibuprofen significantly increases the risk of severe stomach bleeding."
        ),
        "WARNINGS": (
            "Ibuprofen",
            "WARNINGS & PRECAUTIONS",
            "• Cardiovascular Risk: NSAIDs may cause an increased risk of serious cardiovascular thrombotic events, myocardial infarction (heart attack), and stroke.\n"
            "• Gastrointestinal Risk: Severe gastrointestinal inflammation, ulceration, bleeding, and perforation of stomach or intestines can occur at any time without warning."
        ),
        "DOSAGE": (
            "Ibuprofen",
            "DOSAGE AND ADMINISTRATION",
            "• Adults & Children 12+: 200 mg to 400 mg every 4 to 6 hours while symptoms persist.\n"
            "• Maximum OTC Dose: Do not exceed 1,200 mg in 24 hours unless directed by a doctor.\n"
            "• Use the lowest effective dose for the shortest duration necessary."
        )
    },
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

    # 3. Check curated data first if available for high-quality structured answers
    if detected_medicine and detected_medicine in CURATED_FDA_DATA:
        curated_dict = CURATED_FDA_DATA[detected_medicine]
        if target_intent != "ALL" and target_intent in curated_dict:
            med_name, sec_name, content = curated_dict[target_intent]
            doc_text = f"Medicine: {med_name}\nSection: {sec_name}\n\n{content}"
            documents.append(doc_text)
            metadatas.append({"medicine": med_name, "section": sec_name, "content": content})
            return {"documents": [documents], "metadatas": [metadatas]}

    # 4. Search the full 8,118 FDA DailyMed dataset
    dataset = get_fda_dataset()
    if dataset and detected_medicine:
        target_sections = SECTION_MAP.get(target_intent, [])

        # Filter strictly for the target medicine
        med_matches = [
            d for d in dataset
            if d["medicine"].lower().strip() == detected_medicine or detected_medicine in d["medicine"].lower()
        ]

        if med_matches:
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
                    doc_formatted = f"Medicine: {d['medicine']}\nSection: {d['section']}\n\n{content}"
                    documents.append(doc_formatted)
                    metadatas.append({"medicine": d["medicine"], "section": d["section"], "content": content})
                if len(documents) >= 2:
                    break

    # 5. If no documents found, try curated data fallback
    if not documents and detected_medicine:
        for med_key, section_dict in CURATED_FDA_DATA.items():
            if med_key in detected_medicine or detected_medicine in med_key:
                if target_intent in section_dict:
                    med_name, sec_name, content = section_dict[target_intent]
                    doc_text = f"Medicine: {med_name}\nSection: {sec_name}\n\n{content}"
                    documents.append(doc_text)
                    metadatas.append({"medicine": med_name, "section": sec_name, "content": content})
                    break

    print(f"RESULTS FOUND: {len(documents)}")
    return {"documents": [documents], "metadatas": [metadatas]}
