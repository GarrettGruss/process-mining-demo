# Wavelet Analysis Review — Guo et al. (2022)

Survey paper covering wavelet theory, signal decomposition methods, wavelet neural networks, and practical applications (~220 references).

## Why wavelets (vs. Fourier)

Fourier transform gives frequency content but loses time localization. STFT partially fixes this but uses a fixed window size, creating a resolution trade-off. Wavelets provide **adaptive resolution**: high time resolution at high frequencies (sharp transients) and high frequency resolution at low frequencies (slow trends). Naturally suited to non-stationary signals.

## Wavelet construction

- **MRA-based** (Multi-Resolution Analysis): classical approach using scaling functions and nested subspaces
- **Lifting scheme**: faster, less memory, handles arbitrary signal sizes. Extends to rational wavelets.

## Key wavelet properties (trade-offs)

- **Vanishing moments**: higher = better frequency localization and compression, but more computation
- **Support length**: shorter = faster, but fewer vanishing moments
- **Regularity**: smoother = better reconstruction, but longer support
- **Symmetry**: avoids phase distortion; only Haar is both orthogonal and symmetric
- **Orthogonality**: reduces coefficient correlation, good for decomposition

## Common wavelet bases

| Wavelet | Key trait | Best for |
|---|---|---|
| **Haar** | Simplest, discontinuous | Sharp transitions, illustration |
| **Daubechies (dbN)** | Good regularity, no symmetry | Signal reconstruction, general-purpose |
| **Coiflets** | Better symmetry than Daubechies | Similar to Daubechies |
| **Symlets** | Approximately symmetric | Similar to Daubechies |
| **Biorthogonal** | Solves linear phase vs. orthogonality trade-off | Signal and image reconstruction |
| **Meyer** | Infinitely derivable, not compactly supported | Signal decomposition |
| **Gaussian** | Non-orthogonal | WNN activation function |
| **Mexican Hat** | Good time-frequency localization, no scale function | Edge detection, visual processing |
| **Morlet** | Complex wave in Gaussian envelope, extracts amplitude + phase | Oscillating signals, WNN |

## Signal decomposition architectures

### Discrete Wavelet Transform (DWT)

Most widely used. Two-channel filter bank (high-pass + low-pass with downsampling). Recursively decomposes only the low-frequency component. Low-frequency = approximation; high-frequency = details/transients.

### Extensions

- **Stationary Wavelet Transform (SWT)**: DWT without downsampling — shift-invariant, exact timing preserved. Relevant for change-point detection where precise timestamps matter.
- **Wavelet Packet (WP)**: decomposes *both* low and high-frequency bands at each level. Finer frequency resolution at high frequencies. Better when important changes occur in high-frequency bands.
- **Complex Wavelet Transform**: adds phase information, better directional selectivity in 2D+.
- **Dual-Tree Complex WT (DT-CWT)**: efficient complex WT implementation, low redundancy. Widely used in image processing.
- **Rational Wavelet Transform (RWT)**: rational dilation factor (p/q instead of 2), non-uniform and finer frequency partitions. Better for oscillating signals (speech, audio). Underexplored — highlighted as a research direction.

## Wavelet Neural Networks (WNN)

Two approaches:

1. **Wavelet as preprocessing**: decompose signal via wavelet transform, extract features (energy, mean, std, RMS, peak value at each decomposition level), feed into a standard neural network. Can reduce prediction error by ~50%.
2. **Deep fusion**: replace the hidden layer activation function with a wavelet function (Gaussian, Morlet, or Mexican Hat). Scale and translation parameters replace traditional weights/thresholds. Faster convergence, better at approximating singularities.

## Relevance to change-point detection / event generation

- **SWT** is particularly relevant because shift-invariance means detected change timing doesn't depend on signal alignment
- **Wavelet Packet** decomposition is useful when changes occur in high-frequency bands that standard DWT ignores
- High wavelet coefficients at coarse scales = significant structural changes = candidate change points for process mining events
- Wavelet denoising (thresholding small coefficients) can clean up signals *before* applying change-point detection, addressing noise sensitivity

## Implementation: PyWavelets (`pywt`)

Python package for wavelet analysis. Lee et al. (2019), JOSS. `pip install PyWavelets`.

### What it provides

- N-dimensional discrete wavelet transforms (1D, 2D, 3D, and n>3)
- 1D continuous wavelet transform
- Wide variety of **predefined wavelets** — covers all the bases in the table above (Haar, Daubechies, Coiflets, Symlets, Biorthogonal, Meyer, Gaussian, Mexican Hat, Morlet, etc.)
- Custom wavelet filter banks (define your own FIR filters)
- Real and complex-valued data in single or double precision
- Per-axis control: can transform only a subset of axes, vary wavelet and boundary mode per axis

### Key implementation details

- Core convolutions implemented in **C** (via Cython) for performance
- Multi-dimensional transforms built from separable application of 1D transforms
- API modeled after Matlab's wavelet toolbox — familiar interface, tested for accuracy against Matlab counterparts
- Includes common 1D demo signals from the literature for reproducible research

### Relevant functions for change-point detection workflow

- `pywt.dwt()` / `pywt.wavedec()` — single-level / multi-level DWT decomposition
- `pywt.swt()` / `pywt.swtn()` — stationary wavelet transform (shift-invariant, preserves timestamps)
- `pywt.wp` — wavelet packet decomposition
- `pywt.cwt()` — continuous wavelet transform (for exploratory time-frequency analysis)
- `pywt.threshold()` — wavelet coefficient thresholding for denoising
- `pywt.wavelist()` — list all available wavelet families

### Related packages

- **Ruptures** (`ruptures`): change-point detection algorithms. Can be combined with PyWavelets by pre-transforming signals or writing custom cost functions.
- **Kymatio**: wavelet scattering transforms in 1D-3D. Non-separable 2D/3D wavelets in frequency domain. Suited to signal classification, no simple inverse transform.
- **scikit-image**: uses PyWavelets for wavelet-based image denoising.

## Open challenges

1. High-dimensional wavelet theory underdeveloped
2. No principled method for wavelet basis selection — still a research gap
3. RWT underused despite advantages for oscillating signals
4. WNN architecture design is mostly trial-and-error
