import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import xgboost as xgb
import mediapipe as mp
import cv2
import numpy as np
import pandas as pd
import pickle
import random
import time
folder_path = os.path.join(os.path.dirname(__file__))

model = xgb.XGBClassifier()
model.load_model(os.path.join(folder_path, "body_lang_model.json"))

with open(os.path.join(folder_path, "label_encoder.pkl"), "rb") as f:
    label_encoder = pickle.load(f)

feat_names=model.get_booster().feature_names

mp_holistic = mp.solutions.holistic

# Get screen dimensions (update these if needed, to match the actual values)
screen_width = 1920  
screen_height = 1080  

path = r"2_video\vid_2.avi"

# Define weights for each pose (adjust as necessary)
pose_weights = {
    "gesturing": 0.8,
    "thinking": 0.6,
    "steepling_fingers": 0.7,
    "crossing_arms": 0.5,
    "covering_mouth": 0.4,
    "hand_on_neck": 0.6,
    "yawning": 0.1,
    "scratching_head": 0.3,
    "looking_down": 0.3,
    "smiling": 0.8,
    "rubbing_forehead": 0.3,
    "hair_tucking": 0.4,
    "nail_biting": 0.1,
    "folding_palms": 0.3,
    "idle": 0.5,
    "shaking_head": 0.5,
    "nodding": 0.7,
    "pointing_finger": 0.5,
    "head_in_hands": 0.1,
    "sitting_straight": 0.9,
    "touching_ear": 0.4,
    "slouching": 0.2,
    "shrugging": 0.4,
    "tugging_collar": 0.3,
    "waving": 0.7,
    "shaking_fist": 0.1
}

# Poses that should have diminishing returns if overused
diminishing_classes = {"gesturing", "nodding", "steepling_fingers", "smiling", "idle", "thinking", "crossing_arms", "hand_on_neck", "shaking_head", "pointing_finger", "covering_mouth", "waving"}

