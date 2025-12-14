import numpy as np
import matplotlib.pyplot as plt

# Data
Y_2mm = np.array([-10, 0, 2, 4, 6, 8, 10])
dPin_2mm = np.array([20, 22, 24, 14, 27, 31, 33])

Y_19mm = np.array([-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10])
dPin_19mm = np.array([19, 19, 30, 30, 33, 30, 21, 18, 25, 26, 34])

# Multiply dPin values by 2 (binning correction)
dPin_2mm = dPin_2mm * 2
dPin_19mm = dPin_19mm * 2

plt.figure(figsize=(8, 5))

# Plot for ΔX = 2 mm (commented out)
# plt.plot(Y_2mm, dPin_2mm, marker='o', linestyle='-', label='ΔX = 2 mm (doubled)')

# Plot for ΔX = 1.9 mm
plt.plot(Y_19mm, dPin_19mm, marker='o', linestyle='-', label='ΔX = 1.9 mm')

plt.xlabel('Y Hexapod (mm)')
plt.ylabel('ΔPin (pixels)')
plt.title('ΔPin vs Y Hexapod for ΔX = 1.9 mm')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

