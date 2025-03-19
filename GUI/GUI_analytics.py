import customtkinter as ctk
import matplotlib.pyplot as plt
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import clear_screen  # Avoid circular imports
from sqlite import get_recent_and_best_score  # Fetch scores dynamically


BG_COLOR = "#050c30"
BUTTON_COLOR = "#1e3a8a"

def create_analytics_screen(master, back_to_main):
    """Creates the analytics screen displaying performance graphs."""
    clear_screen(master)
    graph_frame = InterviewPerformanceGraph(master, back_to_main)
    graph_frame.pack(fill="both", expand=True)

class InterviewPerformanceGraph(ctk.CTkFrame):
    def __init__(self, master, back_to_main, db_name="maia_scores.db"):
        super().__init__(master, fg_color=BG_COLOR)
        self.db_name = db_name
        self.back_to_main = back_to_main  # Store reference to main screen function
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_data()
        self.create_graph()
        self.create_buttons()

    def load_data(self):
        """Fetches session numbers and scores from the database."""
        self.x_values = []
        self.scores = {
            "Body Language": [],
            "Content Analysis": [],
            "Emotion Detection": [],
            "Job Suitability": [],
            "Overall": []
        }

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        tables = {
            "Body Language": "body_language",
            "Content Analysis": "content_analysis",
            "Emotion Detection": "emotion_detection",
            "Job Suitability": "job_suitability",
            "Overall": "overall"
        }

        for key, table in tables.items():
            cursor.execute(f"SELECT session_no, score FROM {table} ORDER BY session_no ASC")
            rows = cursor.fetchall()
            
            if rows:
                if not self.x_values:
                    self.x_values = [row[0] for row in rows]
                self.scores[key] = [row[1] for row in rows]

        connection.close()

    def create_graph(self):
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor("#13205f")
        ax.set_facecolor("#13205f")
        ax.grid(color="#405488", linestyle="--", linewidth=0.5)

        plot_styles = {
            "Body Language": ('o', '#125282'),
            "Content Analysis": ('s', '#316b41'),
            "Emotion Detection": ('^', '#781c2e'),
            "Job Suitability": ('d', '#663c2c'),
            "Overall": ('*', '#c916c9')
        }

        data_plotted = False  # Flag to check if any data exists

        for key, (marker, color) in plot_styles.items():
            y_values = self.scores.get(key, [])
            if y_values:
                x_values = list(range(1, len(y_values) + 1))  # Ensure whole number x-axis
                ax.plot(x_values, y_values, marker=marker, linestyle='-',
                        label=key, color=color, linewidth=2 if key == "Overall" else 1)
                data_plotted = True

        # ✅ Set Y-axis limit to 0–100
        ax.set_ylim(0, 100)

        if data_plotted:
            ax.set_xlabel("Session Index", color="white")
            ax.set_ylabel("Score (%)", color="white")
            ax.set_title("Interview Performance Over Time", color="white")

            # ✅ Ensure whole numbers on the X-axis
            ax.set_xticks(range(1, len(self.x_values) + 1))  # Ensures x-axis stays whole numbers

            legend = ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), facecolor="#13205f", edgecolor="white", fontsize=10)
            for text in legend.get_texts():
                text.set_color("white")

            ax.tick_params(axis='x', colors="white")
            ax.tick_params(axis='y', colors="white")

            fig.tight_layout()
        else:
            ax.text(0.5, 0.5, "No Data Available", fontsize=20, color="white", ha="center", va="center")
            ax.set_xticks([])  # Remove ticks if no data
            ax.set_yticks([])

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor="center")
        plt.close(fig)

    def create_buttons(self):
        """Creates navigation and reset buttons."""
        back_button = ctk.CTkButton(self, text="Back", fg_color=BUTTON_COLOR, text_color="white",
                                    hover_color="#3b5998", font=("Segoe UI", 18), corner_radius=20,
                                    width=300, height=40, command=self.go_back)
        back_button.place(relx=0.5, rely=0.85, anchor="center")

        reset_button = ctk.CTkButton(self, text="Reset Scores", fg_color=BUTTON_COLOR, text_color="white",
                                     hover_color="#3b5998", font=("Segoe UI", 18), corner_radius=20,
                                     width=300, height=40, command=self.reset_all_scores)
        reset_button.place(relx=0.5, rely=0.93, anchor="center")

    def go_back(self):
        """Returns to the main screen with updated scores."""
        recent_score, best_score = get_recent_and_best_score("overall")
        self.back_to_main(self.master)

    def reset_all_scores(self):
        """Resets scores in the database."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        tables = ["content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"]

        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

        connection.commit()
        connection.close()
        self.load_data()
        self.create_graph()
