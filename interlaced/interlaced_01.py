import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Input parameters
# -----------------------------
detector_x_size = 2048  # horizontal detector size in pixels
r = detector_x_size / 2
frame_rate_with_zero_exposure_time = 50  # Hz (measured for detector configuration)
readout_time = 1 / frame_rate_with_zero_exposure_time  # s

# ---- USER INPUT ----
exposure_time = 0.1        # s
max_blurr_error = 1         # pixels
angles_user = np.array([0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180])  # arbitrary example
# -----------------------------

# Compute maximum angular speed (°/s) to stay below the blur error
theta_max_deg = np.degrees(np.arccos((r - max_blurr_error) / r))
omega_max = theta_max_deg / exposure_time  # °/s

# Compute angular motion during exposure and readout
angular_motion_exposure = omega_max * exposure_time  # = theta_max_deg
angular_motion_readout = omega_max * readout_time
delta_theta_allowed = angular_motion_exposure + angular_motion_readout

# -----------------------------
# Check if the user list is acceptable (with detailed violation report)
# -----------------------------
angles_user = np.sort(angles_user)
diffs = np.diff(angles_user)

acceptable = np.all(diffs >= delta_theta_allowed - 1e-6)  # small tolerance

if acceptable:
    print("✅ The provided list of angles is acceptable.")
    angles_final = angles_user
else:
    print("❌ The provided list violates blur/readout constraints.")
    print(f"Minimum allowed angular step (Δθ_allowed): {delta_theta_allowed:.4f}°\n")

    # Find and report specific violations
    print("Violating angle pairs (start → next):")
    for i, d in enumerate(diffs):
        if d < delta_theta_allowed:
            print(f"  Between {angles_user[i]:7.3f}° → {angles_user[i+1]:7.3f}°  "
                  f"(Δ = {d:7.4f}° < {delta_theta_allowed:.4f}°)")

    # Propose corrected list:
    angles_final = [angles_user[0]]
    for a in angles_user[1:]:
        if a - angles_final[-1] >= delta_theta_allowed:
            angles_final.append(a)
    # Extend up to 180° if possible
    while angles_final[-1] + delta_theta_allowed <= 180:
        angles_final.append(angles_final[-1] + delta_theta_allowed)
    angles_final = np.array(angles_final)

    print("\n👉 Proposed acceptable angles:")
    print(np.round(angles_final, 3))

# -----------------------------
# Visualization
# -----------------------------
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(7, 7))

# Convert degrees → radians
user_rad = np.deg2rad(angles_user)
final_rad = np.deg2rad(angles_final)
exp_arc_rad = np.deg2rad(angular_motion_exposure)
read_arc_rad = np.deg2rad(angular_motion_readout)

# Plot user-supplied triggers
ax.scatter(user_rad, np.ones_like(user_rad), color='C0', s=35, label='User angles')

# Plot adjusted triggers (if changed)
if not acceptable:
    ax.scatter(final_rad, np.ones_like(final_rad), color='C3', s=45, marker='x', label='Adjusted angles')

# Show exposure arcs
for theta in final_rad:
    arc_t = np.linspace(theta, theta + exp_arc_rad, 40)
    ax.plot(arc_t, np.ones_like(arc_t), color='C1', lw=2, alpha=0.7)

# Show readout arcs
for theta in final_rad:
    arc_t = np.linspace(theta + exp_arc_rad, theta + exp_arc_rad + read_arc_rad, 30)
    ax.plot(arc_t, np.ones_like(arc_t), color='C2', lw=2, ls='--', alpha=0.7)

# Aesthetic
ax.set_rticks([])
ax.set_yticklabels([])
ax.set_ylim(0.9, 1.1)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_title(f"Exposure = {exposure_time:.3f}s, Readout = {readout_time:.4f}s\n"
             f"Exposure arc = {angular_motion_exposure:.3f}°, Readout arc = {angular_motion_readout:.3f}°\n"
             f"Δθ_allowed = {delta_theta_allowed:.3f}°", pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(0.95, 0.95), frameon=True, framealpha=0.8)
plt.show()