def video_proc(path):
    preds, probs = [],[]
    cap = cv2.VideoCapture(path)
    with mp_holistic.Holistic(min_detection_confidence=0.7, min_tracking_confidence=0.7) as holistic:        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                # Extract and process landmarks
                pose_present = 1 if results.pose_landmarks else 0
                face_present = 1 if results.face_landmarks else 0
                right_hand_present = 1 if results.right_hand_landmarks else 0
                left_hand_present = 1 if results.left_hand_landmarks else 0
                
                missing_pose = [[np.nan, np.nan, np.nan, np.nan]] * 33
                missing_face = [[np.nan, np.nan, np.nan]] * 468
                missing_hand = [[np.nan, np.nan, np.nan]] * 21
                
                pose = [[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark] if results.pose_landmarks else missing_pose
                face = [[lm.x, lm.y, lm.z] for lm in results.face_landmarks.landmark] if results.face_landmarks else missing_face
                right_hand = [[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark] if results.right_hand_landmarks else missing_hand
                left_hand = [[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark] if results.left_hand_landmarks else missing_hand
                
                row = [pose_present] + list(np.array(pose).flatten()) + \
                    [face_present] + list(np.array(face).flatten()) + \
                    [right_hand_present] + list(np.array(right_hand).flatten()) + \
                    [left_hand_present] + list(np.array(left_hand).flatten())
                
                # Make predictions (replace model and label encoder with your own)
                X = pd.DataFrame([row], columns=feat_names)
                body_language_class = model.predict(X)
                body_language_class = label_encoder.inverse_transform(body_language_class)
                body_language_prob = model.predict_proba(X)
                
                if body_language_class == "smiling" and random.random() < 0.7:
                    body_language_class = ['idle']
                if body_language_class in ["shrugging", "pointing_finger"] and random.random() < 0.4:
                    body_language_class = ['gesturing']
                
                preds.append(str(body_language_class[0]))
                probs.append(round(np.max(body_language_prob) * 100, 2))
            
            except Exception as e:
                print(f"Error processing frame: {e}")

    cap.release()
    return preds, probs

# Function to compute the structured breakdown and score
def compute_interview_analysis(result_df, diminishing_classes=diminishing_classes, pose_weights = pose_weights):
    total_frames = result_df.shape[0]

    # Step 1: Compute Pose Distribution (%)
    pose_counts = result_df["Predicted Class"].value_counts(normalize=True) * 100
    result_df["Pose_Percentage"] = result_df["Predicted Class"].map(pose_counts)

    # Step 2: Adjust for overuse (Diminishing Returns for Certain Poses)
    def adjust_weight(pose, weight, percentage):
        if pose in diminishing_classes:
            reduction_factor = min(0.5, percentage / 50)  # Reduce if over 50% occurrence
            return weight * (1 - reduction_factor)
        return weight

    result_df["Adjusted_Weight"] = result_df.apply(lambda row: adjust_weight(
        row["Predicted Class"], pose_weights.get(row["Predicted Class"], 0.5), row["Pose_Percentage"]
    ), axis=1)

    # Step 3: Weight by Model Confidence (Probability)
    result_df["Confidence_Weighted_Score"] = result_df["Probability"] * result_df["Adjusted_Weight"]

    # Step 4: Apply Smoothing to Reduce Sensitivity to Short-Term Errors
    result_df["Smoothed_Score"] = result_df["Confidence_Weighted_Score"].rolling(window=5, min_periods=1).mean()

    # Step 5: Weight by Duration (Pose Distribution % acts as duration weight)
    result_df["Duration_Weighted_Score"] = result_df["Smoothed_Score"] * result_df["Pose_Percentage"] / 100

    # Step 6: Compute Final Score
    max_possible_score = sum(pose_weights.values()) * 100  # Maximum theoretical score
    final_score = (result_df["Duration_Weighted_Score"].sum() / max_possible_score) * 100
    
    if final_score > 100:
        print("Final score exceeded 100. Recalculating with a simplified approach.")
        pose_score_contributions = [
            pose_weights.get(pose, 0.5) * percentage / 100 for pose, percentage in pose_counts.items()
        ]
        final_score = sum(pose_score_contributions) * 100
    
    final_score = round(final_score, 2)

    # Step 7: Generate Structured Breakdown for LLM Analysis
    analysis = {
    "final_score": round(final_score, 2),
    "pose_distribution": {k: round(v, 2) for k, v in pose_counts.to_dict().items()},
    "duration_weighted_scores": {k: round(v, 2) for k, v in result_df.groupby("Predicted Class")["Duration_Weighted_Score"].sum().to_dict().items()},
    }

    return analysis, result_df

def format_analysis_for_llm(analysis):
    final_score = analysis.get("final_score", "N/A")
    pose_distribution = analysis.get("pose_distribution", {})
    duration_weighted_scores = analysis.get("duration_weighted_scores", {})
    pose_dist_str = "\n".join([f"- {pose}: {percentage:.2f}%" for pose, percentage in pose_distribution.items()])
    duration_scores_str = "\n".join([f"- {pose}: {score:.2f}" for pose, score in duration_weighted_scores.items()])

    formatted_string = f"""Interview Analysis Summary:

        Final Score: {final_score:.2f}/100

        Pose Distribution (% of time spent in each pose):
        {pose_dist_str}

        Duration-Weighted Scores (Higher values indicate more impact on assessment):
        {duration_scores_str}
    """
    return formatted_string

def bodylang(path, diminishing_classes=diminishing_classes, pose_weights=pose_weights):
    preds, probs = video_proc(path)
    result_df = pd.DataFrame({"Predicted Class": preds, "Probability": probs})
    analysis, rdf = compute_interview_analysis(result_df, diminishing_classes, pose_weights)
    final_score = analysis.get("final_score")
    formatted_analysis = format_analysis_for_llm(analysis)
    return int(final_score), formatted_analysis
    # print(final_score)

if __name__=="__main__":
    start_time = time.time()
    # preds, probs = video_proc(path)
    temp, t = bodylang(path, diminishing_classes, pose_weights)
    print(temp)
    end_time = time.time()  # Record end time
    execution_time = end_time - start_time 
    print(f"\nTIME: {round(execution_time),2}")