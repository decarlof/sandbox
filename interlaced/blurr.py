import numpy as np
import matplotlib.pyplot as plt

# Parameters
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2

# Exposure time (s) from 0.01 to 0.5 in 0.01 s steps
exposure_times = np.arange(0.01, 0.5, 0.01)

# Set the maximum blur error acceptable
max_blurr_error = 0.1  # in pixels  

# Detector readout time (s)
frame_rate_with_zero_exposure_time = 163  # Hz
readout_time = 1 / frame_rate_with_zero_exposure_time

# Compute max angular speed (°/s)
max_speeds = np.degrees(np.arccos((r - max_blurr_error) / r)) / exposure_times

# Compute total number of frames over 180° rotation
theta_max_deg = np.degrees(np.arccos((r - max_blurr_error) / r))
N_180 = 180 * exposure_times / ((exposure_times + readout_time) * theta_max_deg)

# Tomography scenario: motor speed to step rotation_step
rotation_step = 0.12  # degrees per projection
motor_speeds = rotation_step / (exposure_times + readout_time)


# Total number of projections in 180° for the tomography motor speed
N_proj_180 = int(np.round(180 / rotation_step))


# Plot
plt.figure(figsize=(10, 5))
plt.plot(exposure_times, max_speeds, 'o-', linewidth=2, 
         label=f'Max Angular Speed (°/s); Total projections in 180 (N_180)°')
plt.plot(exposure_times, motor_speeds, 's-', linewidth=2, 
         label=f'TomoScan fly scan speed (°/s), rotation_step={rotation_step}°, projections in 180°={N_proj_180}')

# Annotate total frames in 180° at min, mid, max exposure times
indices = [0, len(exposure_times)//2, -1]
for i in indices:
    plt.annotate(f'N_180={int(N_180[i])}',
                 xy=(exposure_times[i], max_speeds[i]),
                 xytext=(5, 10),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue')

plt.xlabel('Exposure Time (s)')
plt.ylabel('Speed (°/s)')
plt.title('Max Angular Speed vs Exposure Time and Motor Speed for Tomography')
plt.grid(True)
plt.legend()
plt.show()


# Compute total scan time to cover 180° (s)
# Min time using max speed (depends on exposure time)
total_time_min = 180 / max_speeds       # s
total_time_motor = 180 / motor_speeds   # s

# Plot
plt.figure(figsize=(10, 5))
plt.plot(exposure_times, total_time_min, 'o-', linewidth=2,
         label=f'Min Scan Time (s) at Max Angular Speed; Total projections = {int(np.max(N_180))}')
plt.plot(exposure_times, total_time_motor, 's-', linewidth=2,
         label=f'TomoScan Fly Scan Time (s), rotation_step={rotation_step}°, projections = {N_proj_180}')

# Annotate total scan time and number of projections at start, mid, end
indices = [0, len(exposure_times)//2, -1]
for i in indices:
    plt.annotate(f'{total_time_min[i]:.1f}s\nN={int(N_180[i])}',
                 xy=(exposure_times[i], total_time_min[i]),
                 xytext=(0, 15),           # shift above point
                 textcoords='offset points',
                 ha='center',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue',
                 fontsize=10)

plt.xlabel('Exposure Time (s)')
plt.ylabel('Total Scan Time for 180° (s)')
plt.title('Total Scan Time vs Exposure Time for 180° Rotation')
plt.grid(True)
plt.legend()
plt.show()