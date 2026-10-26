from utils.query_normalizer import normalize_query
from vector_db.embedding import get_embedding
from vector_db.chroma_db import get_collection

FALLBACK_FDA_DATA = {
    "ibuprofen": [
        ("Ibuprofen", "INDICATIONS AND USAGE", "For relief of mild to moderate pain, reduction of fever, and relief of signs and symptoms of osteoarthritis and rheumatoid arthritis."),
        ("Ibuprofen", "ADVERSE REACTIONS", "Common side effects include nausea, epigastric pain, heartburn, diarrhea, abdominal distress, dizziness, and headache."),
        ("Ibuprofen", "WARNINGS & INTERACTIONS", "Risk of serious gastrointestinal events including bleeding, ulceration, and perforation. Concomitant use with aspirin, other NSAIDs, or alcohol increases bleeding risk.")
    ],
    "warfarin": [
        ("Warfarin", "INDICATIONS AND USAGE", "Prophylaxis and treatment of venous thrombosis, pulmonary embolism, and thromboembolic complications associated with atrial fibrillation or cardiac valve replacement."),
        ("Warfarin", "FOOD AND DIETARY INTERACTIONS", "Foods high in vitamin K (such as spinach, kale, broccoli, and dark leafy greens) can decrease warfarin's effectiveness. Maintain a consistent dietary intake of vitamin K. Avoid heavy alcohol intake and cranberry products which can increase bleeding risk."),
        ("Warfarin", "WARNINGS & DRUG INTERACTIONS", "Warfarin can cause major or fatal bleeding. Concomitant use of NSAIDs like ibuprofen increases the risk of bleeding. Regularly monitor INR levels.")
    ],
    "acetaminophen": [
        ("Acetaminophen (Paracetamol)", "INDICATIONS AND USAGE", "Temporary relief of minor aches, pains, headaches, muscular aches, toothaches, and reduction of fever."),
        ("Acetaminophen (Paracetamol)", "WARNINGS", "Severe liver damage may occur if you take more than 4,000 mg in 24 hours, combine with other acetaminophen-containing medications, or consume 3 or more alcoholic drinks daily.")
    ],
    "metformin": [
        ("Metformin", "INDICATIONS AND USAGE", "Adjunct to diet and exercise to improve glycemic control in adults and children with type 2 diabetes mellitus."),
        ("Metformin", "WARNINGS & PRECAUTIONS", "Risk of lactic acidosis, especially with acute alcohol ingestion or renal impairment. Take with meals to reduce gastrointestinal side effects like nausea and diarrhea.")
    ]
}


def retrieve(query: str, medicine: str = None, k: int = 20):
    print("=" * 60)
    print("USER QUERY:", query)

    # Normalize query
    normalized_query = normalize_query(query)
    print("NORMALIZED QUERY:", normalized_query)

    documents = []
    metadatas = []

    # 1. Try ChromaDB only if it has documents (avoids heavy embedding model downloads when DB is empty)
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
            else:
                print("ChromaDB has 0 stored documents. Using curated FDA knowledge base.")
        except Exception as e:
            print(f"ChromaDB retrieval error: {e}")

    # 2. If ChromaDB returned no results, use curated FDA DailyMed knowledge base
    if not documents:
        for med_key, sections in FALLBACK_FDA_DATA.items():
            if med_key in normalized_query or med_key in query.lower():
                for med_name, section_title, content in sections:
                    doc_text = f"Medicine: {med_name}\nSection: {section_title}\nContent:\n{content}"
                    documents.append(doc_text)
                    metadatas.append({"medicine": med_name, "section": section_title})

    print(f"RESULTS FOUND: {len(documents)}")
    return {"documents": [documents], "metadatas": [metadatas]}
