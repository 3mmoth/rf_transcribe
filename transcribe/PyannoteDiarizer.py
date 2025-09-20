from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch

class PyannoteDiarizer:
    def __init__(self, hf_token: str):
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            self.pipeline.to(self.device)
        except Exception as e:
            self.pipeline = None

    def diarize(self, audio_path: str):
        if self.pipeline is None:
            return None

        try:
            with ProgressHook() as hook:
                diarization = self.pipeline(audio_path, hook=hook)
                return diarization
        except Exception as e:
            return None