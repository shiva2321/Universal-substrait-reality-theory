"""
Algebraic Structure of Koide's Relation: U(3) Casimirs and Cubic Invariants.
Proves the exact theorems:
1. Q = 2/3 <=> Tr(Phi_8^2) == Tr(Phi_singlet^2) (Equipartition of quadratic Casimirs).
2. The roots of any cubic with Q = 2/3 are identically of the form:
   lambda_k = phi0 * (1 + sqrt(2) * cos(alpha + 2*pi*k/3))
   with cos(3*alpha) = (1/sqrt(2)) * (1 + 2*det(Phi)/phi0^3).
"""
import math
import numpy as np
import sympy as sp

from koide_anomaly.data.constants import (
    M_ELECTRON, M_MUON, M_TAU,
    compute_koide_Q
)

def verify_algebraic_theorems_symbolic():
    """
    Symbolic proof via SymPy of the equivalence between Q=2/3,
    the Casimir equipartition, and the Chebyshev cubic solution.
    """
    phi0, c8 = sp.symbols('phi0 c8', positive=True, real=True)
    # Phi = phi0 * I + Phi_8
    # Tr(Phi) = 3 * phi0
    # Tr(Phi^2) = 3 * phi0^2 + Tr(Phi_8^2)
    # Let Tr(Phi_8^2) = c8
    tr_phi = 3 * phi0
    tr_phi2 = 3 * phi0**2 + c8

    Q_sym = tr_phi2 / (tr_phi**2)
    # Solve Q_sym == 2/3 for c8:
    sol_c8 = sp.solve(sp.Eq(Q_sym, sp.Rational(2, 3)), c8)[0]
    # Singlet trace of squared operator: Tr((phi0 * I)^2) = 3 * phi0^2
    tr_singlet2 = 3 * phi0**2
    equipartition_holds = sp.simplify(sol_c8 - tr_singlet2) == 0

    # Now verify the cubic resolvent:
    # Characteristic equation: det(lambda*I - Phi) = lambda^3 - c1*lambda^2 - c2*lambda - c3 = 0
    # where c1 = Tr(Phi) = 3*phi0
    # c2 = (1/2)*(Tr(Phi^2) - c1^2) = (1/2)*(6*phi0^2 - 9*phi0^2) = -3/2 * phi0^2
    # c3 = det(Phi)
    lam, det_val = sp.symbols('lam det_val', real=True)
    char_poly = lam**3 - 3*phi0*lam**2 + sp.Rational(3, 2)*phi0**2*lam - det_val

    # Substitute lam = phi0 * (1 + sqrt(2) * cos(theta))
    theta = sp.symbols('theta', real=True)
    lam_sub = phi0 * (1 + sp.sqrt(2) * sp.cos(theta))
    poly_sub = sp.expand(char_poly.subs(lam, lam_sub))

    # Using identity: cos(3*theta) = 4*cos(theta)^3 - 3*cos(theta)
    # Check if poly_sub equals: phi0^3 / sqrt(2) * cos(3*theta) - (phi0^3 / 2 + det_val)
    # Let X = cos(theta)
    X = sp.symbols('X')
    poly_in_X = poly_sub.subs(sp.cos(theta), X)
    poly_in_X = sp.collect(poly_in_X, X)

    # Coeff of X^3 is 2*sqrt(2)*phi0^3
    # Coeff of X is -3*sqrt(2)*phi0^3 / 2
    # Ratio is 4 : -3, exactly the Chebyshev T_3(X) = 4*X^3 - 3*X !
    coeff_X3 = poly_in_X.coeff(X, 3)
    coeff_X1 = poly_in_X.coeff(X, 1)
    coeff_X2 = poly_in_X.coeff(X, 2)
    constant_term = poly_in_X.subs(X, 0)

    chebyshev_ratio_exact = sp.simplify(coeff_X3 / coeff_X1) == sp.Rational(4, -3)
    x2_is_identically_zero = coeff_X2 == 0

    return {
        "equipartition_holds": equipartition_holds,
        "sol_c8": sol_c8,
        "tr_singlet2": tr_singlet2,
        "x2_is_identically_zero": x2_is_identically_zero,
        "chebyshev_ratio_exact": chebyshev_ratio_exact,
        "constant_term": constant_term
    }


