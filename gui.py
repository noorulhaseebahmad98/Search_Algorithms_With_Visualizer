import tkinter as tk
from tkinter import ttk, messagebox
import search_algorithms
import time

class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizer Algo")
        
        # Grid Settings
        self.ROWS = 20
        self.COLS = 20
        self.CELL_SIZE = 25
        self.grid_size = (self.ROWS, self.COLS)
        
        # Colors
        self.COLOR_EMPTY = "white"
        self.COLOR_WALL = "black"
        self.COLOR_START = "orange"
        self.COLOR_GOAL = "purple"
        self.COLOR_FRONTIER = "cyan"
        self.COLOR_EXPLORED = "lightgray"
        self.COLOR_PATH = "green"
        self.COLOR_CURRENT = "yellow"
        
        # State
        self.start_pos = (0, 0)
        self.goal_pos = (self.ROWS - 1, self.COLS - 1)
        self.walls = set()
        self.running = False
        self.generator = None
        self.delay_ms = 50
        
        # UI Setup
        self.setup_ui()
        self.draw_grid()

    def setup_ui(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(control_frame, text="Algorithm:").pack(pady=5)
        self.algo_var = tk.StringVar(value="BFS")
        algo_options = ["BFS", "DFS", "UCS", "DLS", "IDDFS", "Bidirectional"]
        menu = ttk.OptionMenu(control_frame, self.algo_var, "BFS", *algo_options)
        menu.pack(pady=5)
        
        ttk.Button(control_frame, text="Run Search", command=self.run_search).pack(pady=10)
        ttk.Button(control_frame, text="Reset", command=self.reset_visualization).pack(pady=5)
        
        ttk.Label(control_frame, text="Speed (ms):").pack(pady=5)
        self.speed_scale = ttk.Scale(control_frame, from_=10, to=500, value=50, orient=tk.HORIZONTAL)
        self.speed_scale.pack(pady=5)
        
        ttk.Label(control_frame, text="Status:").pack(pady=10)
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(pady=5)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.COLS*self.CELL_SIZE, height=self.ROWS*self.CELL_SIZE, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bindings
        self.canvas.bind("<Button-1>", self.on_click) 
        self.canvas.bind("<Button-3>", self.on_right_click)

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x1 = c * self.CELL_SIZE
                y1 = r * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                
                color = self.COLOR_EMPTY
                if (r, c) == self.start_pos:
                    color = self.COLOR_START
                elif (r, c) == self.goal_pos:
                    color = self.COLOR_GOAL
                elif (r, c) in self.walls:
                    color = self.COLOR_WALL
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray", tags=f"cell_{r}_{c}")

    def update_cell_color(self, r, c, color):
        if (r, c) == self.start_pos or (r, c) == self.goal_pos:
            return # Don't overwrite start/goal
        self.canvas.itemconfig(f"cell_{r}_{c}", fill=color)

    def on_click(self, event):
        r, c = event.y // self.CELL_SIZE, event.x // self.CELL_SIZE
        if 0 <= r < self.ROWS and 0 <= c < self.COLS:
            if (r, c) != self.goal_pos:
                self.start_pos = (r, c)
                self.draw_grid()

    def on_right_click(self, event):
        r, c = event.y // self.CELL_SIZE, event.x // self.CELL_SIZE
        if 0 <= r < self.ROWS and 0 <= c < self.COLS:
            if (r, c) != self.start_pos:
                self.goal_pos = (r, c)
                self.draw_grid()

    def run_search(self):
        if self.running:
            return
        
        algo = self.algo_var.get()
        self.reset_visualization()
        self.running = True
        self.status_label.config(text=f"Running {algo}...")
        
        if algo == "BFS":
            self.generator = search_algorithms.bfs_step(self.start_pos, self.goal_pos, self.grid_size)
        elif algo == "DFS":
            self.generator = search_algorithms.dfs_step(self.start_pos, self.goal_pos, self.grid_size)
        elif algo == "UCS":
            self.generator = search_algorithms.ucs_step(self.start_pos, self.goal_pos, self.grid_size)
        elif algo == "DLS":
            self.generator = search_algorithms.dls_step(self.start_pos, self.goal_pos, self.grid_size, limit=50) 
        elif algo == "IDDFS":
            self.generator = search_algorithms.iddfs_step(self.start_pos, self.goal_pos, self.grid_size)
        elif algo == "Bidirectional":
            self.generator = search_algorithms.bidirectional_search_step(self.start_pos, self.goal_pos, self.grid_size)
            
        self.step_search()

    def step_search(self):
        if not self.running:
            return

        try:
            event = next(self.generator)
            
            if event['type'] == 'step':
                if 'explored' in event:
                    for r, c in event['explored']:
                        self.update_cell_color(r, c, self.COLOR_EXPLORED)
                
                if 'frontier' in event:
                    for r, c in event['frontier']:
                        self.update_cell_color(r, c, self.COLOR_FRONTIER)
                    
                if event.get('current'):
                    r, c = event['current']
                    self.update_cell_color(r, c, self.COLOR_CURRENT)

                self.root.after(int(self.speed_scale.get()), self.step_search)
                    
            elif event['type'] == 'path':
                self.running = False
                path = event['path']
                if path is not None:
                    self.display_path_result(path)
                    self.status_label.config(text="Goal Reached!")
                else:
                    self.status_label.config(text="No Path Found")
            
            elif event['type'] == 'log':
                self.root.after(10, self.step_search)
            
        except StopIteration:
            self.running = False
            self.status_label.config(text="Finished")

    def display_path_result(self, actions):
         r, c = self.start_pos
         moves = {
            "Up": (-1, 0),
            "Right": (0, 1),
            "Bottom": (1, 0),
            "Bottom-Right": (1, 1),
            "Left": (0, -1),
            "Top-Left": (-1, -1)
         }
         
         if actions:
             for action in actions:
                 if action in moves:
                    dr, dc = moves[action]
                    r, c = r + dr, c + dc
                    if (r, c) != self.goal_pos:
                        self.update_cell_color(r, c, self.COLOR_PATH)

    def reset_visualization(self):
        self.running = False
        self.generator = None
        self.draw_grid()
        self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchGUI(root)
    root.mainloop()
