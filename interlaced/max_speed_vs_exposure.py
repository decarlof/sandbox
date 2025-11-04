import numpy as np
import matplotlib.pyplot as plt

# ------------------------
# Parameters
# ------------------------
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2  # detector radius in pixels

# Exposure times (s)
exposure_times = np.arange(0., 0.5, 0.01)

# Maximum allowed blur (pixels)
set_blur = 0.5  # pixels

# Detector readout time (s)
frame_rate_with_zero_exposure_time = 160  # Hz
readout_time = 1 / frame_rate_with_zero_exposure_time

# ------------------------
# Calculate max allowed angle from blur
# ------------------------
theta_max_deg = np.degrees(np.arccos((r - set_blur) / r))  # max angle in degrees

# ------------------------
# Effective angular speed including readout overhead
# ------------------------
time_per_frame = exposure_times + readout_time
effective_speed_deg = theta_max_deg / time_per_frame  # °/s
effective_speed_rad = np.radians(effective_speed_deg)  # rad/s

# ------------------------
# Effective blur during exposure (in pixels)
# ------------------------
theta_during_exposure_rad = effective_speed_rad * exposure_times
effective_blur_px = r * (1 - np.cos(theta_during_exposure_rad))

# ------------------------
# Plot
# ------------------------
plt.figure(figsize=(8, 5))
plt.plot(exposure_times, effective_speed_deg, 'o-', linewidth=2,
         label=f'Set blur = {set_blur} px\nEffective blur = {effective_blur_px[0]:.2f}–{effective_blur_px[-1]:.2f} px\nReadout time = {readout_time:.4f} s')
plt.xlabel('Exposure Time (s)')
plt.ylabel('Effective Angular Speed (°/s)')
plt.title('Effective Maximum Angular Speed vs Exposure Time')
plt.legend()
plt.grid(True)
plt.show()
