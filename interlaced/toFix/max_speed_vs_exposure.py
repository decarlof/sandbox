import numpy as np
import matplotlib.pyplot as plt

# ------------------------
# Parameters
# ------------------------
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2  # detector radius in pixels

# Exposure times (s)
exposure_times = np.arange(0.01, 0.5, 0.01)

# Maximum allowed blur (pixels)
set_blur = 0.5  # pixels

# ------------------------
# Calculate max allowed angle from blur
# ------------------------
theta_exposure_time = np.degrees(np.arccos((r - set_blur) / r))  # theta travel during the exposure tiem
speeds = theta_exposure_time / exposure_times                    # speed is locked to meet the blur requirement

# Detector readout time (s)
frame_rate_with_zero_exposure_time = 16  # Hz
readout_time = 1 / frame_rate_with_zero_exposure_time

theta_readouts  = speeds * readout_time                   # theta travel during the readout time
theta_per_frame = theta_exposure_time + theta_readouts    # theta travel between frames
times_per_frame = exposure_times + readout_time           # time per frame

# ------------------------
# Total number of frames over 180°
# ------------------------
frames_per_180deg = 180 / theta_per_frame

# ------------------------
# Plot
# ------------------------
fig, ax1 = plt.subplots(figsize=(8, 5))

# Left y-axis: Effective angular speed
ax1.plot(exposure_times, speeds, 'o-', linewidth=2, color='tab:blue')
ax1.set_xlabel('Exposure Time (s)')
ax1.set_ylabel('Angular Speed (°/s)', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.grid(True)

# Right y-axis: Total number of frames in 180°
ax2 = ax1.twinx()
ax2.plot(exposure_times, frames_per_180deg, 's--', color='tab:orange')
ax2.set_ylabel('Frames per 180°', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')

# Legend (blur and readout time)
plt.legend([f'Set blur = {set_blur} px\nReadout time = {readout_time:.4f} s'], loc='center right')

plt.title('Angular Speed and Frames per 180° vs Exposure Time')
plt.tight_layout()
plt.show()


# # ------------------------
# # Additional Polar Plot
# # ------------------------
# fig = plt.figure(figsize=(6, 6))
# ax = fig.add_subplot(111, polar=True)

# # Generate theta positions for each exposure time
# for i, (t, theta_step) in enumerate(zip(exposure_times, theta_per_frame)):
#     # Compute number of frames for 180° and angle step in radians
#     n_frames = int(frames_per_180deg[i])
#     theta_positions = np.linspace(0, np.pi, n_frames)  # 0 to 180° in radians
    
#     # Concentric circle radius proportional to exposure time
#     radius = (i + 1) / len(exposure_times)
    
#     # Plot projection positions as points on a circular arc
#     ax.plot(theta_positions, np.full_like(theta_positions, radius), 'o', markersize=3)
    
# # Style
# ax.set_title('Projection Angle Positions per Exposure Time', va='bottom')
# ax.set_yticks([])  # hide radial ticks
# ax.set_xticks(np.linspace(0, np.pi, 7))  # 0–180° markers
# ax.set_xticklabels([f'{np.degrees(a):.0f}°' for a in np.linspace(0, np.pi, 7)])
# ax.grid(True)

# plt.tight_layout()
# plt.show()
