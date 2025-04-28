import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict

class VisualAttentionSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Attention Zoom Lens Model Simulation")
        self.root.geometry("1200x900")  # Increased size for better visualization
        self.root.resizable(True, True)
        self.results_df = pd.DataFrame({
        "trial": [],
        "soa": [],
        "cued_positions": [],
        "distractor_type": [],
        "distance": [],
        "rt": []
        })
        # Set style
        style = ttk.Style()
        style.theme_use('clam')  
        

        self.soa_options = [-50, 0, 50, 100, 200]  
        self.current_soa = tk.IntVar(value=0)
        self.adjacent_locations = tk.IntVar(value=1)
        self.distractor_type = tk.StringVar(value="Neutral")
        self.distance = tk.IntVar(value=1)
        self.target_letters = ["S", "C"]
        self.distractor_letters = ["A", "N", "H"]
        
        # Analysis variables
        self.results_df = pd.DataFrame(columns=["trial", "soa", "cued_positions", 
                                              "distractor_type", "distance", "rt"])
        self.current_trial = 0
        self.total_trials = 0
        self.trial_running = False
        self.automation_running = False
        
        # Create main frames
        self.create_main_layout()
        
    def create_main_layout(self):
        # Create main container frames
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create sub-components
        self.create_control_panel()
        self.create_display_area()
        self.create_results_area()
    
    def create_control_panel(self):
    # Define custom colors
        COLORS = {
            'light_blue': '#ADD8E6',
            'gold': '#FFD700',
            'magenta': '#FF00FF',
            'bittersweet': '#FE6F5E',
            'persian_red': '#C41E3A'
        }

        # Style configuration
        style = ttk.Style()
        
        style.configure('LightBlue.TButton', background=COLORS['light_blue'])
        style.configure('Gold.TButton', background=COLORS['gold'])
        style.configure('Magenta.TButton', background=COLORS['magenta'])
        style.configure('Bittersweet.TButton', background=COLORS['bittersweet'])
        style.configure('PersianRed.TButton', background=COLORS['persian_red'])

        control_frame = ttk.LabelFrame(self.left_frame, text="Experiment Controls")
        control_frame.pack(fill=tk.Y, padx=5, pady=5)
        
        manual_frame = ttk.LabelFrame(control_frame, text="Manual Controls")
        manual_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # SOA control
        ttk.Label(manual_frame, text="SOA (ms):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        soa_combo = ttk.Combobox(manual_frame, textvariable=self.current_soa,
                                values=self.soa_options, width=10)
        soa_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(manual_frame, text="Adjacent Locations:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        locations_combo = ttk.Combobox(manual_frame, textvariable=self.adjacent_locations,
                                    values=[1, 2, 3], width=10)
        locations_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(manual_frame, text="Distractor Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        distractor_combo = ttk.Combobox(manual_frame, textvariable=self.distractor_type,
                                    values=["Neutral", "Compatible", "Incompatible"], width=10)
        distractor_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Distance control
        ttk.Label(manual_frame, text="Distance:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        distance_combo = ttk.Combobox(manual_frame, textvariable=self.distance,
                                    values=[1, 2, 3], width=10)
        distance_combo.grid(row=3, column=1, padx=5, pady=5)
        
        single_trial_btn = tk.Button(
            manual_frame,
            text="Run Single Trial",
            command=self.start_single_trial,
            bg=COLORS['light_blue'],
            relief=tk.RAISED,
            borderwidth=3
        )
        single_trial_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        auto_frame = ttk.LabelFrame(control_frame, text="Automated Testing")
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(auto_frame, text="Trials per condition:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.trials_per_cond = ttk.Spinbox(auto_frame, from_=1, to=10, width=5)
        self.trials_per_cond.set(3)
        self.trials_per_cond.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(auto_frame, text="Response delay (ms):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.response_delay = ttk.Spinbox(auto_frame, from_=200, to=1000, width=5)
        self.response_delay.set(500)
        self.response_delay.grid(row=1, column=1, padx=5, pady=5)
        
        auto_test_btn = tk.Button(
            auto_frame,
            text="Run Automated Tests",
            command=self.start_automated_testing,
            bg=COLORS['gold'],
            relief=tk.RAISED,
            borderwidth=3
        )
        auto_test_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        
        stop_test_btn = tk.Button(
            auto_frame,
            text="Stop Tests",
            command=self.stop_automated_testing,
            bg=COLORS['magenta'],
            relief=tk.RAISED,
            borderwidth=3
        )
        stop_test_btn.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        reset_btn = tk.Button(
            control_frame,
            text="Reset All Data",
            command=self.reset_simulation,
            bg=COLORS['bittersweet'],
            relief=tk.RAISED,
            borderwidth=3
        )
        reset_btn.pack(fill=tk.X, padx=5, pady=15)

        help_frame = ttk.LabelFrame(control_frame, text="Information")
        help_frame.pack(fill=tk.X, padx=5, pady=5)
        
        help_text = """
        Visual Attention Zoom Lens Model
        (Eriksen & St. James, 1986)
        
        Variables:
        - SOA: -50ms to +200ms
        - Cued positions: 1-3
        - Distractor types:
        • Neutral
        • Compatible
        • Incompatible
        - Distance: 1-3
        
        Target Letters: S & C
        Distractor Letters: A, N, H
        """
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=250)
        help_label.pack(padx=5, pady=5)
    def create_display_area(self):

        self.display_frame = ttk.LabelFrame(self.right_frame, text="Visual Display")
        self.display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.display_frame, bg="white", width=600, height=400)
        self.canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.positions = []
        for row in range(3):
            for col in range(3):
                x = 200 + col * 100
                y = 100 + row * 100
                self.positions.append((x, y))
        
        self.instruction_text = self.canvas.create_text(
            300, 350,
            text="Press 'Run Single Trial' or 'Run Automated Tests'",
            font=("Arial", 12)
        )
        
        self.status_frame = ttk.Frame(self.display_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_text,
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        self.root.bind("<s>", lambda event: self.record_manual_response("S"))
        self.root.bind("<c>", lambda event: self.record_manual_response("C"))

    def create_results_area(self):
        self.results_frame = ttk.LabelFrame(self.right_frame, text="Results Analysis")
        self.results_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_plot_controls()
        
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.set_facecolor('#f0f0f0')
        self.plot = self.figure.add_subplot(111)
        self.plot.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas_plot = FigureCanvasTkAgg(self.figure, self.results_frame)
        self.canvas_plot.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas_plot, self.results_frame)
        self.toolbar.update()
        
        self.create_statistics_panel()

    def create_plot_controls(self):
        COLORS = {
            'light_blue': '#ADD8E6',
            'gold': '#FFD700',
            'magenta': '#FF00FF',
            'bittersweet': '#FE6F5E',
            'persian_red': '#C41E3A'
        }
        
        control_frame = ttk.Frame(self.results_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        plot_label = ttk.Label(
            control_frame, 
            text="Plot Type:",
            font=("Arial", 10, "bold")
        )
        plot_label.pack(side=tk.LEFT, padx=5)
        
        self.plot_type = tk.StringVar(value="RT vs SOA")
        plot_combo = ttk.Combobox(
            control_frame,
            textvariable=self.plot_type,
            values=["RT vs SOA", "RT vs Positions", "RT vs Positions & SOA"],
            width=20,
            state="readonly"
        )
        plot_combo.pack(side=tk.LEFT, padx=5)
        plot_combo.bind('<<ComboboxSelected>>', self.on_plot_type_changed)
        
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(side=tk.LEFT, padx=10)
        
        error_bars_frame = tk.Frame(options_frame, bg=COLORS['gold'], relief=tk.RAISED, bd=2)
        error_bars_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.show_error_bars = tk.BooleanVar(value=True)
        tk.Checkbutton(
            error_bars_frame,
            text="Show Error Bars",
            variable=self.show_error_bars,
            command=self.refresh_plot,
            bg=COLORS['gold'],
            activebackground=COLORS['gold'],
            font=("Arial", 9)
        ).pack(padx=3, pady=1)
        
        points_frame = tk.Frame(options_frame, bg=COLORS['light_blue'], relief=tk.RAISED, bd=2)
        points_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.show_individual_points = tk.BooleanVar(value=False)
        tk.Checkbutton(
            points_frame,
            text="Show Individual Points",
            variable=self.show_individual_points,
            command=self.refresh_plot,
            bg=COLORS['light_blue'],
            activebackground=COLORS['light_blue'],
            font=("Arial", 9)
        ).pack(padx=3, pady=1)
        
        export_frame = tk.Frame(control_frame)
        export_frame.pack(side=tk.RIGHT, padx=5)
        
        export_plot_btn = tk.Button(
            export_frame,
            text="Export Plot",
            command=self.export_plot,
            bg=COLORS['persian_red'],
            fg='white',  
            relief=tk.RAISED,
            borderwidth=2,
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2"  
        )
        export_plot_btn.pack(side=tk.RIGHT, padx=5)
        
        export_data_btn = tk.Button(
            export_frame,
            text="Export Data",
            command=self.export_data,
            bg=COLORS['magenta'],
            fg='white',  
            relief=tk.RAISED,
            borderwidth=2,
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2"  
        )
        export_data_btn.pack(side=tk.RIGHT, padx=5)
        
        def on_enter(e):
            e.widget['background'] = COLORS['bittersweet']
    
        def on_leave(e, original_color):
            e.widget['background'] = original_color
    
        export_plot_btn.bind('<Enter>', on_enter)
        export_plot_btn.bind('<Leave>', lambda e: on_leave(e, COLORS['persian_red']))
        export_data_btn.bind('<Enter>', on_enter)
        export_data_btn.bind('<Leave>', lambda e: on_leave(e, COLORS['magenta']))
        
    def on_plot_type_changed(self, event=None):
        self.refresh_plot()
    def refresh_plot(self):
        self.update_plot(self.plot_type.get())
    def create_statistics_panel(self):
        stats_frame = ttk.LabelFrame(self.results_frame, text="Statistics")
        stats_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Create text widget with scrollbar
        stats_scroll = ttk.Scrollbar(stats_frame)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=4,
            yscrollcommand=stats_scroll.set,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        stats_scroll.config(command=self.stats_text.yview)
        
        # Initialize with empty stats
        self.update_statistics()
    def start_single_trial(self):
        if not self.trial_running and not self.automation_running:
            self.current_trial += 1
            self.trial_running = True
            self.status_text.set("Trial running...")
            self.run_trial(manual_mode=True)

    def start_automated_testing(self):
        if not self.trial_running and not self.automation_running:
            self.automation_running = True
            
            # Calculate total trials
            trials_per_condition = int(self.trials_per_cond.get())
            self.total_trials = (trials_per_condition * 
                               len(self.soa_options) * 3 * 3)  # SOAs × distractor types × positions
            self.current_trial = 0
            
            self.status_text.set("Automated testing started...")
            self.progress_var.set(0)
            self.run_automated_batch()
    def run_automated_batch(self):
        if not self.automation_running:
            return
            
        try:
            # Get random parameter combinations
            soa = random.choice(self.soa_options)
            positions = random.choice([1, 2, 3])
            distractor = random.choice(["Neutral", "Compatible", "Incompatible"])
            distance = random.choice([1, 2, 3])
            
            # Set current parameters
            self.current_soa.set(soa)
            self.adjacent_locations.set(positions)
            self.distractor_type.set(distractor)
            self.distance.set(distance)
            
            # Run the trial
            self.current_trial += 1
            self.trial_running = True
            self.run_trial(manual_mode=False)
            
        except Exception as e:
            self.handle_error(f"Error in automated batch: {str(e)}")
            self.automation_running = False
    def stop_automated_testing(self):
        if self.automation_running:
            self.automation_running = False
            self.trial_running = False
            self.status_text.set("Automated testing stopped.")
            self.progress_var.set(0)

    def run_trial(self, manual_mode=True):
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Display fixation cross
            self.canvas.create_text(
                300, 200,
                text="+",
                font=("Arial", 20, "bold"),
                tags="fixation"
            )
            self.canvas.update()
            
            # Schedule next steps
            delay = 1000  # 1 second fixation
            self.root.after(delay, lambda: self.display_cue(manual_mode))
            
        except Exception as e:
            self.handle_error(f"Error in run_trial: {str(e)}")

    def display_cue(self, manual_mode):
        try:
            # Clear fixation
            self.canvas.delete("fixation")
            
            # Determine cued locations
            center_idx = 4  # Center position
            cued_positions = [center_idx]
            
            if self.adjacent_locations.get() > 1:
                potential_adjacent = [1, 3, 5, 7]  # Up, left, right, down
                selected_adjacent = random.sample(
                    potential_adjacent,
                    self.adjacent_locations.get() - 1
                )
                cued_positions.extend(selected_adjacent)
            
            # Store current cued positions
            self.current_cued_positions = cued_positions
            
            # Display cues
            for pos_idx in cued_positions:
                x, y = self.positions[pos_idx]
                self.canvas.create_rectangle(
                    x-40, y-40, x+40, y+40,
                    outline="red",
                    width=2,
                    tags="cue"
                )
            self.canvas.update()
            
            # Schedule target display based on SOA
            soa_ms = self.current_soa.get()
            delay = max(0, soa_ms)
            self.root.after(
                delay,
                lambda: self.display_target(manual_mode, cued_positions, soa_ms)
            )
            
        except Exception as e:
            self.handle_error(f"Error in display_cue: {str(e)}")

    def display_target(self, manual_mode, cued_positions, soa_ms):
        try:
            # Choose target letter and position
            self.target_letter = random.choice(self.target_letters)
            target_pos_idx = random.choice(cued_positions)
            target_x, target_y = self.positions[target_pos_idx]
            
            # Prepare distractor positions and letters
            distractor_positions = [i for i in range(9) if i not in cued_positions]
            
            # Choose distractor letters based on type
            if self.distractor_type.get() == "Compatible":
                distractor_letters = ([self.target_letter] + 
                                    random.choices(self.distractor_letters, 
                                                 k=len(distractor_positions)-1))
            elif self.distractor_type.get() == "Incompatible":
                other_target = [t for t in self.target_letters 
                              if t != self.target_letter][0]
                distractor_letters = ([other_target] + 
                                    random.choices(self.distractor_letters,
                                                 k=len(distractor_positions)-1))
            else:  # Neutral
                distractor_letters = random.choices(self.distractor_letters,
                                                  k=len(distractor_positions))
            
            random.shuffle(distractor_letters)
            
            # Display letters
            self.canvas.create_text(
                target_x, target_y,
                text=self.target_letter,
                font=("Arial", 24, "bold"),
                tags="target"
            )
            
            for i, pos_idx in enumerate(distractor_positions):
                x, y = self.positions[pos_idx]
                self.canvas.create_text(
                    x, y,
                    text=distractor_letters[i],
                    font=("Arial", 24),
                    tags="distractor"
                )
            
            # Handle negative SOA
            if soa_ms < 0:
                self.root.after(abs(soa_ms), lambda: self.canvas.delete("cue"))
            
            # Display instructions
            self.canvas.create_text(
                300, 350,
                text=f"Press '{self.target_letter}' when you see it",
                font=("Arial", 12),
                tags="instruction"
            )
            
            # Record start time
            self.start_time = time.time()
            
            if not manual_mode:
                self.simulate_automated_response()
                
        except Exception as e:
            self.handle_error(f"Error in display_target: {str(e)}")

    def simulate_automated_response(self):
        try:
            # Calculate simulated response time
            base_rt = int(self.response_delay.get())
            
            # Adjust RT based on experimental conditions
            soa_factor = 1.0 - (self.current_soa.get() + 50) / 300
            position_factor = self.adjacent_locations.get() / 3
            
            distractor_factor = {
                "Neutral": 1.0,
                "Compatible": 0.9,
                "Incompatible": 1.2
            }[self.distractor_type.get()]
            
            # Calculate final RT with randomness
            adjusted_rt = (base_rt * 
                         soa_factor * 
                         position_factor * 
                         distractor_factor * 
                         random.uniform(0.9, 1.1))
            
            self.root.after(int(adjusted_rt), self.record_automated_response)
            
        except Exception as e:
            self.handle_error(f"Error in simulate_automated_response: {str(e)}")
    def record_manual_response(self, key):
        if self.trial_running and not self.automation_running:
            if key == self.target_letter:
                rt = (time.time() - self.start_time) * 1000  # Convert to ms
                self.add_result_to_dataframe(rt)
                self.update_statistics()
                self.update_plot(self.plot_type.get())
                
            # Reset display
            self.canvas.delete("all")
            self.canvas.create_text(
                300, 200,
                text="Press 'Run Single Trial' to continue",
                font=("Arial", 12)
            )
            self.status_text.set("Trial completed.")
            self.trial_running = False

    def record_automated_response(self):
        if self.trial_running and self.automation_running:
            rt = (time.time() - self.start_time) * 1000
            self.add_result_to_dataframe(rt)
            
            # Clear canvas
            self.canvas.delete("all")
            
            # Update progress
            progress = (self.current_trial / self.total_trials) * 100
            self.progress_var.set(progress)
            self.status_text.set(
                f"Progress: {self.current_trial}/{self.total_trials} "
                f"trials ({progress:.1f}%)"
            )
            
            # Prepare for next trial
            self.trial_running = False
            
            if self.automation_running and self.current_trial < self.total_trials:
                self.root.after(500, self.run_automated_batch)
            else:
                self.automation_running = False
                self.status_text.set("Automated testing completed.")
                self.update_statistics()
                self.update_plot(self.plot_type.get())

    def add_result_to_dataframe(self, rt):
        try:
            # Create new row as a dictionary
            new_row = {
                "trial": self.current_trial,
                "soa": self.current_soa.get(),
                "cued_positions": self.adjacent_locations.get(),
                "distractor_type": self.distractor_type.get(),
                "distance": self.distance.get(),
                "rt": rt
            }
            
            # Add new row to DataFrame
            self.results_df = pd.concat([
                self.results_df, 
                pd.DataFrame([new_row])
            ], ignore_index=True)
            
        except Exception as e:
            self.handle_error(f"Error adding data to DataFrame: {str(e)}")
            print(f"Debug info - new_row: {new_row}")  # For debugging
    def update_statistics(self):
        if self.results_df.empty:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No data available yet.")
            return
        
        # Calculate statistics
        stats = []
        
        # Overall statistics
        stats.append("=== Overall Statistics ===")
        stats.append(f"Total trials: {len(self.results_df)}")
        stats.append(f"Mean RT: {self.results_df['rt'].mean():.2f} ms")
        stats.append(f"SD RT: {self.results_df['rt'].std():.2f} ms")
        
        # Statistics by condition
        for factor in ['soa', 'cued_positions', 'distractor_type']:
            stats.append(f"\n=== RT by {factor} ===")
            grouped = self.results_df.groupby(factor)['rt'].agg(['mean', 'std', 'count'])
            for idx, row in grouped.iterrows():
                stats.append(
                    f"{idx}: {row['mean']:.2f} ms (SD={row['std']:.2f}, n={row['count']})"
                )
        
        # Update text widget
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats))

    def update_plot(self, plot_type):
        try:
            if self.results_df.empty:
                self.show_no_data_message()
                return
            
            # Clear the current plot
            self.plot.clear()
            
            # Set style parameters without using seaborn
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
            
            if plot_type == "RT vs SOA":
                self._plot_rt_vs_soa(colors)
            elif plot_type == "RT vs Positions":
                self._plot_rt_vs_positions(colors)
            elif plot_type == "RT vs Positions & SOA":
                self._plot_rt_vs_positions_soa(colors)
            
            self.figure.tight_layout()
            self.canvas_plot.draw()
            
        except Exception as e:
            self.handle_error(f"Error updating plot: {str(e)}")
            
    def _plot_rt_vs_positions_soa(self, colors):
        # Create subplot grid
        self.figure.clear()
        
        # Get unique SOA values
        soa_values = sorted(self.results_df['soa'].unique())
        
        # Calculate grid size
        n_plots = len(soa_values)
        n_cols = min(3, n_plots)
        n_rows = (n_plots + n_cols - 1) // n_cols
        
        for i, soa in enumerate(soa_values):
            ax = self.figure.add_subplot(n_rows, n_cols, i+1)
            
            # Filter data for this SOA
            soa_data = self.results_df[self.results_df['soa'] == soa]
            grouped = soa_data.groupby(['cued_positions', 'distractor_type'])['rt'].mean().reset_index()
            
            for j, distractor in enumerate(['Neutral', 'Compatible', 'Incompatible']):
                data = grouped[grouped['distractor_type'] == distractor]
                if not data.empty:
                    ax.plot(data['cued_positions'], data['rt'],
                        color=colors[j], marker='o', label=distractor)
            
            ax.set_title(f'SOA = {soa} ms')
            ax.set_xlabel('Cued Positions')
            ax.set_ylabel('RT (ms)')
            ax.set_xticks([1, 2, 3])
            ax.grid(True, linestyle='--', alpha=0.7)
            
            if i == 0:
                ax.legend()
        
        self.figure.suptitle('RT vs Cued Positions across SOA Values')
        self.figure.tight_layout()

    def show_no_data_message(self):
        self.plot.clear()
        self.plot.text(0.5, 0.5, 
                    "No data available.\nRun some trials to generate plots.",
                    ha='center', va='center', transform=self.plot.transAxes)
        self.canvas_plot.draw()
    def _plot_rt_vs_soa(self, colors):
        self.figure.clear()
        self.plot = self.figure.add_subplot(111)
        
        grouped = self.results_df.groupby(['soa', 'distractor_type'])
        means = grouped['rt'].mean().reset_index()
        sems = grouped['rt'].sem().reset_index() if self.show_error_bars.get() else None
        
        for i, distractor in enumerate(['Neutral', 'Compatible', 'Incompatible']):
            data = means[means['distractor_type'] == distractor]
            
            # Plot mean line
            self.plot.plot(
                data['soa'], data['rt'],
                color=colors[i], marker='o',
                label=distractor, linewidth=2
            )
            
            # Add error bars
            if self.show_error_bars.get():
                err_data = sems[sems['distractor_type'] == distractor]
                self.plot.fill_between(
                    data['soa'],
                    data['rt'] - err_data['rt'],
                    data['rt'] + err_data['rt'],
                    color=colors[i], alpha=0.2
                )
            
            # Add individual points
            if self.show_individual_points.get():
                individual_data = self.results_df[
                    self.results_df['distractor_type'] == distractor
                ]
                self.plot.scatter(
                    individual_data['soa'],
                    individual_data['rt'],
                    color=colors[i], alpha=0.2, s=20
                )
        
        self.plot.set_title("Reaction Time vs SOA by Distractor Type")
        self.plot.set_xlabel("Stimulus Onset Asynchrony (ms)")
        self.plot.set_ylabel("Reaction Time (ms)")
        self.plot.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.plot.grid(True, linestyle='--', alpha=0.7)

    def _plot_rt_vs_positions(self, colors):
        self.figure.clear()
        self.plot = self.figure.add_subplot(111)
        
        grouped = self.results_df.groupby(['cued_positions', 'distractor_type'])
        means = grouped['rt'].mean().reset_index()
        sems = grouped['rt'].sem().reset_index() if self.show_error_bars.get() else None
        
        for i, distractor in enumerate(['Neutral', 'Compatible', 'Incompatible']):
            data = means[means['distractor_type'] == distractor]
            
            self.plot.plot(
                data['cued_positions'], data['rt'],
                color=colors[i], marker='o',
                label=distractor, linewidth=2
            )
            
            if self.show_error_bars.get():
                err_data = sems[sems['distractor_type'] == distractor]
                self.plot.fill_between(
                    data['cued_positions'],
                    data['rt'] - err_data['rt'],
                    data['rt'] + err_data['rt'],
                    color=colors[i], alpha=0.2
                )
            
            if self.show_individual_points.get():
                individual_data = self.results_df[
                    self.results_df['distractor_type'] == distractor
                ]
                self.plot.scatter(
                    individual_data['cued_positions'],
                    individual_data['rt'],
                    color=colors[i], alpha=0.2, s=20
                )
        
        self.plot.set_title("Reaction Time vs Number of Cued Positions")
        self.plot.set_xlabel("Number of Cued Positions")
        self.plot.set_ylabel("Reaction Time (ms)")
        self.plot.set_xticks([1, 2, 3])
        self.plot.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.plot.grid(True, linestyle='--', alpha=0.7)

    def _plot_rt_vs_positions_soa(self, colors):
        self.figure.clear()
        
        soa_values = sorted(self.results_df['soa'].unique())
        n_plots = len(soa_values)
        n_cols = min(3, n_plots)
        n_rows = (n_plots + n_cols - 1) // n_cols
        
        axes = []
        for i, soa in enumerate(soa_values, 1):
            ax = self.figure.add_subplot(n_rows, n_cols, i)
            axes.append(ax)
            
            soa_data = self.results_df[self.results_df['soa'] == soa]
            grouped = soa_data.groupby(['cued_positions', 'distractor_type'])['rt'].mean().reset_index()
            
            for j, distractor in enumerate(['Neutral', 'Compatible', 'Incompatible']):
                data = grouped[grouped['distractor_type'] == distractor]
                if not data.empty:
                    ax.plot(data['cued_positions'], data['rt'],
                        color=colors[j], marker='o', label=distractor)
            
            ax.set_title(f'SOA = {soa} ms')
            ax.set_xlabel('Cued Positions')
            ax.set_ylabel('RT (ms)')
            ax.set_xticks([1, 2, 3])
            ax.grid(True, linestyle='--', alpha=0.7)
            
            if i == 1:  # Only show legend for the first subplot
                ax.legend()
        
        self.figure.suptitle('RT vs Cued Positions across SOA Values')
        self.figure.tight_layout()
        
        # Store the current subplot for future reference
        self.plot = axes[0] if axes else None
    def export_plot(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg")
                ]
            )
            if file_path:
                self.figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight'
                )
                messagebox.showinfo(
                    "Success",
                    "Plot exported successfully!"
                )
        except Exception as e:
            self.handle_error(f"Failed to export plot: {str(e)}")

    def export_data(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if file_path:
                self.results_df.to_csv(file_path, index=False)
                messagebox.showinfo(
                    "Success",
                    "Data exported successfully!"
                )
        except Exception as e:
            self.handle_error(f"Failed to export data: {str(e)}")

    def handle_error(self, message):
        messagebox.showerror("Error", message)
        self.status_text.set("Error occurred. Check error message.")
        print(f"Error: {message}")  # For debugging

    def reset_simulation(self):
        # Reset all variables
        self.current_trial = 0
        
        # Reset DataFrame
        self.results_df = pd.DataFrame({
            "trial": [],
            "soa": [],
            "cued_positions": [],
            "distractor_type": [],
            "distance": [],
            "rt": []
        })
        
        # Stop ongoing processes
        self.automation_running = False
        self.trial_running = False
        
        # Reset display
        self.canvas.delete("all")
        self.canvas.create_text(
            300, 200,
            text="Press 'Run Single Trial' or 'Run Automated Tests'",
            font=("Arial", 12)
        )
        
        # Reset progress and status
        self.progress_var.set(0)
        self.status_text.set("Ready - Data reset")
        
        # Clear statistics and plot
        self.update_statistics()
        self.update_plot(self.plot_type.get())
    def update_statistics(self):
        if self.results_df.empty:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No data available yet.")
            return
        
        # Calculate statistics
        stats = []
        
        # Overall statistics
        stats.append("=== Overall Statistics ===")
        stats.append(f"Total trials: {len(self.results_df)}")
        stats.append(f"Mean RT: {self.results_df['rt'].mean():.2f} ms")
        stats.append(f"SD RT: {self.results_df['rt'].std():.2f} ms")
        
        # Statistics by condition
        for factor in ['soa', 'cued_positions', 'distractor_type']:
            stats.append(f"\n=== RT by {factor} ===")
            grouped = self.results_df.groupby(factor)['rt'].agg(['mean', 'std', 'count'])
            for idx, row in grouped.iterrows():
                stats.append(
                    f"{idx}: {row['mean']:.2f} ms (SD={row['std']:.2f}, n={row['count']})"
                )
        
        # Update text widget
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats))
if __name__ == "__main__":
    root = tk.Tk()
    
    app = VisualAttentionSimulation(root)
    root.mainloop()