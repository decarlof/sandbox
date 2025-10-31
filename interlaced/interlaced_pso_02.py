import matplotlib.pyplot as plt

# Parameters
N = 180   # frames in first rotation
n = 10    # number of rotations
total_range = 180

# Step 1: first rotation - uniform spacing
rotation1 = [i * total_range / N for i in range(N)]
angles = [rotation1]

# Step 2: subsequent rotations - recursive midpoint of all previous angles
for r in range(1, n):
    prev_all = sorted([a for rot in angles for a in rot])
    new_rotation = [(prev_all[i] + prev_all[i+1])/2 for i in range(len(prev_all)-1)]
    angles.append(new_rotation)

# Print interlaced pattern
print("Interlaced pattern within 0–180°:")
for r, a in enumerate(angles, start=1):
    print(f"Rotation {r}: {a}")

# Continuous stage positions
stage_positions = []
for r in range(n):
    base = r * total_range
    stage_positions.extend([a + base for a in angles[r]])

print("\nStage positions for continuous rotation:")
print(stage_positions)

# ---- Plots ----
# Plot interlaced angles within 0–180
plt.figure(figsize=(10, 4))
for r, rotation_angles in enumerate(angles):
    plt.scatter(rotation_angles, [r+1]*len(rotation_angles),
                label=f'Rotation {r+1}', s=100)
plt.xlabel('Angle [deg]')
plt.ylabel('Rotation number')
plt.title('Recursive Interlaced Scan Pattern: 0–180°')
plt.grid(True)
plt.legend(loc='lower right')
plt.show()

# Plot cumulative stage positions
plt.figure(figsize=(10, 4))
plt.plot(stage_positions, 'o-', markersize=8)
plt.xlabel('Frame number')
plt.ylabel('Stage angle [deg]')
plt.title('Continuous Stage Motion for Recursive Interlaced Scan')
plt.grid(True)
plt.show()


# import matplotlib.pyplot as plt

# # Parameters
# N = 18
# n = 3

# # First rotation: uniform spacing
# delta = 180 / N
# angles = [[i * delta for i in range(N)]]

# # Subsequent rotations: midpoints of previous rotation
# for r in range(1, n):
#     prev = angles[-1]
#     new_rotation = []
#     for i in range(N):
#         # For i < N-1, take midpoint between prev[i] and prev[i+1]
#         if i < N-1:
#             new_rotation.append((prev[i] + prev[i+1])/2)
#         else:
#             # For last point, extrapolate same spacing as previous interval
#             spacing = prev[1] - prev[0]
#             new_rotation.append(prev[-1] + spacing/2)
#     angles.append(new_rotation)

# # Print
# print("Interlaced pattern within 0–180°:")
# for r, a in enumerate(angles, start=1):
#     print(f"Rotation {r}: {a}")

# # Cumulative stage positions
# stage_positions = []
# for r in range(n):
#     base = r * 180
#     stage_positions.extend([a + base for a in angles[r]])

# print("\nStage positions for continuous rotation:")
# print(stage_positions)

# # Plots
# plt.figure(figsize=(10, 4))
# for r, rotation_angles in enumerate(angles):
#     plt.scatter(rotation_angles, [r+1]*len(rotation_angles), label=f'Rotation {r+1}', s=100)
# plt.xlabel('Angle [deg]')
# plt.ylabel('Rotation number')
# plt.title('True Interlaced Scan Pattern: 0–180°')
# plt.grid(True)
# plt.legend(loc='lower right')
# plt.show()

# plt.figure(figsize=(10, 4))
# plt.plot(stage_positions, 'o-', markersize=8)
# plt.xlabel('Frame number')
# plt.ylabel('Stage angle [deg]')
# plt.title('Continuous Stage Motion for True Interlaced Scan')
# plt.grid(True)
# plt.show()


# # import matplotlib.pyplot as plt

# # # Parameters
# # N = 6  # frames per rotation
# # n = 3  # number of rotations

# # # Interlaced delta per rotation
# # delta = 180 / N
# # offset = delta / n

# # # Generate interlaced angles (0–180°)
# # angles = []
# # for r in range(n):
# #     rotation_angles = [i * delta + r * offset for i in range(N)]
# #     angles.append(rotation_angles)

# # # Plot of 0–180° interlaced pattern
# # plt.figure(figsize=(10, 4))
# # for r, rotation_angles in enumerate(angles):
# #     plt.scatter(rotation_angles, [r+1]*len(rotation_angles), label=f'Rotation {r+1}', s=100)
# # plt.yticks(range(1, n+1))
# # plt.xlabel('Angle [deg]')
# # plt.ylabel('Rotation number')
# # plt.title(f'Interlaced Scan: N={N} frames, n={n} rotations')
# # plt.grid(True)
# # plt.legend(loc='lower right')
# # plt.show()

