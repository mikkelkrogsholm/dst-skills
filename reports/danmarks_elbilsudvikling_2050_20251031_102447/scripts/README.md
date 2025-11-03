# Analysis Scripts for Danmarks Elbilsudvikling til 2050

## Report Details

- **Report:** Danmarks Elbilsudvikling og Fremskrivning til 2050
- **Generated:** 2025-10-31
- **Data Sources:** BIL10, BIL52, BIL51 (Danmarks Statistik)
- **Report Location:** `../report.html`

## Scripts Overview

### `verify_regression_models.py`

Comprehensive model verification using scipy.optimize.curve_fit.

**Purpose:**
- Verify the original L=70% logistic model
- Compare logistic vs Gompertz curves
- Test different saturation levels (L=70%, 80%, 85%, 90%, 95%)
- Identify the statistically best model

**Output:**
- Console output showing R², RMSE for all models
- Identifies best-fit parameters
- Validates against original analysis

**Key Finding:**
- Gompertz L=84% has the best fit (R²=0.9981)
- Original logistic L=70% is validated (R²=0.9953)
- Gompertz outperforms logistic for technology adoption modeling

## Reproducibility

### Prerequisites

Ensure you have the data science stack installed in the project virtual environment:

```bash
# From project root
source .venv/bin/activate
pip install numpy scipy pandas scikit-learn
```

Verify installation:
```bash
python -c "from scipy.optimize import curve_fit; print('✓ scipy available')"
```

### Running the Analysis

From the report's scripts directory:

```bash
cd reports/danmarks_elbilsudvikling_2050_20251031_102447/scripts/
source ../../../.venv/bin/activate
python verify_regression_models.py
```

Or from project root:

```bash
source .venv/bin/activate
python reports/danmarks_elbilsudvikling_2050_20251031_102447/scripts/verify_regression_models.py
```

### Expected Runtime

- **Duration:** ~2-5 seconds
- **Output:** ~100 lines of model comparison tables

## Results Summary

The verification confirms:

| Model | L (Saturation) | R² | RMSE | Verdict |
|-------|----------------|-----|------|---------|
| Gompertz (frit L) | 84.1% | 0.9981 | 0.156pp | 🏆 Best fit |
| Gompertz (L=85%) | 85% | 0.9981 | 0.156pp | Optimal |
| Logistic (L=70%) | 70% | 0.9953 | 0.249pp | Valid (original) |
| Exponential | 100% | 0.9823 | 0.70pp | Theoretical max |

### Interpretation

1. **Gompertz L=84%** provides the best statistical fit
2. **Logistic L=70%** (original model) is mathematically correct but conservative
3. Gompertz is theoretically superior for technology adoption (asymmetric S-curve)
4. New registrations (68% in 2025) support higher saturation (80-85%)

## Data Dependencies

This script requires:
- `../../../data/ev_annual_bil10.csv` - Annual EV fleet data (1993-2025)

Ensure the data file exists before running. If not, fetch it:

```bash
cd ../../../
source .venv/bin/activate
python scripts/fetch_and_store.py --table-id BIL10
```

## Integration with Report

The results from this script were used to:
1. Validate the original L=70% logistic model
2. Identify Gompertz L=84% as the best-fit alternative
3. Inform the three-scenario approach in the final report:
   - Scenario 1: Exponential (100% by 2028)
   - Scenario 2: Gompertz L=84% (primary forecast)
   - Scenario 3: Logistic L=70% (conservative)

See `../report.html` Section "Methodology" for details.

## Technical Notes

### Optimization Method

Uses scipy's `curve_fit` with:
- **Algorithm:** Levenberg-Marquardt (non-linear least squares)
- **Bounds:** Constrains parameters to realistic ranges
  - L (saturation): 50-100%
  - k (growth rate): 0.1-2.0
  - t0 (inflection point): year 2013-2043
- **Max iterations:** 10,000 (ensures convergence)

### Why Not Grid Search?

Grid search (testing discrete parameter values) was initially attempted but:
- ❌ Coarse step sizes miss optimal values
- ❌ Computationally expensive for 3+ parameters
- ❌ Less accurate than continuous optimization

Scipy's curve_fit is the professional standard for non-linear regression.

### Model Equations

**Logistic (symmetric S-curve):**
```
y = L / (1 + exp(-k*(t - t0)))
```

**Gompertz (asymmetric S-curve):**
```
y = L * exp(-exp(-k*(t - t0)))
```

Where:
- `L` = saturation level (carrying capacity)
- `k` = growth rate
- `t0` = inflection point (year of maximum acceleration)

## Further Analysis Ideas

Potential extensions (not included in current report):

1. **Cross-validation:** Train-test split to validate generalization
2. **Confidence intervals:** Bootstrap or Bayesian methods
3. **Multivariate models:** Include policy variables, battery prices, etc.
4. **Regional analysis:** Model regional adoption differences (urban vs rural)
5. **Scenario modeling:** Simulate policy changes (ICE ban, subsidy removal)

## References

- **scipy.optimize.curve_fit:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
- **Gompertz curve:** https://en.wikipedia.org/wiki/Gompertz_function
- **Technology diffusion:** Rogers, E. M. (2003). Diffusion of Innovations.

## Contact

For questions about this analysis, see project documentation:
- `.claude/skills/data-science-tools/SKILL.md` - Data science setup
- `docs/architecture.md` - Project architecture
- `CLAUDE.md` - Project overview
