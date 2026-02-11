import os
import re
import json
import csv
from glob import glob

INPUT_DIR = os.path.join("finished", "rf")
OUTPUT_DIR = os.path.join(INPUT_DIR, "json_metadata")
LINKS_CSV = os.path.join("resources", "rf", "lankar.csv")  # justera om annat filnamn/sökväg

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_links(csv_path):
    if not os.path.exists(csv_path):
        return []
    for delim in (";", ","):
        with open(csv_path, encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f, delimiter=delim)
                rows = [r for r in reader]
                if rows:
                    return rows
            except Exception:
                continue
    return []

def extract_date_from_filename(fname):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    return m.group(1) if m else None

def gather_links_for_date(rows, date):
    if not rows:
        return []
    matches = []
    for r in rows:
        datum = (r.get("datum") or r.get("date") or "").strip()
        lank = (r.get("lank") or r.get("link") or r.get("url") or r.get("länk") or "").strip()
        if not lank:
            continue
        if date and datum and datum.startswith(date):
            matches.append(lank)
    if not matches:
        for r in rows:
            lank = (r.get("lank") or r.get("link") or r.get("url") or r.get("länk") or "").strip()
            if lank:
                matches.append(lank)
    # dedupe while preserving order
    seen = set()
    out = []
    for l in matches:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return out

def seconds_to_hhmmss(value):
    """Konverterar ett numeriskt värde (sekunder) till 'HH:MM:SS'."""
    if value is None:
        return None
    try:
        total = int(float(value))
    except Exception:
        return value
    hrs = total // 3600
    mins = (total % 3600) // 60
    secs = total % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def process_file(json_path, rows):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        # Läs filinnehåll och visa en bit runt felposition för debug
        with open(json_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        pos = e.pos if hasattr(e, "pos") else None
        start = max(0, (pos or 0) - 200)
        end = (pos or 0) + 200
        print(f"❌ JSONDecodeError i fil: {json_path}")
        print(f"  Fel: {e.msg} vid rad {e.lineno} kolumn {e.colno} (pos {pos})")
        print("---- Kontext ----")
        print(content[start:end])
        print("---- Slut kontext ----")
        return  # hoppar över filen eller ändra till raise för att stoppa
    date = extract_date_from_filename(os.path.basename(json_path))
    links = gather_links_for_date(rows, date)
    metadata = {"date": date, "links": links}

    # Konvertera start/end i varje transcript-entry till HH:MM:SS om möjligt
    converted = []
    for entry in data:
        e = entry.copy()
        if "start" in e:
            e["start"] = seconds_to_hhmmss(e.get("start"))
        if "end" in e:
            e["end"] = seconds_to_hhmmss(e.get("end"))
        converted.append(e)

    out_obj = {"metadata": metadata, "transcript": converted}
    base = os.path.basename(json_path)
    name, ext = os.path.splitext(base)
    out_name = f"{name}.json"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)
    print(f"Sparad: {out_path} (links: {len(links)})")

def main():
    rows = load_links(LINKS_CSV)
    json_files = glob(os.path.join(INPUT_DIR, "*.json"))
    for jf in json_files:
        # skip files already created in json_metadata
        if os.path.commonpath([os.path.abspath(jf), os.path.abspath(OUTPUT_DIR)]) == os.path.abspath(OUTPUT_DIR):
            continue
        process_file(jf, rows)

if __name__ == "__main__":
    main()