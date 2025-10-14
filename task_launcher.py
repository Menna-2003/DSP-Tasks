import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os


class TaskLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("DSP Tasks Launcher")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")
        
        # Center the window
        self.center_window()
        
        # Create the main interface
        self.create_interface()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_interface(self):
        """Create the main interface"""
        # Title
        title_frame = tk.Frame(self.root, bg="#f0f0f0")
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="DSP Tasks Launcher", 
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Choose a task to run:",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Main buttons frame
        buttons_frame = tk.Frame(self.root, bg="#f0f0f0")
        buttons_frame.pack(pady=30, padx=50, fill="both", expand=True)
        
        # Task 1 Button
        self.create_task_button(
            buttons_frame,
            "Task 1: Signal Processing UI",
            "Signal addition, subtraction, multiplication, shifting, and folding operations",
            self.run_task1,
            "#3498db"
        )
        
        # Spacing
        tk.Frame(buttons_frame, height=20, bg="#f0f0f0").pack()
        
        # Task 2 Button
        self.create_task_button(
            buttons_frame,
            "Task 2: Signal Generation Framework",
            "Generate and visualize sine/cosine signals with sampling theorem validation",
            self.run_task2,
            "#e74c3c"
        )
        
        # Status frame
        status_frame = tk.Frame(self.root, bg="#f0f0f0")
        status_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to launch tasks",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#27ae60"
        )
        self.status_label.pack()
    
    def create_task_button(self, parent, title, description, command, color):
        """Create a styled task button with description"""
        # Button frame
        button_frame = tk.Frame(parent, bg="#f0f0f0", relief="raised", bd=1)
        button_frame.pack(fill="x", pady=5)
        
        # Button
        button = tk.Button(
            button_frame,
            text=title,
            font=("Arial", 14, "bold"),
            bg=color,
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=15,
            command=command,
            cursor="hand2"
        )
        button.pack(fill="x", padx=2, pady=2)
        
        # Description
        desc_label = tk.Label(
            button_frame,
            text=description,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e",
            wraplength=400,
            justify="center"
        )
        desc_label.pack(pady=(0, 10))
        
        # Hover effects
        def on_enter(event):
            button.config(bg=self.darken_color(color))
        
        def on_leave(event):
            button.config(bg=color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        color_map = {
            "#3498db": "#2980b9",  # Blue
            "#e74c3c": "#c0392b"   # Red
        }
        return color_map.get(color, color)
    
    def update_status(self, message, color="#27ae60"):
        """Update the status label"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def run_task1(self):
        """Run Task1.py"""
        self.update_status("Launching Task 1...", "#3498db")
        
        try:
            # Check if Task1.py exists
            if not os.path.exists("Task1.py"):
                messagebox.showerror("Error", "Task1.py not found in the current directory!")
                self.update_status("Task 1 not found", "#e74c3c")
                return
            
            # Run Task1.py in a new process
            subprocess.Popen([sys.executable, "Task1.py"])
            self.update_status("Task 1 launched successfully", "#27ae60")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Task 1:\n{str(e)}")
            self.update_status("Failed to launch Task 1", "#e74c3c")
    
    def run_task2(self):
        """Run task2.py"""
        self.update_status("Launching Task 2...", "#e74c3c")
        
        try:
            # Check if task2.py exists
            if not os.path.exists("task2.py"):
                messagebox.showerror("Error", "task2.py not found in the current directory!")
                self.update_status("Task 2 not found", "#e74c3c")
                return
            
            # Run task2.py in a new process
            subprocess.Popen([sys.executable, "task2.py"])
            self.update_status("Task 2 launched successfully", "#27ae60")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Task 2:\n{str(e)}")
            self.update_status("Failed to launch Task 2", "#e74c3c")


def main():
    """Main function to run the launcher"""
    try:
        root = tk.Tk()
        app = TaskLauncher(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting launcher: {e}")
        messagebox.showerror("Error", f"Failed to start launcher:\n{str(e)}")


if __name__ == "__main__":
    main()
