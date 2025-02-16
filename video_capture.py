import customtkinter as ctk
import cv2
import pyaudio
import wave
import threading
import os
import time
from PIL import Image
from datetime import datetime
#from GUI_main_screen import create_main_screen
from utils import clear_screen
import random

# Ensure necessary folders exist
os.makedirs("video", exist_ok=True)
os.makedirs("audio", exist_ok=True)


class VideoCapture:
    def __init__(self, master, num_q=5, back_callback=None):
        """Initialize video capture inside an existing window."""
        self.master = master
        self.back_callback = back_callback
        self.master.title("M.A.I.A - Interview Preparation")

        # Video and audio variables
        self.cap = cv2.VideoCapture(0)
        self.writer = None
        self.running = False
        self.audio_running = False
        self.width, self.height = int(self.cap.get(3)), int(self.cap.get(4))
        self.fps = 30.0 
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.audio_stream = None
        self.audio_frames = []
        self.master.protocol("WM_DELETE_WINDOW", self.quit_scr)
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

        self.selected_questions = [self.questions[random.randint(0, len(self.questions) - 1)] for _ in range(num_q)]
        self.current_question = 0

        self.timer = None

        self.count = 10
        self.countdown_id = None

        self.uf_id = None

        self.video_filename = self.get_new_filename("video", "vid", "avi")
        self.audio_filename = self.get_new_filename("audio", "aud", "wav")

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

        self.next_question_btn = ctk.CTkButton(self.control_frame, text="Next Question", command=self.next_question, fg_color="#1e349e", hover_color="#13205f", state="disabled")
        self.next_question_btn.pack(pady=10)

        self.start_cam_btn = ctk.CTkButton(self.control_frame, text="Start Test", command=self.start_camera, fg_color="#1e349e", hover_color="#13205f")
        self.start_cam_btn.pack(pady=10)

        self.bottom_frame = ctk.CTkFrame(self.container, height=50, fg_color="#050c30")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.end_test_btn = ctk.CTkButton(self.bottom_frame, text="End Test", fg_color="red", hover_color="#91071c", command=self.end_test)
        self.end_test_btn.pack(side="right", padx=20, pady=10)

        self.update_frame()

    def countdown(self):
        if self.count > 0 :
            self.warning_label.configure(fg_color="yellow", text=f"⚠️ Recording will stop in {self.count} seconds!", text_color="black")
            self.count -= 1
            self.countdown_id = self.master.after(1000, self.countdown) 
        else:
            self.stop_camera()
            print(f"Saved video: {self.video_filename}")
            print(f"Saved audio: {self.audio_filename}")
            self.warning_label.configure(text = "Press go to continue >:(")


    def start_camera(self):
        """Starts video and audio recording with improved logic."""
        if not self.running:           
            self.video_filename = self.get_new_filename("video","vid", "avi")
            self.audio_filename = self.get_new_filename("audio","aud", "wav")

            self.writer = cv2.VideoWriter(self.video_filename, self.fourcc, self.fps, (self.width,self.height))

            self.running = True 
            self.audio_running = True

            self.video_thread = threading.Thread(target=self.record_video)
            self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
            
            self.video_thread.start()
            self.audio_thread.start()
            
            self.timer = threading.Timer(5, self.countdown)  # Stop after 10 seconds
            self.timer.start()

            self.start_cam_btn.configure(state="disabled")  
            self.next_question_btn.configure(state="normal") 

    def record_video(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.writer.write(frame)
        self.writer.release() 

    def get_new_filename(self, dir, prefix, extension):
        """Generates a new filename."""
        return f"{dir}/{prefix}_{self.current_question+1}.{extension}"
    
    def update_frame(self):
        """Updates video frame in the GUI."""
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            ctk_img = ctk.CTkImage(dark_image=img, size=(self.width, self.height))
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img 
        self.uf_id = self.master.after(10,self.update_frame)        

    def record_audio(self):
        """Records audio while video is being recorded in a separate thread."""
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        audio = pyaudio.PyAudio()
        stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        frames = []

        while self.audio_running:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))

    def next_question(self):
        """Displays the next question in the randomly selected list."""
        self.new_recording()
        self.warning_label.configure(fg_color = "#050c30", text="") 
        self.current_question+=1    
        if self.current_question < len(self.selected_questions) - 1: 
            self.new_recording()
            print(self.selected_questions[self.current_question])
            self.question_label.configure(text=self.selected_questions[self.current_question])
        elif self.next_question_btn.cget("text") == "Submit Test": # added elif condition so that if the button is clicked more than once it doesnt throw error, need to implement functionality
            self.master.after_cancel(self.uf_id)
            self.video_label.configure(image=None, text="Video feed")
            self.question_label.configure(text=None)
            self.video_label.image = None
            self.stop_camera()
            print("Submitting the test...")  
            self.submit_test()
            return
        else:
            self.question_label.configure(text=self.selected_questions[self.current_question])
            self.next_question_btn.configure(text="Submit Test")  

    def new_recording(self):
        """Stop current recording and start a new one."""
        if self.running:
            self.stop_camera()
            if self.countdown_id:
                self.master.after_cancel(self.countdown_id)
                self.count = 10
        else:
            self.start_camera()

    def stop_camera(self):
        """Stops video and audio recording."""
        if self.running:
            self.running = False
            self.audio_running = False
            self.writer.release()

            self.timer.cancel()
            
            self.video_thread.join()
            self.audio_thread.join()

    def submit_test(self):
        clear_screen(self.master)
        if self.back_callback:
            self.back_callback(self.master)  # Use callback to return to main screen

    def quit_scr(self):
        if self.uf_id:
            self.master.after_cancel(self.uf_id)
        if self.timer:
            self.timer.cancel()
        
        if self.running==True:
            self.running = False
            self.audio_running = False
            self.video_thread.join()
            self.audio_thread.join()
            if self.writer:
                self.writer.release() 
        self.master.destroy()

    def end_test(self):
        """Ends test, deletes files, and returns to main menu."""
        if self.uf_id:
            self.master.after_cancel(self.uf_id)
        if self.timer:
            self.timer.cancel()
        
        if self.running==True:
            self.running = False
            self.audio_running = False
            self.video_thread.join()
            self.audio_thread.join()
            self.writer.release()      

        # Delete video and audio files
        for folder in ["video", "audio"]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        print("Test ended, returning to main screen.")
        clear_screen(self.master)
        if self.back_callback:
            self.back_callback(self.master)

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1420x800")
    VideoCapture(root)  
    root.mainloop()

def start_test(master, back_callback):
    """Clears the screen and starts the Video Capture screen."""
    clear_screen(master)  # Ensure old content is removed
    VideoCapture(master, back_callback=back_callback)  # Initialize Video Capture