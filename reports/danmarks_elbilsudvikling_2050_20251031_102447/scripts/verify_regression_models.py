#!/usr/bin/env python3
"""
Verify regression models with scipy.optimize to ensure accuracy.
Compares grid search results with proper optimization.

Usage:
    cd reports/danmarks_elbilsudvikling_2050_20251031_102447/scripts/
    source ../../../.venv/bin/activate
    python verify_regression_models.py
"""

import csv
import os
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def main():
    # Read data (relative path from scripts/ to project root data/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '../../..')
    data_path = os.path.join(project_root, 'data/ev_annual_bil10.csv')

    years = []
    shares = []
    with open(data_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            years.append(int(row['year']))
            shares.append(float(row['ev_share_pct']))

    years = np.array(years)
    shares = np.array(shares)
    t = years - 1993  # Time since 1993

    print("="*70)
    print("VERIFICERING MED SCIPY.OPTIMIZE.CURVE_FIT")
    print("="*70)
    print(f"\nData: {len(years)} år (1993-2025)")
    print(f"Metode: scipy.optimize.curve_fit (Levenberg-Marquardt)")
    print(f"Dette er den KORREKTE måde at fitte ikke-lineære modeller.")

    # ========================================================================
    # MODEL 1: LOGISTISK MED FRIT L (scipy estimerer alle parametre)
    # ========================================================================
    print("\n\n### MODEL 1: LOGISTISK (frit L - scipy estimerer) ###\n")

    def logistic(t, L, k, t0):
        return L / (1 + np.exp(-k * (t - t0)))

    try:
        # Initial guess
        p0 = [80, 0.5, 30]  # L=80%, k=0.5, t0=30

        # Fit with bounds
        bounds = ([50, 0.1, 20], [100, 2.0, 50])  # L: 50-100%, k: 0.1-2.0, t0: 20-50

        params_free, _ = curve_fit(logistic, t, shares, p0=p0, bounds=bounds, maxfev=10000)
        L_free, k_free, t0_free = params_free

        # Calculate R²
        pred_free = logistic(t, L_free, k_free, t0_free)
        r2_free = r2_score(shares, pred_free)
        rmse_free = np.sqrt(np.mean((shares - pred_free)**2))

        print(f"Optimerede parametre:")
        print(f"  L (mætning) = {L_free:.2f}%")
        print(f"  k (vækstrate) = {k_free:.4f}")
        print(f"  t0 (inflection) = {t0_free:.2f} → år {1993 + t0_free:.0f}")
        print(f"\nModel kvalitet:")
        print(f"  R² = {r2_free:.6f}")
        print(f"  RMSE = {rmse_free:.4f} procentpoint")

        logistic_free_result = {
            'L': L_free,
            'k': k_free,
            't0': t0_free,
            'r2': r2_free,
            'rmse': rmse_free
        }

    except Exception as e:
        print(f"FEJL: {e}")
        logistic_free_result = None

    # ========================================================================
    # MODEL 2: LOGISTISK MED FASTSAT L (test forskellige værdier)
    # ========================================================================
    print("\n\n### MODEL 2: LOGISTISK (fastsat L - test 70%, 80%, 90%, 95%) ###\n")

    def logistic_fixed_L(t, k, t0, L_fixed):
        return L_fixed / (1 + np.exp(-k * (t - t0)))

    results_fixed = {}

    print(f"{'L (fastsat)':>12} {'k':>10} {'t0':>8} {'t0 (år)':>10} {'R²':>10} {'RMSE':>10}")
    print("-"*70)

    for L_fixed in [70, 75, 80, 85, 90, 95]:
        try:
            # Fit only k and t0 with L fixed
            p0 = [0.5, 30]
            bounds = ([0.1, 20], [2.0, 50])

            params, _ = curve_fit(
                lambda t, k, t0: logistic_fixed_L(t, k, t0, L_fixed),
                t, shares, p0=p0, bounds=bounds, maxfev=10000
            )
            k_fit, t0_fit = params

            # Calculate metrics
            pred = logistic_fixed_L(t, k_fit, t0_fit, L_fixed)
            r2 = r2_score(shares, pred)
            rmse = np.sqrt(np.mean((shares - pred)**2))

            results_fixed[L_fixed] = {
                'k': k_fit,
                't0': t0_fit,
                'r2': r2,
                'rmse': rmse,
                'pred': pred
            }

            inflection_year = 1993 + t0_fit
            print(f"{L_fixed:>11}% {k_fit:>10.4f} {t0_fit:>8.2f} {inflection_year:>10.0f} {r2:>10.6f} {rmse:>10.4f}")

        except Exception as e:
            print(f"{L_fixed:>11}% FEJL: {e}")

    # Find best
    if results_fixed:
        best_fixed_L = max(results_fixed.keys(), key=lambda L: results_fixed[L]['r2'])
        print(f"\n✓ Bedste fastsat L: {best_fixed_L}% (R² = {results_fixed[best_fixed_L]['r2']:.6f})")

    # ========================================================================
    # MODEL 3: GOMPERTZ MED FRIT L
    # ========================================================================
    print("\n\n### MODEL 3: GOMPERTZ (frit L - scipy estimerer) ###\n")

    def gompertz(t, L, k, t0):
        return L * np.exp(-np.exp(-k * (t - t0)))

    try:
        p0 = [80, 0.2, 30]
        bounds = ([50, 0.05, 20], [100, 1.0, 50])

        params_gomp, _ = curve_fit(gompertz, t, shares, p0=p0, bounds=bounds, maxfev=10000)
        L_gomp, k_gomp, t0_gomp = params_gomp

        pred_gomp = gompertz(t, L_gomp, k_gomp, t0_gomp)
        r2_gomp = r2_score(shares, pred_gomp)
        rmse_gomp = np.sqrt(np.mean((shares - pred_gomp)**2))

        print(f"Optimerede parametre:")
        print(f"  L (mætning) = {L_gomp:.2f}%")
        print(f"  k (vækstrate) = {k_gomp:.4f}")
        print(f"  t0 (inflection) = {t0_gomp:.2f} → år {1993 + t0_gomp:.0f}")
        print(f"\nModel kvalitet:")
        print(f"  R² = {r2_gomp:.6f}")
        print(f"  RMSE = {rmse_gomp:.4f} procentpoint")

        gompertz_free_result = {
            'L': L_gomp,
            'k': k_gomp,
            't0': t0_gomp,
            'r2': r2_gomp,
            'rmse': rmse_gomp
        }

    except Exception as e:
        print(f"FEJL: {e}")
        gompertz_free_result = None

    # ========================================================================
    # MODEL 4: GOMPERTZ MED FASTSAT L
    # ========================================================================
    print("\n\n### MODEL 4: GOMPERTZ (fastsat L - test 70%, 80%, 90%, 95%) ###\n")

    def gompertz_fixed_L(t, k, t0, L_fixed):
        return L_fixed * np.exp(-np.exp(-k * (t - t0)))

    results_gomp_fixed = {}

    print(f"{'L (fastsat)':>12} {'k':>10} {'t0':>8} {'t0 (år)':>10} {'R²':>10} {'RMSE':>10}")
    print("-"*70)

    for L_fixed in [70, 75, 80, 85, 90, 95]:
        try:
            p0 = [0.2, 30]
            bounds = ([0.05, 20], [1.0, 50])

            params, _ = curve_fit(
                lambda t, k, t0: gompertz_fixed_L(t, k, t0, L_fixed),
                t, shares, p0=p0, bounds=bounds, maxfev=10000
            )
            k_fit, t0_fit = params

            pred = gompertz_fixed_L(t, k_fit, t0_fit, L_fixed)
            r2 = r2_score(shares, pred)
            rmse = np.sqrt(np.mean((shares - pred)**2))

            results_gomp_fixed[L_fixed] = {
                'k': k_fit,
                't0': t0_fit,
                'r2': r2,
                'rmse': rmse
            }

            inflection_year = 1993 + t0_fit
            print(f"{L_fixed:>11}% {k_fit:>10.4f} {t0_fit:>8.2f} {inflection_year:>10.0f} {r2:>10.6f} {rmse:>10.4f}")

        except Exception as e:
            print(f"{L_fixed:>11}% FEJL: {e}")

    if results_gomp_fixed:
        best_gomp_fixed_L = max(results_gomp_fixed.keys(), key=lambda L: results_gomp_fixed[L]['r2'])
        print(f"\n✓ Bedste fastsat L: {best_gomp_fixed_L}% (R² = {results_gomp_fixed[best_gomp_fixed_L]['r2']:.6f})")

    # ========================================================================
    # SAMMENLIGNING OG KONKLUSION
    # ========================================================================
    print("\n\n" + "="*70)
    print("SAMMENLIGNING AF ALLE MODELLER (scipy-optimeret)")
    print("="*70)

    print(f"\n{'Model':>35} {'L':>8} {'k':>10} {'t0 (år)':>10} {'R²':>10} {'RMSE':>10}")
    print("-"*85)

    all_results = []

    if logistic_free_result:
        r = logistic_free_result
        print(f"{'Logistisk (frit L)':>35} {r['L']:>7.2f}% {r['k']:>10.4f} {1993+r['t0']:>10.0f} {r['r2']:>10.6f} {r['rmse']:>10.4f}")
        all_results.append(('Logistisk (frit L)', r['r2'], r['L'], r['rmse']))

    if results_fixed:
        for L in sorted(results_fixed.keys()):
            r = results_fixed[L]
            print(f"{'Logistisk (L=' + str(L) + '%)':>35} {L:>7d}% {r['k']:>10.4f} {1993+r['t0']:>10.0f} {r['r2']:>10.6f} {r['rmse']:>10.4f}")
            all_results.append((f'Logistisk (L={L}%)', r['r2'], L, r['rmse']))

    if gompertz_free_result:
        r = gompertz_free_result
        print(f"{'Gompertz (frit L)':>35} {r['L']:>7.2f}% {r['k']:>10.4f} {1993+r['t0']:>10.0f} {r['r2']:>10.6f} {r['rmse']:>10.4f}")
        all_results.append(('Gompertz (frit L)', r['r2'], r['L'], r['rmse']))

    if results_gomp_fixed:
        for L in sorted(results_gomp_fixed.keys()):
            r = results_gomp_fixed[L]
            print(f"{'Gompertz (L=' + str(L) + '%)':>35} {L:>7d}% {r['k']:>10.4f} {1993+r['t0']:>10.0f} {r['r2']:>10.6f} {r['rmse']:>10.4f}")
            all_results.append((f'Gompertz (L={L}%)', r['r2'], L, r['rmse']))

    # Find best
    if all_results:
        best_model = max(all_results, key=lambda x: x[1])
        print(f"\n{'='*85}")
        print(f"🏆 BEDSTE MODEL OVERORDNET: {best_model[0]}")
        print(f"   R² = {best_model[1]:.6f}")
        print(f"   Mætning (L) = {best_model[2]:.1f}%")
        print(f"   RMSE = {best_model[3]:.4f} procentpoint")
        print(f"{'='*85}")

    # ========================================================================
    # KRITISK ANALYSE
    # ========================================================================
    print("\n\n" + "="*70)
    print("KRITISK ANALYSE")
    print("="*70)

    print("\n### 1. Sammenligning med Oprindelig Model (L=70%)")
    print("\nDen oprindelige dst-analyze-agent fandt:")
    print("  Logistisk L=70%: R²=0.9953, k=0.504, t0=34.28 (år 2027)")

    if 70 in results_fixed:
        print(f"\nDenne scipy-verificering finder:")
        print(f"  Logistisk L=70%: R²={results_fixed[70]['r2']:.4f}, k={results_fixed[70]['k']:.4f}, t0={results_fixed[70]['t0']:.2f} (år {1993+results_fixed[70]['t0']:.0f})")

        diff_r2 = abs(0.9953 - results_fixed[70]['r2'])
        if diff_r2 < 0.001:
            print(f"\n  ✓ VALIDERET: Resultaterne stemmer overens (forskel i R²: {diff_r2:.6f})")
        else:
            print(f"\n  ⚠️ AFVIGELSE: R² forskel = {diff_r2:.6f}")

    print("\n### 2. Er L=70% Den Bedste Model?")

    if logistic_free_result and results_fixed:
        print(f"\nNår scipy får lov til at optimere L frit, vælger den:")
        print(f"  L = {logistic_free_result['L']:.2f}% (R² = {logistic_free_result['r2']:.6f})")

        if logistic_free_result['L'] > 75:
            print(f"\n  💡 INDSIGT: Dataen understøtter HØJERE mætning end 70%!")
            print(f"     Frit estimeret L er {logistic_free_result['L'] - 70:.1f} procentpoint højere.")

        # Compare R²
        if logistic_free_result['r2'] > results_fixed[70]['r2']:
            improvement = (logistic_free_result['r2'] - results_fixed[70]['r2']) * 100
            print(f"\n  📊 Frit L giver {improvement:.3f}% bedre fit end fastsat L=70%")

    print("\n### 3. Gompertz vs Logistisk")

    if gompertz_free_result and logistic_free_result:
        if gompertz_free_result['r2'] > logistic_free_result['r2']:
            improvement = (gompertz_free_result['r2'] - logistic_free_result['r2']) * 100
            print(f"\n  ✓ Gompertz har BEDRE fit end logistisk:")
            print(f"    Gompertz R² = {gompertz_free_result['r2']:.6f}")
            print(f"    Logistisk R² = {logistic_free_result['r2']:.6f}")
            print(f"    Forbedring: {improvement:.3f}%")
            print(f"\n  💡 For teknologi-adoption er Gompertz teoretisk bedre (asymmetrisk kurve)")
        else:
            print(f"\n  Logistisk og Gompertz har lignende fit (forskel < 0.1%)")

    print("\n### 4. Konklusion")
    print("\nBaseret på scipy-optimering:")

    if all_results:
        # Find top 3
        top3 = sorted(all_results, key=lambda x: x[1], reverse=True)[:3]
        print(f"\n  Top 3 modeller:")
        for i, (name, r2, L, rmse) in enumerate(top3, 1):
            print(f"    {i}. {name}: R²={r2:.6f}, L={L:.1f}%, RMSE={rmse:.4f}pp")

        print(f"\n  Anbefaling:")
        if best_model[2] >= 85:
            print(f"    ✓ Brug HØJ mætning scenarie (L=85-95%)")
            print(f"    ✓ Understøttes af: nyregistreringer ved 68.4%")
        elif best_model[2] >= 75:
            print(f"    ✓ Brug MELLEM mætning scenarie (L=75-85%)")
        else:
            print(f"    ⚠️ L=70% er statistisk acceptabel, men nyregistreringer")
            print(f"       ved 68% tyder på højere langsigtet mætning")

if __name__ == '__main__':
    main()
