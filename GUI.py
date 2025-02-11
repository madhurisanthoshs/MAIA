import customtkinter as ctk
import tkinter  # Ensure tkinter is available

# Define global color variables
BG_COLOR = "#050c30"
BUTTON_COLOR = "#13205f"

def create_main_screen(master, score=0, content_analysis_score=0):
    """Creates the main screen layout inside the given master widget."""
    clear_screen(master)

    # Background Frame with BG_COLOR applied
    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    # Title Label
    title_label = ctk.CTkLabel(
        master=background_frame,
        text="M.A.I.A",
        font=("Segoe UI", 100, "bold"),
        text_color="white"
    )
    title_label.pack(pady=(30, 10))

    # Subtitle Label
    subtitle_label = ctk.CTkLabel(
        master=background_frame,
        text="A Multimodal AI Agent for Holistic Interview Preparation",
        font=("Segoe UI", 30),
        wraplength=750,
        justify="center",
        text_color="white"
    )
    subtitle_label.pack(pady=(0, 20))

    # "Created by" Label
    created_by_label = ctk.CTkLabel(
        master=background_frame,
        text="Created by:",
        font=("Segoe UI", 20, "italic"),
        justify="center",
        text_color="white"
    )
    created_by_label.pack()

    # Names Label
    names_label = ctk.CTkLabel(
        master=background_frame,
        text="Anirudh T (21BAI1163)\nMadhuri Santhosh Srinivasan (21BAI1892)",
        font=("Segoe UI", 25),
        justify="center",
        text_color="white"
    )
    names_label.pack(pady=(0, 40))

    # Buttons
    create_buttons(background_frame, master, score, content_analysis_score)

    # Score Label
    score_label = ctk.CTkLabel(
        master=background_frame,
        text=f"Your Score: {score}",
        font=("Segoe UI", 30, "bold"),
        justify="center",
        text_color="white"
    )
    score_label.place(relx=0.5, rely=0.68, anchor="center")

def create_buttons(master, app, score, content_analysis_score):
    """Creates four evenly spaced buttons with rounded corners."""
    button_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    button_frame.place(relx=0.5, rely=0.5, anchor="center")  # 80% width of the window
    
    buttons = {
        "Body Language": lambda: create_work_in_progress_screen(app, score, content_analysis_score),
        "Emotion/Stress Detection": lambda: create_work_in_progress_screen(app, score, content_analysis_score),
        "Content Analysis": lambda: create_content_analysis_screen(app, score, content_analysis_score),
        "Job Suitability": lambda: create_work_in_progress_screen(app, score, content_analysis_score)
    }
    
    for button_text, command in buttons.items():
        button = ctk.CTkButton(
            master=button_frame,
            text=button_text,
            font=("Segoe UI", 18, "bold"),
            corner_radius=20,
            width=300,
            height=50,
            fg_color=BUTTON_COLOR,
            command=command
        )
        button.pack(side="left", padx=20)  

def create_work_in_progress_screen(master, score, content_analysis_score):
    """Displays a 'Work in Progress' screen."""
    clear_screen(master)

    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    message_label = ctk.CTkLabel(
        master=background_frame,
        text="We're still working on these features,\ncheck back soon!",
        font=("Segoe UI", 40, "bold"),
        justify="center",
        text_color="white"
    )
    message_label.pack(expand=True)

    back_button = ctk.CTkButton(
        master=background_frame,
        text="Back to Main Screen",
        font=("Segoe UI", 20, "bold"),
        corner_radius=20,
        fg_color=BUTTON_COLOR,
        command=lambda: create_main_screen(master, score, content_analysis_score)
    )
    back_button.pack(pady=20)


def create_content_analysis_screen(master, score, content_analysis_score):
    """Displays the Content Analysis screen."""
    clear_screen(master)

    # Full background coverage
    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)  # Ensures full window coverage

    # Content Frame (for padding & alignment)
    content_frame = ctk.CTkFrame(master=background_frame, fg_color=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=50, pady=50)  # Added padding

    # Left-aligned Title
    title_label = ctk.CTkLabel(
        master=content_frame,
        text="Content Analysis",
        font=("Segoe UI", 50, "bold"),
        justify="left",
        anchor="w",
        text_color="white"
    )
    title_label.pack(anchor="w", pady=(10, 10))

    # Left-aligned Description
    description_label = ctk.CTkLabel(
        master=content_frame,
        text=(
            "Take a mock interview and we'll analyze the following from your answers:\n"
            "• Speech Rate\n"
            "• Answer Relevance\n"
            "• Jargon and Filler Word Usage\n"
            "• Response Confidence"
        ),
        font=("Segoe UI", 28),
        justify="left",
        anchor="w",
        text_color="white"
    )
    description_label.pack(anchor="w", pady=(10, 20))

    # Content Analysis Score (Centered)
    score_label = ctk.CTkLabel(
        master=content_frame,
        text=f"Your Content Analysis Score: {content_analysis_score}",
        font=("Segoe UI", 35, "bold"),
        justify="center",
        text_color="white"
    )
    score_label.pack(pady=(20, 20))

    # Take Test Button (Centered & Bigger)
    take_test_button = ctk.CTkButton(
        master=content_frame,
        text="Take the Content Analysis Test",
        font=("Segoe UI", 24, "bold"),
        corner_radius=20,
        width=400,
        height=70,
        fg_color=BUTTON_COLOR,
        command=lambda: print("Starting Content Analysis Test...")  # Replace with actual functionality
    )
    take_test_button.pack(pady=10)

    # ✅ Back Button (Centered Below Take Test Button)
    back_button = ctk.CTkButton(
        master=content_frame,
        text="Back to Main Screen",
        font=("Segoe UI", 22, "bold"),
        corner_radius=20,
        width=300,
        height=60,
        fg_color=BUTTON_COLOR,
        command=lambda: create_main_screen(master, score, content_analysis_score)
    )
    back_button.pack(pady=(15, 15))  # Adjusted padding for spacing

def clear_screen(master):
    """Clears all widgets from the given master widget."""
    for widget in master.winfo_children():
        widget.destroy()
        
def run_app(score=0, content_analysis_score=0):
    """Initializes and runs the M.A.I.A application with provided scores."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("1920x1080")
    app.title("M.A.I.A")

    create_main_screen(app, score, content_analysis_score)

    app.mainloop()
