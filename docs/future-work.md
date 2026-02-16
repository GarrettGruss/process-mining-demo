# Future Work

## Threshold methods to identify system events

## Social Network Analysis (SNA) of system events

Reinterpret van der Aalst's SNA metrics in the context of system failure propagation, where subsystems are the performers and failure cases are the process instances. Handover-of-work metrics quantify how one subsystem's failure triggers another's. Subcontracting patterns (A → B → A) reveal feedback loops in failure chains. The working-together metric identifies common-cause failures — subsystems that frequently appear in the same failure cases likely share a vulnerability. Performer-by-activity similarity (via Hamming or Pearson distance on transition profiles) finds subsystems with shared failure patterns even without direct interaction. The result is a weighted, directed sociogram of subsystem relationships during failures that can also validate safety case independence assumptions — strong causal coupling between supposedly independent subsystems indicates a gap in the defence-in-depth argument.

## Wavelet transform to identify system events

### Denoising as preprocessing

Apply wavelet denoising to clean raw sensor channels before running existing threshold or extrema-based event detectors. Decompose the signal with `pywt.wavedec()`, threshold small coefficients (noise) with `pywt.threshold()`, and reconstruct with `pywt.waverec()`. This reduces false positives from noise and false negatives from overly conservative thresholds, making existing detection methods more robust without changing their logic.

### Multi-scale change-point detection

Use wavelet coefficients as an alternative event detection strategy that identifies events based on structural signal changes rather than fixed value thresholds. The Stationary Wavelet Transform (`pywt.swt()`) is the best fit because it is shift-invariant — detected event timestamps do not depend on signal alignment, which matters for the `CaseGenerator` time-window approach. Large coefficients at coarse scales correspond to major state transitions (e.g. throttle on/off, gear shifts), while large coefficients at fine scales correspond to sharp transients (e.g. bumpstop hits, wheel lockups). Different wavelet bases suit different signal types: Haar or db2 for sharp mechanical events, Morlet for oscillating signals, and db4–db6 for general telemetry channels.

## Change-point detection via Ruptures

Use the `ruptures` library to detect points where the statistical properties of a denoised signal change, replacing manual threshold selection with a single penalty parameter. Each detected change point becomes a system event with a timestamp and activity label derived from the sensor and nature of the change. The `Pelt` search method runs in linear time and is a good default. The cost model determines what kind of change is detected: `"l2"` for mean shifts (throttle position, gear state), `"rbf"` for general distributional changes including variance (vibration, noise characteristics), and `"clinear"` for slope changes (temperature drift, pressure trends). The penalty parameter controls sensitivity — higher values yield fewer, more significant events — and can be set using the Guralnik & Srivastava cross-validation approach rather than manual tuning.

## Wavelet basis selection via event detection feedback

There is no principled method for choosing the best wavelet basis for a given signal (Guo et al., 2022). The event detection pipeline offers a potential feedback mechanism: for each candidate wavelet basis, decompose and denoise the signal, run change-point detection, and score the result using a quality metric such as the likelihood criteria or cross-validation risk from Guralnik & Srivastava (1999). The wavelet that produces the best-scoring segmentation wins. This is a natural extension of Guralnik & Srivastava's framework, which explicitly supports arbitrary basis classes including wavelets, and whose leave-one-out cross-validation avoids overfitting without requiring ground truth change points.
