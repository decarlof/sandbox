import numpy as np
import matplotlib.pyplot as plt

# # Parameters
# N = 10  # frames per rotation
# n = 3   # number of rotations

# Parameters
N = 10  # frames per 180° sweep
n = 4   # number of sweeps

step = 180.0 / N  # angular spacing for one sweep

# Function to generate dyadic fractional offsets
def dyadic_offsets(num_sweeps):
    offsets = [0.0]
    level = 1
    while len(offsets) < num_sweeps:
        new_offsets = [o + 1/(2**level) for o in range(0, 2**level, 2)]
        offsets += new_offsets
        level += 1
    return offsets[:num_sweeps]

# Generate the fractional offsets
offsets = dyadic_offsets(n)

# Generate angles for each sweep
angles = []
for r, frac in enumerate(offsets):
    sweep_angles = [(i + frac) * step for i in range(N)]
    angles.append(sweep_angles)

# Print results
for i, sweep in enumerate(angles):
    print(f"Sweep {i+1}: {sweep}")

# Flatten all into one list if needed
all_angles = [a for sweep in angles for a in sweep]

# Print nicely
for i, sweep in enumerate(angles):
    print(f"Sweep {i+1}: {sweep}")

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
