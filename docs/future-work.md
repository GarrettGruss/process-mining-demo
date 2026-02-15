# Future Work

## Wavelet basis selection via event detection feedback

One of the open challenges in wavelet analysis is that there is no principled method for choosing the best wavelet basis for a given signal (Guo et al., 2022). Currently this is done by domain expertise or trial-and-error. The event detection pipeline offers a potential feedback mechanism to automate this.

### Idea

Use change-point detection quality as an objective function for wavelet basis selection. The pipeline would be:

1. For each candidate wavelet basis (e.g. Haar, db4, db8, sym5, coif3, etc.):
   - Decompose the signal using that wavelet (via `pywt.swt()` or `pywt.wavedec()`)
   - Optionally denoise by thresholding small coefficients
   - Run change-point detection (e.g. via Ruptures) on the wavelet coefficients or on the denoised/reconstructed signal
   - Evaluate the quality of the detected change points
2. Select the wavelet basis that produces the best change-point detection results.

### Connection to Guralnik & Srivastava (1999)

The event detection algorithm from Guralnik & Srivastava provides two direct mechanisms for this:

**Approach 1: Wavelets as the basis class.** The paper explicitly states that their approach works with *any* basis class, listing "radial, wavelet, Fourier, etc." as alternatives to the polynomials used in their experiments (Section 2.3). Instead of fitting polynomials (1, t, t², t³) to each segment, wavelet basis functions could be used directly. The model selection via leave-one-out cross-validation would then automatically choose the best wavelet representation for each segment. Different segments could even use different wavelet bases — one segment might be best described by a Haar basis (sharp transition), another by Daubechies (smoother behavior).

**Approach 2: Likelihood criteria as the wavelet selection objective.** The batch algorithm's likelihood criteria and stopping criterion provide a principled, unsupervised scoring function. For each candidate wavelet: denoise the signal → run change-point detection → compute the total likelihood of the resulting segmented model. The wavelet that produces the lowest likelihood criteria wins.

The cross-validation approach is especially valuable here because it avoids overfitting — you don't need ground truth change points to evaluate which wavelet is better.

### Quality metrics to optimize

- **Likelihood criteria** from the Guralnik & Srivastava batch algorithm — lower is better, meaning the piecewise model fits the segments well
- **Cross-validation risk** from the Guralnik model selection step — directly measures how well the wavelet basis generalizes to unseen data points within each segment
- **Stability of detected change points** across multiple wavelet scales — if the same change point appears at coarse and fine scales, it's more likely to be real
- **Consistency with known ground truth** if available (e.g. in a supervised calibration phase)
- **Parsimony** — fewer change points with equivalent likelihood suggests a better denoising/decomposition that removes spurious transitions

### Why this could work

- Different wavelets have different trade-offs (vanishing moments, support length, regularity) that affect how well they capture the signal's characteristics
- A wavelet that matches the signal's structure will produce sparser coefficients with clearer separation between signal and noise
- Cleaner separation → better denoising → fewer spurious change points → more reliable events for process mining
- The Guralnik algorithm already solves the model selection problem for arbitrary basis classes — extending it to wavelet bases is a natural generalization, not a new algorithm
- This turns the "no principled basis selection method" research gap into an optimization problem with a concrete objective function

### Implementation sketch

```
import pywt
import ruptures as rpt

def evaluate_wavelet(signal, wavelet_name, n_levels=4):
    """Score a wavelet basis by change-point detection quality."""
    # Decompose
    coeffs = pywt.swt(signal, wavelet_name, level=n_levels)

    # Denoise via thresholding
    denoised = wavelet_denoise(signal, wavelet_name, n_levels)

    # Detect change points
    algo = rpt.Pelt(model="rbf").fit(denoised)
    change_points = algo.predict(pen=penalty)

    # Score: e.g. likelihood of the segmented model
    return score_segmentation(denoised, change_points)

candidates = pywt.wavelist(kind='discrete')
scores = {w: evaluate_wavelet(signal, w) for w in candidates}
best_wavelet = min(scores, key=scores.get)
```

### Open questions

- How sensitive is the optimal wavelet choice to the specific signal or domain? Is the best wavelet consistent across signals from the same sensor/process, or does it need per-signal selection?
- Should the wavelet selection optimize for the raw change-point detection, or for downstream process mining quality (e.g. do the resulting event logs produce meaningful social networks)?
- Can this be extended to learn custom wavelet filter banks (via `pywt.Wavelet` with custom filters) rather than just selecting from predefined families?
