import zipfile
from io import BytesIO
import sys
from pathlib import Path
from lxml import etree

# Allow importing from backend/
sys.path.append(str(Path(__file__).resolve().parent.parent))

from vector_db.embedding import get_embedding
from vector_db.chroma_db import collection

# ============================================================
# Dataset Path
# ============================================================

DATASET_PATH = Path(
    r"C:\Users\thave\Downloads\dm_spl_release_human_rx_part6\prescription"
)

# XML Namespace
ns = {
    "hl7": "urn:hl7-org:v3"
}

# Sections to Store
important_sections = {
    "DESCRIPTION",
    "CLINICAL PHARMACOLOGY",
    "INDICATIONS AND USAGE",
    "CONTRAINDICATIONS",
    "WARNINGS",
    "PRECAUTIONS",
    "ADVERSE REACTIONS",
    "DOSAGE AND ADMINISTRATION",
    "DRUG INTERACTIONS",
    "INGREDIENTS",
    "INGREDIENTS AND APPEARANCE",
    "ACTIVE INGREDIENT",
    "ACTIVE INGREDIENTS",
    "INACTIVE INGREDIENT",
    "INACTIVE INGREDIENTS",
    "COMPOSITION"
}

medicine_count = 0
section_count = 0
failed_count = 0

# ============================================================
# Iterate through every ZIP
# ============================================================

for zip_file in DATASET_PATH.glob("*.zip"):

    try:

        with zipfile.ZipFile(zip_file, "r") as z:

            xml_name = None

            for file in z.namelist():

                if file.lower().endswith(".xml"):
                    xml_name = file
                    break

            if xml_name is None:
                continue

            xml_data = z.read(xml_name)

            tree = etree.parse(BytesIO(xml_data))
            root = tree.getroot()

        medicine_count += 1

        # ====================================================
        # Extract Medicine Name
        # ====================================================

        medicine_name = None

        name_paths = [
            "//hl7:manufacturedMedicine/hl7:name",
            "//hl7:manufacturedProduct/hl7:manufacturedMedicine/hl7:name",
            "//hl7:manufacturedProduct/hl7:name",
        ]

        for path in name_paths:
            medicine_tags = root.xpath(path, namespaces=ns)

            if medicine_tags:
                name = " ".join(
                    medicine_tags[0].itertext()
                ).strip()

                if name:
                    medicine_name = name
                    break

        # Fallback only if no medicine name exists
        if not medicine_name:
            medicine_name = zip_file.stem

        print("Medicine:", medicine_name)

        # ====================================================
        # Read Sections
        # ====================================================

        sections = root.xpath("//hl7:section", namespaces=ns)

        for section in sections:

            title_element = section.find(
                "hl7:title",
                namespaces=ns
            )

            if title_element is None:
                continue

            title = " ".join(
                title_element.itertext()
            ).strip()

            if title not in important_sections:
                continue

            text_element = section.find(
                "hl7:text",
                namespaces=ns
            )

            if text_element is None:
                continue

            content = " ".join(
                text_element.itertext()
            ).strip()

            if not content:
                continue

            # ====================================================
            # Rich Document for Better Retrieval
            # ====================================================

            text_to_embed = f"""
Medicine: {medicine_name}

Section: {title}

Content:
{content}
"""

            embedding = get_embedding(text_to_embed)

            doc_id = f"{zip_file.stem}_{title}"

            try:

                collection.add(

                    ids=[doc_id],

                    embeddings=[embedding],

                    documents=[text_to_embed],

                    metadatas=[
                        {
                            "medicine": medicine_name,
                            "section": title,
                            "source": zip_file.name
                        }
                    ]
                )

                section_count += 1

            except Exception:
                # Duplicate document
                pass

        # ====================================================
        # Progress
        # ====================================================

        if medicine_count % 100 == 0:

            print(
                f"Processed Medicines: {medicine_count} | Stored Sections: {section_count}"
            )

    except Exception as e:

        failed_count += 1

        print(f"Failed: {zip_file.name}")
        print(e)

# ============================================================
# Summary
# ============================================================

print("\n" + "=" * 60)
print("INGESTION COMPLETE")
print("=" * 60)

print(f"Medicines Processed : {medicine_count}")
print(f"Sections Stored     : {section_count}")
print(f"Failed XMLs         : {failed_count}")