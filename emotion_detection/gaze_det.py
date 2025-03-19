import cv2
from emotion_detection.gaze_tracking.gaze_tracking import GazeTracking
# from gaze_tracking import GazeTracking
import numpy as np
from g4f.client import Client
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# temporarily keeping this code, wont be necessary once it is connected to the frontend
# import sys
# import os
# cur = os.path.dirname(os.path.abspath(__file__))
# par = os.path.abspath(os.path.join(cur, '..'))
# sys.path.insert(0, par)
#till here
from utils import report_generation

class GazeFocusDetector:
    def __init__(self, video_path):
        self.gaze = GazeTracking()
        self.video_path = video_path
        self.op = []
        self.dist_frame_count = 0

    def process_video(self):
        cap = cv2.VideoCapture(self.video_path)       
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.gaze.refresh(frame)
            # if self.gaze.is_blinking():
            #     text = "Blinking"
            if self.gaze.is_left() or self.gaze.is_right():
                text = 1
            elif self.gaze.is_blinking():
                text = 1
            if self.gaze.is_center():
                text = 0
            else:
                text = 1

            if text == 1:
                self.dist_frame_count +=1
            else:
                self.dist_frame_count = max(self.dist_frame_count - 1, 0)
            label = 1 if self.dist_frame_count > 10 else 0
            self.op.append(label)  # 0 = Focused, 1 = Distracted

        cap.release()
        return np.array(self.op)
    
    def compute_focus_score(self, window_size, step_size, threshold):
        labels = self.op
        total_frames = len(labels)
        sustained_distraction_windows = 0
        total_windows = 0

        for start in range(0, total_frames - window_size + 1, step_size):
            window = labels[start:start + window_size]  
            dist_ratio = sum(window) / window_size  
            if dist_ratio >= threshold:
                sustained_distraction_windows += 1  
            total_windows += 1

        return round(100 - ((sustained_distraction_windows / total_windows) * 100), 2) if total_windows > 0 else 10  

    def prompt_formatting(self,score):
        prompt = f"This is how the score is calculated for focus: The sliding window method divides the sequence into overlapping segments of a fixed size. For each window, the average distraction level is calculated, and the ratio of distracted frames to total frames in the window is computed. If this ratio exceeds a set threshold, the window is considered distracted. The final score is then determined by subtracting the percentage of distracted windows from 100, representing the overall focus level.\nThe score obtained by the user is {score}.\nYou are an expert on body language and focus. Given the method for calculating the score, and the score obtained by the user, provide helpful, actionable tips to the user to improve their focus level and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term.\nAnswer format: \n'What you did right:' followed by a brief bulleted list of things the user did right, and \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \nEach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
        return prompt

    def report_generate(self, score):
        prompt = "This is how the score is calculated for focus: The sliding window method divides the sequence into overlapping segments of a fixed size. For each window, the average distraction level is calculated, and the ratio of distracted frames to total frames in the window is computed. If this ratio exceeds a set threshold, the window is considered distracted. The final score is then determined by subtracting the percentage of distracted windows from 100, representing the overall focus level.\nThe score obtained by the user is {score}.\nYou are an expert on body language and focus. Given the method for calculating the score, and the score obtained by the user, provide helpful, actionable tips to the user to improve their focus level and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term.\nAnswer format: \n'What you did right:' followed by a brief bulleted list of things the user did right, and \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \nEach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(score = score)}],
        )        
        # Capture the response text and split into keywords
        #print(prompt)
        result = response.choices[0].message.content
        return result
    
def eye_gaze(video_path):
    detector = GazeFocusDetector(video_path)
    distraction_labels = detector.process_video()
    score = detector.compute_focus_score(30,15,0.35)
    # print(distraction_labels)
    return score

if __name__=="__main__":
    video_path = r"..\2_video\vid_4.avi" # REPLACE WITH VID PATH (i just recorded from mock int and used it)
    detector = GazeFocusDetector(video_path)
    try:        
        distraction_labels = detector.process_video()
        distraction_score = detector.compute_focus_score(45,30,0.35)
        prompt = detector.prompt_formatting(distraction_score)
        report = report_generation(prompt)
        print(distraction_labels)
        print(f"Final score: {distraction_score}%\n\n")
        print(f"REPORT\n {report}")  
    except FileNotFoundError:
        print("Take the mock interview first, please!")  

# COMMENTED STUFF IS TO LOOK AND DEBUG THE GAZE DETECTION STUFF

# """
# Demonstration of the GazeTracking library.
# Check the README.md for complete documentation.
# """

# import cv2
# from gaze_tracking import GazeTracking

# gaze = GazeTracking()
# webcam = cv2.VideoCapture(r"..\2_video\vid_5.avi")

# while True:
#     # We get a new frame from the webcam
#     _, frame = webcam.read()

#     # We send this frame to GazeTracking to analyze it
#     gaze.refresh(frame)

#     frame = gaze.annotated_frame()
#     text = ""

#     if gaze.is_blinking():
#         text = "Blinking"
#     elif gaze.is_right():
#         text = "Looking right"
#     elif gaze.is_left():
#         text = "Looking left"
#     elif gaze.is_center():
#         text = "Looking center"
#     cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

#     left_pupil = gaze.pupil_left_coords()
#     right_pupil = gaze.pupil_right_coords()
#     cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
#     cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

#     cv2.imshow("Demo", frame)

#     if cv2.waitKey(1) == 27:
#         break
   
# webcam.release()
# cv2.destroyAllWindows()
