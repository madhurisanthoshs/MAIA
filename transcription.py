import torch
import librosa
import time
from faster_whisper import WhisperModel

faster_whisper_model = 'nyrahealth/faster_CrisperWhisper'
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# If you have the model already, it loads it from the .cache folder, if not, downloads it into that in the huggingface hub folder
whisper_model = WhisperModel(faster_whisper_model, device=device, compute_type="float")

# Load audio
audio_path = "audio.mp3"
audio_array, sampling_rate = librosa.load(audio_path, sr=16000)  # Resample to 16kHz

# Transcription 
start_time = time.time()
segments, info = whisper_model.transcribe(audio_array, beam_size=5, word_timestamps=True)
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
end_time = time.time()
print(f"\nTime taken: {end_time - start_time:.2f} seconds")
