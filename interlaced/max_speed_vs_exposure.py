import numpy as np
import matplotlib.pyplot as plt

# Parameters
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2

# Exposure time (s) from 0.01 to 0.5 in 0.01 s steps
exposure_times = np.arange(0.01, 0.5, 0.01)

# Set the maximum blur error acceptable
max_blurr_error = 0.1  # in pixel

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
