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
        self.cap = None
        self.writer = None
        self.running = False

        self.audio_stream = None
        self.audio_frames = []
        self.audio_running = False
        self.stop_event = threading.Event()

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
        self.limit_reached = False

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

        self.next_question_btn = ctk.CTkButton(self.control_frame, text="Next Question", command=self.next_question, fg_color="#1e349e", hover_color="#13205f", state="disabled")
        self.next_question_btn.pack(pady=10)

        self.start_cam_btn = ctk.CTkButton(self.control_frame, text="Start Camera", command=self.start_camera, fg_color="#1e349e", hover_color="#13205f")
        self.start_cam_btn.pack(pady=10)

        self.bottom_frame = ctk.CTkFrame(self.container, height=50, fg_color="#050c30")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.end_test_btn = ctk.CTkButton(self.bottom_frame, text="End Test", fg_color="red", hover_color="#91071c", command=self.end_test)
        self.end_test_btn.pack(side="right", padx=20, pady=10)

    def start_camera(self):
        """Starts video and audio recording with improved logic."""
        if not self.running:
            self.running = True
            self.audio_running = True  
            self.stop_event.clear()
            self.start_cam_btn.configure(state="disabled")  
            self.next_question_btn.configure(state="normal")  

            # Release previous camera instance before reinitializing
            if self.cap is not None:
                self.cap.release()
                time.sleep(1)  
                
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.running = False
                self.start_cam_btn.configure(state="normal") 
                return  

            # Get frame size and setup video writer
            width, height = int(self.cap.get(3)), int(self.cap.get(4))
            fps = 40.0 
            fourcc = cv2.VideoWriter_fourcc(*'MPEG')
            
            self.video_filename = f"video/vid_q{self.current_question+1}.avi"
            self.audio_filename = f"audio/aud_q{self.current_question+1}.wav"

            # Initialize video writer
            self.writer = cv2.VideoWriter(self.video_filename, fourcc, fps, (width, height))

            # Start video and audio threads
            self.video_thread = threading.Thread(target=self.update_frame, daemon=True)
            self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.start_time = time.time()
            self.video_thread.start()
            self.audio_thread.start()

            self.update_frame()

    def update_frame(self):
        """Updates video frame in the GUI."""
        if self.limit_reached==True:
            return
        
        fin = time.time() - self.start_time

        if 50 <= fin < 60:  # Show warning for last 10 seconds
            rem = 60 - fin
            self.warning_label.configure(fg_color="yellow", text=f"⚠️ Recording will stop in {int(rem)} seconds!", text_color="black")

        elif fin >= 60 and self.limit_reached!=True:  # Stop recording after 1 minute and go to the next question
            print("1-minute recording limit reached. Stopping...")    
            self.limit_reached = True
            self.warning_label.configure(fg_color="yellow",text="Proceed to the next question please!", text_color="black") 
            self.stop_camera()            
            return

        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return
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
                self.video_label.image = ctk_img 

            time.sleep(0.01)
            if not self.limit_reached:
                self.master.after(30, self.update_frame)

    def record_audio(self):
        """Records audio while video is being recorded in a separate thread."""
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        
        p = pyaudio.PyAudio()
        self.audio_stream = p.open(format=format, 
                                channels=channels, 
                                rate=rate, 
                                input=True, 
                                frames_per_buffer=chunk)
        
        self.audio_frames = []
        self.stop_event = threading.Event() 
        
        while not self.stop_event.is_set():
            elapsed_time = time.time() - self.start_time  
            if elapsed_time >= 60:  
                self.stop_event.set()
                break
            
            data = self.audio_stream.read(chunk, exception_on_overflow=False)
            self.audio_frames.append(data)
            time.sleep(0.01)
        
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        p.terminate()
        
        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(self.audio_frames))

    def next_question(self):
        self.warning_label.configure(fg_color = "#050c30", text="")
        self.stop_camera()
        self.limit_reached = False
        """Displays the next question in the randomly selected list."""
        if self.current_question < len(self.selected_questions) - 1:  # Ensure we don't exceed the list
            self.current_question += 1
            self.master.after(0, self.start_camera)
            self.question_label.configure(text=self.selected_questions[self.current_question])
        elif self.next_question_btn.cget("text") == "Submit Test": # added elif condition so that if the button is clicked more than once it doesnt throw error, need to implement functionality
            print("Submitting the test...")  
            self.submit_test()
            return
        else:
            self.video_label.configure(image=None, text="Video feed")
            self.video_label.image = None
            self.next_question_btn.configure(text="Submit Test")  

    def stop_camera(self):
        """Stops video and audio recording."""
        self.running = False
        self.stop_event.set()
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()
        self.audio_running = False

    def submit_test(self):
        clear_screen(self.master)
        if self.back_callback:
            self.back_callback(self.master)  # Use callback to return to main screen

    def end_test(self):
        """Ends test, deletes files, and returns to main menu."""
        if self.running:
            self.stop_camera()     
            if self.audio_stream is not None:
                try:
                    if self.audio_stream.is_active():
                        self.audio_stream.stop_stream()
                except OSError:
                    print("OSError due to recording stream state")            
                self.audio_stream.close()     

        # Delete video and audio files
        for folder in ["video", "audio"]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        print("Test ended, returning to main screen.")
        clear_screen(self.master)
        if self.back_callback:
            self.back_callback(self.master)

# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("1420x800")
#     VideoCapture(root)  
#     root.mainloop()

def start_test(master, back_callback):
    """Clears the screen and starts the Video Capture screen."""
    clear_screen(master)  # Ensure old content is removed
    VideoCapture(master, back_callback=back_callback)  # Initialize Video Capture