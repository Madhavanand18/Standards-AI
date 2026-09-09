import pymupdf

doc = pymupdf.open()

# Page 1: General Procurement Requirements
p1 = doc.new_page()
p1.insert_text(
    (50, 72),
    "CENTRAL PUBLIC WORKS DEPARTMENT\n"
    "NOTICE INVITING TENDER — CIVIL & STRUCTURAL WORKS\n\n"
    "SECTION 1: STRUCTURAL REINFORCEMENT REQUIREMENTS\n"
    "The contractor shall supply Thermo Mechanically Treated (TMT) steel bars of Grade Fe 500D\n"
    "conforming to IS 1786:2008 with latest amendments for reinforced cement concrete works.\n"
    "All reinforcement bars shall bear the standard ISI certification mark.\n"
    "Diameter requirements: 10 mm, 12 mm, 16 mm, 20 mm, and 25 mm.\n",
    fontsize=11
)

# Page 2: Structural Steel Fabrication
p2 = doc.new_page()
p2.insert_text(
    (50, 72),
    "SECTION 2: STRUCTURAL STEEL FABRICATION\n"
    "All hot rolled structural steel plates and sections for bridge girders\n"
    "shall conform strictly to IS 2062:2011 Grade E250 Quality A.\n"
    "Welding electrodes and consumables shall adhere to relevant Indian Standards.\n"
    "Compliance with Quality Control Order (QCO) issued by Ministry of Steel is mandatory.\n",
    fontsize=11
)

doc.save("c:/Standards-AI/Samples/Sample_Tender.pdf")
doc.close()
print("Sample PDF generated successfully.")