# # print("All interlaced angles (flattened):")
# # print(sorted([a for rot in angles for a in rot]))

# # # Continuous acquisition (within each rotation)
# # continuous_angles = [a for rot in angles for a in rot]
# # print("\nAngles for continuous rotation (acquisition order):")
# # print(continuous_angles)

# # # --- FIXED cumulative stage positions (no bumps) ---
# # stage_positions = []
# # for r in range(n):
# #     rotation_start = r * 180  # add 180° for each rotation
# #     for a in angles[r]:
# #         stage_positions.append(a + rotation_start)

# # print("\nStage positions for continuous rotation (cumulative, smooth):")
# # print(stage_positions)

# # # Plot continuous stage positions
# # plt.figure(figsize=(10, 4))
# # plt.plot(stage_positions, 'o-', markersize=8)
# # plt.xlabel('Frame number')
# # plt.ylabel('Stage angle [deg]')
# # plt.title('Cumulative Stage Positions for Continuous Interlaced Scan')
# # plt.grid(True)
# # plt.show()


# # # import numpy as np
# # # import matplotlib.pyplot as plt

# # # # # Parameters
# # # # N = 10  # frames per rotation
# # # # n = 3   # number of rotations

# # # # Parameters
# # # N = 10  # frames per 180° sweep
# # # n = 4   # number of sweeps

# # # step = 180.0 / N  # angular spacing for one sweep

# # # # Function to generate dyadic fractional offsets
# # # def dyadic_offsets(num_sweeps):
# # #     offsets = [0.0]
# # #     level = 1
# # #     while len(offsets) < num_sweeps:
# # #         new_offsets = [o + 1/(2**level) for o in range(0, 2**level, 2)]
# # #         offsets += new_offsets
# # #         level += 1
# # #     return offsets[:num_sweeps]

# # # # Generate the fractional offsets
# # # offsets = dyadic_offsets(n)

# # # # Generate angles for each sweep
# # # angles = []
# # # for r, frac in enumerate(offsets):
# # #     sweep_angles = [(i + frac) * step for i in range(N)]
# # #     angles.append(sweep_angles)

# # # # Flatten all into one list if needed
# # # all_angles = [a for sweep in angles for a in sweep]


# # # # Plot
# # # plt.figure(figsize=(10, 4))
# # # for r, rotation_angles in enumerate(angles):
# # #     plt.scatter(rotation_angles, [r+1]*len(rotation_angles), label=f'Rotation {r+1}', s=100)

# # # plt.yticks(range(1, n+1))
# # # plt.xlabel('Angle [deg]')
# # # plt.ylabel('Rotation number')
# # # plt.title(f'Interlaced Scan: N={N} frames/rotation, n={n} rotations')
# # # plt.grid(True)
# # # plt.legend(loc='lower right')
# # # plt.show()

# # # print("All interlaced angles (flattened):")
# # # print(sorted(all_angles))

# # # # # Cumulative stage positions for continuous rotations ---
# # # # stage_positions = []
# # # # for rotation_index in range(n):
# # # #     rotation_start = rotation_index * 180  # cumulative offset for physical stage
# # # #     stage_positions += [angle + rotation_start for angle in angles[rotation_index]]

# # # # print("\nStage positions for continuous rotation (cumulative):")
# # # # print(stage_positions)

# # # # --- NEW FIXED VERSION: Properly interlaced continuous rotation order ---
# # # # Interleave frames from all rotations so the stage moves smoothly
# # # interleaved_angles = []
# # # for i in range(N):
# # #     for r in range(n):
# # #         interleaved_angles.append(angles[r][i])

# # # # Compute cumulative stage positions (no bumps)
# # # stage_positions = []
# # # for idx, angle in enumerate(interleaved_angles):
# # #     rotation_index = idx // (N * n)  # not really needed, just clarity
# # #     stage_positions.append(angle)

# # # print("\nStage positions for continuous rotation (smooth, interleaved):")
# # # print(stage_positions)


# # # # Optional: plot cumulative stage positions
# # # plt.figure(figsize=(10, 4))
# # # plt.plot(stage_positions, 'o-', markersize=8)
# # # plt.xlabel('Frame number')
# # # plt.ylabel('Stage angle [deg]')
# # # plt.title('Cumulative Stage Positions for Continuous Interlaced Scan')
# # # plt.grid(True)
# # # plt.show()

# # # # print(np.diff(stage_positions))
