"""
Visualization Window for G-Code Radio
Displays note detection results, movements, and G-code preview
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from pathlib import Path

from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class VisualizationWindow:
    """Visualization window for note and movement data"""
    
    def __init__(self, root, gcode_path):
        """Initialize visualization window"""
        self.root = root
        self.root.title("G-Code Radio - Visualization")
        self.root.geometry("1200x800")
        
        self.gcode_path = Path(gcode_path)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_gcode_preview_tab()
        self.create_movement_viz_tab()
        self.create_stats_tab()
        
        # Load and parse G-code
        self.parse_gcode()
    
    def create_gcode_preview_tab(self):
        """Create G-code preview tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="G-code Preview")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gcode_text = tk.Text(
            text_frame,
            wrap=tk.NONE,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10)
        )
        self.gcode_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.gcode_text.yview)
        
        # Info label
        self.info_label = ttk.Label(frame, text="", font=("Arial", 9))
        self.info_label.pack(side=tk.BOTTOM, pady=5)
    
    def create_movement_viz_tab(self):
        """Create movement visualization tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Movement Visualization")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_stats_tab(self):
        """Create statistics tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Statistics")
        
        # Create stats display
        self.stats_text = tk.Text(frame, wrap=tk.WORD, font=("Courier", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def parse_gcode(self):
        """Parse G-code file"""
        try:
            # Read G-code
            with open(self.gcode_path, 'r') as f:
                self.gcode_content = f.read()
            
            # Display in preview
            self.gcode_text.insert(1.0, self.gcode_content)
            
            # Count lines
            lines = self.gcode_content.split('\n')
            move_lines = [l for l in lines if l.strip().startswith('G1 ')]
            
            self.info_label.config(
                text=f"Total lines: {len(lines)} | Movement commands: {len(move_lines)} | File size: {self.gcode_path.stat().st_size} bytes"
            )
            
            # Parse movements for visualization
            self.parse_movements(move_lines)
            
            # Generate statistics
            self.generate_statistics(move_lines)
        
        except Exception as e:
            logger.error(f"Failed to parse G-code: {e}")
            self.gcode_text.insert(1.0, f"Error loading file: {e}")
    
    def parse_movements(self, move_lines):
        """Parse movement commands"""
        positions = []
        feedrates = []
        
        # Starting position
        current_x = 100.0
        current_y = 100.0
        current_z = 100.0
        
        for line in move_lines:
            parts = line.split()
            
            # Parse coordinates
            for part in parts[1:]:  # Skip G1
                if part.startswith('X'):
                    current_x = float(part[1:])
                elif part.startswith('Y'):
                    current_y = float(part[1:])
                elif part.startswith('Z'):
                    current_z = float(part[1:])
                elif part.startswith('F'):
                    feedrates.append(float(part[1:]))
            
            positions.append((current_x, current_y, current_z))
        
        # Visualize
        self.visualize_movements(positions, feedrates)
    
    def visualize_movements(self, positions, feedrates):
        """Create 3D visualization of movements"""
        if not positions:
            return
        
        self.fig.clear()
        
        # Extract coordinates
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]
        
        # Create 3 subplots
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2, projection='3d')
        ax3 = self.fig.add_subplot(2, 2, 3)
        ax4 = self.fig.add_subplot(2, 2, 4)
        
        # Plot 1: XY movement path
        ax1.plot(xs, ys, 'b-', linewidth=0.5, alpha=0.7)
        ax1.scatter(xs[0], ys[0], c='green', s=100, marker='o', label='Start')
        ax1.scatter(xs[-1], ys[-1], c='red', s=100, marker='x', label='End')
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_title('XY Movement Path')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_aspect('equal')
        
        # Plot 2: 3D path
        ax2.plot(xs, ys, zs, 'b-', linewidth=0.5, alpha=0.7)
        ax2.scatter(xs[0], ys[0], zs[0], c='green', s=100, marker='o', label='Start')
        ax2.scatter(xs[-1], ys[-1], zs[-1], c='red', s=100, marker='x', label='End')
        ax2.set_xlabel('X (mm)')
        ax2.set_ylabel('Y (mm)')
        ax2.set_zlabel('Z (mm)')
        ax2.set_title('3D Movement Path')
        ax2.legend()
        
        # Plot 3: Axis positions over time
        time_steps = list(range(len(positions)))
        ax3.plot(time_steps, xs, label='X', alpha=0.7)
        ax3.plot(time_steps, ys, label='Y', alpha=0.7)
        ax3.plot(time_steps, zs, label='Z', alpha=0.7)
        ax3.set_xlabel('Movement #')
        ax3.set_ylabel('Position (mm)')
        ax3.set_title('Axis Positions Over Time')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Plot 4: Feedrate over time
        if feedrates:
            ax4.plot(feedrates, 'r-', linewidth=1, alpha=0.7)
            ax4.set_xlabel('Movement #')
            ax4.set_ylabel('Feedrate (mm/min)')
            ax4.set_title('Feedrate Over Time')
            ax4.grid(True, alpha=0.3)
            
            # Add horizontal line for mean
            mean_feedrate = np.mean(feedrates)
            ax4.axhline(y=mean_feedrate, color='blue', linestyle='--', label=f'Mean: {mean_feedrate:.0f}')
            ax4.legend()
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def generate_statistics(self, move_lines):
        """Generate statistics about the G-code"""
        if not move_lines:
            self.stats_text.insert(1.0, "No movement data found.")
            return
        
        # Parse data
        xs, ys, zs, feedrates = [], [], [], []
        
        for line in move_lines:
            parts = line.split()
            for part in parts[1:]:
                if part.startswith('X'):
                    xs.append(float(part[1:]))
                elif part.startswith('Y'):
                    ys.append(float(part[1:]))
                elif part.startswith('Z'):
                    zs.append(float(part[1:]))
                elif part.startswith('F'):
                    feedrates.append(float(part[1:]))
        
        # Calculate statistics
        stats = []
        stats.append("=" * 60)
        stats.append("G-CODE STATISTICS")
        stats.append("=" * 60)
        stats.append("")
        
        stats.append("MOVEMENT DATA:")
        stats.append(f"  Total movements: {len(move_lines)}")
        stats.append("")
        
        if xs:
            stats.append("X-AXIS:")
            stats.append(f"  Min: {min(xs):.2f} mm")
            stats.append(f"  Max: {max(xs):.2f} mm")
            stats.append(f"  Range: {max(xs) - min(xs):.2f} mm")
            stats.append(f"  Mean: {np.mean(xs):.2f} mm")
            stats.append("")
        
        if ys:
            stats.append("Y-AXIS:")
            stats.append(f"  Min: {min(ys):.2f} mm")
            stats.append(f"  Max: {max(ys):.2f} mm")
            stats.append(f"  Range: {max(ys) - min(ys):.2f} mm")
            stats.append(f"  Mean: {np.mean(ys):.2f} mm")
            stats.append("")
        
        if zs:
            stats.append("Z-AXIS:")
            stats.append(f"  Min: {min(zs):.2f} mm")
            stats.append(f"  Max: {max(zs):.2f} mm")
            stats.append(f"  Range: {max(zs) - min(zs):.2f} mm")
            stats.append(f"  Mean: {np.mean(zs):.2f} mm")
            stats.append("")
        
        if feedrates:
            stats.append("FEEDRATE:")
            stats.append(f"  Min: {min(feedrates):.0f} mm/min")
            stats.append(f"  Max: {max(feedrates):.0f} mm/min")
            stats.append(f"  Mean: {np.mean(feedrates):.0f} mm/min")
            stats.append(f"  Median: {np.median(feedrates):.0f} mm/min")
            stats.append("")
        
        # Calculate total distance
        if len(xs) > 1 and len(ys) > 1 and len(zs) > 1:
            total_distance = 0
            for i in range(1, len(xs)):
                dx = xs[i] - xs[i-1]
                dy = ys[i] - ys[i-1]
                dz = zs[i] - zs[i-1]
                total_distance += np.sqrt(dx**2 + dy**2 + dz**2)
            
            stats.append("DISTANCE:")
            stats.append(f"  Total travel: {total_distance:.2f} mm")
            stats.append("")
        
        # Estimate time
        if feedrates and len(xs) > 1:
            total_time = 0
            for i in range(1, len(xs)):
                if i-1 < len(feedrates):
                    dx = xs[i] - xs[i-1]
                    dy = ys[i] - ys[i-1]
                    dz = zs[i] - zs[i-1]
                    distance = np.sqrt(dx**2 + dy**2 + dz**2)
                    total_time += (distance / feedrates[i-1]) * 60  # Convert to seconds
            
            stats.append("TIME ESTIMATE:")
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            stats.append(f"  Estimated print time: {minutes}m {seconds}s")
            stats.append("")
        
        stats.append("=" * 60)
        
        # Display
        self.stats_text.insert(1.0, "\n".join(stats))


def main():
    """Test visualization window"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualization.py <gcode_file>")
        sys.exit(1)
    
    root = tk.Tk()
    app = VisualizationWindow(root, sys.argv[1])
    root.mainloop()


if __name__ == "__main__":
    main()
