import csv
import sys
from run_scripts import run_scripts
from itertools import islice

def main(index, fullmaktige, run_queue):
    with open("resources/" + fullmaktige + "/lankar.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)  # Gör reader till en lista så vi kan indexera

    if run_queue == "false":
        run_scripts(rows[int(index)]["lank"].strip(), fullmaktige, rows[int(index)]["datum"].strip())
    elif run_queue == "true":
        for i, row in enumerate(rows[int(index):], start=int(index)):
            print(f"🔄 Kör index {i}: {row['lank'].strip()}")
            run_scripts(row["lank"].strip(), fullmaktige, row["datum"].strip(), row["typ"].strip())
            print(f"✅ Klart med index {i}\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Användning: python run_queue.py <index> <fullmaktige> <run_queue>")
        print("Exempel: python run_queue.py 0 regionfullmaktige false")
        sys.exit(1)
    index = sys.argv[1]
    fullmaktige = sys.argv[2]
    run_queue = sys.argv[3]
    main(index, fullmaktige, run_queue)