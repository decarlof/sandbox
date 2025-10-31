import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 10  # frames per rotation
n = 3   # number of rotations
exposure_time   = 0.2   # detector exposure time in s
detector_x_size = 2048  # horizontal detector size in pixels

# Interlaced delta per rotation
offset = 180./(N * n - 1) # interlacing offset between rotations
delta = n * offset        # spacing within a single rotation

# Generate angles for each rotation
angles = []
for r in range(n):
    rotation_angles = [i * delta + r * offset for i in range(N)]
    angles.append(rotation_angles)

# Flatten for plotting all together
all_angles = [angle for rotation in angles for angle in rotation]

# Plot
plt.figure(figsize=(10, 4))
for r, rotation_angles in enumerate(angles):
    plt.scatter(rotation_angles, [r+1]*len(rotation_angles), label=f'Rotation {r+1}', s=100)

plt.yticks(range(1, n+1))
plt.xlabel('Angle [deg]')
plt.ylabel('Rotation number')
plt.title(f'Interlaced Scan: N={N} frames/rotation, n={n} rotations')
plt.grid(True)
plt.legend(loc='lower right')
plt.show()

print("All interlaced angles (flattened):")
print(sorted(all_angles))

# Flatten angles for continuous acquisition (in order of acquisition)
continuous_angles = [angle for rotation in angles for angle in rotation]

print("\nAngles for continuous rotation (acquisition order):")
print(continuous_angles)


# Cumulative stage positions for continuous rotations ---
stage_positions = []
for rotation_index in range(n):
    rotation_start = rotation_index * 180  # cumulative offset for physical stage
    stage_positions += [angle + rotation_start for angle in angles[rotation_index]]

print("\nStage positions for continuous rotation (cumulative):")
print(stage_positions)

# Optional: plot cumulative stage positions
plt.figure(figsize=(10, 4))
plt.plot(stage_positions, 'o-', markersize=8)
plt.xlabel('Frame number')
plt.ylabel('Stage angle [deg]')
plt.title('Cumulative Stage Positions for Continuous Interlaced Scan')
plt.grid(True)
plt.show()

# print(np.diff(stage_positions))
