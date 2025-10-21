# level = int(input("Enter the number of Levels: "))
# num = int(input("Enter the number of values: "))
# values = []

# print(f"Enter {num} values:")
# for i in range(num):
#     val = float(input(f"Enter value {i+1}: "))
#     values.append(val)

# min_value = min(values)
# max_value = max(values)

# delta = (max_value - min_value) / level

# mid_points = []
# z = min_value
# z_delta = min_value + delta

# while z_delta <= max_value:
#     mid = (z + z_delta) / 2
#     mid_points.append(mid)
#     z = z_delta
#     z_delta = z_delta + delta

# # eq = []
# # eq_sqr = []
# # i=0
# # sum = 0
# # for org_value in values:
# #     eq.append(  mid_points[i] - org_value)
# #     eq_sqr.append( eq[i] * eq[i] )
# #     sum += eq_sqr[i]

# quantized = []
# errors = []
# for x in values:
#     for i in range(level):
#         lower = min_value + i * delta
#         upper = lower + delta
#         if lower <= x <= upper or (i == level-1 and x == max_value):
#             q = mid_points[i]
#             quantized.append(q)
#             errors.append(q - x)
#             break

# avg_error = sum(e**2 for e in errors) / len(errors)


import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Test 1'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Test 2'))
from QuanTest1 import QuantizationTest1
from QuanTest2 import QuantizationTest2
from Task1 import read_signal_from_txt

def quantize_and_encode(values, levels=None, bits=None):
    if not values:
        raise ValueError("Values list cannot be empty.")

    if not levels and not bits:
        raise ValueError("Specify either number of levels or number of bits.")

    # Determine number of levels
    L = 2 ** int(bits) if bits else int(levels)

    # Quantization step
    min_value = min(values)
    max_value = max(values)
    delta = (max_value - min_value) / L

    # Midpoints
    mid_points = []
    z = min_value
    z_delta = min_value + delta

    while z_delta <= max_value + 1e-9:
        mid = (z + z_delta) / 2
        mid_points.append(mid)
        z = z_delta
        z_delta += delta

    # Quantize
    quantized = []
    errors = []
    for x in values:
        for i in range(L):
            lower = min_value + i * delta
            upper = lower + delta
            if lower <= x <= upper or (i == L - 1 and x == max_value):
                q = mid_points[i]
                quantized.append(round(q, 3))
                errors.append(round(q - x, 3))
                break

    # Average quantization error (MSE)
    avg_error = sum(e ** 2 for e in errors) / len(errors)

    # generate encodings and rotate backward by 1 level
    num_bits = math.ceil(math.log2(L))
    encoding = [format(i, f"0{num_bits}b") for i in range(L)]

    encoded_signal = []
    for q in quantized:
        idx = mid_points.index(min(mid_points, key=lambda m: abs(m - q)))
        encoded_signal.append(encoding[idx])

    # QuantizationTest1('Test 1/Quan1_Out.txt', encoded_signal, quantized)

    # Calculate interval indices and sampled errors
    interval_indices = []
    sampled_errors = []
    for i, x in enumerate(values):
        # Find which interval this sample belongs to
        idx = int((x - min_value) / delta)
        if idx >= L:
            idx = L - 1
        if idx < 0:
            idx = 0
        interval_indices.append(idx + 1)
        # Calculate error (quantized - original)
        error = quantized[i] - x
        sampled_errors.append(round(error, 3))
    # Debug: Print the calculated values
    print(f"Interval indices: {interval_indices}")
    print(f"Encoded signal: {encoded_signal}")
    print(f"Quantized values: {quantized}")
    print(f"Sampled errors: {sampled_errors}")
    
    QuantizationTest2('Test 2/Quan2_Out.txt', interval_indices, encoded_signal, quantized, sampled_errors)

    return {
        "levels": L,
        "delta": delta,
        "mid_points": mid_points,
        "quantized": quantized,
        "errors": errors,
        "avg_error": avg_error,
        "encoding": encoding,
        "encoded_signal": encoded_signal,
    }


import tkinter as tk
from tkinter import messagebox, filedialog

def quantize_signal():
    try:
        global selected_file_path
        if not hasattr(quantize_signal, 'selected_file_path') and 'selected_file_path' not in globals():
            messagebox.showwarning("Warning", "Please select a signal file first.")
            return
            
        file_path = globals().get('selected_file_path')
        if not file_path:
            messagebox.showwarning("Warning", "Please select a signal file first.")
            return
            
        # Read signal from file
        indices, values = read_signal_from_txt(file_path)
        values = values.tolist()  # Convert numpy array to list

        levels = entry_levels.get().strip()
        bits = entry_bits.get().strip()

        if not levels and not bits:
            messagebox.showerror("Error", "Enter either number of levels or number of bits.")
            return

        # Convert to proper types
        levels = int(levels) if levels else None
        bits = int(bits) if bits else None

        # --- Use the logic function ---
        result = quantize_and_encode(values, levels=levels, bits=bits)

        # --- Display the output ---
        output = (
            f"Input Signal: {values}\n\n"
            f"Levels (L): {result['levels']}\nΔ = {result['delta']:.3f}\n"
            f"Midpoints: {result['mid_points']}\n\n"
            f"Quantized Signal: {result['quantized']}\n"
            f"Quantization Errors: {result['errors']}\n"
            f"Average Power Error: {result['avg_error']:.6f}\n\n"
            f"Encoding per level: {result['encoding']}\n"
            f"Encoded Signal: {result['encoded_signal']}"
        )

        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, output)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_signal_file():
    file_path = filedialog.askopenfilename(
        title="Select Signal File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        # Store the selected file path for use in quantize_signal
        global selected_file_path
        selected_file_path = file_path
        messagebox.showinfo("File Selected", f"Selected: {os.path.basename(file_path)}")


# --- GUI Setup ---
selected_file_path = None
root = tk.Tk()
root.title("Signal Quantization Tool")
root.geometry("700x600")
root.configure(bg="#f5f5f5")

title = tk.Label(root, text="Signal Quantization & Encoding", font=("Arial", 16, "bold"), bg="#f5f5f5")
title.pack(pady=10)

frame_inputs = tk.Frame(root, bg="#f5f5f5")
frame_inputs.pack(pady=5)

tk.Label(frame_inputs, text="Select Signal File:", bg="#f5f5f5").grid(row=0, column=0, sticky="w")
btn_select_file = tk.Button(frame_inputs, text="Browse Signal File", command=lambda: select_signal_file(), bg="#2196F3", fg="white")
btn_select_file.grid(row=1, column=0, columnspan=2, pady=5)

tk.Label(frame_inputs, text="Number of Levels:", bg="#f5f5f5").grid(row=2, column=0, sticky="w")
entry_levels = tk.Entry(frame_inputs, width=10)
entry_levels.grid(row=2, column=1, sticky="w", pady=5)

tk.Label(frame_inputs, text="OR Number of Bits:", bg="#f5f5f5").grid(row=3, column=0, sticky="w")
entry_bits = tk.Entry(frame_inputs, width=10)
entry_bits.grid(row=3, column=1, sticky="w", pady=5)

btn_calc = tk.Button(root, text="Quantize Signal", command=quantize_signal, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20)
btn_calc.pack(pady=15)

text_output = tk.Text(root, height=18, width=100, font=("Courier", 10))
text_output.pack(padx=10, pady=10)

root.mainloop()