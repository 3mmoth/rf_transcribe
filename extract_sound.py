import subprocess
import sys
import os
import shutil

def extract_wav_yt(mp4_url: str, output_wav: str):
    print("🔽 Laddar ner ljud från YouTube...")
    print("yt-dlp hittades på:", shutil.which("yt-dlp"))
    temp_audio = "temp_audio.m4a"
    # 1. Ladda ner ljudet som m4a
    cmd_dl = [
        "yt-dlp",
        "-x",
        "--audio-format", "m4a",
        "-o", temp_audio,
        mp4_url
    ]
    result = subprocess.run(cmd_dl, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        raise Exception("yt-dlp misslyckades")

    # 2. Konvertera till mono, 16kHz, PCM wav
    cmd_ffmpeg = [
        "ffmpeg",
        "-y",
        "-i", temp_audio,
        "-ac", "1",           # mono
        "-ar", "16000",       # 16 kHz
        "-acodec", "pcm_s16le",  # rå PCM för .wav
        output_wav
    ]
    result = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        raise Exception("ffmpeg misslyckades")

    os.remove(temp_audio)
    print(f"✅ Klar! Ljud sparat i {output_wav}")

def extract_wav_qc(mp4_url: str, out_wav: str):
    """
    Laddar ner en mp4 och extraherar ljud som mono WAV (16 kHz).
    Kräver ffmpeg installerat.
    """
    cmd = [
        "ffmpeg",
        "-i", mp4_url,     # input: mp4 från URL
        "-vn",             # ignorera video
        "-ac", "1",        # en kanal (mono)
        "-ar", "16000",    # samplingsfrekvens 16kHz
        "-acodec", "pcm_s16le",  # rå PCM för .wav
        out_wav
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Användning: python extract_wav.py <mp4-url> <utfil.wav>")
        sys.exit(1)

    mp4_url = sys.argv[1]
    out_wav = sys.argv[2]

    extract_wav_yt(mp4_url, out_wav)
    print(f"✅ Klart! Ljud sparat i {out_wav}")