"""
DSP Task 2: Signal Processing Framework
=====================================

Student Information:
- Name: [Your Name Here]
- Student ID: [Your Student ID]
- Course: Digital Signal Processing
- Assignment: Task 2 - Signal Generation and Visualization

Learning Objectives:
1. Understand signal generation (sine and cosine waves)
2. Learn about sampling theorem and its importance
3. Visualize continuous vs discrete signal representations
4. Implement GUI for interactive signal processing
5. Understand signal parameters: amplitude, frequency, phase, sampling rate

Theory:
- Sampling Theorem: fs >= 2*fmax (Nyquist criterion)
- Continuous signals: Dense time grid for smooth visualization
- Discrete signals: Sampled at specific intervals (1/fs)
- Phase: Measured in degrees, converted to radians for calculations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import math


# =============================================================================
# SIGNAL SPECIFICATION CLASS
# =============================================================================
# This class stores all parameters needed to generate a signal
# It follows the mathematical form: x(t) = A * sin(2πft + φ) or A * cos(2πft + φ)

@dataclass
class SignalSpec:
    """
    Data class to store signal parameters for DSP signal generation.
    
    Mathematical representation:
    - Sine: x(t) = A * sin(2πft + φ)
    - Cosine: x(t) = A * cos(2πft + φ)
    
    Where:
    - A: Amplitude (peak value)
    - f: Analog frequency (Hz)
    - φ: Phase angle (degrees, converted to radians)
    - fs: Sampling frequency (Hz) - must satisfy Nyquist criterion
    """
    enabled: bool = False                    # Whether this signal is active
    kind: str = "sine"                       # Signal type: 'sine' or 'cosine'
    A: float = 1.0                          # Amplitude (peak value)
    phase_deg: float = 0.0                  # Phase in degrees (user input)
    f_analog: float = 5.0                   # Analog frequency in Hz
    fs: float = 100.0                       # Sampling frequency in Hz
    duration: float = 1.0                   # Signal duration in seconds
    representation: str = "continuous"       # Display mode: 'continuous' or 'discrete'
    label: str = "Signal"                   # Label for plotting

    def phase_rad(self) -> float:
        """
        Convert phase from degrees to radians for mathematical calculations.
        Most DSP functions use radians, but users typically think in degrees.
        """
        return math.radians(self.phase_deg)


# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================
# This class creates the GUI interface for signal processing
# It allows users to generate, visualize, and analyze signals interactively

class SignalApp(tk.Tk):
    """
    Main application class for the Signal Processing Framework.
    
    Features:
    - Interactive GUI for signal generation
    - Real-time signal visualization
    - Sampling theorem validation
    - Support for both continuous and discrete representations
    - Dual signal display (Signal A and Signal B)
    """
    
    def __init__(self):
        super().__init__()
        self.title("DSP Task 2: Signal Processing Framework")
        self.geometry("1100x700")

        # Two signals (A and B)
        self.sigA = SignalSpec(enabled=True, label="A")
        self.sigB = SignalSpec(enabled=False, label="B")

        # Top control: choose which signal is 'active' for menu-created signals
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        self.active_signal_var = tk.StringVar(value="A")
        ttk.Label(top_frame, text="Active signal:").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="A", variable=self.active_signal_var, value="A").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="B", variable=self.active_signal_var, value="B").pack(side=tk.LEFT)

        # Create menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        gen_menu = tk.Menu(menubar, tearoff=0)
        gen_menu.add_command(label="Sine Wave", command=lambda: self.open_gen_dialog('sine'))
        gen_menu.add_command(label="Cosine Wave", command=lambda: self.open_gen_dialog('cosine'))
        menubar.add_cascade(label="Signal Generation", menu=gen_menu)

        # Left control panels for Signal A and B
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        self.frameA_vars = self.build_signal_controls(control_frame, "Signal A", self.sigA)
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self.frameB_vars = self.build_signal_controls(control_frame, "Signal B", self.sigB)

        # Plot area (Matplotlib figure)
        fig_frame = ttk.Frame(self)
        fig_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Signals")
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, fig_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Bottom buttons
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
        ttk.Button(bottom_frame, text="Plot / Update", command=self.plot_all).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Clear", command=self.clear_plot).pack(side=tk.LEFT, padx=8)
        ttk.Button(bottom_frame, text="Example: Add 2 signals", command=self.example_two_signals).pack(side=tk.LEFT, padx=8)

        # Initial plot
        self.plot_all()

    def build_signal_controls(self, parent, title, spec: SignalSpec):
        """Create UI controls for a single signal and return a dict of control variables."""
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.X, padx=2, pady=2)

        enabled_var = tk.BooleanVar(value=spec.enabled)
        ttk.Checkbutton(frame, text="Enabled", variable=enabled_var).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(frame, text="Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        kind_var = tk.StringVar(value=spec.kind)
        ttk.Combobox(frame, textvariable=kind_var, values=["sine", "cosine"], state="readonly").grid(row=1, column=1, sticky=tk.W)

        ttk.Label(frame, text="Amplitude (A):").grid(row=2, column=0, sticky=tk.W)
        A_var = tk.StringVar(value=str(spec.A))
        ttk.Entry(frame, textvariable=A_var, width=10).grid(row=2, column=1, sticky=tk.W)

        ttk.Label(frame, text="Phase (deg):").grid(row=3, column=0, sticky=tk.W)
        phase_var = tk.StringVar(value=str(spec.phase_deg))
        ttk.Entry(frame, textvariable=phase_var, width=10).grid(row=3, column=1, sticky=tk.W)

        ttk.Label(frame, text="Analog freq f (Hz):").grid(row=4, column=0, sticky=tk.W)
        f_var = tk.StringVar(value=str(spec.f_analog))
        ttk.Entry(frame, textvariable=f_var, width=10).grid(row=4, column=1, sticky=tk.W)

        ttk.Label(frame, text="Sampling fs (Hz):").grid(row=5, column=0, sticky=tk.W)
        fs_var = tk.StringVar(value=str(spec.fs))
        ttk.Entry(frame, textvariable=fs_var, width=10).grid(row=5, column=1, sticky=tk.W)

        ttk.Label(frame, text="Duration (s):").grid(row=6, column=0, sticky=tk.W)
        dur_var = tk.StringVar(value=str(spec.duration))
        ttk.Entry(frame, textvariable=dur_var, width=10).grid(row=6, column=1, sticky=tk.W)

        ttk.Label(frame, text="Display:").grid(row=7, column=0, sticky=tk.W)
        rep_var = tk.StringVar(value=spec.representation)
        ttk.Combobox(frame, textvariable=rep_var, values=["continuous", "discrete"], state="readonly").grid(row=7, column=1, sticky=tk.W)

        return {
            'enabled': enabled_var,
            'kind': kind_var,
            'A': A_var,
            'phase': phase_var,
            'f': f_var,
            'fs': fs_var,
            'duration': dur_var,
            'rep': rep_var,
            'frame': frame,
            'spec': spec,
        }

    def open_gen_dialog(self, kind: str):
        """Open a small dialog to create a signal (used by the menu). The result populates the 'active' signal's controls."""
        active = self.active_signal_var.get()
        target_vars = self.frameA_vars if active == 'A' else self.frameB_vars

        # Ask user for parameters (simple dialog sequence)
        try:
            A = float(simpledialog.askstring("Amplitude", "Amplitude A:", initialvalue=target_vars['A'].get(), parent=self))
            phase = float(simpledialog.askstring("Phase (deg)", "Phase in degrees:", initialvalue=target_vars['phase'].get(), parent=self))
            f = float(simpledialog.askstring("Analog freq (Hz)", "Analog frequency f (Hz):", initialvalue=target_vars['f'].get(), parent=self))
            fs = float(simpledialog.askstring("Sampling freq (Hz)", "Sampling frequency fs (Hz):", initialvalue=target_vars['fs'].get(), parent=self))
            duration = float(simpledialog.askstring("Duration (s)", "Duration in seconds:", initialvalue=target_vars['duration'].get(), parent=self))
        except (TypeError, ValueError):
            messagebox.showinfo("Canceled", "Signal creation canceled or invalid input.")
            return

        # Fill into target controls
        target_vars['enabled'].set(True)
        target_vars['kind'].set(kind)
        target_vars['A'].set(str(A))
        target_vars['phase'].set(str(phase))
        target_vars['f'].set(str(f))
        target_vars['fs'].set(str(fs))
        target_vars['duration'].set(str(duration))

        self.plot_all()

    def parse_signal_from_vars(self, vars_map) -> SignalSpec:
        spec = vars_map['spec']
        try:
            spec.enabled = bool(vars_map['enabled'].get())
            spec.kind = vars_map['kind'].get()
            spec.A = float(vars_map['A'].get())
            spec.phase_deg = float(vars_map['phase'].get())
            spec.f_analog = float(vars_map['f'].get())
            spec.fs = float(vars_map['fs'].get())
            spec.duration = float(vars_map['duration'].get())
            spec.representation = vars_map['rep'].get()
        except ValueError as e:
            raise ValueError(f"Invalid parameter: {e}")
        return spec

    def check_sampling_theorem(self, spec: SignalSpec) -> bool:
        """
        Validate the Nyquist Sampling Theorem: fs >= 2 * fmax
        
        The sampling theorem states that to avoid aliasing, the sampling frequency
        must be at least twice the highest frequency component in the signal.
        
        For a sine/cosine wave with frequency f:
        - Minimum required fs = 2 * f
        - We use 2.2 * f for safety margin
        
        If violated, aliasing occurs and the signal cannot be perfectly reconstructed.
        
        Args:
            spec: SignalSpec object containing signal parameters
            
        Returns:
            bool: True if sampling theorem is satisfied or user chooses to proceed
        """
        # Check if sampling theorem is satisfied
        if spec.fs >= 2.0 * spec.f_analog:
            return True

        # Sampling theorem violated - explain the issue to the user
        msg = (
            f"⚠️ SAMPLING THEOREM VIOLATION ⚠️\n\n"
            f"Signal {spec.label}: fs = {spec.fs:.3f} Hz\n"
            f"Required minimum: 2 × f = 2 × {spec.f_analog:.3f} = {2*spec.f_analog:.3f} Hz\n\n"
            f"Current sampling rate is too low! This will cause aliasing.\n\n"
            f"Choose an action:"
        )
        
        res = messagebox.askyesnocancel(
            "Sampling Theorem Violation", 
            msg + "\n\nYes: Auto-correct fs to 2.2×f (recommended)\n"
                  "No: Proceed anyway (will show aliasing effects)\n"
                  "Cancel: Abort plotting"
        )
        
        # Handle user choice
        if res is True:
            # Auto-correct: set fs to 2.2 * f for safety margin
            old_fs = spec.fs
            spec.fs = 2.2 * spec.f_analog
            messagebox.showinfo(
                "Auto-correction Applied", 
                f"Sampling frequency corrected:\n"
                f"From: {old_fs:.3f} Hz\n"
                f"To: {spec.fs:.3f} Hz\n\n"
                f"This ensures proper signal reconstruction."
            )
            return True
        elif res is False:
            # User wants to proceed anyway (educational: shows aliasing)
            messagebox.showwarning(
                "Proceeding with Aliasing", 
                "You chose to proceed with the current settings.\n"
                "The displayed signal may show aliasing effects.\n"
                "This is useful for learning about sampling theorem!"
            )
            return True
        else:
            # User cancelled
            return False

    def generate_signal(self, spec: SignalSpec):
        """
        Generate signal data based on the signal specification.
        
        This function implements the mathematical signal generation:
        - Sine: x(t) = A * sin(2πft + φ)
        - Cosine: x(t) = A * cos(2πft + φ)
        
        Two representation modes:
        1. Continuous: Dense time grid for smooth visualization
        2. Discrete: Sampled at regular intervals (1/fs)
        
        Args:
            spec: SignalSpec object containing all signal parameters
            
        Returns:
            tuple: (time_array, amplitude_array, is_discrete_flag)
        """
        if spec.representation == 'continuous':
            # CONTINUOUS REPRESENTATION
            # Use dense time grid to create smooth, continuous-looking curve
            # This is for visualization purposes only - not actual continuous signal
            
            # Calculate number of points based on duration
            # More points = smoother curve, but slower computation
            num_pts = max(1000, int(2000 * spec.duration))
            t = np.linspace(0, spec.duration, num_pts)
            
            # Generate signal using mathematical formula
            if spec.kind == 'sine':
                y = spec.A * np.sin(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            else:  # cosine
                y = spec.A * np.cos(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            
            return t, y, False  # False = not discrete
            
        else:
            # DISCRETE REPRESENTATION
            # Sample the signal at regular intervals defined by sampling frequency
            # This represents how signals are actually digitized in real systems
            
            if spec.fs <= 0:
                raise ValueError(
                    'Sampling frequency fs must be positive for discrete representation. '
                    f'Current value: {spec.fs} Hz'
                )
            
            # Create time array with sampling interval = 1/fs
            # This gives us discrete time points: t = n/fs where n = 0, 1, 2, ...
            t = np.arange(0, spec.duration, 1.0 / spec.fs)
            
            # Generate discrete signal samples
            if spec.kind == 'sine':
                y = spec.A * np.sin(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            else:  # cosine
                y = spec.A * np.cos(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            
            return t, y, True  # True = discrete

    def plot_all(self):
        """
        Main plotting function that generates and displays signals.
        
        This function:
        1. Parses user input parameters
        2. Validates sampling theorem
        3. Generates signal data
        4. Plots signals with appropriate visualization
        
        Different plot styles:
        - Continuous: Smooth line plot
        - Discrete: Stem plot showing individual samples
        """
        # STEP 1: Parse user input parameters from GUI controls
        try:
            specA = self.parse_signal_from_vars(self.frameA_vars)
            specA.label = 'A'
            specB = self.parse_signal_from_vars(self.frameB_vars)
            specB.label = 'B'
        except ValueError as e:
            messagebox.showerror(
                "Invalid Parameters", 
                f"Please check your input values:\n{str(e)}\n\n"
                "Common issues:\n"
                "- Non-numeric values in numeric fields\n"
                "- Empty fields\n"
                "- Invalid characters"
            )
            return

        # STEP 2: Validate sampling theorem for enabled signals
        # This is crucial for understanding DSP fundamentals
        for spec in (specA, specB):
            if spec.enabled:
                ok = self.check_sampling_theorem(spec)
                if not ok:
                    return  # User cancelled or there was an error

        # STEP 3: Clear previous plot and prepare for new visualization
        self.ax.clear()
        plotted_any = False

        # STEP 4: Generate and plot Signal A (if enabled)
        if specA.enabled:
            try:
                tA, yA, dA = self.generate_signal(specA)
            except Exception as e:
                messagebox.showerror(
                    "Error Generating Signal A", 
                    f"Failed to generate Signal A:\n{str(e)}\n\n"
                    "Check your parameters and try again."
                )
                return
            
            # Choose appropriate plot style based on representation
            if dA:
                # DISCRETE: Use stem plot to show individual samples
                # This clearly shows the discrete nature of the signal
                markerline, stemlines, baseline = self.ax.stem(
                    tA, yA, 
                    label=f"Signal A ({specA.kind}) [DISCRETE]"
                )
                # Optional: Customize stem appearance for better readability
                # markerline.set_markerfacecolor('blue')
                # stemlines.set_linewidth(0.5)
            else:
                # CONTINUOUS: Use line plot for smooth curve
                self.ax.plot(tA, yA, label=f"Signal A ({specA.kind}) [CONTINUOUS]", linewidth=2)
            plotted_any = True

        # STEP 5: Generate and plot Signal B (if enabled)
        if specB.enabled:
            try:
                tB, yB, dB = self.generate_signal(specB)
            except Exception as e:
                messagebox.showerror(
                    "Error Generating Signal B", 
                    f"Failed to generate Signal B:\n{str(e)}\n\n"
                    "Check your parameters and try again."
                )
                return
            
            # Choose appropriate plot style based on representation
            if dB:
                # DISCRETE: Use stem plot
                self.ax.stem(tB, yB, label=f"Signal B ({specB.kind}) [DISCRETE]")
            else:
                # CONTINUOUS: Use line plot
                self.ax.plot(tB, yB, label=f"Signal B ({specB.kind}) [CONTINUOUS]", linewidth=2)
            plotted_any = True

        # STEP 6: Handle case when no signals are enabled
        if not plotted_any:
            self.ax.text(
                0.5, 0.5, 
                'No signals enabled\n\nEnable Signal A or B to see plots', 
                ha='center', va='center', 
                transform=self.ax.transAxes,
                fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7)
            )

        # STEP 7: Finalize plot appearance
        self.ax.set_xlabel('Time (s)', fontsize=12)
        self.ax.set_ylabel('Amplitude', fontsize=12)
        self.ax.set_title('DSP Signal Visualization', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='best')
        
        # Refresh the display
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title('Signals')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.canvas.draw()

    def example_two_signals(self):
        """
        Load example signals to demonstrate the application.
        
        This function sets up two different signals:
        - Signal A: Sine wave (continuous representation)
        - Signal B: Cosine wave (discrete representation)
        
        This example helps students understand:
        - Different signal types (sine vs cosine)
        - Different representations (continuous vs discrete)
        - Phase differences
        - Sampling theorem compliance
        """
        # Signal A: Sine wave with continuous representation
        # This demonstrates a smooth, continuous-looking signal
        self.frameA_vars['enabled'].set(True)
        self.frameA_vars['kind'].set('sine')           # Sine wave
        self.frameA_vars['A'].set('1.0')              # Amplitude = 1
        self.frameA_vars['phase'].set('0')            # No phase shift
        self.frameA_vars['f'].set('5')                # Frequency = 5 Hz
        self.frameA_vars['fs'].set('200')             # High sampling rate
        self.frameA_vars['duration'].set('1.0')       # 1 second duration
        self.frameA_vars['rep'].set('continuous')     # Continuous representation

        # Signal B: Cosine wave with discrete representation
        # This demonstrates discrete sampling and phase shift
        self.frameB_vars['enabled'].set(True)
        self.frameB_vars['kind'].set('cosine')        # Cosine wave
        self.frameB_vars['A'].set('0.7')              # Amplitude = 0.7
        self.frameB_vars['phase'].set('30')           # 30° phase shift
        self.frameB_vars['f'].set('12')               # Frequency = 12 Hz
        self.frameB_vars['fs'].set('200')             # High sampling rate (satisfies Nyquist)
        self.frameB_vars['duration'].set('1.0')       # 1 second duration
        self.frameB_vars['rep'].set('discrete')       # Discrete representation

        # Generate and display the example signals
        self.plot_all()
        
        # Show educational message
        messagebox.showinfo(
            "Example Loaded",
            "Example signals loaded successfully!\n\n"
            "Signal A: Sine wave (continuous)\n"
            "Signal B: Cosine wave (discrete)\n\n"
            "Notice the differences:\n"
            "• Continuous vs discrete visualization\n"
            "• Phase difference between sine and cosine\n"
            "• Different amplitudes and frequencies"
        )


# =============================================================================
# MAIN EXECUTION
# =============================================================================
# This section runs the application when the script is executed directly

if __name__ == '__main__':
    """
    Main execution block for the DSP Signal Processing Framework.
    
    This creates and runs the GUI application that allows students to:
    1. Generate sine and cosine signals with custom parameters
    2. Visualize signals in both continuous and discrete forms
    3. Learn about the sampling theorem through interactive validation
    4. Compare different signals side by side
    
    Educational Benefits:
    - Hands-on learning of DSP concepts
    - Visual understanding of signal properties
    - Interactive exploration of sampling theorem
    - Real-time parameter adjustment and visualization
    """
    
    try:
        # Create and start the application
        print("Starting DSP Signal Processing Framework...")
        print("=" * 50)
        print("Learning Objectives:")
        print("• Understand signal generation (sine/cosine)")
        print("• Learn sampling theorem and aliasing")
        print("• Visualize continuous vs discrete signals")
        print("• Explore signal parameters interactively")
        print("=" * 50)
        
        app = SignalApp()
        app.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Please ensure all required packages are installed:")
        print("- tkinter (usually included with Python)")
        print("- matplotlib")
        print("- numpy")