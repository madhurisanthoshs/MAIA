import customtkinter as ctk
import tkinter  # Ensure tkinter is available

# Define global color variables
BG_COLOR = "#050c30"  # Muted warm purple background
BUTTON_COLOR = "#13205f"  # Neutral blue button color

def run_app(score):
    """Launches the M.A.I.A GUI with the given score value."""
    
    # Set appearance and theme
    ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
    ctk.set_default_color_theme("blue")

    # Create the main application window
    app = ctk.CTk()
    app.geometry("1920x1080")
    app.title("M.A.I.A")

    # Background Frame
    background_frame = ctk.CTkFrame(master=app, fg_color=BG_COLOR, width=1920, height=1080)
    background_frame.pack(fill="both", expand=True)  # Fill the entire window

    # Title Label
    title_label = ctk.CTkLabel(
        master=background_frame,
        text="M.A.I.A",
        font=("Segoe UI", 100, "bold")
    )
    title_label.pack(pady=(30, 10))

    # Subtitle Label
    subtitle_label = ctk.CTkLabel(
        master=background_frame,
        text="A Multimodal AI Agent for Holistic Interview Preparation",
        font=("Segoe UI", 30),
        wraplength=750,
        justify="center"
    )
    subtitle_label.pack(pady=(0, 20))

    # "Created by" Label (smaller, italicized)
    created_by_label = ctk.CTkLabel(
        master=background_frame,
        text="Created by:",
        font=("Segoe UI", 20, "italic"),
        justify="center"
    )
    created_by_label.pack()

    # Names Label (larger, bold for emphasis)
    names_label = ctk.CTkLabel(
        master=background_frame,
        text="Anirudh T (21BAI1163)\nMadhuri Santhosh Srinivasan (21BAI1892)",
        font=("Segoe UI", 25),
        justify="center"
    )
    names_label.pack(pady=(0, 40))  # Added padding below credits

    # Button Frame (for alignment and background consistency)
    button_frame = ctk.CTkFrame(master=background_frame, fg_color=BG_COLOR)
    button_frame.pack(pady=(20, 40), fill="x")  # Increased space below buttons

    # Buttons
    buttons = ["Body Language", "Emotion/Stress Detection", "Content Analysis", "Job Suitability"]
    for button_text in buttons:
        button = ctk.CTkButton(
            master=button_frame,
            text=button_text,
            font=("Segoe UI", 18, "bold"),
            corner_radius=20,
            width=300,
            height=50,
            fg_color=BUTTON_COLOR,
            command=lambda button_text=button_text: print(f"Button '{button_text}' clicked")
        )
        button.pack(side="left", padx=20)  # Evenly spaced buttons

    # Score Label (Placed Below Buttons)
    score_label = ctk.CTkLabel(
        master=background_frame,
        text=f"Your Score: {score}",
        font=("Segoe UI", 30, "bold"),
        justify="center"
    )
    score_label.pack(pady=(40, 20))  # Spacing before and after

    # Run the application
    app.mainloop()
