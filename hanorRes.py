import tkinter as tk
from tkinter import messagebox

class TowerOfHanoi:
    def __init__(self, root):
        self.root = root
        self.root.title("टॉवर ऑफ हनोई")
        
        self.canvas = tk.Canvas(root, width=400, height=300)
        self.canvas.pack()

        self.towers = [[], [], []]
        self.disks = [3, 2, 1]  # Disk sizes
        self.colors = ["#FF4500", "#FFD700", "#87CEEB"]  # Disk colors

        for i, size in enumerate(self.disks):
            self.towers[0].append(size)
            self.draw_disk(0, i, size)

        self.selected_tower = None
        self.canvas.bind("<Button-1>", self.select_tower)

    def draw_disk(self, tower, position, size):
        x0 = 50 + tower * 150 - size * 10
        y0 = 250 - position * 20
        x1 = 50 + tower * 150 + size * 10
        y1 = 270 - position * 20
        color = self.colors[size - 1]
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def select_tower(self, event):
        tower = event.x // 150
        if self.selected_tower is None:
            if self.towers[tower]:
                self.selected_tower = tower
        else:
            if self.move_disk(self.selected_tower, tower):
                self.selected_tower = None
                self.canvas.delete("all")
                for t in range(3):
                    for p, size in enumerate(self.towers[t]):
                        self.draw_disk(t, p, size)
                if len(self.towers[2]) == 3:
                    messagebox.showinfo("सफलता", "आपने खेल को सफलतापूर्वक पूरा कर लिया है!")
            else:
                self.selected_tower = None

    def move_disk(self, from_tower, to_tower):
        if self.towers[from_tower]:
            disk = self.towers[from_tower][-1]
            if not self.towers[to_tower] or self.towers[to_tower][-1] > disk:
                self.towers[from_tower].pop()
                self.towers[to_tower].append(disk)
                return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    game = TowerOfHanoi(root)
    root.mainloop()