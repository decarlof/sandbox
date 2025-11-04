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
set_blur = 0.0021897 # pixels

# ------------------------
# Calculate max allowed angle from blur
# ------------------------
theta_exposure_time = np.degrees(np.arccos((r - set_blur) / r))  # theta travel during the exposure time
speeds = theta_exposure_time / exposure_times                    # speed is locked to meet the blur requirement

# Detector readout time (s)
frame_rate_with_zero_exposure_time = 160  # Hz
readout_time = 1 / frame_rate_with_zero_exposure_time

theta_readouts  = speeds * readout_time                   # theta travel during the readout time
theta_per_frame = theta_exposure_time + theta_readouts    # theta travel between frames
times_per_frame = exposure_times + readout_time           # time per frame

# ------------------------
# Total number of frames over 180°
# ------------------------
frames_per_180deg = 180 / theta_per_frame

# ##############################################
# Tomography scenario: user enters the step size
rotation_step = 0.12  # degrees per projection this should be read from tomoScan
motor_speeds = rotation_step / (exposure_times + readout_time) # this is close to the way TomoScan sets the speed to make sure the detector is able to take an image at each angle step

# Total number of projections in 180° for the tomography motor speed
N_proj_180 = int(np.round(180 / rotation_step))

# Convert readout time to ms for legend
readout_time_ms = readout_time * 1000

# Compute effective blur for fly scan
# TomoScan blurs change with the speed
effective_blur_rad = np.radians(rotation_step - motor_speeds * readout_time)  # angular rotation during exposure
effective_blur_px = r * (1 - np.cos(effective_blur_rad))

# === Create one figure with two stacked subplots ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# --- Top plot: Angular Speeds ---
ax1.plot(exposure_times, speeds, 'o-', linewidth=2,
          label=f'At max speed with  blur={set_blur} px, readout={readout_time_ms:.2f} ms, projections = N')
ax1.plot(exposure_times, motor_speeds, 's-', linewidth=2,
          label=f'At TomoScan scan speed, blur≈{effective_blur_px[0]:.7f}-{effective_blur_px[-1]:.7f}px, step={rotation_step}°, readout={readout_time_ms:.4f} ms, projections={N_proj_180}')

indices = [0, len(exposure_times)//2, -1]
for i in indices:
    ax1.annotate(f'frames per 180°={int(frames_per_180deg[i])}',
                 xy=(exposure_times[i], speeds[i]),
                 xytext=(5, 10),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue')

ax1.set_xlabel('Exposure Time (s)')
ax1.set_ylabel('Speed (°/s)')
ax1.set_title('Rotation speed vs Exposure Time')
ax1.grid(True)
ax1.legend(fontsize=7)  # smaller legend font for top plot

# --- Bottom plot: Total Scan Time ---
total_time_min = 180 / speeds
total_time_motor = 180 / motor_speeds

ax2.plot(exposure_times, total_time_min, 'o-', linewidth=2,
          label=f'Scan time at max speed with blur={set_blur}px, readout={readout_time_ms:.2f}ms, projections=N')
ax2.plot(exposure_times, total_time_motor, 's-', linewidth=2,
          label=f'TomoScan time, step={rotation_step}°, blur≈blur≈{effective_blur_px[0]:.7f}-{effective_blur_px[-1]:.7f}px readout={readout_time_ms:.2f}ms, projections = {N_proj_180}')

for i in indices:
    ax2.annotate(f'{total_time_min[i]:.1f}s\nN={int(frames_per_180deg[i])}',
                 xy=(exposure_times[i], total_time_min[i]),
                 xytext=(0, 15),
                 textcoords='offset points',
                 ha='center',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue',
                 fontsize=10)

ax2.set_xlabel('Exposure Time (s)')
ax2.set_ylabel('Total Scan Time for 180° (s)')
ax2.set_title('Total Scan Time vs Exposure Time')
ax2.grid(True)
ax2.legend(fontsize=7)  # smaller legend font for bottom plot


plt.tight_layout()
plt.show()
