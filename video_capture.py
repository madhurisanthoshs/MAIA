import customtkinter as ctk
import cv2
import pyaudio
import wave
import threading
import os
import time
from PIL import Image
from datetime import datetime
from GUI import clear_screen, create_main_screen
import random

# Ensure necessary folders exist
os.makedirs("video", exist_ok=True)
os.makedirs("audio", exist_ok=True)

class VideoCapture:
    def __init__(self, master, num_q=5):
        """Initialize video capture inside an existing window."""
        self.master = master
        self.master.title("M.A.I.A - Interview Preparation")

        # Video and audio variables
        self.cap = None
        self.writer = None
        self.running = False

        self.audio_stream = None
        self.audio_frames = []
        self.audio_running = False

        self.questions = [
            "Tell me about yourself.",
            "Tell me about a time when you demonstrated leadership?",
            "Tell me about a time when you were working with a team and faced a challenge. How did you overcome the problem?",
            "What is one of your weaknesses and how do you plan to overcome it?",
            "Tell me about a time you made a mistake at work. How did you resolve the problem, and what did you learn from your mistake?",
            "Give an example of a time when you had to make a difficult decision. How did you handle it?",
            "Tell me about settling into your last job. What did you do to learn the ropes?",
            "Tell me about a time when you had to make a decision without all the information you needed.",
            "Tell me about a time you failed. How did you deal with the situation?",
            "Tell me about a situation when you had a conflict with a teammate."
        ]
        self.selected_questions = random.sample(self.questions, min(num_q, len(self.questions)))
        self.current_question = 0

        self.video_filename = None
        self.audio_filename = None

        self.create_widgets()

    def create_widgets(self):
        """Creates UI elements for video capture."""
        self.container = ctk.CTkFrame(self.master, fg_color="#050c30")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.top_frame = ctk.CTkFrame(self.container, fg_color="#091654")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.video_frame = ctk.CTkFrame(self.top_frame, fg_color="#050c30")
        self.video_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.warning_label = ctk.CTkLabel(self.video_frame, text="", text_color="black")
        self.warning_label.pack(padx=10, pady=10)

        self.video_label = ctk.CTkLabel(self.video_frame, text="Video Feed")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(self.top_frame, width=550, fg_color="#050c30")
        self.control_frame.pack(side="right", fill="y", padx=10, pady=10)
      
        self.question_label = ctk.CTkLabel(self.control_frame, text=self.selected_questions[self.current_question], wraplength=180)
        self.question_label.pack(pady=20)

        self.next_question_btn = ctk.CTkButton(self.control_frame, text="Next Question", command=self.next_question, fg_color="#1e349e", hover_color="#13205f")
        self.next_question_btn.pack(pady=10)

        self.start_cam_btn = ctk.CTkButton(self.control_frame, text="Start Camera", command=self.start_camera, fg_color="#1e349e", hover_color="#13205f")
        self.start_cam_btn.pack(pady=10)

        self.bottom_frame = ctk.CTkFrame(self.container, height=50, fg_color="#050c30")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.submit_btn = ctk.CTkButton(self.bottom_frame, text="Submit Video", command=self.stop_camera, fg_color="#1e349e", hover_color="#13205f")
        self.submit_btn.pack(side="left", padx=20, pady=10)

        self.end_test_btn = ctk.CTkButton(self.bottom_frame, text="End Test", fg_color="red", hover_color="#91071c", command=self.end_test)
        self.end_test_btn.pack(side="right", padx=20, pady=10)

    def start_camera(self):
        """Starts video and audio recording."""
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Camera not accessible")
                return

            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_filename = f"video/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            fps = 30.0
            frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
            self.writer = cv2.VideoWriter(self.video_filename, fourcc, fps, frame_size)

            self.running = True
            self.start_time = time.time()  # Track start time
            print(f"Recording started: {self.video_filename}")

            threading.Thread(target=self.update_frame, daemon=True).start()

            # Start audio recording
            self.audio_running = True
            self.audio_frames = []
            self.audio_filename = f"audio/audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            threading.Thread(target=self.record_audio, daemon=True).start()

    def update_frame(self):
        """Updates video frame in the GUI."""
        fin = time.time() - self.start_time
        
        if 50 <= time.time() - self.start_time < 60: 
            rem = 60 - fin
            self.warning_label.configure(fg_color="yellow", text=f"⚠️ Recording will stop in {int(rem)} seconds! ", text_color="black")
            
        elif time.time() - self.start_time >= 60:  # Stop after 1 minute
            print("1-minute recording limit reached. Stopping...")
            self.warning_label.configure(fg_color = "green", text = "The test has concluded! :) ")
            self.stop_camera()
            self.master.after(1500, lambda: self.warning_label.configure(fg_color = "#050c30",text = ""))
            return

        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.writer.write(frame)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                if (self.video_label.winfo_width()!=0 and self.video_label.winfo_height()):
                    label_width = 640
                    label_height = 480
                    img = img.resize((label_width, label_height))
                else:
                    time.sleep(0.3)

                ctk_img = ctk.CTkImage(dark_image=img, size=(label_width, label_height))
                self.video_label.configure(image=ctk_img, text="")
                self.video_label.image = ctk_img  # Keep reference

            time.sleep(0.01)
            self.master.after(30, self.update_frame)

    def record_audio(self):
        """Records audio while video is being recorded."""
        p = pyaudio.PyAudio()
        self.audio_stream = p.open(format=pyaudio.paInt16,
                                   channels=1,
                                   rate=44100,
                                   input=True,
                                   frames_per_buffer=1024)

        while self.audio_running:
            elapsed_time = time.time() - self.start_time  # Check elapsed time
            if elapsed_time >= 60:  # Stop recording after 1 minute
                self.audio_running = False
                break
            data = self.audio_stream.read(1024, exception_on_overflow=False)
            self.audio_frames.append(data)
            time.sleep(0.01)

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        p.terminate()

        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()

    def next_question(self):
        """Displays the next question in the randomly selected list."""
        if self.current_question < len(self.selected_questions) - 1:  # Ensure we don't exceed the list
            self.current_question += 1
            self.question_label.configure(text=self.selected_questions[self.current_question])
        else:
            self.next_question_btn.configure(state="disabled")  # Disable button after last question

    def stop_camera(self):
        """Stops video and audio recording."""
        if self.running:
            self.running = False
            if self.cap:
                self.cap.release()
            if self.writer:
                self.writer.release()

            self.audio_running = False

            self.video_label.configure(image=None, text="Video feed")
            self.video_label.image = None
            print("Video and audio recording stopped.")

    def end_test(self):
        """Ends test, deletes files, and returns to main menu."""
        if self.running:
            self.stop_camera()          
            if self.audio_stream.is_active():
                self.audio_stream.stop_stream()  
            self.audio_stream.close()
            time.sleep(0.5)

        # Delete video and audio files
        if self.video_filename and os.path.exists(self.video_filename):
            os.remove(self.video_filename)
        if self.audio_filename and os.path.exists(self.audio_filename):
            os.remove(self.audio_filename)

        print("Test ended, returning to main screen.")
        clear_screen(self.master)
        create_main_screen(self.master)

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1420x800")
    VideoCapture(root)  
    root.mainloop()
