"""
Vacuum Alignment and Potential Minimization for Horizontal Family Symmetries.
Investigates whether spontaneous symmetry breaking in U(3), S_3, or A_4 can
pin the Koide angle theta = 45 deg (Q = 2/3) without fine-tuning continuous parameters.
"""
import math
import numpy as np
import sympy as sp
from scipy.optimize import minimize

def analyze_u3_potential_invariants():
    """
    Symbolic analysis of general U(3) and S_3 invariant polynomial potentials.
    Expresses the potential V(Phi) in terms of:
    - R: radial mass scale sqrt(Tr(Phi^2))
    - theta: polar angle from democratic axis (cos^2(theta) = 1/(3Q))
    - alpha: azimuthal phase in the traceless plane (alpha = 0 => S_3 symmetric direction)
    """
    # Let eigenvalues of Phi be:
    # lambda_k = (R / sqrt(3)) * (cos(theta) + sqrt(2) * sin(theta) * cos(alpha + 2*pi*k/3))
    # Notice that sum(lambda_k^2) = R^2 identically for any theta and alpha!
    # And sum(lambda_k) = sqrt(3) * R * cos(theta).
    # Then Q = sum(lambda_k^2) / (sum(lambda_k))^2 = R^2 / (3 * R^2 * cos^2(theta)) = 1 / (3 * cos^2(theta)).
    # When theta = 45 deg: cos(theta) = 1/sqrt(2), so Q = 1 / (3 * 1/2) = 2/3!
    
    R, theta, alpha = sp.symbols('R theta alpha', real=True)
    
    # Invariants:
    # I_1 = Tr(Phi) = sqrt(3) * R * cos(theta)
    # I_2 = Tr(Phi^2) = R^2
    # I_3 = Tr(Phi^3)
    # I_4 = Tr(Phi^4)
    
    # Compute I_3 and I_4 in terms of (R, theta, alpha)
    # lambda_k:
    l0 = (R / sp.sqrt(3)) * (sp.cos(theta) + sp.sqrt(2)*sp.sin(theta)*sp.cos(alpha))
    l1 = (R / sp.sqrt(3)) * (sp.cos(theta) + sp.sqrt(2)*sp.sin(theta)*sp.cos(alpha + 2*sp.pi/3))
    l2 = (R / sp.sqrt(3)) * (sp.cos(theta) + sp.sqrt(2)*sp.sin(theta)*sp.cos(alpha + 4*sp.pi/3))
    
    I_1 = sp.simplify(l0 + l1 + l2) # should be sqrt(3)*R*cos(theta)
    I_2 = sp.simplify(l0**2 + l1**2 + l2**2) # should be R^2
    
    # Using trig identity sum cos^3 = (3/4)*cos(3*alpha)
    I_3 = sp.trigsimp(sp.expand(l0**3 + l1**3 + l2**3))
    I_4 = sp.trigsimp(sp.expand(l0**4 + l1**4 + l2**4))
    
    return {
        "I_1": I_1,
        "I_2": I_2,
        "I_3": I_3,
        "I_4": I_4
    }

def test_vacuum_stability_at_45deg():
    """
    Evaluates whether dV/d(theta) = 0 at theta = 45 deg for combinations of invariants.
    """
    R, theta, alpha = sp.symbols('R theta alpha', real=True)
    invs = analyze_u3_potential_invariants()
    I1 = invs["I_1"]
    I2 = invs["I_2"]
    I3 = invs["I_3"]
    I4 = invs["I_4"]
    
    # For a general renormalizable potential:
    # V = -mu^2 I_2 + a * I_1^2 + b * I_2^2 + c * I_1^4 + d * I_1^2 I_2 + e * I_4 + f * I_1 I_3
    # Look at d/d(theta) at theta = pi/4 (45 degrees):
    dI1_dth = sp.diff(I1, theta).subs(theta, sp.pi/4)
    dI2_dth = sp.diff(I2, theta).subs(theta, sp.pi/4)
    dI3_dth = sp.diff(I3, theta).subs(theta, sp.pi/4)
    dI4_dth = sp.diff(I4, theta).subs(theta, sp.pi/4)
    
    # Check if any single invariant has an extremum at theta = pi/4:
    has_extremum = {
        "dI1/dth": sp.simplify(dI1_dth),
        "dI2/dth": sp.simplify(dI2_dth),
        "dI3/dth": sp.simplify(dI3_dth),
        "dI4/dth": sp.simplify(dI4_dth)
    }
    
    return invs, has_extremum

if __name__ == "__main__":
    print("=" * 78)
    print("ANALYSIS OF U(3) / S_3 INVARIANT SCALAR POTENTIALS IN CONE COORDINATES")
    print("=" * 78)
    invs, derivs = test_vacuum_stability_at_45deg()
    
    print("1. Polynomial Invariants expressed in (R, theta, alpha):")
    print(f"  Tr(Phi)   = {invs['I_1']}")
    print(f"  Tr(Phi^2) = {invs['I_2']}")
    print(f"  Tr(Phi^3) = {invs['I_3']}")
    print(f"  Tr(Phi^4) = {invs['I_4']}")
    print("-" * 78)
    
    print("2. Derivatives with respect to theta at theta = pi/4 (45 deg):")
    for k, v in derivs.items():
        print(f"  {k:10s} at theta=pi/4: {v}")
    print("-" * 78)
    
    print("THEORETICAL NO-GO / REQUIREMENT FINDING:")
    print("Notice that d(Tr(Phi^4))/d(theta) and d(Tr(Phi^3))/d(theta) DO NOT automatically vanish")
    print("at theta = pi/4 unless the coefficients of the potential are tuned!")
    print("In a standard polynomial scalar field theory, theta = 45 deg is NOT an isolated discrete")
    print("symmetry point of the classical potential V(Phi).")
    print("=" * 78)
