import customtkinter as ctk
import cv2
from PIL import Image
import threading
import os
from datetime import datetime

# Initialize the main window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M.A.I.A - Interview Preparation")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Video capture and writer
        self.cap = None
        self.writer = None
        self.running = False

        # Ensure recordings folder exists
        os.makedirs("recordings", exist_ok=True)

        self.questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Why do you want this job?"
        ]
        self.current_question = 0

        # Layout setup
        self.create_widgets()

    def create_widgets(self):
        # Main container frame with padding
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top Frame (Video Feed + Controls)
        self.top_frame = ctk.CTkFrame(self.container)
        self.top_frame.pack(side="top", fill="both", expand=True)

        # Video display frame (Left side)
        self.video_frame = ctk.CTkFrame(self.top_frame)
        self.video_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.video_label = ctk.CTkLabel(self.video_frame, text="Video Feed")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Right panel for questions and controls
        self.control_frame = ctk.CTkFrame(self.top_frame, width=200)
        self.control_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.question_label = ctk.CTkLabel(self.control_frame, text=self.questions[self.current_question], wraplength=180)
        self.question_label.pack(pady=20)

        self.next_question_btn = ctk.CTkButton(self.control_frame, text="Next Question", command=self.next_question)
        self.next_question_btn.pack(pady=10)

        self.start_cam_btn = ctk.CTkButton(self.control_frame, text="Start Camera", command=self.start_camera)
        self.start_cam_btn.pack(pady=10)

        # Bottom Frame for Submit Button
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

            # Setup VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            filename = f"recordings/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            fps = 20.0
            frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
            self.writer = cv2.VideoWriter(filename, fourcc, fps, frame_size)

            self.running = True
            self.update_frame()
            print(f"Recording started: {filename}")

    def update_frame(self):
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Write frame to video file
                self.writer.write(frame)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                label_width = self.video_label.winfo_width() or 640
                label_height = self.video_label.winfo_height() or 480
                img = img.resize((label_width, label_height))

                ctk_img = ctk.CTkImage(dark_image=img, size=(label_width, label_height))
                self.video_label.configure(image=ctk_img)
                self.video_label.image = ctk_img  # Keep reference

            # Schedule next frame update
            self.after(30, self.update_frame)

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

            self.video_label.configure(image=None, text="Video Feed")  # Clear
            print("Video submitted and saved successfully.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()
