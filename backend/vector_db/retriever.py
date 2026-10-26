from utils.query_normalizer import normalize_query
from vector_db.embedding import get_embedding
from vector_db.chroma_db import get_collection

FALLBACK_FDA_DATA = {
    "ibuprofen": {
        "INGREDIENTS": (
            "Ibuprofen",
            "INGREDIENTS & COMPOSITION",
            "• Active Ingredient: Ibuprofen (200 mg in OTC tablets; 400 mg, 600 mg, 800 mg in prescription formulations) — a nonsteroidal anti-inflammatory drug (NSAID).\n"
            "• Inactive Ingredients: Colloidal silicon dioxide, croscarmellose sodium, hypromellose, magnesium stearate, microcrystalline cellulose, polyethylene glycol, polysorbate 80, pregelatinized starch, titanium dioxide, carnauba wax."
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
            "• Aspirin & other NSAIDs (Naproxen): Increases the risk of serious gastrointestinal bleeding and diminishes aspirin's cardioprotective effect.\n"
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
            "• Active Ingredient: Warfarin Sodium (1 mg, 2 mg, 2.5 mg, 3 mg, 4 mg, 5 mg, 6 mg, 7.5 mg, 10 mg scored tablets) — a vitamin K antagonist anticoagulant.\n"
            "• Inactive Ingredients: Lactose monohydrate, magnesium stearate, povidone, corn starch, and color additives (D&C Yellow No. 10, FD&C Blue No. 1, FD&C Red No. 40 depending on tablet strength)."
        ),
        "INDICATIONS": (
            "Warfarin",
            "INDICATIONS AND USAGE",
            "• Prophylaxis and treatment of venous thrombosis (DVT) and pulmonary embolism (PE).\n"
            "• Prophylaxis and treatment of thromboembolic complications associated with atrial fibrillation and/or cardiac valve replacement.\n"
            "• Reduction in the risk of recurrent myocardial infarction and stroke after heart attack."
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
            "• Antibiotics (Ciprofloxacin, Metronidazole, Bactrim, Erythromycin): Alter gut flora and metabolism, dangerously elevating INR.\n"
            "• Antifungals (Fluconazole) and SSRI antidepressants: Inhibit warfarin clearance.\n"
            "• Herbal supplements: St. John's Wort decreases warfarin levels; Ginkgo, Garlic, and Ginseng can increase bleeding."
        ),
        "ADVERSE": (
            "Warfarin",
            "ADVERSE REACTIONS & SIDE EFFECTS",
            "• Major or Fatal Hemorrhage: Uncontrolled bleeding (nosebleeds, bleeding gums, dark/red urine, tarry stools, unusual bruising, coughing up blood).\n"
            "• Tissue Necrosis & Gangrene of skin.\n"
            "• Systemic Atheroemboli / Purple Toes Syndrome, nausea, abdominal pain."
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
    },
    "acetaminophen": {
        "INGREDIENTS": (
            "Acetaminophen (Paracetamol)",
            "INGREDIENTS & COMPOSITION",
            "• Active Ingredient: Acetaminophen (325 mg Regular Strength; 500 mg Extra Strength; 650 mg Extended Release).\n"
            "• Inactive Ingredients: Corn starch, crospovidone, povidone, pregelatinized starch, stearic acid, sodium starch glycolate, hypromellose, polyethylene glycol, titanium dioxide."
        ),
        "INDICATIONS": (
            "Acetaminophen (Paracetamol)",
            "INDICATIONS AND USAGE",
            "• Temporary relief of minor aches and pains due to headache, muscular aches, backache, minor pain of arthritis, the common cold, toothache, and premenstrual/menstrual cramps.\n"
            "• Temporary reduction of fever."
        ),
        "ADVERSE": (
            "Acetaminophen (Paracetamol)",
            "ADVERSE REACTIONS & SIDE EFFECTS",
            "• Generally well tolerated at recommended dosages.\n"
            "• Serious Risks: Hepatotoxicity (acute liver failure), allergic skin reactions (Stevens-Johnson syndrome, toxic epidermal necrolysis), and angioedema."
        ),
        "WARNINGS": (
            "Acetaminophen (Paracetamol)",
            "WARNINGS & LIVER RISK",
            "• Severe Liver Damage Warning: Severe liver injury can occur if you take more than 4,000 mg in 24 hours, take with other drugs containing acetaminophen, or consume 3 or more alcoholic drinks daily."
        ),
        "INTERACTIONS": (
            "Acetaminophen (Paracetamol)",
            "DRUG INTERACTIONS",
            "• Other Acetaminophen Products: Combining with multi-symptom cold/flu medicines (NyQuil, DayQuil) or prescription pain relievers (Percocet, Vicodin) risks toxic overdose.\n"
            "• Warfarin: Chronic high-dose acetaminophen (over 2,000 mg/day) may increase INR and bleeding risk."
        ),
        "FOOD": (
            "Acetaminophen (Paracetamol)",
            "FOOD AND DIETARY INTERACTIONS",
            "• May be taken with or without food.\n"
            "• Avoid alcohol: Chronic or heavy alcohol intake depletes liver glutathione, drastically increasing the susceptibility to acetaminophen-induced liver necrosis."
        ),
        "DOSAGE": (
            "Acetaminophen (Paracetamol)",
            "DOSAGE AND ADMINISTRATION",
            "• Adults: 325 mg to 650 mg every 4 to 6 hours, or 1,000 mg every 6 hours as needed.\n"
            "• Maximum Daily Limit: Never exceed 4,000 mg in a 24-hour period (or 3,000 mg/day for vulnerable individuals)."
        )
    },
    "metformin": {
        "INGREDIENTS": (
            "Metformin",
            "INGREDIENTS & COMPOSITION",
            "• Active Ingredient: Metformin Hydrochloride (500 mg, 850 mg, 1,000 mg immediate-release and extended-release tablets).\n"
            "• Inactive Ingredients: Hypromellose, magnesium stearate, microcrystalline cellulose, polyethylene glycol, povidone, titanium dioxide."
        ),
        "INDICATIONS": (
            "Metformin",
            "INDICATIONS AND USAGE",
            "• Adjunct to diet and exercise to improve glycemic control in adults and pediatric patients (10 years and older) with type 2 diabetes mellitus."
        ),
        "ADVERSE": (
            "Metformin",
            "ADVERSE REACTIONS & SIDE EFFECTS",
            "• Common GI Effects: Diarrhea, nausea, vomiting, abdominal bloating, flatulence, anorexia, unpleasant metallic taste.\n"
            "• Vitamin B12 Deficiency: Long-term use can reduce serum Vitamin B12 absorption."
        ),
        "FOOD": (
            "Metformin",
            "FOOD AND DIETARY INTERACTIONS",
            "• Always take with meals to minimize gastrointestinal adverse effects.\n"
            "• Avoid excessive alcohol: Acute or chronic alcohol ingestion potentiates the effect of metformin on lactate metabolism and drastically increases lactic acidosis risk."
        ),
        "WARNINGS": (
            "Metformin",
            "WARNINGS & PRECAUTIONS",
            "• Boxed Warning: Lactic Acidosis — a rare but serious metabolic complication characterized by elevated blood lactate levels, hypothermia, hypotension, and resistant bradyarrhythmias.\n"
            "• Contraindicated in severe renal impairment (eGFR < 30 mL/min/1.73 m²)."
        ),
        "INTERACTIONS": (
            "Metformin",
            "DRUG INTERACTIONS",
            "• Iodinated Radiopaque Contrast Agents: Must temporarily discontinue metformin before or at the time of procedure due to acute renal failure risks.\n"
            "• Carbonic Anhydrase Inhibitors (Topiramate, Zonisamide): Increase lactic acidosis danger."
        ),
        "DOSAGE": (
            "Metformin",
            "DOSAGE AND ADMINISTRATION",
            "• Starting Dose: 500 mg orally twice a day with meals or 850 mg once daily with a meal.\n"
            "• Titration: Increase by 500 mg weekly or 850 mg every 2 weeks up to a maximum of 2,550 mg daily."
        )
    }
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


def retrieve(query: str, medicine: str = None, k: int = 20):
    print("=" * 60)
    print("USER QUERY:", query)

    normalized_query = normalize_query(query)
    print("NORMALIZED QUERY:", normalized_query)

    documents = []
    metadatas = []

    # Detect user's question intent (e.g. INGREDIENTS, ADVERSE, FOOD, INDICATIONS)
    target_intent = detect_section_intent(query)
    print("DETECTED INTENT:", target_intent)

    # 1. Try ChromaDB if it has documents
    col = get_collection()
    if col is not None:
        try:
            doc_count = col.count()
            if doc_count > 0:
                query_embedding = get_embedding(normalized_query)
                where_filter = {"medicine": medicine} if medicine else None
                results = col.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=where_filter
                )
                if results.get("documents") and results["documents"][0]:
                    documents = results["documents"][0]
                    metadatas = results["metadatas"][0]
        except Exception as e:
            print(f"ChromaDB retrieval error: {e}")

    # 2. If ChromaDB has no documents, use curated FDA knowledge base filtered by user's question intent
    if not documents:
        for med_key, section_dict in FALLBACK_FDA_DATA.items():
            if med_key in normalized_query or med_key in query.lower():
                # If a specific section was asked, return ONLY that section
                if target_intent != "ALL" and target_intent in section_dict:
                    med_name, section_title, content = section_dict[target_intent]
                    doc_text = f"### {med_name} — {section_title}\n\n{content}"
                    documents.append(doc_text)
                    metadatas.append({"medicine": med_name, "section": section_title})
                else:
                    # If intent was general (e.g. "What is Ibuprofen?"), return INDICATIONS + SUMMARY
                    preferred_keys = ["INDICATIONS", "ADVERSE", "WARNINGS"]
                    for key in preferred_keys:
                        if key in section_dict:
                            med_name, section_title, content = section_dict[key]
                            doc_text = f"### {med_name} — {section_title}\n\n{content}"
                            documents.append(doc_text)
                            metadatas.append({"medicine": med_name, "section": section_title})

    print(f"RESULTS FOUND: {len(documents)}")
    return {"documents": [documents], "metadatas": [metadatas]}
