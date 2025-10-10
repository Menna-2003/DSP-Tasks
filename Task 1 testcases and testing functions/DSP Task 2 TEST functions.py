import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
import os


def read_signal_from_txt(path):
  base_dir = os.path.dirname(__file__)
  file_path = path
  if not os.path.isabs(path):
      candidate = os.path.join(base_dir, path)
      if os.path.exists(candidate):
          file_path = candidate
  with open(file_path, 'r') as f:
      N = int(f.readline().strip())
      data = np.loadtxt(f)               # Read the rest (indices + values)

  data = np.atleast_2d(data)
  indices = data[:, 0]
  values = data[:, 1]
  return indices, values

def plot_signal(indices, values, title="Signal"):
  plt.figure()
  plt.stem(indices, values)
  plt.title(title)
  plt.xlabel("Index (n)")
  plt.ylabel("Amplitude")
  plt.grid(True)
  plt.show()

def add_signals(signals):
  indices, values = signals[0]
  result_indices = indices.copy()
  result_values = values.copy()
  
  for s_indices, s_values in signals[1:]:
      for i, idx in enumerate(s_indices):
          if idx in result_indices:
              pos = np.where(result_indices == idx)[0][0]
              result_values[pos] += s_values[i]
          else:
              # If new index → append it
              result_indices = np.append(result_indices, idx)
              result_values = np.append(result_values, s_values[i])

  return result_indices, result_values

def multiply_signal(indices, values, constant):
  return indices, values * constant

def subtract_signals(sig1, sig2):
  inverted_sig2 = (sig2[0], -1 * sig2[1])
  return add_signals([sig1, inverted_sig2])

def shifting_signal(indices, values, k, method):
  if method == "delay":
    delayed_indices = indices + k
    return delayed_indices, values
  
  elif method == "advance":
    advanced_indices = indices - k
    return advanced_indices, values

def fold_signal(indices, values):
  """
  Fold (reverse) the signal → x(-n)
  """
  folded_indices = -indices
  # print("folded_indicies",folded_indices)
  sort_order = np.argsort(folded_indices)
  # print(" sort_order",folded_indices)
  folded_indices = folded_indices[sort_order]
  # print("folded_indices",folded_indices)
  folded_values = values[sort_order]
  # print("folded_values",folded_values)
  return folded_indices, folded_values

class SignalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Signal Processing UI")
        self.root.geometry("750x600")
        self.root.configure(bg="#e9f7ef")
        self.signals = []

        # Upload button
        tk.Button(root, text="Upload Signal", width=20, command=self.upload_signal).pack(pady=10)

        # Combobox (general plotting)
        tk.Label(root, text="Choose a Signal to Plot:").pack(pady=5)
        self.signal_var = tk.StringVar()
        self.signal_combo = ttk.Combobox(root, textvariable=self.signal_var, state="readonly")
        self.signal_combo.pack(pady=5)
        tk.Button(root, text="Plot Selected Signal", width=25, command=self.plot_selected).pack(pady=10)

        # ==== ADD/SUBTRACT FRAME ====
        addsub_frame = tk.Frame(root, bg="#e9f7ef")
        addsub_frame.pack(pady=10)

        tk.Label(addsub_frame, text="Choose Signal A:").grid(row=0, column=0, padx=5)
        self.addsub1_var = tk.StringVar(root)
        self.addsub1_combo = ttk.Combobox(addsub_frame, textvariable=self.addsub1_var, state="readonly", width=15)
        self.addsub1_combo.grid(row=0, column=1, padx=5)

        tk.Label(addsub_frame, text="Choose Signal B:").grid(row=1, column=0, padx=5)
        self.addsub2_var = tk.StringVar(root)
        self.addsub2_combo = ttk.Combobox(addsub_frame, textvariable=self.addsub2_var, state="readonly", width=15)
        self.addsub2_combo.grid(row=1, column=1, padx=5)

        tk.Button(addsub_frame, text="Add A + B", width=15, command=self.add).grid(row=2, column=0, pady=5)
        tk.Button(addsub_frame, text="Subtract A - B", width=15, command=self.subtract).grid(row=2, column=1, pady=5)

        # ==== MULTIPLY FRAME ====
        mult_frame = tk.Frame(root, bg="#e9f7ef")
        mult_frame.pack(pady=10, fill="x")

        tk.Label(mult_frame, text="Multiply - Choose Signal:").grid(row=0, column=0, padx=5, sticky="w")
        self.multiply_signal_var = tk.StringVar(root)
        self.multiply_signal_combo = ttk.Combobox(mult_frame, textvariable=self.multiply_signal_var, state="readonly", width=15)
        self.multiply_signal_combo.grid(row=0, column=1, padx=5)

        tk.Label(mult_frame, text="Constant:").grid(row=0, column=2, padx=5, sticky="e")
        self.multiply_var = tk.StringVar(value="1")
        tk.Entry(mult_frame, textvariable=self.multiply_var, width=10).grid(row=0, column=3, padx=5)
        tk.Button(mult_frame, text="Apply Multiply", width=15, command=self.apply_multiply).grid(row=0, column=4, padx=5)

        # ==== SHIFT FRAME ====
        shift_frame = tk.Frame(root, bg="#e9f7ef")
        shift_frame.pack(pady=10, fill="x")

        tk.Label(shift_frame, text="Shift - Choose Signal:").grid(row=0, column=0, padx=5, sticky="w")
        self.shift_signal_var = tk.StringVar(root)
        self.shift_signal_combo = ttk.Combobox(shift_frame, textvariable=self.shift_signal_var, state="readonly", width=15)
        self.shift_signal_combo.grid(row=0, column=1, padx=5)

        tk.Label(shift_frame, text="k:").grid(row=0, column=2, padx=5, sticky="e")
        self.shift_k_var = tk.StringVar(value="0")
        tk.Entry(shift_frame, textvariable=self.shift_k_var, width=10).grid(row=0, column=3, padx=5)

        tk.Label(shift_frame, text="Method:").grid(row=0, column=4, padx=5, sticky="e")
        self.shift_method_var = tk.StringVar(value="advance")
        tk.Entry(shift_frame, textvariable=self.shift_method_var, width=12).grid(row=0, column=5, padx=5)

        tk.Button(shift_frame, text="Apply Shift", width=15, command=self.apply_shift).grid(row=0, column=6, padx=5)

        # ==== FOLD FRAME ====
        fold_frame = tk.Frame(root, bg="#e9f7ef")
        fold_frame.pack(pady=10, fill="x")

        tk.Label(fold_frame, text="Fold - Choose Signal:").grid(row=0, column=0, padx=5, sticky="w")
        self.fold_signal_var = tk.StringVar(root)
        self.fold_signal_combo = ttk.Combobox(fold_frame, textvariable=self.fold_signal_var, state="readonly", width=15)
        self.fold_signal_combo.grid(row=0, column=1, padx=5)
        tk.Button(fold_frame, text="Apply Fold", width=15, command=self.apply_fold).grid(row=0, column=2, padx=5)

    # ==== Other methods (same as before) ====
    def upload_signal(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            try:
                sig = read_signal_from_txt(path)
                self.signals.append(sig)

                items = [f"Signal {i+1}" for i in range(len(self.signals))]
                self.signal_combo["values"] = items
                self.signal_var.set(items[-1])

                self.addsub1_combo["values"] = items
                self.addsub2_combo["values"] = items
                self.multiply_signal_combo["values"] = items
                self.shift_signal_combo["values"] = items
                self.fold_signal_combo["values"] = items

                messagebox.showinfo("Success", f"Loaded {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def plot_selected(self):
        if not self.signal_var.get():
            messagebox.showwarning("Warning", "Please select a signal first")
            return
        idx = int(self.signal_var.get().split()[-1]) - 1
        indices, values = self.signals[idx]
        plot_signal(indices, values, self.signal_var.get())

    def get_signal(self, var):
        if not var.get():
            return None
        idx = int(var.get().split()[-1]) - 1
        return self.signals[idx]

    def add(self):
        sig1 = self.get_signal(self.addsub1_var)
        sig2 = self.get_signal(self.addsub2_var)
        if sig1 and sig2:
            idx, val = add_signals([sig1, sig2])
            plot_signal(idx, val, "Signal A + Signal B")

    def subtract(self):
        sig1 = self.get_signal(self.addsub1_var)
        sig2 = self.get_signal(self.addsub2_var)
        if sig1 and sig2:
            idx, val = subtract_signals(sig1, sig2)
            plot_signal(idx, val, "Signal A - Signal B")

    def apply_multiply(self):
        sig = self.get_signal(self.multiply_signal_var)
        if not sig:
            messagebox.showwarning("Warning", "Please select a signal for multiplication")
            return
        try:
            constant = float(self.multiply_var.get())
        except ValueError:
            messagebox.showerror("Error", "Multiply value must be a number")
            return
        out_idx, out_val = multiply_signal(sig[0], sig[1], constant)
        plot_signal(out_idx, out_val, f"{self.multiply_signal_var.get()} * {constant}")

    def apply_shift(self):
        sig = self.get_signal(self.shift_signal_var)
        if not sig:
            messagebox.showwarning("Warning", "Please select a signal for shifting")
            return
        try:
            k = int(self.shift_k_var.get())
        except ValueError:
            messagebox.showerror("Error", "Shift k must be an integer")
            return
        method = self.shift_method_var.get().strip().lower()
        if method not in ("advance", "delay"):
            messagebox.showerror("Error", "Method must be 'advance' or 'delay'")
            return
        out_idx, out_val = shifting_signal(sig[0], sig[1], k, method)
        plot_signal(out_idx, out_val, f"{self.shift_signal_var.get()} shift {k} ({method})")

    def apply_fold(self):
        sig = self.get_signal(self.fold_signal_var)
        if not sig:
            messagebox.showwarning("Warning", "Please select a signal for folding")
            return
        out_idx, out_val = fold_signal(sig[0], sig[1])
        plot_signal(out_idx, out_val, f"Folded {self.fold_signal_var.get()}")
        

# ---------------- Run ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SignalApp(root)
    root.mainloop()



# indices1, values1 = read_signal_from_txt("sig1.txt")
# indices2, values2 = read_signal_from_txt("sig2.txt")
# plot_signal(indices1, values1, "Original Signal1")
# plot_signal(indices2, values2, "Original Signal2")

# signals = [(indices1, values1), (indices2, values2)]
# indecies, values = add_signals(signals)
# plot_signal(indecies, values, "added signals")

# indecies, values = subtract_signals((indices1, values1), (indices2, values2))
# plot_signal(indecies, values, "subtracted signals")

# indecies, values = shifting_signal(indices1,values1, 2, "advance")
# plot_signal(indecies, values, "shifted signals")

# folded_indices, folded_values = fold_signal(indices1, values1)
# plot_signal(folded_indices, folded_values, "Folded Signal (x(-n))")
