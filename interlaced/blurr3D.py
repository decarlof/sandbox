import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameters
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2

# Exposure time (s) from 0.01 to 1.0 in 0.05 s steps
exposure_times = np.arange(0.01, .5, 0.01)

# set the maximum blurr error acceptable
max_blurr_error     = .1  # in pixel  

# Calculate max_speed for each exposure_time
max_speeds = np.degrees(np.arccos((r - max_blurr_error) / r)) / exposure_times

# Plot
plt.figure(figsize=(7, 5))
plt.plot(exposure_times, max_speeds, 'o-', linewidth=2)
plt.xlabel('Exposure Time (s)')
plt.ylabel('Max Angular Speed (°/s)')
plt.title('Maximum Angular Speed vs Exposure Time')
plt.legend([f'Max blur = {max_blurr_error} px'])
plt.grid(True)
plt.show()


# 3D surface plot showing how the maximum angular speed depends 
# on both exposure_time and blurr_error.

# Blurring error (pixels) from 0.1 to 1.0 in 0.1 px steps
blurr_errors = np.arange(0.01, max_blurr_error, 0.001)

# Create meshgrid
E, B = np.meshgrid(exposure_times, blurr_errors)

# Compute max angular speed (°/s)
max_speeds = np.degrees(np.arccos((r - B) / r)) / E

# 3D surface plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(E, B, max_speeds, cmap='viridis', edgecolor='none')

ax.set_xlabel('Exposure Time (s)', labelpad=10)
ax.set_ylabel('Blurring Error (pixels)', labelpad=10)
ax.set_zlabel('Max Angular Speed (°/s)', labelpad=10)
ax.set_title('Maximum Angular Speed vs Exposure Time and Blur Error')

# Move the colorbar to the right (slightly detached)
cbar = fig.colorbar(surf, shrink=0.8, aspect=10, pad=0.15)
cbar.set_label('Max Angular Speed (°/s)')
plt.tight_layout()
plt.show()

# The detector readout time depends on settings such as ROI size, binning, and bit depth.
# It can be estimated by measuring the detector frame rate with the exposure time set to zero,
# and then taking the reciprocal of that frame rate (1 / frame_rate_with_zero_exposure_time).

frame_rate_with_zero_exposure_time = 163
readout_time = 1 / frame_rate_with_zero_exposure_time

# --- Compute theta_max (degrees) ---
arg = (r - B) / r
arg = np.clip(arg, -1.0, 1.0)          # numerical safety
theta_max_deg = np.degrees(np.arccos(arg))

# --- Compute total number of frames over 180° ---
N_180 = 180 * E / ((E + readout_time) * theta_max_deg)

# --- 3D Surface plot ---
fig = plt.figure(figsize=(9, 6))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(E, B, N_180, cmap='cividis', edgecolor='none', alpha=0.95)

ax.set_xlabel('Exposure Time (s)', labelpad=10)
ax.set_ylabel('Blurring Error (pixels)', labelpad=10)
ax.set_zlabel('Total Frames in 180°', labelpad=15)
ax.set_title('Total Number of Frames in 180° vs Exposure Time and Blur Error\n(readout_time = {:.6f} s)'.format(readout_time))

cbar = fig.colorbar(surf, shrink=0.6, aspect=10, pad=0.18)
cbar.set_label('Frames per 180°')

plt.tight_layout()
plt.show()