import os
import re
from ovrigt.timestamps import extract_chapters
from get_download_url import get_download_url
from ovrigt.extract_sound import extract_wav_from_mp4
from transcribe.transcribe import transcribe
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

def run_scripts(url, fullmaktige, date):
    try:
        download_url = get_download_url(url)
        audio_output_path = "extracted_audio/" + fullmaktige + "_" + date + ".wav"
        transcribe_output_path = "transcribe/transcription/" + fullmaktige + "_" + date + ".json"
        finished_output_path = "finished/" + fullmaktige + "/" + fullmaktige + "_" + date + ".json"
        print("✅ Hittade download-URL:", download_url)
        if not os.path.exists(audio_output_path):
            try:
                extract_wav_from_mp4(download_url, audio_output_path)
                print("✅ Ljud extraherat till", audio_output_path)
            except Exception as e:
                # Ta bort ev. korrupt ljudfil
                if os.path.exists(audio_output_path):
                    os.remove(audio_output_path)
                print("❌ Fel vid extrahering av ljud:", e)
                raise  # Skicka vidare felet till yttre except
        else:
            print("Ljudfilen finns redan:", audio_output_path)
        if not os.path.exists(transcribe_output_path):
            try:
                transcribe(audio_output_path, transcribe_output_path)
                print("✅ Transkription klar! Resultat sparat i", transcribe_output_path)
            except Exception as e:
                if os.path.exists(transcribe_output_path):
                    os.remove(transcribe_output_path)
                print("❌ Fel vid transkribering:", e)
                raise
        else:
            print("Transkriptionsfilen finns redan:", transcribe_output_path)
        if not os.path.exists(finished_output_path):
            try:
                correct_speakers_in_transcript(transcribe_output_path, finished_output_path, fullmaktige, date)
            except Exception as e:
                if os.path.exists(finished_output_path):
                    os.remove(finished_output_path)
                print("❌ Fel vid korrigering:", e)
                raise
        else:
            print("Korrigerad transkriptionsfil finns redan:", finished_output_path)
    except Exception as e:
        print("❌ Ett fel inträffade:", e)
    # correct_speakers_in_transcript("output.json", "output_corrected.json", "rf", "2025-04-24")

# for chapter in chapters:
#     print(f"{chapter['formatted_time']} - {chapter['title']}")