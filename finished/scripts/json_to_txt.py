import json
from datetime import timedelta

# Filnamn in/ut
input_file = "trans30small5_speaker_corrected_updated.json"
output_file = "transkribering.txt"

def seconds_to_hhmmss(seconds: float) -> str:
    """Konverterar sekunder till hh:mm:ss"""
    return str(timedelta(seconds=int(seconds)))

def main():
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

if __name__ == "__main__":
    main()