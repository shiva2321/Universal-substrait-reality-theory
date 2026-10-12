"""
Master Test Runner for Koide Anomaly Research Package.
Executes all verification modules and produces an integrated report.
"""
import subprocess
import sys
import os

MODULES = [
    "koide_anomaly.data.constants",
    "koide_anomaly.geometry.cone_decomposition",
    "koide_anomaly.algebra.u3_casimirs",
    "koide_anomaly.vacuum_potential.alignment_solver",
    "koide_anomaly.algebra.clifford_idempotents",
    "koide_anomaly.rg_flow.qed_running",
    "koide_anomaly.algebra.cl6_generation_embedding",
    "koide_anomaly.rg_flow.sumino_mechanism",
    "koide_anomaly.algebra.unification_synthesis",
    "koide_anomaly.vacuum_potential.coleman_weinberg_potential",
    "koide_anomaly.simulations.prediction_1_tau_mass",
    "koide_anomaly.simulations.prediction_2_fcnc_decays",
    "koide_anomaly.simulations.prediction_3_quark_qcd_shift"
]

def run_suite():
    print("=" * 78)
    print("KOIDE RELATION & CHARGED LEPTON SPECTRUM: VERIFICATION SUITE")
    print("=" * 78)
    
    passed = 0
    failed = 0
    
    for mod in MODULES:
        print(f"\n[RUNNING] python -m {mod}")
        res = subprocess.run([sys.executable, "-m", mod], capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout)
            passed += 1
        else:
            print(f"FAILED with return code {res.returncode}")
            print("STDOUT:", res.stdout)
            print("STDERR:", res.stderr)
            failed += 1
            
    print("=" * 78)
    print(f"SUITE COMPLETE: {passed} passed, {failed} failed.")
    print("=" * 78)
    return failed == 0

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
