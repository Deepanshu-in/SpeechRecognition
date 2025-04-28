import tkinter as tk
from tkinter import messagebox
import json, threading, os

DATA_FILE = 'friends.json'

# Load friends from file
def load_friends():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print("File load mein truti:", e)
    return []

# Save friends list asynchronously
def save_friends(friends):
    def save():
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(friends, f, indent=4)
        except Exception as e:
            print("File save mein truti:", e)
    threading.Thread(target=save).start()

class MitraPrabandhakTkinter:
    def __init__(self, master):
        self.master = master
        self.master.title("Mitra Prabandhak - Tkinter")

        # Load friends list
        self.sampurn_mitra = load_friends()  
        self.chhanti_mitra = self.sampurn_mitra.copy()  

        self.frame = tk.Frame(master)
        self.frame.pack(padx=10, pady=10)

        # Search bar
        self.khoj_label = tk.Label(self.frame, text="Mitra Khoj:")
        self.khoj_label.pack()
        self.khoj_entry = tk.Entry(self.frame, width=40)
        self.khoj_entry.pack(pady=5)
        self.khoj_entry.bind("<KeyRelease>", self.update_filter)  # Update list on typing

        # Listbox to display friends
        self.suchibox = tk.Listbox(self.frame, width=40, height=10)
        self.suchibox.pack()

        # Input for adding new friends
        self.jod_label = tk.Label(self.frame, text="Naya Mitra Jodne:")
        self.jod_label.pack()
        self.jod_entry = tk.Entry(self.frame, width=40)
        self.jod_entry.pack(pady=5)

        # Buttons for adding and removing friends
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(pady=5)
        self.jod_button = tk.Button(self.button_frame, text="Mitra Jodo", command=self.add_mitra)
        self.jod_button.pack(side=tk.LEFT, padx=5)
        self.hatao_button = tk.Button(self.button_frame, text="Mitra Hatao", command=self.remove_mitra)
        self.hatao_button.pack(side=tk.LEFT, padx=5)

        self.refresh_listbox()

    # Update friend list based on search query
    def update_filter(self, event=None):
        query = self.khoj_entry.get().strip().lower()
        self.chhanti_mitra = [m for m in self.sampurn_mitra if query in m.lower()] if query else self.sampurn_mitra.copy()
        self.refresh_listbox()

    # Refresh listbox display
    def refresh_listbox(self):
        self.suchibox.delete(0, tk.END)
        for mitra in self.chhanti_mitra:
            self.suchibox.insert(tk.END, mitra)

    # Add new friend
    def add_mitra(self):
        mitra_naam = self.jod_entry.get().strip()
        if not mitra_naam:
            messagebox.showerror("Pravesh Truti", "Mitra naam khaali nahin ho sakta!")
            return
        if mitra_naam in self.sampurn_mitra:
            messagebox.showerror("Dohrav Truti", "Mitra pahle se maujood hai!")
            return
        self.sampurn_mitra.append(mitra_naam)
        save_friends(self.sampurn_mitra)
        self.jod_entry.delete(0, tk.END)
        self.update_filter()

    # Remove selected friend
    def remove_mitra(self):
        try:
            selected_index = self.suchibox.curselection()[0]  # Get selected index
            mitra_naam = self.suchibox.get(selected_index)
            self.sampurn_mitra.remove(mitra_naam)
            save_friends(self.sampurn_mitra)
            self.update_filter()
        except IndexError:
            messagebox.showerror("Chayan Truti", "Koi mitra chayan nahin hua hai!")

# Initialize Tkinter window
if __name__ == '__main__':
    root = tk.Tk()
    app = MitraPrabandhakTkinter(root)
    root.mainloop()