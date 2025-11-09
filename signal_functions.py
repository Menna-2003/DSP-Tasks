import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import os


# ========== File Reading ==========
def read_signal_from_txt(path):
    base_dir = os.path.dirname(__file__)
    file_path = path
    if not os.path.isabs(path):
        candidate = os.path.join(base_dir, path)
        if os.path.exists(candidate):
            file_path = candidate

    # Skip first 3 lines (like Task 1)
    data = np.loadtxt(file_path, skiprows=3)
    data = np.atleast_2d(data)
    indices = data[:, 0]
    values = data[:, 1]
    return indices, values


# ========== Signal Operations ==========
def moving_average(x, M):
    y = []
    for n in range(len(x)):
        start = max(0, n - M + 1)
        window = x[start:n+1]
        avg = sum(window) / len(window)
        y.append(avg)
    return y


def first_derivative(x):
    y = []
    for n in range(len(x)):
        if n == 0:
            y.append(x[0])
        else:
            y.append(x[n] - x[n - 1])
    return y


def second_derivative(x):
    y = []
    N = len(x)
    for n in range(N):
        xn_minus = x[n - 1] if n > 0 else 0
        xn_plus = x[n + 1] if n < N - 1 else 0
        y.append(xn_plus - 2 * x[n] + xn_minus)
    return y


def convolve_signals(x, h):
    Nx = len(x)
    Nh = len(h)
    y_conv = []
    for n in range(Nx + Nh - 1):
        sum_val = 0
        for k in range(Nh):
            if 0 <= n - k < Nx:
                sum_val += x[n - k] * h[k]
        y_conv.append(sum_val)
    return y_conv


# ========== Plot Helper ==========
def plot_signal(indices, values, title="Signal"):
    plt.figure()
    plt.stem(indices, values)
    plt.title(title)
    plt.xlabel("Index (n)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()


# ========== GUI ==========
class SignalAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Signal Analysis Functions")
        self.root.geometry("700x600")
        self.root.configure(bg="#f8f8f8")

        self.signals = []

        tk.Label(root, text="Signal Analysis Toolkit", font=("Arial", 18, "bold"), bg="#f8f8f8", fg="#2c3e50").pack(pady=10)
        tk.Button(root, text="Upload Signal", width=20, command=self.upload_signal).pack(pady=10)

        # Choose signal
        tk.Label(root, text="Select Signal to Process:", bg="#f8f8f8").pack(pady=5)
        self.signal_var = tk.StringVar()
        self.signal_combo = ttk.Combobox(root, textvariable=self.signal_var, state="readonly")
        self.signal_combo.pack(pady=5)
        tk.Button(root, text="Plot Selected Signal", command=self.plot_selected).pack(pady=5)

        # Moving Average
        frame1 = tk.Frame(root, bg="#f8f8f8")
        frame1.pack(pady=10)
        tk.Label(frame1, text="Moving Average (M):", bg="#f8f8f8").grid(row=0, column=0)
        self.M_var = tk.StringVar(value="3")
        tk.Entry(frame1, textvariable=self.M_var, width=10).grid(row=0, column=1, padx=5)
        tk.Button(frame1, text="Apply", command=self.apply_moving_avg).grid(row=0, column=2, padx=5)

        # Derivatives
        tk.Button(root, text="First Derivative", width=20, command=self.apply_first_derivative).pack(pady=5)
        tk.Button(root, text="Second Derivative", width=20, command=self.apply_second_derivative).pack(pady=5)

        # Convolution
        frame2 = tk.Frame(root, bg="#f8f8f8")
        frame2.pack(pady=10)

        tk.Label(frame2, text="Select Signal 1:", bg="#f8f8f8").grid(row=0, column=0, padx=5)
        self.conv_sig1_var = tk.StringVar()
        self.conv_sig1_combo = ttk.Combobox(frame2, textvariable=self.conv_sig1_var, state="readonly", width=15)
        self.conv_sig1_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame2, text="Select Signal 2:", bg="#f8f8f8").grid(row=0, column=2, padx=5)
        self.conv_sig2_var = tk.StringVar()
        self.conv_sig2_combo = ttk.Combobox(frame2, textvariable=self.conv_sig2_var, state="readonly", width=15)
        self.conv_sig2_combo.grid(row=0, column=3, padx=5)

        tk.Button(frame2, text="Apply Convolution", command=self.apply_convolution).grid(row=0, column=4, padx=10)

    # ===== Functions =====
    def upload_signal(self):
        path = filedialog.askopenfilename(title="Select Signal File", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                indices, values = read_signal_from_txt(path)
                self.signals.append((indices, values))
                # items = [f"Signal {i+1}" for i in range(len(self.signals))]
                # self.signal_combo["values"] = items
                # self.signal_var.set(items[-1])
                items = [f"Signal {i+1}" for i in range(len(self.signals))]
                self.signal_combo["values"] = items
                self.signal_var.set(items[-1])
                self.conv_sig1_combo["values"] = items
                self.conv_sig2_combo["values"] = items


                messagebox.showinfo("Success", f"Loaded {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load signal:\n{e}")

    def get_signal(self):
        if not self.signal_var.get():
            messagebox.showwarning("Warning", "Please select a signal first")
            return None
        idx = int(self.signal_var.get().split()[-1]) - 1
        return self.signals[idx]

    def plot_selected(self):
        sig = self.get_signal()
        if sig:
            plot_signal(sig[0], sig[1], self.signal_var.get())

    def apply_moving_avg(self):
        sig = self.get_signal()
        if not sig:
            return
        try:
            M = int(self.M_var.get())
        except ValueError:
            messagebox.showerror("Error", "M must be an integer")
            return
        result = moving_average(sig[1], M)
        plot_signal(sig[0], result, f"{self.signal_var.get()} Moving Average (M={M})")

    def apply_first_derivative(self):
        sig = self.get_signal()
        if not sig:
            return
        result = first_derivative(sig[1])
        plot_signal(sig[0], result, f"{self.signal_var.get()} First Derivative")

    def apply_second_derivative(self):
        sig = self.get_signal()
        if not sig:
            return
        result = second_derivative(sig[1])
        plot_signal(sig[0], result, f"{self.signal_var.get()} Second Derivative")

    def apply_convolution(self):
        sig1_name = self.conv_sig1_var.get()
        sig2_name = self.conv_sig2_var.get()

        if not sig1_name or not sig2_name:
            messagebox.showwarning("Warning", "Please select both signals for convolution.")
            return

        idx1 = int(sig1_name.split()[-1]) - 1
        idx2 = int(sig2_name.split()[-1]) - 1

        if idx1 == idx2:
            messagebox.showwarning("Warning", "Select two different signals for convolution.")
            return

        try:
            indices1, values1 = self.signals[idx1]
            indices2, values2 = self.signals[idx2]

            y = convolve_signals(values1, values2)
            new_indices = np.arange(indices1[0] + indices2[0],
                                    indices1[-1] + indices2[-1] + 1)

            plot_signal(new_indices, y, f"Convolution: {sig1_name} * {sig2_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply convolution:\n{e}")


# ========== Run ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = SignalAnalysisApp(root)
    root.mainloop()
