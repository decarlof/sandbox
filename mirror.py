import numpy as np
import matplotlib.pyplot as plt
import xraylib

# --- Parameters ---
theta_deg = 0.15                # incidence angle (degrees)
theta = np.radians(theta_deg)
energies = np.linspace(5, 50, 800)  # keV
thicknesses = [5e-9, 53e-9]     # Pt thickness in meters

# --- Helper to get δ and β from xraylib ---
def delta_beta(element, E_keV):
    n_complex = xraylib.Refractive_Index(element, E_keV, 1.0)
    n_complex = complex(n_complex)
    delta = 1 - n_complex.real
    beta = n_complex.imag
    return delta, beta

# --- Reflectivity calculation for Pt on Si ---
def reflectivity_pt_on_si(E_keV, t_Pt, theta):
    delta_Pt, beta_Pt = delta_beta('Pt', E_keV)
    delta_Si, beta_Si = delta_beta('Si', E_keV)

    n0 = 1.0
    n1 = 1 - delta_Pt + 1j * beta_Pt
    n2 = 1 - delta_Si + 1j * beta_Si

    k = 2 * np.pi / (1.239841984e-9 / E_keV)  # wavevector magnitude
    cos0 = np.cos(theta)
    sin1 = np.sqrt(1 - (n0 / n1 * np.sin(theta)) ** 2)
    sin2 = np.sqrt(1 - (n0 / n2 * np.sin(theta)) ** 2)

    r01 = (n0 * cos0 - n1 * sin1) / (n0 * cos0 + n1 * sin1)
    r12 = (n1 * sin1 - n2 * sin2) / (n1 * sin1 + n2 * sin2)

    phi = 2 * k * n1 * sin1 * t_Pt
    r_total = (r01 + r12 * np.exp(2j * phi)) / (1 + r01 * r12 * np.exp(2j * phi))

    return np.abs(r_total) ** 2

# --- Compute reflectivity curves ---
R_5nm  = [reflectivity_pt_on_si(E, 5e-9, theta)  for E in energies]
R_53nm = [reflectivity_pt_on_si(E, 53e-9, theta) for E in energies]

# --- Plot ---
plt.figure(figsize=(8,5))
plt.plot(energies, R_53nm, label='Pt 53 nm', lw=2)
plt.plot(energies, R_5nm,  label='Pt 5 nm',  lw=2, ls='--')
plt.xlabel('Photon Energy (keV)')
plt.ylabel('Reflectivity')
plt.title(f'Pt-coated Si mirror reflectivity at {theta_deg}° incidence')
plt.legend()
plt.grid(alpha=0.3)
plt.ylim(0, 1)
plt.xlim(5, 50)
plt.show()
