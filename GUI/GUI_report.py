import customtkinter as ctk
import os

class Report(ctk.CTkFrame):
    def __init__(self, root, sections, back_to_main=None, score = None):
        self.root = root
        self.root.update_idletasks()
        self.main = back_to_main
        self.mod_score = score
        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")  

        self.above_frame =ctk.CTkFrame(root,fg_color="#050c30")
        self.above_frame.pack(fill="both")

        self.background_frame = ctk.CTkScrollableFrame(root, fg_color="#050c30")
        self.background_frame.pack(fill="both", expand=True)

        self.below_frame =ctk.CTkFrame(root,fg_color="#050c30")
        self.below_frame.pack(fill="both")

        self.title_label = ctk.CTkLabel(self.above_frame, text="REPORT", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(pady=(10, 5))  

        self.create_report(sections)

        self.score_label = ctk.CTkLabel(self.below_frame, text = f"\nYour Score: {round(self.mod_score)}", font = ("Segoe UI", 20, "bold"))
        self.score_label.pack(fill = "both")
        self.back_button = ctk.CTkButton(self.below_frame, text="Back", fg_color="#1e3a8a", text_color="white", hover_color="#3b5998", font=("Segoe UI", 18), corner_radius=20, width=300, height=40, command=self.go_back)
        self.back_button.pack(pady=20)

    def create_section(self, parent, heading_text, body=None):
        """Creates a section with a heading and a scrollable frame"""
        section_frame = ctk.CTkFrame(parent, fg_color="#142373")
        section_frame.pack(pady=(5, 10), padx=20, fill="both")  

        heading = ctk.CTkLabel(section_frame, text=heading_text, font=("Segoe UI", 16, "bold"), anchor="w")
        heading.pack(pady=(5, 2), padx=10, anchor="center")  

        scrollable_frame = ctk.CTkScrollableFrame(section_frame, width=300, height=100, fg_color="#050c30")  
        scrollable_frame.pack(pady=(5, 15), padx=70, fill="both", expand=True)

        self.display_report(scrollable_frame, body)  

    def display_report(self, parent, body):
        sections = body.split("Tips for improvement:")
        right_part = sections[0].replace("What you did right:", "").strip()
        improvement_part = sections[1].strip() if len(sections) > 1 else ""
        def add_section(title, points):
            ctk.CTkLabel(parent, text=title, font=("Segoe UI", 16, "bold"), anchor="w").pack(pady=(10, 5), padx=10, anchor="w")
            for point in points.split("- "):
                point = point.strip()
                if point:
                    ctk.CTkLabel(parent, text="- " + point, font=("Segoe UI", 12), anchor="w").pack(pady=2, padx=20, anchor="w")
            ctk.CTkLabel(parent, text="", height=10).pack()
        add_section("What you did right:", right_part)
        if improvement_part:
            add_section("Tips for improvement:", improvement_part)

    def create_report(self, sections):
        """Creates multiple sections from a dictionary"""
        for key, val in sections.items():
            self.create_section(self.background_frame, key, val)

    def go_back(self):
        for folder in ["2_video", "1_audio"]:
            for file in os.listdir(folder):
                try:
                    os.remove(os.path.join(folder, file))
                except FileNotFoundError:
                    break
        self.main(self.root)
    
# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    sections_dict = {"Eyebrow Furrow": "bruh", "Eye Gaze": "this", "Emotion Speech": "is lame", "Cont": "as hell"}
    app = Report(root, sections_dict)
    root.mainloop()
