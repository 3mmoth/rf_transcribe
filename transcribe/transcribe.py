import sys
import json
import time
from transcribe.PyannoteDiarizer import PyannoteDiarizer
from transcribe.WhisperAudioTranscriber import WhisperAudioTranscriber
from transcribe.SpeakerAligner import SpeakerAligner

def transcribe(audio_path, output_json, hf_token):
    start_time = time.time()

    # 1. Initiera diarizer och transcriber
    diarizer = PyannoteDiarizer(hf_token)
    transcriber = WhisperAudioTranscriber()
    aligner = SpeakerAligner()

    # 2. Diarisera ljudet
    diarization = diarizer.diarize(audio_path)
    if diarization is None:
        print("Diarization failed.")
        return
    print("Diarisering klar ✅")
    # 3. Transkribera ljudet
    transcription, timestamps = transcriber.transcribe(audio_path)
    if transcription is None or timestamps is None:
        print("Transcription failed.")
        return
    print("Transkribering klar ✅")
    # 4. Aligna talare till transkript
    speaker_segments = aligner.align(transcription, timestamps, diarization)
    print("Talare alignering klar ✅")
    # 5. Spara som JSON
    output = []
    for speaker, start, end, text in speaker_segments:
        output.append({
            "speaker": speaker,
            "start": float(start),
            "end": float(end),
            "text": text.strip()
        })

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ Klar! Resultat sparat i {output_json}")

    elapsed = time.time() - start_time
    print(f"⏱️ Körtid: {elapsed/60:.1f} minuter ({elapsed:.1f} sekunder)")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Användning: python run_pipeline.py <ljudfil.wav> <output.json> <hf_token>")
        sys.exit(1)
    audio_path = sys.argv[1]
    output_json = sys.argv[2]
    hf_token = sys.argv[3]
    transcribe(audio_path, output_json, hf_token)