import json
import sys
import pandas as pd
import re

# --- Förbered talarnamn, parti och inläggstyp ---
def parse_title(title):
    """
    Dela upp title i namn, parti och ev. inläggstyp (Replik/Genmäle).
    Exempel: 'Anna Andersson (M) - Replik'
             => name='Anna Andersson', party='M', inlagg='Replik'
    """
    inlagg = None
    if "-" in title:
        title, inlagg = [x.strip() for x in title.split("-", 1)]

    if "(" in title and ")" in title:
        name = title.split("(")[0].strip()
        party = title.split("(")[1].replace(")", "").strip()
    else:
        name = title.strip()
        party = None

    return name, party, inlagg
# --- Matcha varje block i transcriptet ---
def find_speaker(start_time, timestamps):
    """Hitta talaren vars starttid är närmast men inte större än blockets start."""
    match = timestamps[timestamps["start_time_seconds"] <= start_time]
    if match.empty:
        return None, None, None
    row = match.iloc[-1]
    return row["name"], row["party"], row["inlagg"]

# --- Dela upp block som inleds med 'Varsågod' ---
def split_chairman_phrase(block):
    """
    Om blocket börjar med 'Varsågod' (ev. skiljetecken/whitespace) följt av annan text,
    dela upp blocket i två: ett för ordförande och ett för talaren.
    """
    # Regex: fångar inledande 'varsågod' (ev. skiljetecken/whitespace), resten i en grupp
    match = re.match(r"^\s*(varsågod[.!?:,;…»”\"']*)(\s+)(.+)$", block["text"], re.IGNORECASE)
    if match:
        chairman_text = match.group(1)
        speaker_text = match.group(3)
        # Skapa två block: ett för ordförande, ett för talaren
        chairman_block = block.copy()
        chairman_block["text"] = chairman_text
        chairman_block["talare"] = "Anna Sotkasiira Wik"
        chairman_block["parti"] = "Moderaterna"
        chairman_block["inlagg"] = "Fördela ordet"
        # Justera tidsstämplar om du vill (t.ex. dela på mitten), annars behåll samma
        speaker_block = block.copy()
        speaker_block["text"] = speaker_text
        # speaker_block behåller sina ursprungliga talare/parti/inlagg
        return [chairman_block, speaker_block]
    else:
        return [block]

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

def main(input_file, output_file):
# --- Ladda data ---
    with open(input_file, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    timestamps = pd.read_csv("tidsstamplar.csv")
    timestamps[["name", "party", "inlagg"]] = timestamps["title"].apply(lambda x: pd.Series(parse_title(x)))
    timestamps = timestamps.sort_values("start_time_seconds").reset_index(drop=True)
    for block in transcript:
        name, party, inlagg = find_speaker(block["start"], timestamps)
        block["talare"] = name
        block["parti"] = party
        block["inlagg"] = inlagg

    # --- Slå ihop block från samma talare, men bryt vid vissa nyckelord ---
    BREAK_PATTERNS = [
        r"varsågod[.!?:,;…»”\"']*$",      # matchar "varsågod" med ev. skiljetecken på slutet
        r"då går replik till",
        r"då går genmäle till",
        r"då går ordet till",
    ]
    merged = []
    for block in transcript:
        text_lower = block["text"].lower()
        should_break = any(
            re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for pattern in BREAK_PATTERNS
        )

        if (
            merged 
            and merged[-1]["talare"] == block["talare"] 
            and merged[-1]["parti"] == block["parti"] 
            and merged[-1].get("inlagg") == block.get("inlagg") 
            and not should_break
        ):
            # uppdatera slut och text
            merged[-1]["end"] = block["end"]
            merged[-1]["text"] += " " + block["text"]
        else:
            merged.append(block.copy())

    # Dela upp block i merged som inleds med 'Varsågod'
    final_blocks = []
    for block in merged:
        final_blocks.extend(split_chairman_phrase(block))

    # --- Sätt talare/parti för exakt "Varsågod" i slutresultatet ---
    for block in final_blocks:
        if re.fullmatch(r"\s*varsågod[.!?:,;…»”\"']*\s*", block["text"], re.IGNORECASE):
            block["talare"] = "Anna Sotkasiira Wik"
            block["parti"] = "Moderaterna"
            block["inlagg"] = "Fördela ordet"

    # Applicera ordförandematchning på alla block i final_blocks
    for block in final_blocks:
        if is_chairman_phrase(block["text"]):
            block["talare"] = "Anna Sotkasiira Wik"
            block["parti"] = "Moderaterna"
            block["inlagg"] = "Fördela ordet"

    # --- Spara till ny fil ---
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_blocks, f, ensure_ascii=False, indent=2)

    print("Klart! Filen finns som:", output_file)   

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Användning: python rf_transcribe.py <input.json> <output.json>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)