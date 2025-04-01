import ast
import customtkinter as ctk
import cv2
import pyaudio
import wave
import threading
import os
import time
from PIL import Image
#from GUI_main_screen import create_main_screen
from utils import clear_screen, report_generation, LoadingScreen, end
import random
from content_analysis.speech_rate import speechrate
from content_analysis.fill_jarg_use import filljarg
from emotion_detection.furrow_det import brow_furrow
from emotion_detection.gaze_det import eye_gaze
from emotion_detection.SER import ser
from GUI.GUI_report import Report
from sqlite import insert_score
from RoleFit.role_fit import RoleFit
from content_analysis.transcription import AudioTranscriber
from content_analysis.answer_cont_rel import answer_relevance
from content_analysis.resp_conf import response_confidence
from body_language.body_lang import bodylang

# Ensure necessary folders exist
os.makedirs("2_video", exist_ok=True)
os.makedirs("1_audio", exist_ok=True)


class VideoCapture:
    def __init__(self, master, num_q=5, back_callback=None, mod=None):
        """Initialize video capture inside an existing window."""
        self.master = master
        self.back_callback = back_callback
        self.master.title("M.A.I.A - Interview Preparation")
        self.sr = []
        self.fj_sc = []
        self.brow = []
        self.gaze = []
        self.emo = []
        self.emo_sc = []
        self.cont_rel_sc = []
        self.resp_conf_sc = []
        self.bld_sc = []
        self.bld_fstr = []
        self.rf_score = 0
        self.prompt = ""
        self.brow_rep = "" 
        self.gaze_rep = ""
        self.ser_rep = ""
        self.rf_rep = ""
        self.cr_rep = ""
        self.fj_rep = ""
        self.sr_rep = ""
        self.resp_rep = ""
        self.bld_rep = ""
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
        self.master.protocol("WM_DELETE_WINDOW", lambda:end(self.master))
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
         
        self.rf = RoleFit()
        
        self.transcript = []

        self.mod = mod
        if self.mod == "j":
            try:
                with open(r"RoleFit\rolefit_q.txt", "r", encoding="utf-8") as file:
                    self.selected_questions = [line.strip() for line in file]
            except FileNotFoundError:
                print("The file does not exist.")
        self.timer = None

        self.threads = []

        self.count = 10
        self.countdown_id = None #to stop the countdown process when we go to next vid

        self.uf_id = None #to stop the updating of frames when next        

        self.video_filename = self.get_new_filename("2_video", "vid", "avi")
        self.audio_filename = self.get_new_filename("1_audio", "aud", "wav")
        
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
      
        self.question_label = ctk.CTkLabel(self.control_frame, text=f"{self.current_question+1}. {self.selected_questions[self.current_question]}", wraplength=180)
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

    def start_camera(self):
        """Starts video and audio recording with improved logic."""
        if not self.running:           
            self.video_filename = self.get_new_filename("2_video","vid", "avi")
            self.audio_filename = self.get_new_filename("1_audio","aud", "wav")

            self.writer = cv2.VideoWriter(self.video_filename, self.fourcc, self.fps, (self.width,self.height))

            self.running = True 
            self.audio_running = True

            self.video_thread = threading.Thread(target=self.record_video)
            self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
            
            self.video_thread.start()
            self.audio_thread.start()
            
            self.timer = threading.Timer(50, self.countdown)  # Stop after 10 seconds
            self.timer.start()

            self.start_cam_btn.configure(state="disabled")  
            self.next_question_btn.configure(state="normal") 
    
    def record_video(self):
        """Records the video."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.writer.write(frame)
        self.writer.release() 

    def get_new_filename(self, dir, prefix, extension):
        """Generates a new filename."""
        return f"{dir}/{prefix}_{self.current_question+1}.{extension}"      

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
            
            self.timer.cancel()
            
            self.video_thread.join()
            self.audio_thread.join()

    def countdown(self):
        """Starts a countdown so the user is informed that the recording will be stopped in 1 minute."""
        if self.count > 0 :
            self.warning_label.configure(fg_color="yellow", text=f"⚠️ Recording will stop in {self.count} seconds!", text_color="black")
            self.count -= 1
            self.countdown_id = self.master.after(1000, self.countdown) 
        else:
            self.stop_camera()
            self.warning_label.configure(text = "Proceeding to the next question :(")
            time.sleep(0.5)
            self.count = 10
            self.next_question()

    def next_question(self):
        """Displays the next question in the randomly selected list."""
        if self.running:
            self.new_recording()
        self.warning_label.configure(fg_color = "#050c30", text="") 

        # processing the currently stored recording depending on the selected test
        if self.mod == "b":
            self.bld_thr = threading.Thread(target = self.body_thr)
            self.bld_thr.start()
            self.threads.append(self.bld_thr)
        elif self.mod == "e":
            self.brow_thr = threading.Thread(target=self.brow_fur_thr)
            self.gaze_thr = threading.Thread(target=self.eye_gaze_thr)
            self.SER_thr = threading.Thread(target=self.ser_thr)
            self.brow_thr.start()
            self.gaze_thr.start()
            self.SER_thr.start()
            self.threads.append(self.brow_thr)
            self.threads.append(self.gaze_thr)
            self.threads.append(self.SER_thr)
        elif self.mod == "c":
            a = AudioTranscriber()
            self.curr_trans = a.transcribe(self.audio_filename)
            self.cr_thr = threading.Thread(target = self.cont_rel_thr, daemon=True)
            self.respconf_thr = threading.Thread(target = self.resp_conf_thr, daemon=True)
            self.filljarg_thr = threading.Thread(target=self.fj_thr, daemon=True)
            self.speech_thr = threading.Thread(target=self.sr_thr, daemon=True)
            self.cr_thr.start()
            self.respconf_thr.start()
            self.filljarg_thr.start()
            self.speech_thr.start()            
            self.threads.append(self.cr_thr)
            self.threads.append(self.filljarg_thr)
            self.threads.append(self.speech_thr)
            self.threads.append(self.respconf_thr)
        elif self.mod is None:
            pass

        self.current_question+=1  

        # navigating to the next question and related logic
        if self.current_question < len(self.selected_questions) - 1: 
            self.new_recording()
            # print(self.selected_questions[self.current_question])
            self.question_label.configure(text=f"{self.current_question + 1}. {self.selected_questions[self.current_question]}")
        elif self.next_question_btn.cget("text") == "Submit Test": # added elif condition so that if the button is clicked more than once it doesnt throw error, need to implement functionality
            self.master.after_cancel(self.uf_id)
            self.video_label.configure(image=None, text="Video feed")
            self.question_label.configure(text=None)
            self.video_label.image = None
            self.stop_camera()
            self.cap.release()
            print("Submitting the test...")  
            clear_screen(self.master)
            LoadingScreen(self.master)
            self.thread_sub = threading.Thread(target = self.submit_test)
            self.thread_sub.start()
        else:
            self.new_recording()
            self.question_label.configure(text=f"{self.current_question+1}. {self.selected_questions[self.current_question]}")
            self.next_question_btn.configure(text="Submit Test")  

    def submit(self):
        """Terminates all the active feature threads."""
        for thread in self.threads:
            thread.join()

    def submit_test(self):
        """Calculates the final score and creates the report screen."""
        self.submit()
        d = self.gen_res()
        if (self.mod == "e"):
            self.br = sum(self.brow)/len(self.brow)
            self.ga = sum(self.gaze)/len(self.gaze)
            self.se = sum(self.emo_sc)/len(self.emo_sc)
            self.mod_score = (0.4 * self.se) + (0.3 * self.br) + (0.3 * self.ga)
            insert_score("emotion_detection", round(self.mod_score))
        elif (self.mod == "j"):
            self.mod_score = self.rf_score
            insert_score("job_suitability", round(self.mod_score))
        elif (self.mod == "b"):
            bld = sum(self.bld_sc)/len(self.bld_sc)
            self.mod_score = bld
            insert_score("body_language", round(self.mod_score))
        elif (self.mod == "c"):
            fj = sum(self.fj_sc)/len(self.fj_sc)
            cr = sum(self.cont_rel_sc)/len(self.cont_rel_sc)
            rc = sum(self.resp_conf_sc)/len(self.resp_conf_sc)
            sr = sum(self.sr)/len(self.sr)
            self.mod_score = (fj+cr+rc+sr)/4
            insert_score("content_analysis", round(self.mod_score))
        self.master.after(0, lambda: clear_screen(self.master))
        r = Report(self.master, d, self.back_callback, self.mod_score)

    def gen_res(self): 
        """Generates the reports."""
        print("Generating results...")
        if (self.mod == "e"):
            thr1 = threading.Thread(target = self.brow_re)
            thr2 = threading.Thread(target = self.gaze_re)
            thr3 = threading.Thread(target = self.ser_re)
            thr1.start()
            thr2.start()
            thr3.start()
            thr1.join()
            thr2.join()
            thr3.join()
            dic = {f"Eyebrow Furrowing: {round(sum(self.brow)/len(self.brow))}": self.brow_rep, f"Gaze Detection: {round(sum(self.gaze)/len(self.gaze))}": self.gaze_rep, f"Emotion Recognition: {round(sum(self.emo_sc)/len(self.emo_sc))}": self.ser_rep}
        elif self.mod == "j":
            thr1 = threading.Thread(target = self.trans_all)
            thr2 = threading.Thread(target = self.rf_thr)
            thr1.start()
            thr1.join()
            thr2.start()
            thr2.join()
            dic = {f"Job Suitability: {round(self.rf_score)}": self.rf_rep}
        elif self.mod == "b":
            thr1 = threading.Thread(target = self.bld_re)
            thr1.start()
            thr1.join()
            dic = {f"Body Language Detection: {round(sum(self.bld_sc)/len(self.bld_sc))}": self.bld_rep}
        elif self.mod == "c":
            thr1 = threading.Thread(target = self.rc_re)
            thr2 = threading.Thread(target = self.fj_re)
            thr3 = threading.Thread(target = self.sr_re)
            thr4 = threading.Thread(target = self.cr_re)
            thr1.start()
            thr2.start()
            thr3.start()
            thr4.start()
            thr1.join()
            thr2.join()
            thr3.join()
            thr4.join()
            dic = {f"Answer Content Relevance: {round(sum(self.cont_rel_sc)/len(self.cont_rel_sc))}": self.cr_rep, f"Response Confidence: {round(sum(self.resp_conf_sc)/len(self.resp_conf_sc))}": self.resp_rep, f"Filler/Jargon Use: {round(sum(self.fj_sc)/len(self.fj_sc))}": self.fj_rep, f"Speech Rate: {round(sum(self.sr)/len(self.sr))}": self.sr_rep}
        return dic
    
    # SCORE CALCULATION    
    # BDOY LANGUAGE FEATURES
    def body_thr(self):
        temp, formtemp = bodylang(self.video_filename)
        self.bld_sc.append(temp)
        self.bld_fstr.append(formtemp)

    # EMOTION DETECTION FEATURES
    def brow_fur_thr(self):
        temp = brow_furrow(self.video_filename)
        self.brow.append(temp)
        print(f"brow scores: {self.brow}")

    def eye_gaze_thr(self):
        temp = eye_gaze(self.video_filename)
        self.gaze.append(temp)
        print(f"gaze scores: {self.gaze}")

    def ser_thr(self):
        t1, t2 = ser(self.audio_filename)
        self.emo.append(t1)
        self.emo_sc.append(t2)
        print(f"emotions: {self.emo}\nscores:{self.emo_sc}")

    # CONTENT ANALYSIS FEATURES
    def sr_thr(self):
        temp = speechrate(self.audio_filename)
        self.sr.append(temp)
        print(f"speech rate score: {self.sr}")
    
    def fj_thr(self):
        temp = filljarg(self.audio_filename)
        self.fj_sc.append(temp)
        print(f"filler/jargon score: {self.fj_sc}")

    def cont_rel_thr(self):
        temp = answer_relevance(self.curr_trans, self.selected_questions[self.current_question])
        self.cont_rel_sc.append(temp)
        print(f"content relevance scores: {self.cont_rel_sc}")

    def resp_conf_thr(self):
        temp = response_confidence(self.curr_trans)
        self.resp_conf_sc.append(temp)
        print(f"response confidence scores: {self.resp_conf_sc}")

    # JOB SUITABILITY FEATURES (SCORE+REPORT)
    def rf_thr(self):
        self.rf_score = self.rf.role_fit_score('\n'.join(self.transcript))   
        self.prompt = self.rf.prompt_formatting(self.transcript, self.rf_score)
        self.rf_rep = report_generation(self.prompt)

    # REPORT FORMATTING FUNCTIONS
    # BODY LANGUAGE REPORT
    def bld_re(self):
        temp = "\n".join(self.bld_fstr)
        bld_prompt = f"Given below is a summary of a user's mock interview that tests their body language. You are an expert on interviews. Analyze the provided information critically, and provide helpful, actionable tips on how the user can improve their body language during interviews and thus their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points. Here are their scores along with pose distribution and duration weighted scores associated with their responses for each question: \n{temp}"
        self.bld_rep = report_generation(bld_prompt)

    # EMOTION DETECTION
    def brow_re(self):
        brow_prompt = f"This is how the score is calculated for eyebrow furrowing: The sliding window method divides the sequence into overlapping segments of a fixed size. For each window, the average eyebrow distance is calculated, and the ratio of furrowed frames to total frames in the window is computed. If this ratio exceeds a set threshold, the window is considered stressed. The final score is then determined by subtracting the percentage of stressed windows from 100, representing the overall relaxation level.\nThe scores obtained by the user for each question are given to you in the form of a list: {self.brow}.\nYou are an expert on body language. Given the method for calculating the score, and the score obtained by the user, provide helpful, actionable tips to the user to improve their relaxation level and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term.\n answer format: \n'What you did right:' followed by a brief bulleted list of things the user did right, and \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
        self.brow_rep = report_generation(brow_prompt)

    def gaze_re(self):
        gaze_prompt = f"This is how the score is calculated for focus: The sliding window method divides the sequence into overlapping segments of a fixed size. For each window, the average distraction level is calculated, and the ratio of distracted frames to total frames in the window is computed. If this ratio exceeds a set threshold, the window is considered distracted. The final score is then determined by subtracting the percentage of distracted windows from 100, representing the overall focus level.\nThe score obtained by the user is {self.gaze}.\nYou are an expert on body language and focus. Given the method for calculating the score, and the score obtained by the user, provide helpful, actionable tips to the user to improve their focus level and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term.\nAnswer format: \n'What you did right:' followed by a brief bulleted list of things the user did right, and \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \nEach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
        self.gaze_rep = report_generation(gaze_prompt)

    def ser_re(self):
        temp = "\n".join([f"Score: {s}  Emotions: {e}\n" for s,e in zip(self.emo_sc, self.emo)])
        ser_prompt = (
            "This is how the score is calculated for speech emotion recognition: The system assigns different weights to detected emotions based on their impact on interview performance. Positive emotions such as 'positive' and 'calm' contribute positively to the score, while negative emotions like 'frustrated' and 'disengaged' lower it. Each detected emotion's weight is summed and averaged, then normalized to a 0-100 scale to ensure interpretability. A higher score indicates a confident, composed speaking style, while a lower score suggests emotional distress or disengagement.\n"
            "The following are the scores and emotions for each question asked in the interview."
            f"{temp}\n"
            "You are an expert on interview coaching and emotional intelligence. Given the method for calculating the score, the user's scores, and the detected emotions, provide helpful, actionable feedback on what the user did well and how they can improve their emotional expressiveness during an interview. Provide only the most necessary, unique tips, ensuring they are practical and applicable even in the short term.\n"
            "Answer format:\n"
            "'What you did right:' followed by a brief bulleted list of things the user did well, and\n"
            "'Tips for improvement:' followed by a brief bulleted list of concise, actionable tips explaining what the user can improve, why it matters in an interview, and how they can work on it.\n"
            "Each tip should be one sentence long. Do not reply in markdown format, just give me clean text with points."
        )
        self.ser_rep = report_generation(ser_prompt)
        pass
    
    # CONTENT ANALYSIS
    def fj_re(self):
        fj_prompt = f"This is how the score is calculated for filler and jargon usage: The score is based on the proportion of filler words and excessive jargon used relative to the total number of words in the transcript. Filler words (e.g., 'uh', 'um') are penalized more heavily, while jargon is only penalized if it exceeds 10% of the total word count. Each filler word reduces the score more significantly than jargon, reflecting how distracting fillers are in interviews. The final score is scaled from 0 to 100, with a minimum possible score of 10 to ensure fairness even in poor performances. The fewer fillers and excess jargon present, the higher the score. The scores obtained by the user for each question are given to you in the form of a list: {self.fj_sc}. You are an expert on interviews. Given the method for calculating the score, and the scores obtained by the user, provide helpful, actionable tips to the user to improve their use of clear and concise language and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term. 'What you did right:' followed by a brief bulleted list of things the user did right, and 'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. Each tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points."
        self.fj_rep = report_generation(fj_prompt)

    def sr_re(self):
        sr_prompt = f"This is how the score is calculated for speech rate: The score is calculated based on how close the speaker's speech rate is to an optimal target of 142 words per minute (wpm), which lies within the ideal interview range of 125-160 wpm. A Gaussian function is applied, giving the highest scores when the speech rate is near the optimal value and progressively lower scores as it deviates from it. The sigma value of 60 determines how sensitive the score is to fluctuations away from the optimal rate. Finally, the score is scaled to a range of 0 to 100, with a minimum guaranteed score of 20 out of 100, even when the speech rate is significantly off from the ideal. The scores obtained by the user for each question are given to you in the form of a list: {self.sr}. You are an expert on interviews. Given the method for calculating the score, and the scores obtained by the user, provide helpful, actionable tips to the user to improve their speech rate and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term. Answer format: 'What you did right:' followed by a brief bulleted list of things the user did right, and 'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. Each tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points."
        self.sr_rep = report_generation(sr_prompt)

    def cr_re(self):
        question_score_str = "\n".join(
            [f"Question: {q}\nScore: {s}\n" for q, s in zip(self.selected_questions, self.cont_rel_sc)]
        )
        cr_prompt = (
            f"The following are mock interview questions and the relevance scores their responses received:\n"
            f"{question_score_str}\n"
            "You are an expert on interviews. Given the list of scores, please provide helpful and actionable tips on how the user can improve their response's relevance and improve their performance in interviews and as a result, their score.\n\n"
            "Please provide your response exactly as follows:"
            "'What you did right:' followed by a brief bulleted list of strengths that can be inferred from the provided information.\n"
            "'Tips for improvement:' followed by a brief bulleted list of tips, explaining clearly what the user can improve, why it's relevant from an interview standpoint, and how to improve it.\n"
            "Each tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with bullet points for each section. Also, keep the points unique and specific to the topic, not overly general."
        )
        self.cr_rep = report_generation(cr_prompt)

    def rc_re(self):
        rc_prompt = f"The score you are analyzing reflects the level of response confidence in a mock interview. Higher scores indicate clearer, more assertive communication, while lower scores may reflect hesitation, uncertainty, or lack of conviction in responses. The scores obtained by the user for each question are given to you in the form of a list: {self.resp_conf_sc}. You are an expert on interviews. Given the nature of the score and the values obtained by the user, provide helpful, actionable tips to improve their response confidence and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term. Answer format: 'What you did right:' followed by a brief bulleted list of things the user did right, and 'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant to confidence (from an interview standpoint), and how the user can improve it. Each tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points."
        self.resp_rep = report_generation(rc_prompt)

    def trans_all(self):
        """Transcribes all the recordings and stores their transcripts in a list."""
        audio_dir = "1_audio"
        for file in os.listdir(audio_dir):
            file_path = os.path.join(audio_dir, file)
            a = AudioTranscriber()
            trans = a.transcribe(file_path)
            self.transcript.append(trans)

    def quit_scr(self):
        """Ends the threads and closes the window."""
        if self.running==True:
            self.running = False
            self.audio_running = False
            self.video_thread.join()
            self.audio_thread.join()
            if self.writer:
                self.writer.release() 
            self.cap.release()
        if self.uf_id:
            self.master.after_cancel(self.uf_id)
        if self.timer:
            self.timer.cancel()
        if self.countdown_id:
            self.master.after_cancel(self.countdown_id)        
        if self.threads:
            for thread in self.threads:
                thread.join()
        self.master.destroy()

    def end_test(self):
        """Ends test, deletes files, and returns to main menu."""
        if self.uf_id:
            self.master.after_cancel(self.uf_id)
        if self.timer:
            self.timer.cancel()
        if self.countdown_id:
            self.master.after_cancel(self.countdown_id)        
        if self.running==True:
            self.running = False
            self.audio_running = False
            self.video_thread.join()
            self.audio_thread.join() 
        self.cap.release()    
        # Delete video and audio files
        for folder in ["2_video", "1_audio"]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
        with open(r"RoleFit\rolefit_q.txt", 'w', encoding="utf-8") as file:
            pass
        with open(r"RoleFit\job_description.txt","r", encoding="utf-8") as file:
            pass
        for thread in self.threads:
            thread.join()
        print("Test ended, returning to main screen.")
        clear_screen(self.master)
        if self.back_callback:
            self.back_callback(self.master)

def start_test(master, back_callback, mod=None):
    """Clears the screen and starts the Video Capture screen."""
    clear_screen(master)  # Ensure old content is removed
    VideoCapture(master, back_callback=back_callback, mod=mod)  # Initialize Video Capture

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1420x800")
    VideoCapture(root)  
    root.mainloop()