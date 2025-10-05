import json
import csv
import re
from .CompareName import CompareName

PRESIDIET = "presidiet"
REPLIK = "replik"
GENMALE = "genmäle" 
ANFORANDE = "anförande"
UNDEFINED = "undefined"
INFORMATION = "information"
FORDELA_REPLIK = "fördela replik"
FORDELA_GENMALE = "fördela genmäle"
FORDELA_ANFORANDE = "fördela anförande"
FORDELA_VALARENDE = "fördela valärende"

def is_presidie_phrase(text):
    """
    Returnerar True om texten är en typisk presidiefras.
    """
    patterns = [
        r"\s*varsågod[.!?:,;…»”\"']*\s*$",
        r"\s*och då går ordet till .+,\s*.+,\s*varsågod[.!?:,;…»”\"']*\s*$",
        r"\s*då har vi .+,\s*.+,\s*följt av .+,\s*.+[.!?:,;…»”\"']*\s*$",
        r"\s*vars?ågod[.!?:,;…»”\"']*\s*$",
        r"\s*då går replik till .+",
        r"\s*då går genmäle till .+",
        r"\s*då går ordet till .+",
        r"\s*då lämnar jag över ordet .+",
        r"\bavsägelser?\b",
        r"\bvalärenden?\b",
        r"\s*förslag till beslut .+",
        r"\s*ingen har begärt ordet .+"
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def is_mixed_row(text):
    """
    Returnerar True om texten innehåller både ordförandefras och talarfras.
    Exempel: "Då går ordet till Andreas Wästö för genmäle."
    """
    pattern = r"\sVarsågod[.!?:,;…»”\"']+\s*Tack"
    if re.search(pattern, text, re.IGNORECASE):
        return True
    return False

def is_too_short(text):
    if len(text) < 30:
        return True
    return False

def is_genmale(previous_type_of_speech):
    if previous_type_of_speech == "replik" or previous_type_of_speech == "genmäle":
        return True
    return False

def is_fordela_replik(text):
    if re.search(r"\breplik\b", text, re.IGNORECASE):
        return True
    return False

def is_fordela_genmale(text):
    if re.search(r"\bgenmäle\b", text, re.IGNORECASE):
        return True
    return False

def is_valarende(text):
    patterns = [r"\bvalärenden?\b", 
                r"\bavsägelser?\b", 
                r"\bfyllnadsval\b"]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def find_names_in_text(text):
    """
    Returnerar en lista med namn (två eller fler ord i följd som börjar med versal).
    Exempel: "Jag ger ordet till Anna Andersson och Per Larsson." -> ["Anna Andersson", "Per Larsson"]
    """
    # Matcha två eller fler ord som börjar med versal, ev. bindestreck, åäö
    pattern = r'\b([A-ZÅÄÖ][a-zåäöéèêëüûùúïîìíôöòóa-z\-]+(?:-[A-ZÅÄÖ][a-zåäöéèêëüûùúïîìíôöòóa-z\-]+)?(?:\s+[A-ZÅÄÖ][a-zåäöéèêëüûùúïîìíôöòóa-z\-]+)+)\b'    
    return re.findall(pattern, text)

def set_presidie(data, obj):
    old_speaker = obj.get("speaker")
    obj["speaker"] = PRESIDIET
    obj["party"] = PRESIDIET
    if old_speaker and len(obj["text"]) < 200:
        for o in data:
            if o.get("speaker") == old_speaker:
                o["speaker"] = PRESIDIET
                o["party"] = PRESIDIET
                o["role"] = PRESIDIET

        data = merge_same_speaker(data)
                
        for o in data:
            if is_fordela_replik(o["text"]):
                o["type_of_speech"] = FORDELA_REPLIK
            elif is_fordela_genmale(o["text"]):
                o["type_of_speech"] = FORDELA_GENMALE
            elif is_valarende(o["text"]):
                o["type_of_speech"] = FORDELA_VALARENDE
            else:
                o["type_of_speech"] = FORDELA_ANFORANDE

def merge_same_speaker(data):
    merged_data = []
    i = 0
    while i < len(data):
        current = data[i].copy()
            # Slå ihop så länge nästa objekt har samma speaker
        while i + 1 < len(data) and data[i + 1].get("speaker") == current.get("speaker"):
                # Lägg till texten från nästa objekt
            current["text"] = current["text"].rstrip() + " " + data[i + 1]["text"].lstrip()
                # (valfritt) slå ihop andra fält om du vill
            current["end"] = data[i + 1]["end"]
            i += 1
        merged_data.append(current)
        i += 1

    data = merged_data
    return data

def merge_same_speaker_okand(data):
    merged_data = []
    i = 0
    while i < len(data):
        current = data[i].copy()
        # Slå ihop så länge nästa objekt har samma speaker
        while i + 1 < len(data) and data[i + 1].get("speaker").startswith("SPEAKER") and current.get("speaker").startswith("SPEAKER"):
            # Lägg till texten från nästa objekt
            current["text"] = current["text"].rstrip() + " " + data[i + 1]["text"].lstrip()
            # (valfritt) slå ihop andra fält om du vill
            current["end"] = data[i + 1]["end"]
            current["speaker"] = "SPEAKER_UNDEFINED_" + str(i)
            i += 1
        merged_data.append(current)
        i += 1

    data = merged_data
    return data

def get_type_of_speech(obj):
    anforande_pattern = r"\banförande\b"
    replik_pattern = r"\breplik\b"
    genmäle_pattern = r"\bgenmäle\b"
    speechtype = None
    if re.search(anforande_pattern, obj["text"], re.IGNORECASE):
        speechtype = ANFORANDE
    elif re.search(replik_pattern, obj["text"], re.IGNORECASE):
        speechtype = REPLIK
    elif re.search(genmäle_pattern, obj["text"], re.IGNORECASE):
        speechtype = GENMALE
    else:
        speechtype = ANFORANDE
    return speechtype

def correct_speakers_in_transcript(input_file, output_name, fullmaktige, date):
# 1b. Läs in alla namn och partier från fortroendevalda.csv
    namn_till_parti = {}
    namn_till_uppdrag = {}
    name_comparator = CompareName()
    ordforande_namn = None
    ordforande_number = None
    with open("resources/" + fullmaktige +"/fortroendevalda/fortroendevalda_" + fullmaktige + ".csv", encoding="utf-8") as f:
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

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    for obj in data:
        obj["index"] = None
        obj["start"] = obj.get("start")
        obj["end"] = obj.get("end")
        obj["text"] = obj["text"]
        obj["speaker"] = obj.get("speaker")
        obj["party"] = obj.get("party")
        obj["role"] = obj.get("role")
        obj["type_of_speech"] = obj.get("type_of_speech")

    new_data = []
    for i, obj in enumerate(data):
        if is_mixed_row(obj["text"]):
            print(f"Delar upp rad {i} med text: '{obj['text']}'")
            # Dela på första "Varsågod" + skiljetecken + ev. mellanslag
            parts = re.split(r"(\sVarsågod[.!?:,;…»”\"']+\s*)", obj["text"], maxsplit=1)
            if len(parts) == 3:
                first_obj = obj.copy()
                first_obj["text"] = parts[0].strip() + parts[1].strip()
                second_obj = obj.copy()
                second_obj["text"] = parts[2].strip()
                second_obj["speaker"] = "UNDEFINED"
                new_data.append(first_obj)
                new_data.append(second_obj)
            else:
                new_data.append(obj)
        else:
            new_data.append(obj)

    data = new_data

    data = [obj for obj in data if not is_too_short(obj["text"])]

    # 3. Gå igenom objekten och populera speaker och party
    for i, obj in enumerate(data):
        data[i]["index"] = i
        if is_presidie_phrase(obj["text"]) or is_valarende(obj["text"]):
            set_presidie(data, obj)

    for i, obj in enumerate(data):        
        forekommande_namn = find_names_in_text(obj["text"])
        if len(forekommande_namn) > 0:
            for fn in forekommande_namn:
                print(f"  Hittade namn i text: '{fn}'")
                match, score = name_comparator.match_name(fn, "resources/" + fullmaktige+"/fortroendevalda/fortroendevalda_" + fullmaktige + ".csv", 80)
                if match is not None and not is_valarende(obj["text"]):
                    target_idx = i + 1
                    if target_idx < len(data) and data[i].get("role") == PRESIDIET:
                        data[target_idx]["speaker"] = match
                        data[target_idx]["party"] = namn_till_parti.get(match)
                        data[target_idx]["role"] = namn_till_uppdrag.get(match)
                        if data[target_idx - 1].get("role") == PRESIDIET:
                            data[target_idx]["type_of_speech"] = get_type_of_speech(data[target_idx - 1])
                    break  # Bryt loopen över forekommande_namn när första match är funnen
                elif is_valarende(obj["text"]):
                    data[i]["type_of_speech"] = "fördela valärende"
        elif (is_genmale(data[i-1].get("type_of_speech"))) and (data[i-1].get("role") != PRESIDIET):
            if data[i].get("speaker").startswith("SPEAKER") and data[i-1].get("role") != PRESIDIET:
                data[i]["speaker"] = data[i-3].get("speaker")
                data[i]["party"] = data[i-3].get("party")
                data[i]["role"] = data[i-3].get("role")
                data[i]["type_of_speech"] = "corrected genmäle"

    data = merge_same_speaker_okand(data)

    for i, obj in enumerate(data):
        if obj.get("speaker") and obj.get("speaker").startswith("SPEAKER") and obj.get("index") <=10:
            data[i]["speaker"] = INFORMATION
            data[i]["party"] = INFORMATION
            data[i]["role"] = INFORMATION
            data[i]["type_of_speech"] = INFORMATION

    # 4. Spara resultatet
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Klart! Speaker- och party-populering utförd.")