"""
GUI Interface for G-Code Radio
Simple graphical interface using tkinter for easier user interaction
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

from src.utils.logger import Logger
from src.utils.error_handler import handle_error, GCodeRadioException

logger = Logger.get_logger(__name__)


class GCodeRadioGUI:
    """Graphical user interface for G-Code Radio"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("G-Code Radio - 3D Printer Music Player")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar(value="output/music.gcode")
        self.speed_var = tk.DoubleVar(value=1.0)
        self.pitch_var = tk.IntVar(value=0)
        self.complexity_var = tk.IntVar(value=50)
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(
            header_frame,
            text="🎵 G-Code Radio 🖨️",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=5)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Convert music to 3D printer G-code",
            font=("Arial", 10)
        )
        subtitle_label.grid(row=1, column=0)
        
        # Main content frame
        content_frame = ttk.Frame(self.root, padding="10")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Input section
        input_frame = ttk.LabelFrame(content_frame, text="Input", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="YouTube URL or Audio File:").grid(row=0, column=0, sticky=tk.W)
        
        input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=60)
        input_entry.grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Browse File", command=self.browse_input).grid(row=1, column=1)
        
        # Output section
        output_frame = ttk.LabelFrame(content_frame, text="Output", padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="Output G-code File:").grid(row=0, column=0, sticky=tk.W)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        output_entry.grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=1, column=1)
        
        # Parameters section
        params_frame = ttk.LabelFrame(content_frame, text="Parameters", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Speed control
        ttk.Label(params_frame, text="Speed (0.5x - 3.0x):").grid(row=0, column=0, sticky=tk.W, padx=5)
        speed_scale = ttk.Scale(
            params_frame,
            from_=0.5,
            to=3.0,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.update_speed_label
        )
        speed_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.speed_label = ttk.Label(params_frame, text="1.0x")
        self.speed_label.grid(row=0, column=2, padx=5)
        
        # Pitch control
        ttk.Label(params_frame, text="Pitch (-12 to +12):").grid(row=1, column=0, sticky=tk.W, padx=5)
        pitch_scale = ttk.Scale(
            params_frame,
            from_=-12,
            to=12,
            orient=tk.HORIZONTAL,
            variable=self.pitch_var,
            command=self.update_pitch_label
        )
        pitch_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.pitch_label = ttk.Label(params_frame, text="0")
        self.pitch_label.grid(row=1, column=2, padx=5)
        
        # Complexity control
        ttk.Label(params_frame, text="Complexity (0-100):").grid(row=2, column=0, sticky=tk.W, padx=5)
        complexity_scale = ttk.Scale(
            params_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.complexity_var,
            command=self.update_complexity_label
        )
        complexity_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        self.complexity_label = ttk.Label(params_frame, text="50%")
        self.complexity_label.grid(row=2, column=2, padx=5)
        
        params_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame, padding="10")
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.convert_button = ttk.Button(
            button_frame,
            text="Convert to G-code",
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Visualize", command=self.show_visualization).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Log output
        log_frame = ttk.LabelFrame(content_frame, text="Log Output", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        content_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
    
    def update_speed_label(self, value):
        """Update speed label"""
        self.speed_label.config(text=f"{float(value):.1f}x")
    
    def update_pitch_label(self, value):
        """Update pitch label"""
        val = int(float(value))
        self.pitch_label.config(text=f"{val:+d}")
    
    def update_complexity_label(self, value):
        """Update complexity label"""
        self.complexity_label.config(text=f"{int(float(value))}%")
    
    def browse_input(self):
        """Browse for input file"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.m4a *.flac *.aac"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
    
    def browse_output(self):
        """Browse for output file"""
        filename = filedialog.asksaveasfilename(
            title="Save G-code As",
            defaultextension=".gcode",
            filetypes=[("G-code Files", "*.gcode"), ("All Files", "*.*")]
        )
        if filename:
            self.output_var.set(filename)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear log output"""
        self.log_text.delete(1.0, tk.END)
    
    def start_conversion(self):
        """Start conversion process"""
        if self.processing:
            messagebox.showwarning("Processing", "A conversion is already in progress!")
            return
        
        # Validate input
        input_path = self.input_var.get().strip()
        if not input_path:
            messagebox.showerror("Error", "Please provide a YouTube URL or audio file!")
            return
        
        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file!")
            return
        
        # Start conversion in thread
        self.processing = True
        self.convert_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Processing...")
        
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()
    
    def run_conversion(self):
        """Run the actual conversion"""
        try:
            self.log("\n" + "="*60)
            self.log("Starting conversion...")
            self.log("="*60)
            
            # Import main processing function
            from src.main import process_youtube_url, process_audio_file
            
            # Create args object
            class Args:
                def __init__(self, input_val, output, speed, pitch, complexity):
                    self.input = input_val
                    self.output = output
                    self.speed = speed
                    self.pitch = pitch
                    self.complexity = complexity
                    self.log_level = "INFO"
            
            args = Args(
                self.input_var.get(),
                self.output_var.get(),
                self.speed_var.get(),
                self.pitch_var.get(),
                self.complexity_var.get()
            )
            
            # Detect URL vs file
            if args.input.startswith(('http://', 'https://')):
                self.log("Detected YouTube URL")
                process_youtube_url(args)
            else:
                self.log("Detected audio file")
                process_audio_file(args)
            
            self.log("\n" + "="*60)
            self.log("✓ Conversion complete!")
            self.log(f"Output: {args.output}")
            self.log("="*60 + "\n")
            
            self.root.after(0, self.conversion_complete, True)
        
        except Exception as e:
            error_msg = handle_error(e) if isinstance(e, GCodeRadioException) else str(e)
            self.log(f"\n✗ Error: {error_msg}\n")
            self.root.after(0, self.conversion_complete, False)
    
    def conversion_complete(self, success):
        """Called when conversion completes"""
        self.processing = False
        self.convert_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        if success:
            self.status_var.set("Conversion complete!")
            messagebox.showinfo("Success", "G-code file created successfully!")
        else:
            self.status_var.set("Conversion failed")
            messagebox.showerror("Error", "Conversion failed. Check the log for details.")
    
    def show_visualization(self):
        """Show visualization window"""
        # Check if we have output
        output_path = self.output_var.get()
        if not Path(output_path).exists():
            messagebox.showwarning(
                "No Output",
                "Please convert a file first to visualize the results."
            )
            return
        
        # Open visualization window
        from src.ui.visualization import VisualizationWindow
        viz_window = tk.Toplevel(self.root)
        VisualizationWindow(viz_window, output_path)


def main():
    """Main GUI entry point"""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = GCodeRadioGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
