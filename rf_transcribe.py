from datetime import datetime
import glob, os, subprocess
from unittest import result
import librosa
import whisperx
import torch
import torch
from datasets import load_dataset
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import whisper
# import whisper
import pyannote.audio
import argparse
from sklearn.cluster import AgglomerativeClustering
from pyannote.audio import Audio
from pyannote.core import Segment
import wave
import contextlib
import numpy as np
import pandas as pd
import time
import json

from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding

def transcribe_and_diarize(input_file):
    model_repo = "KBLab/kb-whisper-small"
    device = "cpu"
    device_id = -1 if device == "mps" else (-1 if device == "cpu" else 0)
    torch_dtype = torch.float32
    embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb",
        device=torch.device("mps" if torch.backends.mps.is_available() else "cpu"))
    # model = whisper.load_model("small")
    audio_file = input_file
    batch_size = 16  # reduce if low on GPU mem
    compute_type = "float32"  # change to "int8" if low on GPU mem (may reduce accuracy)

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model(
        "KBLab/kb-whisper-small", device, compute_type=compute_type, download_root="cache"  # cache_dir
    )

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result["segments"])  # before alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device,
        model_name="KBLab/wav2vec2-large-voxrex-swedish",
        model_dir="cache",  # cache_dir
    )
    result = whisperx.align(
        result["segments"], model_a, metadata, audio, device, return_char_alignments=False
    )

    segments = result["segments"]
    with contextlib.closing(wave.open(input_file,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    embeddings = np.zeros(shape=(len(segments), 192))
    for i, segment in enumerate(segments):
        embeddings[i] = segment_embedding(segment, duration, embedding_model, input_file)

    embeddings = np.nan_to_num(embeddings)
    clustering = AgglomerativeClustering(20).fit(embeddings)
    labels = clustering.labels_
    for i in range(len(segments)):
        segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

    # f = open("transcript.txt", "w")

    # for (i, segment) in enumerate(segments):
    #     if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
    #         f.write("\n" + segment["speaker"] + ' ' + str(time_intern(segment["start"])) + '\n')
    #     f.write(segment["text"].strip() + ' ')
    # f.close()
    output_data = []
    for segment in segments:
        output_data.append({
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2), 
            "text": segment["text"].strip(),
            "talare": segment["speaker"],
            "parti": None  # Du kan lägga till logik för att identifiera parti senare
        })

    # Skriv till JSON-fil
    with open("transcript.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        print("Transkription och diarization klar!")

def segment_embedding(segment, duration, embedding_model, input_file):
    audio = Audio()
    start = segment["start"]
    # Whisper overshoots the end timestamp in the last segment
    end = min(duration, segment["end"])
    clip = Segment(start, end)
    waveform, sample_rate = audio.crop(input_file, clip)
    return embedding_model(waveform[None])

def time_intern(secs):
    return datetime.time(datetime.fromtimestamp(secs)).strftime("%H:%M:%S")

def main():
    input_file = "output.wav"
    duration = librosa.get_duration(filename=input_file)
    script_start_time = time.time()
    transcribe_and_diarize(input_file)
    script_end_time = time.time()
    execution_time = script_end_time - script_start_time
    print(f"\n⏱️ Exekveringstid: {execution_time:.2f} sekunder för {duration:.2f} sekunder ljudfil.")

if __name__ == "__main__":
    main()