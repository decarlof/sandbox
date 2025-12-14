import numpy as np
import matplotlib.pyplot as plt

# Data for the additional plot
Y_rev = np.array([10, 8, 6, 4, 2, 0, -2, -4, -6, -8, -10])
dPin_francesco = np.array([74, 72, 56, 40, 32, 38, 82, 78, 76, 42, 54])
dPin_pasha = np.array([70, 65, 54, 38, 31, 35, 75, 75, 70, 35, 54])

# Subtract constant offset
offset = 76.5
dPin_francesco = (dPin_francesco - offset) * 0.345
dPin_pasha = (dPin_pasha - offset) * 0.345

plt.figure(figsize=(8, 5))

plt.plot(Y_rev, dPin_francesco, marker='o', label='ΔPin Francesco')
plt.plot(Y_rev, dPin_pasha, marker='o', label='ΔPin Pasha')

plt.xlabel('Y Hexapod (mm)')
plt.ylabel('ΔPin (µm)')
plt.title('X travel error when moving from 0 to 2.1 mm — Francesco vs Pasha (Y = 2.1)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

