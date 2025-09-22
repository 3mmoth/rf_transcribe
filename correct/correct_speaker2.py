import json
import csv
import re
from CompareName import CompareName

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

def find_names_in_text(text):
    """
    Returnerar en lista med namn (två eller fler ord i följd som börjar med versal).
    Exempel: "Jag ger ordet till Anna Andersson och Per Larsson." -> ["Anna Andersson", "Per Larsson"]
    """
    # Matcha två eller fler ord som börjar med versal, ev. bindestreck, åäö
    pattern = r'\b([A-ZÅÄÖ][a-zåäöéèêëüûùúïîìíôöòóa-z\-]+(?:\s+[A-ZÅÄÖ][a-zåäöéèêëüûùúïîìíôöòóa-z\-]+)+)\b'
    return re.findall(pattern, text)

def set_chairman_phrase(data, obj):
    old_speaker = obj.get("speaker")
    obj["speaker"] = ordforande_namn
    obj["party"] = namn_till_parti.get(ordforande_namn)
    if old_speaker and len(obj["text"]) < 200:
        for o in data:
            if o.get("speaker") == old_speaker:
                o["speaker"] = ordforande_namn
                o["party"] = namn_till_parti.get(ordforande_namn)
                o["role"] = namn_till_uppdrag.get(ordforande_namn)


def get_type_of_speech(obj):
    anforande_pattern = r"\banförande\b"
    replik_pattern = r"\breplik\b"
    genmäle_pattern = r"\bgenmäle\b"
    speechtype = None
    if re.search(anforande_pattern, obj["text"], re.IGNORECASE):
        speechtype = "anförande"
    elif re.search(replik_pattern, obj["text"], re.IGNORECASE):
        speechtype = "replik"
    elif re.search(genmäle_pattern, obj["text"], re.IGNORECASE):
        speechtype = "genmäle"
    else:
        speechtype = "anförande"
    return speechtype

# 1. Läs in alla namn och partier från fortroendevalda.csv
namn_till_parti = {}
namn_till_uppdrag = {}
name_comparator = CompareName()
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
    # Sätt speaker till ordförandens namn om det är en ordförandefras
    if is_chairman_phrase(obj["text"]) and ordforande_namn:
        set_chairman_phrase(data, obj)
    # Sätt speaker och party på nästföljande objekt om namn hittas i text
    forekommande_namn = find_names_in_text(obj["text"])
    if len(forekommande_namn) > 0:
        for fn in forekommande_namn:
            print(f"  Hittade namn i text: '{fn}'")
            match, score = name_comparator.match_name(fn, "fortroendevalda.csv", 80)
            if match != None:
                for n in namn_till_parti:
                    target_idx = i + 1
                    if target_idx < len(data):
                        data[target_idx]["speaker"] = match
                        data[target_idx]["party"] = namn_till_parti.get(match)
                        data[target_idx]["role"] = namn_till_uppdrag.get(match)
                        if data[target_idx - 1].get("role") == "ordförande":
                            data[target_idx]["type_of_speech"] = get_type_of_speech(data[target_idx - 1])
                    break

# 4. Spara resultatet
with open("trans30small5_speaker_corrected_updated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Klart! Speaker- och party-populering utförd.")