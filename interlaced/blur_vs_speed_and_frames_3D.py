import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameters
detector_x_size = 2048
r = detector_x_size / 2
exposure_times = np.arange(0.01, 0.5, 0.01)
max_blurr_error = 0.1

# Blurring error range
blurr_errors = np.arange(0.01, max_blurr_error, 0.001)
E, B = np.meshgrid(exposure_times, blurr_errors)

# --- 3D Plot 1: Max Angular Speed ---
max_speeds = np.degrees(np.arccos((r - B) / r)) / E

# --- Readout parameters ---
frame_rate_with_zero_exposure_time = 163
readout_time = 1 / frame_rate_with_zero_exposure_time

# --- Compute theta_max and total frames ---
arg = np.clip((r - B) / r, -1.0, 1.0)
theta_max_deg = np.degrees(np.arccos(arg))
N_180 = 180 * E / ((E + readout_time) * theta_max_deg)

# --- Combined Figure with two stacked 3D plots ---
fig = plt.figure(figsize=(10, 12))

# ---- Upper plot: Angular Speed ----
ax1 = fig.add_subplot(2, 1, 1, projection='3d')
surf1 = ax1.plot_surface(E, B, max_speeds, cmap='viridis', edgecolor='none')
ax1.set_xlabel('Exposure Time (s)', labelpad=10)
ax1.set_ylabel('Blurring Error (pixels)', labelpad=10)
ax1.set_zlabel('Max Angular Speed (°/s)', labelpad=10)
ax1.set_title('Maximum Angular Speed vs Exposure Time and Blur Error')
cbar1 = fig.colorbar(surf1, ax=ax1, shrink=0.6, aspect=10, pad=0.1)
cbar1.set_label('Max Angular Speed (°/s)')

# ---- Lower plot: Total Frames in 180° ----
ax2 = fig.add_subplot(2, 1, 2, projection='3d')
surf2 = ax2.plot_surface(E, B, N_180, cmap='cividis', edgecolor='none', alpha=0.95)
ax2.set_xlabel('Exposure Time (s)', labelpad=10)
ax2.set_ylabel('Blurring Error (pixels)', labelpad=10)
ax2.set_zlabel('Total Frames in 180°', labelpad=15)
ax2.set_title(f'Total Frames in 180° vs Exposure Time and Blur Error\n(readout_time = {readout_time:.6f} s)')
cbar2 = fig.colorbar(surf2, ax=ax2, shrink=0.6, aspect=10, pad=0.1)
cbar2.set_label('Frames per 180°')

plt.tight_layout()
plt.show()
