import subprocess
import sys

def extract_wav_from_mp4(mp4_url: str, out_wav: str):
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

    extract_wav_from_mp4(mp4_url, out_wav)
    print(f"✅ Klart! Ljud sparat i {out_wav}")