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
frame_rate_with_zero_exposure_time = 1  # Hz this should be measured for each detector configuration
readout_time = 1 / frame_rate_with_zero_exposure_time

# Compute max angular speed (°/s)
max_speeds = np.degrees(np.arccos((r - max_blurr_error) / r)) / exposure_times

# Compute total number of frames over 180° rotation
theta_max_deg = np.degrees(np.arccos((r - max_blurr_error) / r))
N_180 = 180 * exposure_times / ((exposure_times + readout_time) * theta_max_deg)



# angles_list = []
# for i, exp_time in enumerate(exposure_times):
#     omega_max = max_speeds[i]  # °/s
#     delta_theta = omega_max * (exp_time + readout_time)  # ° per frame
#     n_frames = int(np.floor(180 / delta_theta))
#     angles = np.arange(0, n_frames) * delta_theta
#     angles_list.append(angles)

# # --- Circular plot showing the image acquisition angles ---
# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))

# # Choose which exposure time to visualize (index)
# i_plot = 10  # e.g., exposure_times[10] = 0.11 s
# angles_deg = angles_list[i_plot]
# exp_time = exposure_times[i_plot]
# omega_max = max_speeds[i_plot]
# delta_theta = omega_max * (exp_time + readout_time)
# theta_max_deg = np.degrees(np.arccos((r - max_blurr_error) / r))
# arc_length_deg = theta_max_deg  # approximate blur span

# # Convert to radians for plotting
# angles_rad = np.deg2rad(angles_deg)
# arc_rad = np.deg2rad(arc_length_deg)

# # Plot acquisition positions
# ax.scatter(angles_rad, np.ones_like(angles_rad), s=30, color='C0', label='Projection angles')

# # Draw arcs showing exposure blur range
# for theta in angles_rad:
#     arc_thetas = np.linspace(theta - arc_rad / 2, theta + arc_rad / 2, 30)
#     ax.plot(arc_thetas, np.ones_like(arc_thetas), color='C1', lw=1.2, alpha=0.6)

# # Format plot
# ax.set_rticks([])
# ax.set_yticklabels([])
# ax.set_title(f"Projection Angles (Exposure = {exp_time:.2f}s, Blur Arc = {arc_length_deg:.3f}°)")
# ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
# plt.show()

# --- Additional code for visualization and angle list ---
# Choose exposure-time index to visualize (change as needed; keep within exposure_times range)
i_plot = 10  # for example; exposure_times[i_plot] is the exposure shown

exp_time = exposure_times[i_plot]
omega_max = max_speeds[i_plot]           # °/s (as you computed)
# angular motion while exposing (°). For your max_speeds this equals theta_max_deg
exposure_arc_deg = omega_max * exp_time
# angular motion during readout (°)
readout_arc_deg = omega_max * readout_time
# Angular step between triggers (°): exposure + readout
delta_theta = exposure_arc_deg + readout_arc_deg

# Number of frames that fit in 180 degrees
n_frames = int(np.floor(180.0 / delta_theta))
if n_frames < 1:
    raise ValueError("No frames fit in 180°. Reduce exposure or readout time or increase allowed blur.")

# Trigger angles (deg) where a trigger is sent and exposure begins
trigger_angles_deg = np.arange(0, n_frames) * delta_theta

# Convert degrees -> radians for polar plotting
trigger_angles_rad = np.deg2rad(trigger_angles_deg)
exposure_arc_rad = np.deg2rad(exposure_arc_deg)
readout_arc_rad = np.deg2rad(readout_arc_deg)

# --- Circular plot with legend inside the plot area ---
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(7, 7))

# Plot triggers (blue dots)
ax.scatter(trigger_angles_rad, np.ones_like(trigger_angles_rad), s=40,
           label='Trigger (exposure starts)', zorder=3)

# Plot exposure arcs (solid)
for theta0 in trigger_angles_rad:
    arc_t = np.linspace(theta0, theta0 + exposure_arc_rad, 50)
    ax.plot(arc_t, np.ones_like(arc_t), lw=3, alpha=0.8,
            label='_nolegend_' if theta0 != trigger_angles_rad[0] else 'Exposure arc')

