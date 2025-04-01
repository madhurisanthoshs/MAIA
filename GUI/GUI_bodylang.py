import customtkinter as ctk
from utils import clear_screen
from sqlite import get_recent_and_best_score  # Fetch scores dynamically
from video_capture import start_test

BG_COLOR = "#050c30"
BUTTON_COLOR = "#162884"

def create_bodylang_screen(master, back_to_main):
    """Displays the Body Language Detection screen."""
    clear_screen(master)

    # Fetch scores dynamically
    recent_score, best_score = get_recent_and_best_score("body_language")

    background_frame = ctk.CTkFrame(master=master, fg_color=BG_COLOR)
    background_frame.pack(fill="both", expand=True)

    content_frame = ctk.CTkFrame(master=background_frame, fg_color=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=50, pady=50)

    title_label = ctk.CTkLabel(
        master=content_frame, text="Body Language Detection",
        font=("Segoe UI", 50, "bold"), text_color="white"
    )
    title_label.pack(anchor="w", pady=(10, 10))

    description_label = ctk.CTkLabel(
        master=content_frame,
        text=(
            "Take a mock interview and we'll analyze your posture, gestures and smiles to determine the overall body language conveyed to the interviewer."
        ),
        font=("Segoe UI", 28), text_color="white",
        anchor="w", justify="left", wraplength=750
    )
    description_label.pack(anchor="w", pady=(10, 10))

    # ✅ Dynamically Updated Score Labels
    score_label = ctk.CTkLabel(
        master=content_frame, text=f"Your Body Language Score: {recent_score if recent_score is not None else 'N/A'}",
        font=("Segoe UI", 35, "bold"), text_color="white"
    )
    score_label.pack(pady=(20, 5))

    best_score_label = ctk.CTkLabel(
        master=content_frame, text=f"Best Score: {best_score if best_score is not None else 'N/A'}",
        font=("Segoe UI", 35, "bold"), text_color="white"
    )
    best_score_label.pack(pady=(20, 5))

    take_test_button = ctk.CTkButton(
        master=content_frame, text="Take the Body Language Test",
        font=("Segoe UI", 24, "bold"), fg_color=BUTTON_COLOR,
        command=lambda: start_test(master, back_callback=back_to_main, mod="b")  # Pass main screen callback
    )
    take_test_button.pack(pady=5)

    back_button = ctk.CTkButton(
        master=content_frame, text="Back to Main Screen",
        font=("Segoe UI", 22, "bold"), fg_color=BUTTON_COLOR,
        command=lambda: back_to_main(master)
    )
    back_button.pack(pady=(15, 5))
