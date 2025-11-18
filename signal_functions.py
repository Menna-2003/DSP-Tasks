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
    N = len(x)
    if M > N:
        raise ValueError("Window size M cannot exceed signal length")

    y = np.zeros(N - M + 1)
    for n in range(len(y)):
        window = x[n:n + M]
        y[n] = np.sum(window) / M

    return y


def first_derivative(x):
    y = []
    for n in range(len(x) - 1):
        y.append(x[n + 1] - x[n])
    return y


def second_derivative(x):
    y = []
    for n in range(len(x) - 2):
        y.append(x[n + 2] - 2 * x[n + 1] + x[n])
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
            messagebox.showerror("Error", "Window size M must be an integer")
            return

        indices, values = sig
        result = moving_average(values, M)

        # --- Locate correct reference test file based on M ---
        base_dir = os.path.dirname(__file__)
        if M == 3:
            ref_filename = "MovingAvg_out1.txt"
        elif M == 5:
            ref_filename = "MovingAvg_out2.txt"
        else:
            ref_filename = None

        # --- Perform comparison if reference file exists ---
        if ref_filename:
            ref_path = os.path.join(base_dir, "task5", "testcases", "Moving Average testcases", ref_filename)

            # If not found, search recursively
            if not os.path.exists(ref_path):
                found = None
                search_root = os.path.join(base_dir, "task5", "testcases")
                for root, dirs, files in os.walk(search_root):
                    for file in files:
                        if file.lower() == ref_filename.lower():
                            found = os.path.join(root, file)
                            break
                    if found:
                        break
                if found:
                    ref_path = found
                else:
                    messagebox.showerror(
                        "Error",
                        f"Reference file '{ref_filename}' not found anywhere under:\n{search_root}"
                    )
                    return

            # --- Load and compare reference ---
            ref_indices, ref_values = read_signal_from_txt(ref_path)
            min_len = min(len(result), len(ref_values))
            result_trimmed = np.array(result[:min_len])
            ref_trimmed = np.array(ref_values[:min_len])

            print("result_trimmed: ", result_trimmed)
            print("ref_trimmed: ", ref_trimmed)
            if np.allclose(result_trimmed, ref_trimmed, atol=1e-3):
                messagebox.showinfo("Success", f"Moving Average (M={M}) matches {ref_filename}!")
            else:
                messagebox.showerror("Mismatch", f"Moving Average (M={M}) does NOT match {ref_filename}.")

            # --- Plot comparison ---
            plt.figure()
            plt.stem(indices[:min_len], result_trimmed, linefmt='b-', markerfmt='bo',
                    basefmt='k-', label=f'Computed MA (M={M})')
            plt.stem(ref_indices[:min_len], ref_trimmed, linefmt='r--', markerfmt='rx',
                    basefmt='k-', label=f'Expected ({ref_filename})')
            plt.title(f"{self.signal_var.get()} - Moving Average Comparison (M={M})")
            plt.xlabel("Index (n)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.show()

        else:
            # No reference file for other M values
            plot_signal(indices, result, f"{self.signal_var.get()} Moving Average (M={M})")
            messagebox.showinfo(
                "Info",
                f"Moving Average (M={M}) computed.\nNo reference test case exists for this window size."
            )

    def apply_first_derivative(self):
        sig = self.get_signal()
        if not sig:
            return
        try:
            indices, values = sig
            result = first_derivative(values)

            # --- Locate reference output file ---
            base_dir = os.path.dirname(__file__)
            ref_path = os.path.join(base_dir, "task5", "testcases", "Derivative testcases", "1st_derivative_out.txt")

            # If not found, search automatically inside testcases/
            if not os.path.exists(ref_path):
                found = None
                search_root = os.path.join(base_dir, "task5", "testcases")
                for root, dirs, files in os.walk(search_root):
                    for file in files:
                        if file.lower() == "1st_derivative_out.txt":
                            found = os.path.join(root, file)
                            break
                    if found:
                        break

                if found:
                    ref_path = found
                else:
                    messagebox.showerror(
                        "Error",
                        "Reference file '1st_derivative_out.txt' not found under:\n"
                        f"{search_root}"
                    )
                    return

            # --- Load reference ---
            ref_indices, ref_values = read_signal_from_txt(ref_path)

            # Compare computed and reference
            min_len = min(len(result), len(ref_values))
            result_trimmed = np.array(result[:min_len])
            ref_trimmed = np.array(ref_values[:min_len])

            if np.allclose(result_trimmed, ref_trimmed, atol=1e-6):
                messagebox.showinfo("Success", "First derivative matches the reference output!")
            else:
                messagebox.showerror("Mismatch", "First derivative does NOT match the expected output.")

            # --- Plot comparison ---
            plt.figure()
            plt.stem(indices[:min_len], result_trimmed, linefmt='b-', markerfmt='bo',
                     basefmt='k-', label='Computed 1st Derivative')
            plt.stem(ref_indices[:min_len], ref_trimmed, linefmt='r--', markerfmt='rx',
                     basefmt='k-', label='Expected (1st_derivative_out.txt)')
            plt.title(f"{self.signal_var.get()} - First Derivative Comparison")
            plt.xlabel("Index (n)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply first derivative:\n{e}")

    def apply_second_derivative(self):
        sig = self.get_signal()
        if not sig:
            return
        try:
            indices, values = sig
            result = second_derivative(values)

            # --- Locate reference output file ---
            base_dir = os.path.dirname(__file__)
            ref_path = os.path.join(base_dir, "task5", "testcases", "Derivative testcases", "2nd_derivative_out.txt")

            # If not found, search automatically inside testcases/
            if not os.path.exists(ref_path):
                found = None
                search_root = os.path.join(base_dir, "task5", "testcases")
                for root, dirs, files in os.walk(search_root):
                    for file in files:
                        if file.lower() == "2nd_derivative_out.txt":
                            found = os.path.join(root, file)
                            break
                    if found:
                        break

                if found:
                    ref_path = found
                else:
                    messagebox.showerror(
                        "Error",
                        "Reference file '2nd_derivative_out.txt' not found under:\n"
                        f"{search_root}"
                    )
                    return

            # --- Load reference ---
            ref_indices, ref_values = read_signal_from_txt(ref_path)

            # Compare computed and reference
            min_len = min(len(result), len(ref_values))
            result_trimmed = np.array(result[:min_len])
            ref_trimmed = np.array(ref_values[:min_len])

            if np.allclose(result_trimmed, ref_trimmed, atol=1e-6):
                messagebox.showinfo("Success", "Second derivative matches the reference output!")
            else:
                messagebox.showerror("Mismatch", "Second derivative does NOT match the expected output.")

            # --- Plot comparison ---
            plt.figure()
            plt.stem(indices[:min_len], result_trimmed, linefmt='b-', markerfmt='bo',
                     basefmt='k-', label='Computed 2nd Derivative')
            plt.stem(ref_indices[:min_len], ref_trimmed, linefmt='r--', markerfmt='rx',
                     basefmt='k-', label='Expected (2nd_derivative_out.txt)')
            plt.title(f"{self.signal_var.get()} - Second Derivative Comparison")
            plt.xlabel("Index (n)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply second derivative:\n{e}")

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

            # Perform convolution
            y = convolve_signals(values1, values2)
            new_indices = np.arange(indices1[0] + indices2[0],
                                    indices1[-1] + indices2[-1] + 1)

            # --- Locate reference output file ---
            base_dir = os.path.dirname(__file__)
            ref_path = os.path.join(base_dir, "task5", "testcases", "Convolution testcases", "Conv_output.txt")

            # If not found, search automatically inside testcases/
            if not os.path.exists(ref_path):
                found = None
                search_root = os.path.join(base_dir, "task5", "testcases")
                for root, dirs, files in os.walk(search_root):
                    for file in files:
                        if file.lower() == "conv_output.txt":
                            found = os.path.join(root, file)
                            break
                    if found:
                        break

                if found:
                    ref_path = found
                else:
                    messagebox.showerror(
                        "Error",
                        "Reference file 'Conv_output.txt' not found anywhere under:\n"
                        f"{search_root}"
                    )
                    return

            # --- Load reference output ---
            ref_indices, ref_values = read_signal_from_txt(ref_path)

            # Ensure both have the same length for comparison
            min_len = min(len(y), len(ref_values))
            y_trimmed = np.array(y[:min_len])
            ref_trimmed = np.array(ref_values[:min_len])

            # --- Compare results ---
            if np.allclose(y_trimmed, ref_trimmed, atol=1e-6):
                messagebox.showinfo("Success", "Convolution result matches the test case output!")
            else:
                messagebox.showerror("Mismatch", "Convolution result does NOT match the expected output.")

            # --- Plot comparison ---
            plt.figure()
            plt.stem(new_indices[:min_len], y_trimmed, linefmt='b-', markerfmt='bo',
                     basefmt='k-', label='Computed Output')
            plt.stem(ref_indices[:min_len], ref_trimmed, linefmt='r--', markerfmt='rx',
                     basefmt='k-', label='Expected Output (Conv_output.txt)')
            plt.title(f"Convolution Comparison: {sig1_name} * {sig2_name}")
            plt.xlabel("Index (n)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply convolution:\n{e}")

# ========== Run ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = SignalAnalysisApp(root)
    root.mainloop()
