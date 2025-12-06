"""G-Code Radio - Professional GUI with Note Selector and Movement Visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.utils.logger import Logger
from src.utils.error_handler import handle_error, GCodeRadioException

logger = Logger.get_logger(__name__)


class ModernGCodeRadioGUI:
    """Professional tabbed GUI for G-Code Radio with note selection and visualization"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("G-Code Radio - 3D Printer Music Studio")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Set background color
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar(value="output/music.gcode")
        self.speed_var = tk.DoubleVar(value=1.0)
        self.pitch_var = tk.IntVar(value=0)
        self.complexity_var = tk.IntVar(value=50)
        self.processing = False
        self.last_notes = []
        self.manual_notes = []
        self.manual_selected = None
        
        # Manual note form vars
        self.selected_midi = tk.IntVar(value=69)  # A4
        self.manual_dur_var = tk.DoubleVar(value=0.5)
        self.manual_pause_var = tk.BooleanVar(value=False)
        self.piano_octave = tk.IntVar(value=4)  # Default octave
        
        self.setup_style()
        self.setup_ui()
    
    def setup_style(self):
        """Configure modern dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.bg_dark = '#1e1e1e'
        self.bg_light = '#2d2d2d'
        self.accent1 = '#00d4ff'
        self.accent2 = '#ff006e'
        self.accent3 = '#8338ec'
        self.text_light = '#ffffff'
        self.text_dim = '#a0a0a0'
        
        # Configure ttk styles
        style.configure('Dark.TFrame', background=self.bg_dark)
        style.configure('Dark.TLabel', background=self.bg_dark, foreground=self.text_light)
        style.configure('Dark.TLabelframe', background=self.bg_light, foreground=self.accent1)
        style.configure('Dark.TLabelframe.Label', background=self.bg_light, foreground=self.accent1, font=('Arial', 10, 'bold'))
        style.configure('Dark.TButton', background=self.bg_light, foreground=self.text_light, font=('Arial', 9))
        style.map('Dark.TButton', background=[('active', self.accent1), ('pressed', self.accent2)])
        style.configure('Accent.TButton', background=self.accent1, foreground=self.bg_dark, font=('Arial', 11, 'bold'))
        style.map('Accent.TButton', background=[('active', self.accent2)])
        style.configure('Danger.TButton', background=self.accent2, foreground=self.text_light, font=('Arial', 9))
        style.configure('Dark.Treeview', background=self.bg_light, foreground=self.text_light, fieldbackground=self.bg_light)
        style.configure('Dark.Treeview.Heading', background=self.accent1, foreground=self.bg_dark)
    
    def setup_ui(self):
        """Setup main interface"""
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with gradient effect
        header = tk.Frame(main_frame, bg=self.accent1, height=70)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🎵 G-CODE RADIO", font=('Arial', 28, 'bold'),
                        bg=self.accent1, fg=self.bg_dark)
        title.pack(pady=12)
        
        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Audio
        self.audio_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.audio_tab, text="🎙️  Audio Conversion")
        self.setup_audio_tab(self.audio_tab)
        
        # Tab 2: Manual Notes
        self.manual_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.manual_tab, text="🎹  Manual Notes Studio")
        self.setup_manual_tab(self.manual_tab)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.bg_light, height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="✓ Ready")
        status_label = tk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10),
                               bg=self.bg_light, fg=self.accent1)
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def setup_audio_tab(self, parent):
        """Audio conversion tab"""
        parent.configure(bg=self.bg_dark)
        container = tk.Frame(parent, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        left_col = tk.Frame(container, bg=self.bg_dark)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Input
        input_frame = tk.LabelFrame(left_col, text="📁 Audio File", bg=self.bg_light,
                                   fg=self.accent1, font=('Arial', 10, 'bold'), padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(input_frame, textvariable=self.input_var, font=('Arial', 10)).pack(fill=tk.X, pady=5)
        ttk.Button(input_frame, text="Browse File", command=self.browse_input, style='Dark.TButton').pack(fill=tk.X, pady=5)
        
        # Output
        output_frame = tk.LabelFrame(left_col, text="💾 Output G-code", bg=self.bg_light,
                                    fg=self.accent1, font=('Arial', 10, 'bold'), padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(output_frame, textvariable=self.output_var, font=('Arial', 10)).pack(fill=tk.X, pady=5)
        ttk.Button(output_frame, text="Browse Location", command=self.browse_output, style='Dark.TButton').pack(fill=tk.X, pady=5)
        
        # Parameters
        params_frame = tk.LabelFrame(left_col, text="⚙️ Parameters", bg=self.bg_light,
                                    fg=self.accent1, font=('Arial', 10, 'bold'), padx=10, pady=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(params_frame, text="Speed:", bg=self.bg_light, fg=self.text_light).pack(anchor=tk.W)
        speed_frame = tk.Frame(params_frame, bg=self.bg_light)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Scale(speed_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL,
                 variable=self.speed_var, command=self.update_speed_label).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.speed_label = tk.Label(speed_frame, text="1.0x", bg=self.bg_light, fg=self.accent1, width=6, font=('Arial', 9, 'bold'))
        self.speed_label.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(params_frame, text="Pitch:", bg=self.bg_light, fg=self.text_light).pack(anchor=tk.W, pady=(8, 0))
        pitch_frame = tk.Frame(params_frame, bg=self.bg_light)
        pitch_frame.pack(fill=tk.X, pady=5)
        ttk.Scale(pitch_frame, from_=-12, to=12, orient=tk.HORIZONTAL,
                 variable=self.pitch_var, command=self.update_pitch_label).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.pitch_label = tk.Label(pitch_frame, text="0", bg=self.bg_light, fg=self.accent1, width=6, font=('Arial', 9, 'bold'))
        self.pitch_label.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(params_frame, text="Complexity:", bg=self.bg_light, fg=self.text_light).pack(anchor=tk.W, pady=(8, 0))
        complexity_frame = tk.Frame(params_frame, bg=self.bg_light)
        complexity_frame.pack(fill=tk.X, pady=5)
        ttk.Scale(complexity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                 variable=self.complexity_var, command=self.update_complexity_label).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.complexity_label = tk.Label(complexity_frame, text="50%", bg=self.bg_light, fg=self.accent1, width=6, font=('Arial', 9, 'bold'))
        self.complexity_label.pack(side=tk.RIGHT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(left_col, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.convert_button = ttk.Button(button_frame, text="▶️  CONVERT TO G-CODE",
                                        command=self.start_conversion, style='Accent.TButton')
        self.convert_button.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="🎵  Play Preview", command=self.play_midi_preview, style='Dark.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="📊  Note Table", command=self.show_note_freq_table, style='Dark.TButton').pack(fill=tk.X, pady=5)
        
        # Right: Log
        right_col = tk.Frame(container, bg=self.bg_dark)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        log_frame = tk.LabelFrame(right_col, text="📝 Log Output", bg=self.bg_light,
                                 fg=self.accent1, font=('Arial', 10, 'bold'), padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=35, wrap=tk.WORD,
                                                 font=('Courier', 8), bg=self.bg_dark, fg=self.accent1,
                                                 insertbackground=self.accent1)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        log_btn_frame = tk.Frame(right_col, bg=self.bg_dark)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(log_btn_frame, text="Copy", command=self.copy_log, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(log_btn_frame, text="Clear", command=self.clear_log, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(log_btn_frame, text="📊 Visualize", command=self.show_visualization, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    
    def setup_manual_tab(self, parent):
        """Manual notes studio with piano-like note selection"""
        parent.configure(bg=self.bg_dark)
        container = tk.Frame(parent, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top: Note selector (piano-style)
        piano_frame = tk.LabelFrame(container, text="🎹 Note Selector", bg=self.bg_light,
                                   fg=self.accent1, font=('Arial', 11, 'bold'), padx=15, pady=15)
        piano_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.setup_piano_selector(piano_frame)
        
        # Middle: Duration and controls
        controls_frame = tk.LabelFrame(container, text="⏱️ Note Settings", bg=self.bg_light,
                                      fg=self.accent2, font=('Arial', 11, 'bold'), padx=15, pady=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        controls_grid = tk.Frame(controls_frame, bg=self.bg_light)
        controls_grid.pack(fill=tk.X)
        
        tk.Label(controls_grid, text="Duration (s):", bg=self.bg_light, fg=self.text_light, font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(controls_grid, textvariable=self.manual_dur_var, width=10, font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Checkbutton(controls_grid, text="Rest (pause)", variable=self.manual_pause_var).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(controls_grid, text="🔊 Preview Note", command=self.preview_note, style='Accent.TButton').grid(row=0, column=3, padx=10, pady=5)
        ttk.Button(controls_grid, text="➕ Add to Queue", command=self.add_manual_note_end, style='Accent.TButton').grid(row=0, column=4, padx=10, pady=5)
        
        # Bottom-left: Queue
        bottom_container = tk.Frame(container, bg=self.bg_dark)
        bottom_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        queue_frame = tk.LabelFrame(bottom_container, text="🎼 Note Queue", bg=self.bg_light,
                                   fg=self.accent3, font=('Arial', 11, 'bold'), padx=5, pady=5)
        queue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        canvas_container = tk.Frame(queue_frame, bg=self.bg_light)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.note_canvas = tk.Canvas(canvas_container, height=200, bg=self.bg_dark, highlightthickness=1, highlightbackground=self.accent3)
        self.note_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.note_canvas.yview)
        self.note_list_frame = tk.Frame(self.note_canvas, bg=self.bg_dark)
        self.note_list_frame.bind('<Configure>', lambda e: self.note_canvas.configure(scrollregion=self.note_canvas.bbox("all")))
        self.note_canvas.create_window((0, 0), window=self.note_list_frame, anchor='nw')
        self.note_canvas.configure(yscrollcommand=self.note_scroll.set)
        self.note_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.note_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.render_manual_notes()
        
        # Bottom-right: Visualization and controls
        viz_frame = tk.LabelFrame(bottom_container, text="📊 Movement Preview", bg=self.bg_light,
                                 fg=self.accent2, font=('Arial', 11, 'bold'), padx=5, pady=5)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.viz_canvas = tk.Canvas(viz_frame, bg=self.bg_dark, highlightthickness=1, highlightbackground=self.accent2)
        self.viz_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Playback controls
        playback_frame = tk.Frame(container, bg=self.bg_dark)
        playback_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(playback_frame, text="▶️  Play Full Queue", command=self.play_manual_queue, style='Dark.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(playback_frame, text="▶️  Play From Selected", command=self.play_from_selected, style='Dark.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(playback_frame, text="🗑️  Clear Queue", command=self.clear_manual_notes, style='Danger.TButton').pack(side=tk.LEFT, padx=3)
        
        ttk.Button(playback_frame, text="💾 GENERATE G-CODE", command=self.generate_from_manual, style='Accent.TButton').pack(side=tk.RIGHT, padx=3)
    
    def setup_piano_selector(self, parent):
        """Create piano-like note selector with realistic appearance - 2 octaves"""
        # Outer frame for centering
        outer_frame = tk.Frame(parent, bg=self.bg_light)
        outer_frame.pack(fill=tk.X, expand=True)
        
        # Inner container for piano + arrows
        piano_container = tk.Frame(outer_frame, bg=self.bg_light)
        piano_container.pack(anchor=tk.CENTER)

        def shift_octave(delta):
            new_octave = self.piano_octave.get() + delta
            if 0 <= new_octave <= 7:  # Max octave 7 to show 7 and 8
                self.piano_octave.set(new_octave)
                render_piano_keys()

        # Left arrow
        left_btn = tk.Button(piano_container, text='◀', command=lambda: shift_octave(-1), 
                           bg=self.accent1, fg=self.bg_dark, font=('Arial', 16, 'bold'), 
                           width=3, height=2, relief=tk.RAISED, bd=3)
        left_btn.pack(side=tk.LEFT, padx=20)

        # Canvas for piano keys (2 octaves = 14 white keys)
        self.piano_canvas = tk.Canvas(piano_container, width=730, height=120, 
                                     bg=self.bg_light, highlightthickness=0)
        self.piano_canvas.pack(side=tk.LEFT, padx=10)

        # Right arrow
        right_btn = tk.Button(piano_container, text='▶', command=lambda: shift_octave(1), 
                            bg=self.accent1, fg=self.bg_dark, font=('Arial', 16, 'bold'), 
                            width=3, height=2, relief=tk.RAISED, bd=3)
        right_btn.pack(side=tk.LEFT, padx=20)

        def render_piano_keys():
            self.piano_canvas.delete('all')
            octave = self.piano_octave.get()
            
            # White key layout: C D E F G A B (repeat for 2 octaves)
            white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] * 2
            white_midi_offsets = [0, 2, 4, 5, 7, 9, 11] + [12, 14, 16, 17, 19, 21, 23]
            black_info = [
                (1, 'C#'), (3, 'D#'), (6, 'F#'), (8, 'G#'), (10, 'A#'),  # First octave
                (13, 'C#'), (15, 'D#'), (18, 'F#'), (20, 'G#'), (22, 'A#')  # Second octave
            ]
            
            key_width = 50
            white_height = 100
            black_height = 60
            start_x = 10
            
            # Draw white keys for 2 octaves
            for i, (note, offset) in enumerate(zip(white_keys, white_midi_offsets)):
                midi = (octave + 1) * 12 + offset
                x = start_x + i * key_width
                rect = self.piano_canvas.create_rectangle(x, 10, x + key_width - 2, 10 + white_height, 
                                                          fill='white', outline='#333', width=2, tags=f'key_{midi}')
                octave_num = octave + (offset // 12)
                text = self.piano_canvas.create_text(x + key_width//2 - 1, 90, text=f"{note}{octave_num}", 
                                                    font=('Arial', 9, 'bold'), fill='#222', tags=f'key_{midi}')
                self.piano_canvas.tag_bind(f'key_{midi}', '<Button-1>', lambda e, m=midi: self.select_piano_note(m))
            
            # Draw black keys on top
            for offset, note_name in black_info:
                midi = (octave + 1) * 12 + offset
                white_key_index = sum(1 for o in white_midi_offsets if o < offset)
                x = start_x + white_key_index * key_width - 15
                rect = self.piano_canvas.create_rectangle(x, 10, x + 30, 10 + black_height, 
                                                          fill='#111', outline='#000', width=2, tags=f'key_{midi}')
                self.piano_canvas.tag_bind(f'key_{midi}', '<Button-1>', lambda e, m=midi: self.select_piano_note(m))
            
            # Display octave range
            self.piano_canvas.create_text(365, 5, text=f'Octaves {octave} - {octave + 1}', 
                                        font=('Arial', 10, 'bold'), fill=self.accent1, anchor='n')

        render_piano_keys()

        # Selected note display
        display_frame = tk.Frame(parent, bg=self.bg_light)
        display_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Center the display
        center_container = tk.Frame(display_frame, bg=self.bg_light)
        center_container.pack(anchor=tk.CENTER)
        
        tk.Label(center_container, text="Selected Note:", bg=self.bg_light, fg=self.text_light, 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.selected_note_label = tk.Label(center_container, text="A4 (440 Hz)", bg=self.bg_light,
                                           fg=self.accent1, font=('Arial', 14, 'bold'))
        self.selected_note_label.pack(side=tk.LEFT, padx=5)

    def select_piano_note(self, midi):
        """Select note and play it immediately"""
        self.selected_midi.set(midi)
        self.update_selected_note_label()
        # Play the note with current duration
        if not self.manual_pause_var.get():
            threading.Thread(target=self._play_single_note, args=(midi,), daemon=True).start()
    
    def _play_single_note(self, midi):
        """Play a single note with current duration setting"""
        try:
            import sounddevice as sd
            duration = float(self.manual_dur_var.get())
            freq = 440.0 * (2 ** ((midi - 69) / 12.0))
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            waveform = 0.3 * np.sin(2 * np.pi * freq * t)
            waveform += 0.1 * np.sin(4 * np.pi * freq * t)
            waveform += 0.05 * np.sin(6 * np.pi * freq * t)
            waveform = waveform.astype(np.float32) * 0.8
            waveform = waveform.reshape(-1, 1)
            sd.play(waveform, sample_rate, blocking=False)
        except Exception as e:
            logger.warning(f"Playback error: {e}")
    
    def update_selected_note_label(self):
        midi = self.selected_midi.get()
        freq = 440.0 * (2 ** ((midi - 69) / 12.0))
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_name = note_names[midi % 12]
        octave = (midi // 12) - 1
        self.selected_note_label.config(text=f"{note_name}{octave} ({freq:.1f} Hz)")
    
    def preview_note(self):
        """Play the selected note for preview"""
        if self.manual_pause_var.get():
            messagebox.showinfo("Rest", "This is a rest (pause) - no sound to preview")
            return
        
        midi = self.selected_midi.get()
        duration = float(self.manual_dur_var.get())
        
        def play_preview():
            try:
                import sounddevice as sd
                freq = 440.0 * (2 ** ((midi - 69) / 12.0))
                sample_rate = 44100
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                waveform = 0.3 * np.sin(2 * np.pi * freq * t)
                waveform += 0.1 * np.sin(4 * np.pi * freq * t)
                waveform += 0.05 * np.sin(6 * np.pi * freq * t)
                waveform = waveform.astype(np.float32) * 0.8
                waveform = waveform.reshape(-1, 1)
                sd.play(waveform, sample_rate, blocking=False)
            except Exception as e:
                messagebox.showerror("Error", f"Playback error: {e}")
        
        threading.Thread(target=play_preview, daemon=True).start()
    
    def add_manual_note_end(self):
        try:
            if self.manual_pause_var.get():
                note = {'frequency': 440.0, 'duration': float(self.manual_dur_var.get()), 'pause': True}
            else:
                midi = self.selected_midi.get()
                freq = 440.0 * (2 ** ((midi - 69) / 12.0))
                note = {'frequency': freq, 'duration': float(self.manual_dur_var.get()), 'pause': False}
            self.manual_notes.append(note)
            self.render_manual_notes()
            self.draw_movement_preview()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def render_manual_notes(self):
        for child in self.note_list_frame.winfo_children():
            child.destroy()
        
        if not self.manual_notes:
            ttk.Label(self.note_list_frame, text="Queue empty", background=self.bg_dark, foreground=self.text_dim).pack(anchor=tk.W, padx=4, pady=2)
            return
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        for idx, note in enumerate(self.manual_notes):
            frame = tk.Frame(self.note_list_frame, bg=self.bg_dark)
            frame.pack(fill=tk.X, padx=2, pady=2)
            
            is_selected = (self.manual_selected == idx)
            bg = self.accent1 if is_selected else self.bg_light
            fg = self.bg_dark if is_selected else self.text_light
            
            inner = tk.Frame(frame, bg=bg, highlightthickness=2, highlightbackground=self.accent3 if is_selected else self.bg_light)
            inner.pack(fill=tk.X)
            
            freq = note['frequency']
            dur = note['duration']
            pause = note.get('pause', False)
            
            if not pause:
                midi = int(round(69 + 12 * np.log2(freq / 440.0))) if freq > 0 else 69
                note_name = note_names[midi % 12]
                octave = (midi // 12) - 1
                label_text = f"#{idx+1}  {note_name}{octave}  {freq:.2f}Hz  {dur:.3f}s"
            else:
                label_text = f"#{idx+1}  Rest  {dur:.3f}s"
            
            lbl = tk.Label(inner, text=label_text, bg=bg, fg=fg, anchor='w', font=('Arial', 9, 'bold'))
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=3)
            lbl.bind('<Button-1>', lambda e, i=idx: self.select_manual_note(i))
            
            tk.Button(inner, text="✕", command=lambda i=idx: self.remove_manual_note(i),
                     bg=self.accent2, fg=self.text_light, font=('Arial', 8, 'bold'), width=2, padx=2).pack(side=tk.RIGHT, padx=4, pady=2)
        
        self.draw_movement_preview()
    
    def select_manual_note(self, idx):
        self.manual_selected = idx
        self.render_manual_notes()
    
    def remove_manual_note(self, idx):
        self.manual_notes.pop(idx)
        if self.manual_selected == idx:
            self.manual_selected = None
        self.render_manual_notes()
    
    def clear_manual_notes(self):
        self.manual_notes = []
        self.manual_selected = None
        self.render_manual_notes()
    
    def draw_movement_preview(self):
        """Draw movement visualization for manual notes"""
        try:
            from src.mapping.note_mapper import NoteMapper
            from src.printer.moment_s1_config import MomentS1Config
            self.viz_canvas.delete("all")
            if not self.manual_notes:
                self.viz_canvas.create_text(200, 100, text="Queue empty", fill=self.text_dim, font=('Arial', 12))
                return
            printer_config = MomentS1Config()
            note_mapper = NoteMapper(printer_config)
            movements = []
            positions = [(0, 0, 0)]
            for note in self.manual_notes:
                if note.get('pause'):
                    movements.append({'pause': True, 'duration': note['duration'], 'distance': 0, 'axis': None})
                    positions.append(positions[-1])
                else:
                    midi = int(round(69 + 12 * np.log2(note['frequency'] / 440.0)))
                    mv = note_mapper.note_to_movement(midi, note['duration'])
                    movements.append(mv)
                    # Simulate position update
                    x, y, z = positions[-1]
                    axis = mv.get('axis', 'X')
                    dist = mv.get('distance', 0)
                    if axis == 'X':
                        x += dist
                    elif axis == 'Y':
                        y += dist
                    elif axis == 'Z':
                        z += dist
                    positions.append((x, y, z))
            # Draw printer path
            w, h = self.viz_canvas.winfo_width(), self.viz_canvas.winfo_height()
            if w < 2:
                w, h = 400, 200
            # Normalize positions for display
            xs = [p[0] for p in positions]
            ys = [p[1] for p in positions]
            zs = [p[2] for p in positions]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            min_z, max_z = min(zs), max(zs)
            def norm(val, minv, maxv, size):
                if maxv - minv == 0:
                    return size // 2
                return int((val - minv) / (maxv - minv) * (size - 40) + 20)
            # Draw path (X/Y)
            for i in range(1, len(positions)):
                x1 = norm(xs[i-1], min_x, max_x, w)
                y1 = norm(ys[i-1], min_y, max_y, h)
                x2 = norm(xs[i], min_x, max_x, w)
                y2 = norm(ys[i], min_y, max_y, h)
                color = self.accent1 if movements[i-1].get('axis') == 'X' else self.accent3 if movements[i-1].get('axis') == 'Y' else self.accent2
                self.viz_canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
            # Draw start/end
            self.viz_canvas.create_oval(norm(xs[0], min_x, max_x, w)-6, norm(ys[0], min_y, max_y, h)-6,
                                       norm(xs[0], min_x, max_x, w)+6, norm(ys[0], min_y, max_y, h)+6,
                                       fill=self.accent2, outline='')
            self.viz_canvas.create_oval(norm(xs[-1], min_x, max_x, w)-6, norm(ys[-1], min_y, max_y, h)-6,
                                       norm(xs[-1], min_x, max_x, w)+6, norm(ys[-1], min_y, max_y, h)+6,
                                       fill=self.accent1, outline='')
        except Exception as e:
            logger.warning(f"Visualization error: {e}")
    
    def play_manual_queue(self):
        if not self.manual_notes:
            messagebox.showwarning("Queue Empty", "Add notes first")
            return
        notes = self.manual_notes_to_note_dicts(self.manual_notes)
        threading.Thread(target=self._play_notes_directly, args=(notes,), daemon=True).start()
    
    def play_from_selected(self):
        if self.manual_selected is None:
            messagebox.showwarning("No Selection", "Select a note first")
            return
        notes = self.manual_notes_to_note_dicts(self.manual_notes[self.manual_selected:])
        threading.Thread(target=self._play_notes_directly, args=(notes,), daemon=True).start()
    
    def manual_notes_to_note_dicts(self, manual_notes):
        result = []
        speed = max(0.1, float(self.speed_var.get()))
        pitch_shift = int(self.pitch_var.get())
        for note in manual_notes:
            dur = float(note.get('duration', 0.2)) / speed
            if note.get('pause'):
                result.append({'pause': True, 'duration': dur, 'midi': 69})
            else:
                freq = float(note.get('frequency', 440.0))
                midi = int(round(69 + 12 * np.log2(max(freq, 1e-3) / 440.0)))
                midi = max(0, min(127, midi + pitch_shift))
                result.append({'pause': False, 'duration': dur, 'midi': midi})
        return result
    
    def _play_notes_directly(self, notes, sample_rate=44100):
        try:
            import sounddevice as sd
            
            audio_data = np.array([], dtype=np.float32)
            for note in notes:
                midi_note = note.get('midi', 69)
                freq = 440.0 * (2 ** ((midi_note - 69) / 12.0))
                duration_s = float(note.get('duration', 0.2))
                num_samples = int(sample_rate * duration_s)
                t = np.linspace(0, duration_s, num_samples, False)
                
                if note.get('pause'):
                    waveform = np.zeros(num_samples, dtype=np.float32)
                else:
                    waveform = 0.3 * np.sin(2 * np.pi * freq * t)
                    waveform += 0.1 * np.sin(4 * np.pi * freq * t)
                    waveform += 0.05 * np.sin(6 * np.pi * freq * t)
                
                envelope = np.ones(num_samples)
                attack = int(num_samples * 0.05)
                release = int(num_samples * 0.15)
                if attack > 0:
                    envelope[:attack] = np.linspace(0, 1, attack)
                if release > 0:
                    envelope[-release:] = np.linspace(1, 0, release)
                
                waveform = (waveform * envelope).astype(np.float32)
                audio_data = np.concatenate([audio_data, waveform])
            
            audio_data = audio_data.reshape(-1, 1) if audio_data.ndim == 1 else audio_data
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.8
            
            sd.play(audio_data, sample_rate, blocking=False)
        except Exception as e:
            messagebox.showerror("Error", f"Playback error: {e}")
    
    def generate_from_manual(self):
        if not self.manual_notes:
            messagebox.showerror("Queue Empty", "Add notes first!")
            return
        self.start_conversion()
    
    def process_manual_queue(self):
        from src.mapping.note_mapper import NoteMapper
        from src.mapping.bounds_validator import BoundsValidator
        from src.gcode.gcode_generator import GCodeGenerator
        from src.printer.moment_s1_config import MomentS1Config

        speed = max(0.1, float(self.speed_var.get()))
        pitch_shift = int(self.pitch_var.get())

        adjusted_notes = []
        for note in self.manual_notes:
            dur = max(0.01, float(note.get('duration', 0.2))) / speed
            if note.get('pause'):
                adjusted_notes.append({'pause': True, 'duration': dur})
            else:
                freq = max(1e-3, float(note.get('frequency', 440.0)))
                midi = int(round(69 + 12 * np.log2(freq / 440.0)))
                midi = max(0, min(127, midi + pitch_shift))
                adjusted_notes.append({'pause': False, 'duration': dur, 'midi': midi})

        printer_config = MomentS1Config()
        note_mapper = NoteMapper(printer_config)

        movements = []
        for n in adjusted_notes:
            if n.get('pause'):
                movements.append({'pause': True, 'duration': n['duration']})
            else:
                mv = note_mapper.note_to_movement(n['midi'], n['duration'])
                movements.append(mv)

        bounds_validator = BoundsValidator(printer_config)
        movements = bounds_validator.validate_all_movements(movements)

        gcode_generator = GCodeGenerator(printer_config)
        gcode_path = gcode_generator.write_gcode_file(
            movements,
            self.output_var.get(),
            title=Path(self.output_var.get()).stem
        )
        return gcode_path
    
    def start_conversion(self):
        if self.processing:
            messagebox.showwarning("Processing", "Conversion already in progress!")
            return
        
        input_path = self.input_var.get().strip()
        if not input_path and not self.manual_notes:
            messagebox.showerror("Error", "Provide an audio file or add manual notes!")
            return
        
        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showerror("Error", "Specify an output file!")
            return
        
        self.processing = True
        self.convert_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("⏳ Processing...")
        
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()
    
    def run_conversion(self):
        try:
            self.log("\n" + "="*60)
            self.log("Starting conversion...")
            self.log("="*60)
            
            if self.manual_notes:
                self.log("Using manual note queue...")
                gcode_path = self.process_manual_queue()
                self.last_notes = self.manual_notes_to_note_dicts(self.manual_notes)
            else:
                from src.main import process_audio_file
                
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
                
                self.log("Detected audio file")
                process_audio_file(args)
                gcode_path = args.output
                self.last_notes = self.extract_notes_from_audio(self.input_var.get())
            
            self.log("="*60)
            self.log("✓ Conversion complete!")
            self.log(f"Output: {gcode_path}")
            self.log("="*60 + "\n")
            
            self.root.after(0, self.conversion_complete, True)
        except Exception as e:
            error_msg = handle_error(e) if isinstance(e, GCodeRadioException) else str(e)
            self.log(f"\n✗ Error: {error_msg}\n")
            self.root.after(0, self.conversion_complete, False)
    
    def conversion_complete(self, success):
        self.processing = False
        self.convert_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        if success:
            self.status_var.set("✓ Conversion complete!")
            messagebox.showinfo("Success", "G-code created successfully!")
        else:
            self.status_var.set("✗ Conversion failed")
            messagebox.showerror("Error", "Conversion failed!")
    
    def extract_notes_from_audio(self, audio_file):
        try:
            from src.audio.extractor import AudioExtractor
            from src.audio.analyzer import AudioAnalyzer
            from src.signal_processing.pitch_detection import PitchDetector
            from src.signal_processing.note_detection import NoteDetector
            from src.mapping.parameter_controller import ParameterController
            
            extractor = AudioExtractor()
            if not audio_file.endswith('.wav'):
                audio_file = extractor.convert_to_wav(audio_file)
            
            analyzer = AudioAnalyzer()
            analyzer.extract_features(audio_file)
            onsets = analyzer.get_onset_frames(audio_file)
            
            pitch_detector = PitchDetector()
            pitch_data = pitch_detector.detect_pitch(audio_file)
            confidence = pitch_detector.get_pitch_confidence(audio_file)
            
            note_detector = NoteDetector()
            voiced = pitch_detector.extract_voicing(pitch_data['frequencies'], confidence, threshold=0.1)
            notes = note_detector.detect_notes(pitch_data, onsets, voiced)
            
            if not notes:
                return []
            
            param_controller = ParameterController()
            notes = param_controller.apply_all_parameters(notes, self.speed_var.get(), self.pitch_var.get(), self.complexity_var.get())
            return notes
        except Exception as e:
            logger.warning(f"Extract notes failed: {e}")
            return []
    
    def play_midi_preview(self):
        if self.processing:
            messagebox.showwarning("Processing", "Wait for conversion!")
            return
        
        audio_file = self.input_var.get().strip()
        if not audio_file and not self.manual_notes:
            messagebox.showerror("Error", "Provide audio file or add manual notes!")
            return
        
        threading.Thread(target=self._play_midi_preview_worker, daemon=True).start()
    
    def _play_midi_preview_worker(self):
        try:
            self.status_var.set("⏳ Generating preview...")
            
            if self.manual_notes:
                notes = self.manual_notes_to_note_dicts(self.manual_notes)
            else:
                notes = self.extract_notes_from_audio(self.input_var.get())
            
            if not notes:
                self.log("✗ No notes detected")
                self.status_var.set("✓ Ready")
                return
            
            self.status_var.set("▶️ Playing preview...")
            self.log(f"Playing {len(notes)} notes...")
            self._play_notes_directly(notes)
            self.log("✓ Preview finished")
            self.status_var.set("✓ Ready")
        except Exception as e:
            self.log(f"✗ Error: {e}")
            self.status_var.set("✓ Ready")
    
    def show_visualization(self):
        output_path = self.output_var.get()
        if not Path(output_path).exists():
            messagebox.showwarning("No Output", "Convert a file first!")
            return
        
        from src.ui.visualization import VisualizationWindow
        viz_window = tk.Toplevel(self.root)
        VisualizationWindow(viz_window, output_path)
    
    def show_note_freq_table(self):
        top = tk.Toplevel(self.root)
        top.title("Note Frequency Reference")
        top.geometry("450x700")
        top.configure(bg=self.bg_dark)
        
        frame = tk.Frame(top, bg=self.bg_light, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ('Note', 'MIDI', 'Freq (Hz)')
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=25, style='Dark.Treeview')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor=tk.CENTER, width=130)
        tree.pack(fill=tk.BOTH, expand=True)
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        for midi in range(21, 109):
            freq = 440.0 * (2 ** ((midi - 69) / 12.0))
            name = f"{note_names[midi % 12]}{(midi // 12) - 1}"
            tree.insert('', tk.END, values=(name, midi, f"{freq:.2f}"))
        
        ttk.Button(frame, text="Close", command=top.destroy).pack(pady=10)
    
    def update_speed_label(self, value):
        self.speed_label.config(text=f"{float(value):.1f}x")
    
    def update_pitch_label(self, value):
        self.pitch_label.config(text=f"{int(float(value)):+d}")
    
    def update_complexity_label(self, value):
        self.complexity_label.config(text=f"{int(float(value))}%")
    
    def browse_input(self):
        filename = filedialog.askopenfilename(title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a *.flac"), ("All", "*.*")])
        if filename:
            self.input_var.set(filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(title="Save G-code As",
            defaultextension=".gcode", filetypes=[("G-code", "*.gcode"), ("All", "*.*")])
        if filename:
            self.output_var.set(filename)
    
    def log(self, message=""):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def copy_log(self):
        try:
            text = self.log_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    app = ModernGCodeRadioGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
