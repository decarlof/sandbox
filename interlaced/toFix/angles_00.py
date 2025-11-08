import matplotlib.pyplot as plt
import numpy as np

# Parameters
total_images = 1500    # total images
n = 10    # number of rotations
total_range = 180 * n

step_size = total_range / total_images


theta = [i * step_size for i in range(total_images)]

print(theta)
print(len(theta))
# ---- Plot ----
plt.figure(figsize=(8, 3))
plt.plot(theta, 'o-', markersize=8)
plt.title(f'Projection Angles (total={total_images}, step={step_size}°)')
plt.xlabel('Image index')
plt.ylabel('Angle [deg]')
plt.grid(True)
plt.show()