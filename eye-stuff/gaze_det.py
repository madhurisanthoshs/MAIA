import cv2
from gaze_tracking import GazeTracking
import numpy as np

class GazeFocusDetector:
    def __init__(self, video_path):
        self.gaze = GazeTracking()
        self.video_path = video_path
        self.op = []

    def process_video(self):
        cap = cv2.VideoCapture(self.video_path)       
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.gaze.refresh(frame)
            # if self.gaze.is_blinking():
            #     text = "Blinking"
            if self.gaze.is_right():
                text = 1
            elif self.gaze.is_left():
                text = 1
            elif self.gaze.is_center():
                text = 0

            self.op.append(text)  # 0 = Focused, 1 = Distracted

        cap.release()
        return np.array(self.op)
    
    # def compute_focus_score(self, window_size=30, step_size=15, threshold=0.6):
    #     labels = self.op
    #     total_frames = len(labels)
    #     sustained_distraction_windows = 0
    #     total_windows = 0

    #     for start in range(0, total_frames - window_size + 1, step_size):
    #         window = labels[start:start + window_size]  
    #         dist_ratio = sum(window) / window_size  

    #         if dist_ratio >= threshold:
    #             sustained_distraction_windows += 1  

    #         total_windows += 1

    #     return round(100 - ((sustained_distraction_windows / total_windows) * 100), 2) if total_windows > 0 else 0  


# Usage Example
if __name__=="__main__":
    video_path = r"..\video\vid_1.avi" # REPLACE WITH VID PATH (i just recorded from mock int and used it)
    detector = GazeFocusDetector(video_path)
    distraction_labels = detector.process_video()
    # distraction_score = detector.compute_focus_score(10,5,0.6)
    # print(f"Final score: {distraction_score}%")
    print(distraction_labels) 
