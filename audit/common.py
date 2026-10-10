"""
Shared reference data for the independent USRT audit.

All values are written out explicitly (not taken from scipy.constants) so the
audit does not silently change when a library updates its CODATA edition.
Each entry is (value, one-sigma uncertainty).

Sources
-------
CODATA 2022 (Tiesinga et al., Rev. Mod. Phys. 97, 025002 (2025); NIST wallet card)
PDG 2024   (Navas et al., Phys. Rev. D 110, 030001 (2024))
Planck 2018 cosmological parameters (Aghanim et al., A&A 641, A6 (2020)),
            TT,TE,EE+lowE+lensing column.
"""
import math

# --- exact SI constants -----------------------------------------------------
c = 299_792_458.0                 # m/s (exact)
h = 6.626_070_15e-34              # J s (exact)
hbar = h / (2.0 * math.pi)        # J s
e = 1.602_176_634e-19             # C (exact)
eV = e                            # J

# --- CODATA 2022 measured constants -----------------------------------------
G = (6.674_30e-11, 0.000_15e-11)                  # m^3 kg^-1 s^-2 (rel. 2.2e-5)
alpha = (7.297_352_5643e-3, 0.000_000_0011e-3)    # fine-structure constant
m_e_kg = (9.109_383_7139e-31, 0.000_000_0028e-31)
m_e_MeV = (0.510_998_950_69, 0.000_000_000_16)
mu_pe = (1836.152_673_426, 0.000_000_032)         # proton/electron mass ratio
dm_np_MeV = (1.293_332_51, 0.000_000_38)          # m_n - m_p

# --- PDG 2024 lepton masses ---------------------------------------------------
m_mu_MeV = (105.658_3755, 0.000_0023)
m_tau_MeV = (1776.93, 0.09)

# --- Planck 2018 (TT,TE,EE+lowE+lensing) --------------------------------------
omega_c_h2 = (0.1200, 0.0012)
omega_b_h2 = (0.02237, 0.00015)


def planck_mass():
    """Planck mass in kg and its 1-sigma uncertainty (dominated by G)."""
    G0, dG = G
    mP = math.sqrt(hbar * c / G0)
    dmP = 0.5 * mP * dG / G0
    return mP, dmP


def planck_length():
    return math.sqrt(hbar * G[0] / c**3)


def banner(title):
    line = "=" * 78
    return f"\n{line}\n{title}\n{line}"
