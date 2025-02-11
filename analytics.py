import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InterviewPerformanceGraph(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#050c30")  # Set frame background color
        self.pack(fill="both", expand=True, padx=20, pady=20)

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

    def create_graph(self):
        fig, ax = plt.subplots(figsize=(12, 8))

        # Set figure and graph background colors
        fig.patch.set_facecolor("#13205f")
        ax.set_facecolor("#13205f")

        # Customize grid lines for better visibility
        ax.grid(color="#405488", linestyle="--", linewidth=0.5)

        # Plot the lines with different colors and markers
        ax.plot(self.x_values, self.body_language_score, marker='o', linestyle='-', 
                label="Body Language", color='#125282')
        ax.plot(self.x_values, self.content_score, marker='s', linestyle='-', 
                label="Content", color='#316b41')
        ax.plot(self.x_values, self.emotion_score, marker='^', linestyle='-', 
                label="Emotion", color='#781c2e')
        ax.plot(self.x_values, self.job_suitability_score, marker='d', linestyle='-', 
                label="Job Suitability", color='#663c2c')
        ax.plot(self.x_values, self.combined_score, marker='*', linestyle='-', label="Combined Score", color='#c916c9')

        # Set labels and title
        ax.set_xlabel("Session Number", color="white")
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
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")

        plt.close(fig)  # Prevent memory issues

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.geometry("900x600")  # Increased width for legend space
    app.title("M.A.I.A Performance Graph")
    app.configure(fg_color="#050c30")  # Set window background color

    graph_frame = InterviewPerformanceGraph(app)
    graph_frame.pack(fill="both", expand=True)

    app.mainloop()
