import cv2
import dlib
import numpy as np

class KalmanFilter:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-1):
        self.kf = cv2.KalmanFilter(2, 1)  
        self.kf.transitionMatrix = np.array([[1, 1], [0, 1]], dtype=np.float32)
        self.kf.measurementMatrix = np.array([[1, 0]], dtype=np.float32)
        self.kf.processNoiseCov = np.eye(2, dtype=np.float32) * process_noise
        self.kf.measurementNoiseCov = np.eye(1, dtype=np.float32) * measurement_noise
        self.kf.statePost = np.array([[0], [0]], dtype=np.float32)  

    def update(self, measurement):
        self.kf.predict()
        self.kf.correct(np.array([[measurement]], dtype=np.float32))
        return self.kf.statePost[0, 0]  

class EyebrowFurrowDetector:
    def __init__(self, predictor_path = "gaze_tracking/trained_models/shape_predictor_68_face_landmarks.dat"):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)

        self.kalman_filter = KalmanFilter()
        self.stress_frame_count = 0
        self.stress_labels = []

        self.FURROW_THRESHOLD = 0.16  
        self.STRESS_FRAMES_THRESHOLD = 10  

        self.LEFT_EYEBROW = (17, 18, 19, 20, 21)
        self.RIGHT_EYEBROW = (22, 23, 24, 25, 26)
        self.LEFT_EYE = (36, 37, 38, 39, 40, 41)
        self.RIGHT_EYE = (42, 43, 44, 45, 46, 47)

    def normalized_distance(self, landmarks, eyebrow_indices, eye_indices):
        eyebrow_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eyebrow_indices])
        eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_indices])
        
        avg_eyebrow_y = np.mean(eyebrow_points[:, 1])
        avg_eye_y = np.mean(eye_points[:, 1])
        vertical_distance = avg_eye_y - avg_eyebrow_y
        
        face_width = abs(landmarks.part(16).x - landmarks.part(0).x)
        
        return vertical_distance / face_width

    def detect_furrow(self, landmarks):
        left_dist = self.normalized_distance(landmarks, self.LEFT_EYEBROW, self.LEFT_EYE)
        right_dist = self.normalized_distance(landmarks, self.RIGHT_EYEBROW, self.RIGHT_EYE)
        avg_dist = (left_dist + right_dist) / 2
        smoothed_dist = self.kalman_filter.update(avg_dist)
        return smoothed_dist < self.FURROW_THRESHOLD

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        self.stress_labels = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            for face in faces:
                landmarks = self.predictor(gray, face)
                is_furrowed = self.detect_furrow(landmarks)

                if is_furrowed:
                    self.stress_frame_count += 1
                else:
                    self.stress_frame_count = max(self.stress_frame_count - 1, 0)

                stress_label = 1 if self.stress_frame_count > self.STRESS_FRAMES_THRESHOLD else 0
                self.stress_labels.append(stress_label)

        cap.release()
        return np.array(self.stress_labels)

    # def compute_relax_score(self, window_size=30, step_size=15, threshold=0.6):
    #     labels = self.stress_labels
    #     total_frames = len(labels)
    #     sustained_stress_windows = 0
    #     total_windows = 0

    #     for start in range(0, total_frames - window_size + 1, step_size):
    #         window = labels[start:start + window_size]  
    #         stress_ratio = sum(window) / window_size  

    #         if stress_ratio >= threshold:
    #             sustained_stress_windows += 1  

    #         total_windows += 1

    #     return round(100 - ((sustained_stress_windows / total_windows) * 100), 2) if total_windows > 0 else 0  

# Usage Example:
if __name__=="__main__":
    detector = EyebrowFurrowDetector()
    video_path = r"..\video\vid_1.avi" # REPLACE WITH VID PATH (i just recorded from mock int and used it)
    stress_array = detector.process_video(video_path)
    # stress_score = detector.compute_relax_score(window_size=10, step_size=5, threshold=0.6)
    # print(f"Final Stress Score: {stress_score}%")
    print(stress_array)
