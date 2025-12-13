import numpy as np
import matplotlib.pyplot as plt

# Data for the additional plot
Y_rev = np.array([10, 8, 6, 4, 2, 0, -2, -4, -6, -8, -10])
dPin_francesco = np.array([74, 72, 56, 40, 32, 38, 82, 78, 76, 42, 54])
dPin_pasha = np.array([70, 65, 54, 38, 31, 35, 75, 75, 70, 35, 54])

# Subtract constant offset and convert to microns
offset = 76.5
scale = 0.345
dPin_francesco = (dPin_francesco - offset) * scale
dPin_pasha = (dPin_pasha - offset) * scale

plt.figure(figsize=(8, 5))

# Plot the ΔPin curves
plt.plot(Y_rev, dPin_francesco, marker='o', label='measurement 1')
plt.plot(Y_rev, dPin_pasha, marker='o', label='measurement 2')

# Add semi-transparent area between -1 and 1 µm
plt.fill_between(Y_rev, -1, 1, color='red', alpha=0.3, label='Spec range (-1 to 1 µm)')

plt.xlabel('Y Hexapod (mm)')
plt.ylabel('X travel error (µm)')
plt.title('Hexapod SN 451679-01: 2.1 mm X travel error')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

