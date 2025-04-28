import tkinter as tk
from tkinter import messagebox
import json
import random

class NumberGuessingGame:
    def __init__(self, master):
        self.master = master
        master.title("Number Guessing Game")
        
        # Overall layout: game area left, sidebar right
        self.game_frame = tk.Frame(master, padx=10, pady=10)
        self.game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sidebar_frame = tk.Frame(master, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Sidebar components (daayen taraf)
        tk.Label(self.sidebar_frame, text="Enter Name:", font=("Arial", 12)).pack(pady=5)
        self.name_entry = tk.Entry(self.sidebar_frame, font=("Arial", 12))
        self.name_entry.pack(pady=5)
        
        tk.Label(self.sidebar_frame, text="Select Difficulty:", font=("Arial", 12)).pack(pady=5)
        self.difficulty = tk.StringVar(value="Easy")
        for text in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(self.sidebar_frame, text=text, variable=self.difficulty, value=text, font=("Arial", 12)).pack(anchor=tk.W)
        
        self.save_button = tk.Button(self.sidebar_frame, text="Save Settings", bg="red", fg="blue", font=("Arial", 12), command=self.save_settings)
        self.save_button.pack(pady=10)
        
        # Game area components (baaye taraf)
        self.header = tk.Label(self.game_frame, text="Minhaas's Number Guessing Game", font=("Arial", 16, "bold"), fg="green")
        self.header.pack(pady=10)
        
        # Start button to initiate game
        self.start_button = tk.Button(self.game_frame, text="Start", bg="green", fg="white", font=("Arial", 14), command=self.start_game)
        self.start_button.pack(pady=5)
        
        # Label for showing the guessing range (displayed after game starts)
        self.range_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        
        # Controls frame for guess input, check guess, reset (initially hidden)
        self.controls_frame = tk.Frame(self.game_frame)
        self.guess_entry = tk.Entry(self.controls_frame, font=("Arial", 12))
        self.guess_button = tk.Button(self.controls_frame, text="Check Guess", font=("Arial", 12), command=self.check_guess)
        self.reset_button = tk.Button(self.controls_frame, text="Reset", font=("Arial", 12), command=self.reset_game)
        
        # Feedback label to show messages
        self.feedback_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        
        # Progress bar (hidden initially)
        self.progress_canvas = tk.Canvas(self.game_frame, width=300, height=20, bg="lightgrey")
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 300, 20, fill="green")
        
        # Game settings variables
        self.user_name = ""
        self.total_attempts = 10  # Default for Easy
        self.remaining_attempts = 10
        self.target_number = None
        
    def save_settings(self):
        """User ka naam aur difficulty save karta hai."""
        self.user_name = self.name_entry.get().strip()
        if not self.user_name:
            messagebox.showerror("Error", "Please enter your name.")
            return
        messagebox.showinfo("Settings Saved", f"Settings saved for {self.user_name} with difficulty {self.difficulty.get()}.")
    
    def start_game(self):
        """Difficulty ke hisaab se game parameters set karke game shuru karta hai."""
        diff = self.difficulty.get()
        if diff == "Easy":
            self.total_attempts = 10
            self.target_number = random.randint(1, 50)
            range_text = "Guess a number between 1 and 50."
        elif diff == "Medium":
            self.total_attempts = 7
            self.target_number = random.randint(1, 100)
            range_text = "Guess a number between 1 and 100."
        elif diff == "Hard":
            self.total_attempts = 5
            self.target_number = random.randint(1, 150)
            range_text = "Guess a number between 1 and 150."
        else:
            self.total_attempts = 10
            self.target_number = random.randint(1, 50)
            range_text = "Guess a number between 1 and 50."
        
        self.remaining_attempts = self.total_attempts
        
        # Hide start button and show range info and controls
        self.start_button.pack_forget()
        self.range_label.config(text=range_text)
        self.range_label.pack(pady=5)
        
        self.controls_frame.pack(pady=5)
        self.guess_entry.pack(side=tk.LEFT, padx=5)
        self.guess_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.feedback_label.config(text="")
        self.feedback_label.pack(pady=5)
        
        # Show progress bar only after game starts
        self.progress_canvas.pack(pady=10)
        self.update_progress()
    
    def check_guess(self):
        """User ke guess ko target number se compare karke feedback deta hai."""
        try:
            guess = int(self.guess_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")
            return
        
        if guess == self.target_number:
            self.feedback_label.config(text=f"Congratulations {self.user_name}! You guessed correctly with {self.remaining_attempts} attempts remaining.", fg="green")
            self.save_score()
            self.guess_button.config(state=tk.DISABLED)
            self.guess_entry.config(state=tk.DISABLED)
        else:
            if guess < self.target_number:
                self.feedback_label.config(text="Too low!", fg="red")
            else:
                self.feedback_label.config(text="Too high!", fg="red")
            self.remaining_attempts -= 1
            self.update_progress()
            
            if self.remaining_attempts <= 0:
                self.feedback_label.config(text=f"Game Over! The number was {self.target_number}.", fg="red")
                self.guess_button.config(state=tk.DISABLED)
                self.guess_entry.config(state=tk.DISABLED)
    
    def update_progress(self):
        """Bache hue attempts ke hisaab se progress bar update karta hai."""
        ratio = self.remaining_attempts / self.total_attempts
        new_width = int(300 * ratio)
        # Green se red ki taraf linear interpolation
        red_val = int((1 - ratio) * 255)
        green_val = int(ratio * 255)
        color = f"#{red_val:02x}{green_val:02x}00"
        self.progress_canvas.coords(self.progress_bar, 0, 0, new_width, 20)
        self.progress_canvas.itemconfig(self.progress_bar, fill=color)
    
    def reset_game(self):
        """Game ko initial state mein reset karta hai."""
        # Hide controls, range info, and progress bar; then show start button again
        self.controls_frame.pack_forget()
        self.range_label.pack_forget()
        self.progress_canvas.pack_forget()
        self.guess_entry.delete(0, tk.END)
        self.guess_button.config(state=tk.NORMAL)
        self.guess_entry.config(state=tk.NORMAL)
        self.start_button.pack(pady=5)
        self.feedback_label.config(text="")
        self.remaining_attempts = self.total_attempts

    def save_score(self):
        """User ke score ko JSON file mein save karta hai."""
        score_data = {
            "name": self.user_name,
            "score": self.remaining_attempts,
            "difficulty": self.difficulty.get()
        }
        try:
            with open("game_scores.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append(score_data)
        with open("game_scores.json", "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Score Saved", "Your score has been saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()