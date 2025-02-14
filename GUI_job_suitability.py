import customtkinter as ctk
from utils import clear_screen
from sqlite import get_recent_and_best_score  # Fetch scores dynamically
from video_capture import start_test

BG_COLOR = "#050c30"
BUTTON_COLOR = "#162884"

def create_job_suitability_screen(master, back_to_main):
    """Displays the job suitability screen."""
    clear_screen(master)

    # Fetch scores dynamically
    recent_score, best_score = get_recent_and_best_score("job_suitability")

    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    content_frame = ctk.CTkFrame(master=background_frame, fg_color=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=50, pady=50)

    title_label = ctk.CTkLabel(
        master=content_frame, text="Job Suitability",
        font=("Segoe UI", 50, "bold"), text_color="white"
    )
    title_label.pack(anchor="w", pady=(10, 10))

    description_label = ctk.CTkLabel(
        master=content_frame,
        text=(
            "Share a job description and take a mock interview—we'll assess your answers and show how well you fit the role."
        ),
        font=("Segoe UI", 28), text_color="white",
        anchor="w", justify="left", wraplength=750
    )
    description_label.pack(anchor="w", pady=(10, 10))

    # Job Description Input Box
    job_description_box = ctk.CTkTextbox(
        master=content_frame, height=110, width=750, font=("Segoe UI", 20),
        fg_color=BUTTON_COLOR, text_color="white"
    )
    job_description_box.insert("1.0", "Paste your job description here...")
    job_description_box.pack(pady=(10, 10))

    # ✅ Dynamically Updated Score Labels
    score_label = ctk.CTkLabel(
        master=content_frame, text=f"Your Role Fit Score: {recent_score if recent_score is not None else 'N/A'}",
        font=("Segoe UI", 35, "bold"), text_color="white"
    )
    score_label.pack(pady=(20, 5))

    best_score_label = ctk.CTkLabel(
        master=content_frame, text=f"Best Score: {best_score if best_score is not None else 'N/A'}",
        font=("Segoe UI", 35, "bold"), text_color="white"
    )
    best_score_label.pack(pady=(20, 5))

    def handle_take_test():
        job_description = job_description_box.get("1.0", "end").strip()
        start_test(master, back_callback=back_to_main)
        print(job_description)

    take_test_button = ctk.CTkButton(
        master=content_frame, text="Take the Job Suitability Test",
        font=("Segoe UI", 24, "bold"), fg_color=BUTTON_COLOR,
        command=handle_take_test  # Pass job description to test
    )
    take_test_button.pack(pady=5)

    back_button = ctk.CTkButton(
        master=content_frame, text="Back to Main Screen",
        font=("Segoe UI", 22, "bold"), fg_color=BUTTON_COLOR,
        command=lambda: back_to_main(master)
    )
    back_button.pack(pady=(15, 5))
