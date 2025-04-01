import customtkinter as ctk
from GUI.GUI_content_analysis import create_content_analysis_screen
from GUI.GUI_emotion_detection import create_emotion_detection_screen
from GUI.GUI_job_suitability import create_job_suitability_screen
from GUI.GUI_analytics import create_analytics_screen
from GUI.GUI_bodylang import create_bodylang_screen
from utils import clear_screen, end
from sqlite import get_recent_and_best_score  # Fetch scores dynamically

BG_COLOR = "#050c30"
BUTTON_COLOR = "#162884"

def create_main_screen(master):
    """Creates the main screen layout inside the given master widget."""
    clear_screen(master)

    # Fetch scores dynamically from the database
    recent_score, best_score = get_recent_and_best_score("overall")

    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    title_label = ctk.CTkLabel(
        master=background_frame, text="M.A.I.A",
        font=("Segoe UI", 100, "bold"), text_color="white"
    )
    title_label.pack(pady=(30, 10))

    subtitle_label = ctk.CTkLabel(
        master=background_frame, text="A Multimodal AI Agent for Holistic Interview Preparation",
        font=("Segoe UI", 30), wraplength=750, justify="center", text_color="white"
    )
    subtitle_label.pack(pady=(0, 20))

    names_label = ctk.CTkLabel(
        master=background_frame, text="Anirudh T (21BAI1163)\nMadhuri Santhosh Srinivasan (21BAI1892)",
        font=("Segoe UI", 25), justify="center", text_color="white"
    )
    names_label.pack(pady=(0, 40))

    create_buttons(background_frame, master)

    analytics_button = ctk.CTkButton(
        master=background_frame, text="View Analytics", font=("Segoe UI", 22, "bold"), fg_color=BUTTON_COLOR,
        command=lambda: create_analytics_screen(master, create_main_screen)
    )
    analytics_button.place(relx=0.5, rely=0.75, anchor="center")

def create_buttons(master, app):
    """Creates buttons for navigation."""
    button_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    button_frame.place(relx=0.5, rely=0.65, anchor="center")

    buttons = {
        "Body Language": lambda: create_bodylang_screen(app, create_main_screen),
        "Emotion/Stress Detection": lambda: create_emotion_detection_screen(app, create_main_screen),
        "Content Analysis": lambda: create_content_analysis_screen(app, create_main_screen),
        "Job Suitability": lambda: create_job_suitability_screen(app, create_main_screen)
    }

    for button_text, command in buttons.items():
        button = ctk.CTkButton(
            master=button_frame, text=button_text,
            font=("Segoe UI", 18, "bold"), corner_radius=20,
            width=250, height=50, fg_color=BUTTON_COLOR, command=command
        )
        button.pack(side="left", padx=15)

def create_work_in_progress_screen(master):
    """Displays a 'Work in Progress' screen."""
    clear_screen(master)
    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    message_label = ctk.CTkLabel(
        master=background_frame, text="We're still working on these features,\ncheck back soon!",
        font=("Segoe UI", 40, "bold"), justify="center", text_color="white"
    )
    message_label.pack(expand=True)

    back_button = ctk.CTkButton(
        master=background_frame, text="Back to Main Screen",
        font=("Segoe UI", 20, "bold"), corner_radius=20,
        fg_color=BUTTON_COLOR, command=lambda: create_main_screen(master)
    )
    back_button.pack(pady=20)

def run_app():
    """Initializes and runs the M.A.I.A application."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    width= app.winfo_screenwidth()               
    height= app.winfo_screenheight()               
    app.geometry("%dx%d" % (width, height))
    app.title("M.A.I.A")
    app.protocol("WM_DELETE_WINDOW", lambda:end(app))
    create_main_screen(app)
    app.mainloop()
