import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class WhisperAudioTranscriber():
    def __init__(self, model_name="KBLab/kb-whisper-large"):
        # Configure the device for computation
        if torch.cuda.is_available():
            self.device = "cuda:0"
            self.torch_dtype = torch.float16
        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.torch_dtype = torch.float16
        else:
            self.device = "cpu"
            self.torch_dtype = torch.float32

        # Load the model and processor
        try:
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=False,
                use_safetensors=True,
            )
            self.model.to(self.device)

            self.processor = AutoProcessor.from_pretrained(model_name)

            # Configure the pipeline for automatic speech recognition
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=self.device,
                return_timestamps=True,
                generate_kwargs={"max_new_tokens": 400},
                chunk_length_s=30,
                stride_length_s=(5, 5),
            )
        except Exception as e:
            raise

    def transcribe(self, audio_path: str) -> tuple:
        try:
            # Perform transcription with timestamps
            result = self.pipe(audio_path)
            transcription = result['text']
            timestamps = result['chunks']
            return transcription, timestamps
        except Exception as e:
            return None, None