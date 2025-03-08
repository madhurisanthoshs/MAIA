import os
import warnings
import logging
import absl.logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

warnings.filterwarnings('ignore', category=UserWarning, module='keras')
logging.getLogger('absl').setLevel(logging.ERROR)
absl.logging.set_verbosity(absl.logging.ERROR)

from tensorflow.keras.models import load_model
import pickle
import librosa
import numpy as np
import soundfile as sf

# Load model and preprocessing tools
model = load_model(r"emotion_detection\SER\final_model.keras")

with open('emotion_detection\SER\scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
    
with open('emotion_detection\SER\encoder.pkl', 'rb') as f:
    encoder = pickle.load(f)

# Define feature extraction functions
def zcr(data, frame_length, hop_length):
    return np.squeeze(librosa.feature.zero_crossing_rate(data, frame_length=frame_length, hop_length=hop_length))

def rmse(data, frame_length=2048, hop_length=512):
    return np.squeeze(librosa.feature.rms(y=data, frame_length=frame_length, hop_length=hop_length))

def mfcc(data, sr, frame_length=2048, hop_length=512, flatten=True):
    mfcc_feat = librosa.feature.mfcc(y=data, sr=sr)
    return np.squeeze(mfcc_feat.T) if not flatten else np.ravel(mfcc_feat.T)

def extract_features(data, sr=22050, frame_length=2048, hop_length=512):
    result = np.array([])
    result = np.hstack((result, 
                        zcr(data, frame_length, hop_length),
                        rmse(data, frame_length, hop_length),
                        mfcc(data, sr, frame_length, hop_length)))
    return result

# Function to prepare input for the model
def get_predict_feat(path):
    d, s_rate = librosa.load(path, sr=22050)
    res = extract_features(d)
    result = np.array(res).reshape(1, -1)
    i_result = scaler.transform(result)
    final_result = np.expand_dims(i_result, axis=2)
    return final_result

# Function to split audio into 2.5s snippets
def split_audio(file_path, output_dir, snippet_duration=2.5, start_offset=1.0, sr=22050):
    audio, sr = librosa.load(file_path, sr=sr)
    total_duration = librosa.get_duration(y=audio, sr=sr)
    
    snippets = []
    snippet_index = 1
    current_offset = start_offset

    while current_offset + snippet_duration <= total_duration:
        snippet = audio[int(current_offset * sr): int((current_offset + snippet_duration) * sr)]
        snippet_filename = os.path.join(output_dir, f"snippet_{snippet_index}.wav")
        sf.write(snippet_filename, snippet, sr)
        snippets.append(snippet_filename)
        snippet_index += 1
        current_offset += snippet_duration

    return snippets

# Function to predict emotions for all snippets
def predict_emotions(file_path):
    output_dir = "./snippets"
    os.makedirs(output_dir, exist_ok=True)

    snippet_files = split_audio(file_path, output_dir)
    predictions_list = []

    for snippet in snippet_files:
        res = get_predict_feat(snippet)
        predictions = model.predict(res)
        y_pred = encoder.inverse_transform(predictions)
        predictions_list.append(y_pred[0][0])
    predictions_list=adj(predictions_list)
    print("emotions identified: ",predictions_list)
    return predictions_list

def adj(pred):
    ov_pred = {'disappointed', 'frustrated', 'disengaged'}
    count_ov_pred = 0
    adj_pred = []
    for em in pred:
        if em in ov_pred:
            if count_ov_pred < 2:
                adj_pred.append(em)
                count_ov_pred += 1
            else:
                adj_pred.append('calm')
        else:
            adj_pred.append('calm')
    return adj_pred

def calculate_interview_score(predictions):
    # Emotion weights
    emotion_weights = {
        'positive': 0.9,
        'calm': 0.7,
        'surprise': 0.1,
        'nervous': -0.1,
        'disappointed': -0.2,
        'disengaged': -0.3,
        'frustrated': -0.4
    }
    # Ensure we have valid predictions
    if not predictions:
        return 50.0  # Neutral score if no predictions are given
    # Compute weighted sum
    total_weight = sum(emotion_weights.get(emotion, 0) for emotion in predictions)
    # Compute average score
    raw_score = total_weight / len(predictions)
    # Normalize to range 0-100
    normalized_score = ((raw_score + 1) / 2) * 100
    # Ensure score is within [0, 100]
    return max(0, min(100, normalized_score))

def main():
    # Run prediction
    file_path = r"1_audio\aud_4.wav"
    preds=predict_emotions(file_path)
    score=calculate_interview_score(preds)
    print(f"emotion score: {score:.2f}%")

main()