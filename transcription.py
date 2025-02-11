# import torch
# import librosa
# import time
# from faster_whisper import WhisperModel

# class AudioTranscription:
#     def __init__(self, model_name="nyrahealth/faster_CrisperWhisper", device=None):
#         """
#         Initializes the Whisper model for transcription.
#         :param model_name: Hugging Face model name.
#         :param device: Automatically selects CUDA if available, else CPU.
#         """
#         self.model_name = model_name
#         self.device = device if device else ("cuda:0" if torch.cuda.is_available() else "cpu")

#         # Load Faster-Whisper model
#         self.model = WhisperModel(self.model_name, device=self.device, compute_type="float")

#     def load_audio(self, audio_path, target_sr=16000):
#         """
#         Loads an audio file and resamples it to 16kHz.
#         :param audio_path: Path to the audio file.
#         :param target_sr: Target sampling rate (default: 16kHz).
#         :return: Audio array and sampling rate.
#         """
#         audio_array, sr = librosa.load(audio_path, sr=target_sr)
#         return audio_array, sr

#     def transcribe_audio(self, audio_path, beam_size=3):
#         """
#         Transcribes an audio file using Faster-Whisper.
#         :param audio_path: Path to the audio file.
#         :param beam_size: Beam search size for transcription.
#         :return: List of transcribed segments.
#         """
#         print(f"\nLoading audio: {audio_path}")
#         audio_array, _ = self.load_audio(audio_path)

#         print("\nStarting transcription...")
#         start_time = time.time()
#         segments, info = self.model.transcribe(audio_array, beam_size=beam_size, word_timestamps=True)
#         end_time = time.time()

#         # Print transcription results
#         for segment in segments:
#             print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

#         print(f"\nTime taken: {end_time - start_time:.2f} seconds")
#         return segments

# # Example usage
# if __name__ == "__main__":
#     transcriber = AudioTranscription()
#     transcriber.transcribe_audio(r"audio\audio_20250210_184541.wav")

# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai
#
# Note: Some macOS users may need to use `pip3` instead of `pip`.

import os
from dotenv import load_dotenv
import assemblyai as aai

class AudioTranscriber:
    def __init__(self):
        """Load API key from .env file and initialize transcriber."""
        load_dotenv()  # Load environment variables from .env
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Add it to a .env file or set an environment variable.")
        aai.settings.api_key = self.api_key
        self.transcriber = None

    def load_audio(self, file_path):
        """Load an audio file for transcription."""
        config = aai.TranscriptionConfig(disfluencies=True)
        self.transcriber = aai.Transcriber(config=config)
        self.transcript = self.transcriber.transcribe(file_path)

    def print_transcript(self):
        """Print the transcribed text."""
        if not self.transcriber or not hasattr(self, 'transcript'):
            raise ValueError("No transcription found. Use load_audio() first.")
        if self.transcript.status == aai.TranscriptStatus.error:
            print(f"Error: {self.transcript.error}")
        else:
            print(self.transcript.text)

# Example Usage
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    transcriber.load_audio(r"audio\audio_20250210_184541.wav")
    transcriber.print_transcript()



