import pandas as pd
from rapidfuzz import fuzz
import phonetics

class CompareName:

    def normalize_name(self, name: str) -> str:
        return name.strip().lower()

    def phonetic_code(self, name: str) -> str:
        return phonetics.metaphone(name)

    def compare_names(self, transcribed: str, target: str) -> int:
        """Jämför två namn (kan vara för- och efternamn)."""
        trans_parts = self.normalize_name(transcribed).split()
        target_parts = self.normalize_name(target).split()

        scores = []
        for t_part in trans_parts:
            best_part_score = 0
            for g_part in target_parts:
                fuzzy_score = fuzz.WRatio(t_part, g_part)
                phon_score = 20 if self.phonetic_code(t_part) == self.phonetic_code(g_part) else 0
                total = fuzzy_score + phon_score
                if total > best_part_score:
                    best_part_score = total
            scores.append(best_part_score)

        return int(sum(scores) / len(scores)) if scores else 0

    def match_name(self, transcribed: str, namn_csv: str, threshold: int):
        """Matcha ett transkriberat namn mot namnlistan i CSV."""
        df_namn = pd.read_csv(namn_csv, delimiter=";")
        namn_lista = df_namn["namn"].dropna().tolist()

        bästa_match = None
        bästa_score = 0
        # print(f"Jämför: '{transcribed}'")
        for namn in namn_lista:
            
            score = self.compare_names(transcribed, namn)
            if score > bästa_score:
                bästa_score = score
                bästa_match = namn
                # print(f"  Ny bästa match: '{bästa_match}' med poäng {bästa_score}")
        if bästa_score >= threshold:
            return bästa_match, bästa_score
        return None, bästa_score


    # === Exempelanvändning ===
    if __name__ == "__main__":
        input_namn = "Elvira Wiberg"   # Detta kan komma från ett annat script
        match, score = match_name(input_namn, "fortroendevalda.csv", threshold=80)

        print(f"Input: {input_namn}")
        print(f"Bästa match: {match} (poäng: {score})")