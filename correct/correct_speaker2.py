import json
import csv
import re

def is_chairman_phrase(text):
    """
    Returnerar True om texten är en typisk ordförandefras.
    """
    patterns = [
        r"^\s*varsågod[.!?:,;…»”\"']*\s*$",
        r"^\s*och då går ordet till .+,\s*.+,\s*varsågod[.!?:,;…»”\"']*\s*$",
        r"^\s*då har vi .+,\s*.+,\s*följt av .+,\s*.+[.!?:,;…»”\"']*\s*$",
        r"^\s*vars?ågod[.!?:,;…»”\"']*\s*$",
        r"^\s*då går replik till .+",
        r"^\s*då går genmäle till .+",
        r"^\s*då går ordet till .+",
    ]
    for pattern in patterns:
        if re.fullmatch(pattern, text, re.IGNORECASE):
            return True
    return False

# 1. Läs in alla namn och partier från fortroendevalda.csv
namn_till_parti = {}
namn_till_uppdrag = {}
ordforande_namn = None
ordforande_number = None
with open("fortroendevalda.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        namn = row["namn"].strip()
        parti = row["parti"].strip()
        uppdrag = row["uppdrag"].strip().lower()
        namn_till_parti[namn] = parti
        namn_till_uppdrag[namn] = uppdrag
        if uppdrag == "ordförande":
            ordforande_namn = namn

# 2. Läs in JSON-filen
with open("transcribe/trans30small5.json", encoding="utf-8") as f:
    data = json.load(f)

# 3. Gå igenom objekten och populera speaker och party
for i, obj in enumerate(data):
    if "text" in obj:
        # Sätt speaker till ordförandens namn om det är en ordförandefras
        if is_chairman_phrase(obj["text"]) and ordforande_namn:
            old_speaker = obj.get("speaker")
            obj["speaker"] = ordforande_namn
            obj["party"] = namn_till_parti.get(ordforande_namn)
            if old_speaker and len(obj["text"]) < 200:
                for o in data:
                    if o.get("speaker") == old_speaker:
                        o["speaker"] = ordforande_namn
                        o["party"] = namn_till_parti.get(ordforande_namn)
                        o["role"] = namn_till_uppdrag.get(ordforande_namn)
        # Sätt speaker och party på nästföljande objekt om namn hittas i text
        for namn in namn_till_parti:
            if namn in obj["text"]:
                target_idx = i + 1
                if target_idx < len(data):
                    data[target_idx]["speaker"] = namn
                    data[target_idx]["party"] = namn_till_parti[namn]
                    data[target_idx]["role"] = namn_till_uppdrag[namn]
                break

# 4. Spara resultatet
with open("trans30small5_speaker_corrected.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Klart! Speaker- och party-populering utförd.")