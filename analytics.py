import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InterviewPerformanceGraph(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#050c30")  # Set frame background color
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Generate synthetic data
        self.x_values = np.arange(1, 11)
        self.body_language_score = np.random.randint(50, 90, 10)
        self.content_score = np.random.randint(40, 95, 10)
        self.emotion_score = np.random.randint(45, 85, 10)
        self.job_suitability_score = np.random.randint(30, 80, 10)
        self.combined_score = (self.body_language_score + self.content_score +
                               self.emotion_score + self.job_suitability_score) / 4

        # Create and display the graph
        self.create_graph()

        # Create buttons
        self.create_buttons()

    def create_graph(self):
        fig, ax = plt.subplots(figsize=(12, 7))

        # Set figure and graph background colors
        fig.patch.set_facecolor("#13205f")
        ax.set_facecolor("#13205f")

        # Customize grid lines for better visibility
        ax.grid(color="#405488", linestyle="--", linewidth=0.5)

        # Plot the lines with different colors and markers
        ax.plot(self.x_values, self.body_language_score, marker='o', linestyle='-', 
                label="Body Language", color='#125282')
        ax.plot(self.x_values, self.content_score, marker='s', linestyle='-', 
                label="Content Analysis", color='#316b41')
        ax.plot(self.x_values, self.emotion_score, marker='^', linestyle='-', 
                label="Emotion Detection", color='#781c2e')
        ax.plot(self.x_values, self.job_suitability_score, marker='d', linestyle='-', 
                label="Job Suitability", color='#663c2c')
        ax.plot(self.x_values, self.combined_score, marker='*', linestyle='-', 
                linewidth=3, label="Overall Score", color='#c916c9')

        # Set labels and title
        ax.set_xlabel("Session", color="white")
        ax.set_ylabel("Score (%)", color="white")
        ax.set_title("Interview Performance Over Time", color="white")

        # Move the legend outside the plot
        legend = ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), facecolor="#13205f", edgecolor="white", fontsize=10)
        for text in legend.get_texts():
            text.set_color("white")  # Set legend text color to white

        # Set tick label colors for readability
        ax.tick_params(axis='x', colors="white")
        ax.tick_params(axis='y', colors="white")

        # Adjust layout to prevent overlap
        fig.tight_layout()

        # Embed the Matplotlib figure inside CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor="center")

        plt.close(fig)  # Prevent memory issues

    def create_buttons(self):
        """Creates the Back and Reset Scores buttons."""

        # Create "Back" button
        back_button = ctk.CTkButton(self, 
                                    text="Back", 
                                    fg_color="#1e3a8a", 
                                    text_color="white", 
                                    hover_color="#3b5998", 
                                    font=("Segoe UI", 18), 
                                    corner_radius=20, 
                                    width=300, 
                                    height=40, 
                                    command=self.go_back)
        back_button.place(relx=0.5, rely=0.85, anchor="center")  # Centered below graph

        # Create "Reset Scores" button (identical to Back button)
        reset_button = ctk.CTkButton(self, 
                                     text="Reset Scores", 
                                     fg_color="#1e3a8a", 
                                     text_color="white", 
                                     hover_color="#3b5998", 
                                     font=("Segoe UI", 18), 
                                     corner_radius=20, 
                                     width=300, 
                                     height=40, 
                                     command=self.reset_all_scores)
        reset_button.place(relx=0.5, rely=0.93, anchor="center")  # Slightly below Back button

    def go_back(self):
        """Handles back button click event."""
        print("Back button clicked")

    def reset_all_scores(self):
        """Handles reset scores button click event."""
        print("Reset Scores button clicked - Implement score reset logic here.")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.geometry("1920x1080")  # Increased width for legend space
    app.title("M.A.I.A Performance Graph")
    app.configure(fg_color="#050c30")  # Set window background color

    graph_frame = InterviewPerformanceGraph(app)
    graph_frame.pack(fill="both", expand=True)

    app.mainloop()
