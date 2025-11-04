import numpy as np
import matplotlib.pyplot as plt

# Parameters
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2

# Exposure time (s) from 0.01 to 0.5 in 0.01 s steps
exposure_times = np.arange(0.01, 0.5, 0.01)

# Set the maximum blur error acceptable
max_blurr_error = 1  # in pixels  

# Detector readout time (s)
frame_rate_with_zero_exposure_time = 160  # Hz this should be measured for each detector configuration
readout_time = 1 / frame_rate_with_zero_exposure_time

# Compute max angular speed (°/s)
max_speeds = np.degrees(np.arccos((r - max_blurr_error) / r)) / exposure_times

# Compute total number of frames over 180° rotation
theta_max_deg = np.degrees(np.arccos((r - max_blurr_error) / r))
N_180 = 180 * exposure_times / ((exposure_times + readout_time) * theta_max_deg)

# ##############################################
# Tomography scenario: user enters the step size
rotation_step = 2.57  # degrees per projection this should be read from tomoStan
motor_speeds = rotation_step / (exposure_times + readout_time)

# Total number of projections in 180° for the tomography motor speed
N_proj_180 = int(np.round(180 / rotation_step))

# Convert readout time to ms for legend
readout_time_ms = readout_time * 1000

# Compute effective blur for fly scan
effective_blur_rad = np.radians(motor_speeds * (exposure_times + readout_time))  # angular rotation during exposure
effective_blur_px = r * (1 - np.cos(effective_blur_rad))
effective_blur_px_val = effective_blur_px[0]

# === Create one figure with two stacked subplots ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# --- Top plot: Angular Speeds ---
ax1.plot(exposure_times, max_speeds, 'o-', linewidth=2,
          label=f'At max speed with  blur={max_blurr_error} px, readout_time={readout_time_ms:.4f} ms; Total projections = N')
ax1.plot(exposure_times, motor_speeds, 's-', linewidth=2,
          label=f'At TomoScan scan speed, blur≈{effective_blur_px_val:.3f} px, step={rotation_step}°, readout={readout_time_ms:.4f} ms, projections in 180°={N_proj_180}')

indices = [0, len(exposure_times)//2, -1]
for i in indices:
    ax1.annotate(f'N_180={int(N_180[i])}',
                 xy=(exposure_times[i], max_speeds[i]),
                 xytext=(5, 10),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue')

ax1.set_xlabel('Exposure Time (s)')
ax1.set_ylabel('Speed (°/s)')
ax1.set_title('Rotation speed vs Exposure Time')
ax1.grid(True)
ax1.legend()

# --- Bottom plot: Total Scan Time ---
total_time_min = 180 / max_speeds
total_time_motor = 180 / motor_speeds

ax2.plot(exposure_times, total_time_min, 'o-', linewidth=2,
          label=f'Scan time at max speed with blur={max_blurr_error} px, readout={readout_time_ms:.2f} ms, projections = N')
ax2.plot(exposure_times, total_time_motor, 's-', linewidth=2,
          label=f'TomoScan Time, step={rotation_step}°, effective blur ≈ {effective_blur_px_val:.3f} px readout={readout_time_ms:.2f} ms, projections = {N_proj_180}')

for i in indices:
    ax2.annotate(f'{total_time_min[i]:.1f}s\nN={int(N_180[i])}',
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
ax2.legend()

plt.tight_layout()
plt.show()
