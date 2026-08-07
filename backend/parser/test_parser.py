from lxml import etree

tree = etree.parse(
    r"C:\Users\raghu\Downloads\dm_spl_release_human_rx_part1\prescription\20060131_dffb4544-0e47-40cd-9baa-d622075838cc\dffb4544-0e47-40cd-9baa-d622075838cc.xml"
)

root = tree.getroot()

ns = {"hl7": "urn:hl7-org:v3"}

important_sections = {
    "DESCRIPTION",
    "CLINICAL PHARMACOLOGY",
    "INDICATIONS AND USAGE",
    "CONTRAINDICATIONS",
    "WARNINGS",
    "PRECAUTIONS",
    "ADVERSE REACTIONS",
    "DOSAGE AND ADMINISTRATION",
    "DRUG INTERACTIONS"
}

sections = root.xpath("//hl7:section", namespaces=ns)

for section in sections:

    title_element = section.find("hl7:title", namespaces=ns)

    if title_element is None:
        continue

    title = " ".join(title_element.itertext()).strip()

    if not title:
        continue

    if title not in important_sections:
        continue

    text_element = section.find("hl7:text", namespaces=ns)

    if text_element is None:
        continue

    content = " ".join(text_element.itertext()).strip()

    if not content:
        continue

    print("=" * 80)
    print(f"SECTION: {title}")
    print("=" * 80)
    print(content)
    print()