import csv
from run_scripts import run_scripts
from itertools import islice

def main(index, fullmaktige, run_queue):
    with open("resources/" + fullmaktige + "/lankar.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)  # Gör reader till en lista så vi kan indexera

    if run_queue == "true":
        run_scripts(rows[int(index)]["lank"].strip(), fullmaktige, rows[int(index)]["datum"].strip())
    elif run_queue == "false":
        for i, row in enumerate(rows[int(index):], start=int(index)):
            run_scripts(row["lank"].strip(), fullmaktige, row["datum"].strip())