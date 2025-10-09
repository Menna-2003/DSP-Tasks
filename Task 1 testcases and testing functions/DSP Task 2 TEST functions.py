import tkinter as tk
from tkinter import filedialog, messagebox
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


indices1, values1 = read_signal_from_txt("sig1.txt")
indices2, values2 = read_signal_from_txt("sig2.txt")
plot_signal(indices1, values1, "Original Signal1")
plot_signal(indices2, values2, "Original Signal2")

# signals = [(indices1, values1), (indices2, values2)]
# indecies, values = add_signals(signals)
# plot_signal(indecies, values, "added signals")

# indecies, values = subtract_signals((indices1, values1), (indices2, values2))
# plot_signal(indecies, values, "subtracted signals")

# indecies, values = shifting_signal(indices1,values1, 2, "advance")
# plot_signal(indecies, values, "shifted signals")

# folded_indices, folded_values = fold_signal(indices1, values1)
# plot_signal(folded_indices, folded_values, "Folded Signal (x(-n))")