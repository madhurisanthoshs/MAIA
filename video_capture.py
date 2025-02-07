import customtkinter as ctk
import cv2
import pyaudio
import wave
import threading
import os
import time
from PIL import Image
from datetime import datetime

# Ensure folders exist
os.makedirs("video", exist_ok=True)
os.makedirs("audio", exist_ok=True)

class VideoCapture(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M.A.I.A - Interview Preparation")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Video capture and writer
        self.cap = None
        self.writer = None
        self.running = False

        # Audio variables
        self.audio_stream = None
        self.audio_frames = []
        self.audio_running = False

        self.questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Why do you want this job?"
        ]
        self.current_question = 0

        self.create_widgets()

    def create_widgets(self):
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.top_frame = ctk.CTkFrame(self.container)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.video_frame = ctk.CTkFrame(self.top_frame)
        self.video_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.video_label = ctk.CTkLabel(self.video_frame, text="Video Feed")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(self.top_frame, width=200)
        self.control_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.question_label = ctk.CTkLabel(self.control_frame, text=self.questions[self.current_question], wraplength=180)
        self.question_label.pack(pady=20)

        self.next_question_btn = ctk.CTkButton(self.control_frame, text="Next Question", command=self.next_question)
        self.next_question_btn.pack(pady=10)

        self.start_cam_btn = ctk.CTkButton(self.control_frame, text="Start Camera", command=self.start_camera)
        self.start_cam_btn.pack(pady=10)

        self.bottom_frame = ctk.CTkFrame(self.container, height=50)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.submit_btn = ctk.CTkButton(self.bottom_frame, text="Submit Video", command=self.stop_camera)
        self.submit_btn.pack(pady=10)

    def start_camera(self):
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
            print(f"Recording started: {self.video_filename}")

            # Start video thread
            threading.Thread(target=self.update_frame, daemon=True).start()

            # Start audio recording
            self.audio_running = True
            self.audio_frames = []
            self.audio_filename = f"audio/audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            threading.Thread(target=self.record_audio, daemon=True).start()

    def update_frame(self):
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.writer.write(frame)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                label_width = self.video_label.winfo_width() or 640
                label_height = self.video_label.winfo_height() or 480
                img = img.resize((label_width, label_height))

                ctk_img = ctk.CTkImage(dark_image=img, size=(label_width, label_height))
                self.video_label.configure(image=ctk_img, text="")
                self.video_label.image = ctk_img  # Keep reference

            # Avoid CPU overload
            time.sleep(0.01)
            self.after(30, self.update_frame)

    def record_audio(self):
        p = pyaudio.PyAudio()
        self.audio_stream = p.open(format=pyaudio.paInt16,
                                   channels=1,
                                   rate=44100,
                                   input=True,
                                   frames_per_buffer=1024)

        while self.audio_running:
            data = self.audio_stream.read(1024, exception_on_overflow=False)
            self.audio_frames.append(data)
            time.sleep(0.01)  # Prevent CPU overload

        # Stop and save audio
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        p.terminate()

        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()
        print("Audio saved:", self.audio_filename)

    def next_question(self):
        self.current_question = (self.current_question + 1) % len(self.questions)
        self.question_label.configure(text=self.questions[self.current_question])

    def stop_camera(self):
        if self.running:
            self.running = False
            if self.cap:
                self.cap.release()
            if self.writer:
                self.writer.release()

            # Stop audio recording
            self.audio_running = False

            self.video_label.configure(image=None, text="Video feed")
            self.video_label.image = None
            print("Video and audio recording stopped and saved.")

if __name__ == "__main__":
    app = VideoCapture()
    app.mainloop()