# Plot readout arcs (dashed)
for theta0 in trigger_angles_rad:
    start = theta0 + exposure_arc_rad
    arc_t = np.linspace(start, start + readout_arc_rad, 30)
    ax.plot(arc_t, np.ones_like(arc_t), lw=3, alpha=0.6, linestyle='--',
            label='_nolegend_' if theta0 != trigger_angles_rad[0] else 'Readout arc')

# Visual aids: 0° and 180° reference lines
ax.plot([0, 0], [0, 1.2], color='k', linewidth=0.6)
ax.plot([np.pi, np.pi], [0, 1.2], color='k', linewidth=0.6)

# Formatting
ax.set_rticks([])
ax.set_yticklabels([])
ax.set_ylim(0.9, 1.1)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

# Title and legend inside the plot
title = (f"Exposure = {exp_time:.3f} s, Readout = {readout_time:.4f} s\n"
         f"Exposure arc = {exposure_arc_deg:.3f}°, Readout arc = {readout_arc_deg:.3f}°\n"
         f"Δθ/frame = {delta_theta:.3f}°, Frames in 180° = {n_frames}")
ax.set_title(title, va='bottom', pad=20)

# Move legend inside the plot
ax.legend(loc='upper right', bbox_to_anchor=(0.95, 0.95), frameon=True, framealpha=0.8)

plt.show()

# --- Create and print the list of trigger angles (degrees) for this exposure time ---
print(f"\nTrigger angles (deg) for exposure {exp_time:.3f}s (n_frames = {n_frames}):")
print(trigger_angles_deg.tolist())

# ##############################################
# Tomography scenario: user enters the step size
rotation_step = 0.12  # degrees per projection this should be read from tomoStan
motor_speeds = rotation_step / (exposure_times + readout_time)


# Total number of projections in 180° for the tomography motor speed
N_proj_180 = int(np.round(180 / rotation_step))

# Convert readout time to ms for legend
readout_time_ms = readout_time * 1000


# Compute effective blur for fly scan
effective_blur_rad = np.radians(motor_speeds * (exposure_times + readout_time))  # angular rotation during exposure
effective_blur_px = r * (1 - np.cos(effective_blur_rad))
# Since all values are identical, pick the first
effective_blur_px_val = effective_blur_px[0]


# Plot: Angular Speeds
plt.figure(figsize=(10, 5))
plt.plot(exposure_times, max_speeds, 'o-', linewidth=2, 
         label=f'At max speed with  blur={max_blurr_error} px, readout_time={readout_time_ms:.4f} ms; Total projections = N')
plt.plot(exposure_times, motor_speeds, 's-', linewidth=2, 
         label=f'At TomoScan scan speed, blur≈{effective_blur_px_val:.3f} px, step={rotation_step}°, readout={readout_time_ms:.4f} ms, projections in 180°={N_proj_180}')

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
plt.title('Rotation speed vs Exposure Time')
plt.grid(True)
plt.legend()
plt.show()




# Total scan time (s)
total_time_min = 180 / max_speeds
total_time_motor = 180 / motor_speeds

# Plot: Total Scan Time
plt.figure(figsize=(10, 5))
plt.plot(exposure_times, total_time_min, 'o-', linewidth=2,
         label=f'Scan time  at max speed with blur={max_blurr_error} px, readout={readout_time_ms:.2f} ms, projections = N')
plt.plot(exposure_times, total_time_motor, 's-', linewidth=2,
         label=f'TomoScan Time, step={rotation_step}°, effective blur ≈ {effective_blur_px_val:.3f} px readout={readout_time_ms:.2f} ms, projections = {N_proj_180}')

# Annotate Min Scan Time (blue) and number of projections at start, mid, end
indices = [0, len(exposure_times)//2, -1]
for i in indices:
    plt.annotate(f'{total_time_min[i]:.1f}s\nN={int(N_180[i])}',
                 xy=(exposure_times[i], total_time_min[i]),
                 xytext=(0, 15),
                 textcoords='offset points',
                 ha='center',
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='blue',
                 fontsize=10)

plt.xlabel('Exposure Time (s)')
plt.ylabel('Total Scan Time for 180° (s)')
plt.title('Total Scan Time vs Exposure Time')
plt.grid(True)
plt.legend()
plt.show()