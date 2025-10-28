import json
from datetime import timedelta
import os
from glob import glob

input_dir = "rf"
output_dir = os.path.join(input_dir, "txt")
os.makedirs(output_dir, exist_ok=True)

def seconds_to_hhmmss(seconds: float) -> str:
    """Konverterar sekunder till hh:mm:ss"""
    return str(timedelta(seconds=int(seconds)))

def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_file, "w", encoding="utf-8") as out:
        for entry in data:
            speaker = entry.get("speaker", "Okänd talare")
            party = entry.get("party", "Okänt parti")
            start_time = seconds_to_hhmmss(entry.get("start", 0))
            text = entry.get("text", "").strip()
            out.write(f"[{start_time}] {speaker} ({party}):\n{text}\n\n")

    print(f"Transkriberingen sparad i '{output_file}'")

def main():
    json_files = glob(os.path.join(input_dir, "*.json"))
    for input_file in json_files:
        base = os.path.basename(input_file).replace(".json", ".txt")
        output_file = os.path.join(output_dir, base)
        process_file(input_file, output_file)

if __name__ == "__main__":
    main()