from g4f.client import Client
import customtkinter as ctk
import os
from content_analysis.transcription import AudioTranscriber

def clear_screen(master):
    """Clears all widgets from the given master widget."""
    for widget in master.winfo_children():
        widget.destroy()

# content analysis/report calling function
def report_generation(prompt):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result

def generate_questions(num_q, prompt, filename = r"RoleFit\job_description.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        temp = file.read().strip()
    prompt = f"'{temp}'\n the above is a job description.\nYou are an expert on interviews. Analyze the above job description and provide '{num_q}' interview question(s) aimed at analyzing if the user is a good fit for the given role. Reply only with 1 question in each line, with no empty lines between them, no text before or after the question(s), and no bullet point indicators before the question (eg. '1.'). Do not reply in markdown format, just give me clean text with points. No lines in between either. If the job description is incomplete or doesn't seem correct, respond by providing 5 general behavioural questions for interviews."
    questions = report_generation(prompt)
    with open(r"RoleFit\rolefit_q.txt", "w", encoding= "utf-8") as file:
        file.write(questions)
    # questions = questions.split()
    # return questions

def end(root: ctk.CTkFrame):
    for folder in ["2_video", "1_audio"]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    with open(r"RoleFit\rolefit_q.txt", 'w') as file:
        pass
    with open(r"RoleFit\job_description.txt","w") as file:
        pass
    root.destroy()

class LoadingScreen:
    def __init__(self, master):
        self.master = master
        self.master.update_idletasks()
        self.bgframe = ctk.CTkFrame(master=master, fg_color="#050c30")
        self.bgframe.pack(fill="both", expand=True, padx=10, pady=10)
        self.label = ctk.CTkLabel(
            master=self.bgframe,
            text="Loading",
            text_color="white",
            font=("Segoe UI", 24)
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.dot_count = 0
        self.animate_dots()

    def animate_dots(self):
        if self.label.winfo_exists():  # Only update if the label exists
            dots = "." * (self.dot_count % 4)
            self.label.configure(text=f"Loading{dots}")
            self.dot_count += 1
            self.animate_id = self.master.after(500, self.animate_dots)  # Store the after() ID
  # Update every 500ms