def compute_numerical_invariants():
    """
    Computes the exact numerical invariants for the physical charged lepton sector.
    """
    me = M_ELECTRON.val
    mm = M_MUON.val
    mt = M_TAU.val

    v = np.array([math.sqrt(me), math.sqrt(mm), math.sqrt(mt)])
    phi0 = np.sum(v) / 3.0
    det_phi = np.prod(v)

    # Invariants
    tr_phi = 3.0 * phi0
    tr_phi2 = np.sum(v**2)
    tr_phi_singlet2 = 3.0 * phi0**2
    tr_phi8_2 = tr_phi2 - tr_phi_singlet2

    ratio_equipartition = tr_phi8_2 / tr_phi_singlet2

    # Chebyshev phase alpha:
    # cos(3*alpha) = (1/sqrt(2)) * (1 + 2*det(Phi)/phi0^3)
    det_ratio = det_phi / (phi0**3)
    cos_3alpha = (1.0 / math.sqrt(2.0)) * (1.0 + 2.0 * det_ratio)
    alpha_rad = math.acos(cos_3alpha) / 3.0
    alpha_deg = math.degrees(alpha_rad)

    # Reconstruct masses from Chebyshev formula:
    reconstructed_sqrt = np.array([
        phi0 * (1.0 + math.sqrt(2.0) * math.cos(alpha_rad + 2.0 * math.pi * k / 3.0))
        for k in range(3)
    ])
    # Sort to match [me, mm, mt]
    reconstructed_masses = np.sort(reconstructed_sqrt ** 2)
    measured_masses = np.sort(np.array([me, mm, mt]))
    diffs = np.abs(reconstructed_masses - measured_masses)

    return {
        "phi0": phi0,
        "det_phi": det_phi,
        "det_ratio": det_ratio,
        "tr_phi_singlet2": tr_phi_singlet2,
        "tr_phi8_2": tr_phi8_2,
        "ratio_equipartition": ratio_equipartition,
        "cos_3alpha": cos_3alpha,
        "alpha_rad": alpha_rad,
        "alpha_deg": alpha_deg,
        "reconstructed_masses": reconstructed_masses,
        "measured_masses": measured_masses,
        "diffs": diffs
    }


if __name__ == "__main__":
    print("=" * 78)
    print("SYMBOLIC PROOF OF U(3) CASIMIR EQUIPARTITION AND CUBIC CHEBYSHEV THEOREM")
    print("=" * 78)
    sym = verify_algebraic_theorems_symbolic()
    print(f"1. Equipartition Condition Tr(Phi_8^2) == Tr(Phi_singlet^2): {sym['equipartition_holds']}")
    print(f"   Tr(Phi_8^2) required by Q=2/3: {sym['sol_c8']}")
    print(f"   Tr(Phi_singlet^2):             {sym['tr_singlet2']}")
    print(f"2. Shifted quadratic term (X^2 coefficient): {sym['x2_is_identically_zero']} (identically 0)")
    print(f"3. Cubic Chebyshev ratio coeff(X^3)/coeff(X) == -4/3: {sym['chebyshev_ratio_exact']}")
    print("-" * 78)

    print("NUMERICAL PHYSICAL VALUES (Charged Lepton Sector):")
    num = compute_numerical_invariants()
    print(f"  Singlet scale phi0:             {num['phi0']:.8f} MeV^(1/2)")
    print(f"  Determinant det(Phi):           {num['det_phi']:.8f} MeV^(3/2)")
    print(f"  Dimensionless ratio det/phi0^3: {num['det_ratio']:.8f}")
    print(f"  Tr(Phi_singlet^2):              {num['tr_phi_singlet2']:.8f} MeV")
    print(f"  Tr(Phi_8^2):                    {num['tr_phi8_2']:.8f} MeV")
    print(f"  Equipartition ratio Tr8 / Tr0:  {num['ratio_equipartition']:.10f}  (Exact target: 1.0000000000)")
    print(f"  Chebyshev angle alpha:          {num['alpha_rad']:.8f} rad ({num['alpha_deg']:.6f} deg)")
    print("-" * 78)
    print("Reconstructed vs Measured Masses (MeV):")
    for name, rec, meas, d in zip(["Electron", "Muon", "Tau"], num['reconstructed_masses'], num['measured_masses'], num['diffs']):
        print(f"  {name:8s}: Reconstructed = {rec:12.6f} | Measured = {meas:12.6f} | Diff = {d:.2e} MeV")
    print("=" * 78)
