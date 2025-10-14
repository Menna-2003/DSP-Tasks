import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import math


@dataclass
class SignalSpec:
    enabled: bool = False
    kind: str = "sine"
    A: float = 1.0
    phase_deg: float = 0.0
    f_analog: float = 5.0
    fs: float = 100.0
    duration: float = 1.0
    representation: str = "continuous"
    label: str = "Signal"

    def phase_rad(self) -> float:
        return math.radians(self.phase_deg)


class SignalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DSP Task 2: Signal Processing Framework")
        self.geometry("1100x700")

        self.sigA = SignalSpec(enabled=True, label="A")
        self.sigB = SignalSpec(enabled=False, label="B")

        # Top controls
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        self.active_signal_var = tk.StringVar(value="A")
        ttk.Label(top_frame, text="Active signal:").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="A", variable=self.active_signal_var, value="A").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="B", variable=self.active_signal_var, value="B").pack(side=tk.LEFT)

        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        gen_menu = tk.Menu(menubar, tearoff=0)
        gen_menu.add_command(label="Sine Wave", command=lambda: self.open_gen_dialog('sine'))
        gen_menu.add_command(label="Cosine Wave", command=lambda: self.open_gen_dialog('cosine'))
        menubar.add_cascade(label="Signal Generation", menu=gen_menu)

        # Control panels
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        self.frameA_vars = self.build_signal_controls(control_frame, "Signal A", self.sigA)
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self.frameB_vars = self.build_signal_controls(control_frame, "Signal B", self.sigB)

        # Plot area
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

        self.plot_all()

    def build_signal_controls(self, parent, title, spec: SignalSpec):
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
            'enabled': enabled_var, 'kind': kind_var, 'A': A_var, 'phase': phase_var,
            'f': f_var, 'fs': fs_var, 'duration': dur_var, 'rep': rep_var,
            'frame': frame, 'spec': spec,
        }

    def open_gen_dialog(self, kind: str):
        active = self.active_signal_var.get()
        target_vars = self.frameA_vars if active == 'A' else self.frameB_vars

        try:
            A = float(simpledialog.askstring("Amplitude", "Amplitude A:", initialvalue=target_vars['A'].get(), parent=self))
            phase = float(simpledialog.askstring("Phase (deg)", "Phase in degrees:", initialvalue=target_vars['phase'].get(), parent=self))
            f = float(simpledialog.askstring("Analog freq (Hz)", "Analog frequency f (Hz):", initialvalue=target_vars['f'].get(), parent=self))
            fs = float(simpledialog.askstring("Sampling freq (Hz)", "Sampling frequency fs (Hz):", initialvalue=target_vars['fs'].get(), parent=self))
            duration = float(simpledialog.askstring("Duration (s)", "Duration in seconds:", initialvalue=target_vars['duration'].get(), parent=self))
        except (TypeError, ValueError):
            messagebox.showinfo("Canceled", "Signal creation canceled or invalid input.")
            return

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
        if spec.fs >= 2.0 * spec.f_analog:
            return True

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
        
        if res is True:
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
            messagebox.showwarning(
                "Proceeding with Aliasing", 
                "You chose to proceed with the current settings.\n"
                "The displayed signal may show aliasing effects.\n"
                "This is useful for learning about sampling theorem!"
            )
            return True
        else:
            return False

    def generate_signal(self, spec: SignalSpec):
        if spec.representation == 'continuous':
            num_pts = max(1000, int(2000 * spec.duration))
            t = np.linspace(0, spec.duration, num_pts)
            
            if spec.kind == 'sine':
                y = spec.A * np.sin(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            else:
                y = spec.A * np.cos(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            
            return t, y, False
        else:
            if spec.fs <= 0:
                raise ValueError(f'Sampling frequency fs must be positive for discrete representation. Current value: {spec.fs} Hz')
            
            t = np.arange(0, spec.duration, 1.0 / spec.fs)
            
            if spec.kind == 'sine':
                y = spec.A * np.sin(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            else:
                y = spec.A * np.cos(2 * np.pi * spec.f_analog * t + spec.phase_rad())
            
            return t, y, True

    def plot_all(self):
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

        for spec in (specA, specB):
            if spec.enabled:
                ok = self.check_sampling_theorem(spec)
                if not ok:
                    return

        self.ax.clear()
        plotted_any = False

        if specA.enabled:
            try:
                tA, yA, dA = self.generate_signal(specA)
            except Exception as e:
                messagebox.showerror("Error Generating Signal A", f"Failed to generate Signal A:\n{str(e)}\n\nCheck your parameters and try again.")
                return
            
            if dA:
                self.ax.stem(tA, yA, label=f"Signal A ({specA.kind}) [DISCRETE]")
            else:
                self.ax.plot(tA, yA, label=f"Signal A ({specA.kind}) [CONTINUOUS]", linewidth=2)
            plotted_any = True

        if specB.enabled:
            try:
                tB, yB, dB = self.generate_signal(specB)
            except Exception as e:
                messagebox.showerror("Error Generating Signal B", f"Failed to generate Signal B:\n{str(e)}\n\nCheck your parameters and try again.")
                return
            
            if dB:
                self.ax.stem(tB, yB, label=f"Signal B ({specB.kind}) [DISCRETE]")
            else:
                self.ax.plot(tB, yB, label=f"Signal B ({specB.kind}) [CONTINUOUS]", linewidth=2)
            plotted_any = True

        if not plotted_any:
            self.ax.text(
                0.5, 0.5, 
                'No signals enabled\n\nEnable Signal A or B to see plots', 
                ha='center', va='center', 
                transform=self.ax.transAxes,
                fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7)
            )

        self.ax.set_xlabel('Time (s)', fontsize=12)
        self.ax.set_ylabel('Amplitude', fontsize=12)
        self.ax.set_title('DSP Signal Visualization', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='best')
        
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title('Signals')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.canvas.draw()

    def example_two_signals(self):
        self.frameA_vars['enabled'].set(True)
        self.frameA_vars['kind'].set('sine')
        self.frameA_vars['A'].set('1.0')
        self.frameA_vars['phase'].set('0')
        self.frameA_vars['f'].set('5')
        self.frameA_vars['fs'].set('200')
        self.frameA_vars['duration'].set('1.0')
        self.frameA_vars['rep'].set('continuous')

        self.frameB_vars['enabled'].set(True)
        self.frameB_vars['kind'].set('cosine')
        self.frameB_vars['A'].set('0.7')
        self.frameB_vars['phase'].set('30')
        self.frameB_vars['f'].set('12')
        self.frameB_vars['fs'].set('200')
        self.frameB_vars['duration'].set('1.0')
        self.frameB_vars['rep'].set('discrete')

        self.plot_all()
        
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


if __name__ == '__main__':
    try:
        print("Starting DSP Signal Processing Framework...")
        app = SignalApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Please ensure all required packages are installed:")
        print("- tkinter (usually included with Python)")
        print("- matplotlib")
        print("- numpy")