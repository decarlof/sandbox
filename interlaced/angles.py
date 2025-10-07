import time
import numpy as np
import matplotlib.pyplot as plt


def genang(numproj, nProj_per_rot):
    """Interlaced angles generator
    Parameters
    ----------
    numproj : int
            Total number of projections.
    nProj_per_rot : int
            Number of projections per rotation.
    """
    prime = 3
    pst = 0
    pend = 360
    seq = []
    i = 0
    while len(seq) < numproj:
        b = i
        i += 1
        r = 0
        q = 1 / prime
        while (b != 0):
            a = np.mod(b, prime)
            r += (a * q)
            q /= prime
            b = np.floor(b / prime)
        r *= ((pend-pst) / nProj_per_rot)
        k = 0
        while (np.logical_and(len(seq) < numproj, k < nProj_per_rot)):
            seq.append((pst + (r + k * (pend-pst) / nProj_per_rot))/180*np.pi)
            k += 1
    return seq

def line_plot(theta):

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(theta, marker='o', linestyle='-', color='b')  # you can customize markers, colors, etc.
    plt.title('Theta values')
    plt.xlabel('Index')
    plt.ylabel('Theta (rad)')
    plt.grid(True)
    plt.show()

def circle_plot(theta):

    # Convert to x, y coordinates
    x = np.cos(theta)
    y = np.sin(theta)

    # Identify rotation number for each point
    rotations = np.floor(theta / (2 * np.pi)).astype(int)
    num_rotations = rotations.max() + 1

    # Create the plot
    plt.figure(figsize=(6, 6))
    cmap = plt.cm.viridis

    # Plot each rotation with a different color (dots only)
    for r in range(num_rotations):
        mask = rotations == r
        if np.any(mask):
            plt.scatter(x[mask], y[mask], color=cmap(r / max(1, num_rotations - 1)), s=15, label=f'Rotation {r+1}')

    # Make it look like a circle
    plt.gca().set_aspect('equal', 'box')
    plt.title('Theta plotted on a circle (colored per rotation)')
    plt.xlabel('cos(θ)')
    plt.ylabel('sin(θ)')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":

    ntheta = 45  # Total number of projections
    nthetap = 15  # Number of angles per rotation
    theta = np.array(genang(ntheta, nthetap), dtype='float32')
    line_plot(theta)
    circle_plot(theta)
