
import re
from ovrigt.timestamps import extract_chapters
from get_download_url import get_download_url
from ovrigt.extract_sound import extract_wav_from_mp4
from correct.correct_speaker import correct_speakers_in_transcript


def get_date(text):
    # Försök hitta ett datum på formen ÅÅÅÅ-MM-DD i slutet av strängen
    match = re.search(r'(\d{4}-\d{2}-\d{2})$', text)
    if match:
        return match.group(1)
    return None

def get_fullmaktige(text):
    # Försök hitta "rf" eller "rfk" i texten (case-insensitive)
    match_rf = re.search(r'\bregionostergotland\b', text, re.IGNORECASE)
    match_kf = re.search(r'\bnorrkoping\b', text, re.IGNORECASE)
    if match_rf:
        return "rf"
    elif match_kf:
        return "kf"
    return None

url = "https://regionostergotland.screen9.tv/media/t4fJlbzqCkayMBqqc30Xzw/Regionfullm%C3%A4ktige%20%C3%96sterg%C3%B6tland%202025-04-24"
# chapters = extract_chapters(url)
download_url = get_download_url(url)

print("✅ Hittade download-URL:", download_url)
extract_wav_from_mp4(download_url, "/extracted_audio/" + get_fullmaktige(url) + get_date(url) + ".wav")
print("✅ Ljud extraherat till output.wav")

correct_speakers_in_transcript("output.json", "output_corrected.json", "rf", "2025-04-24")

# for chapter in chapters:
#     print(f"{chapter['formatted_time']} - {chapter['title']}")