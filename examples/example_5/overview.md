# Overview

This project will take the FSAE data, apply a wavelit denoising function across the time-series data, classify it using an event extractor that adheres to the SHIP standards, then perform a social network analysis (SNA) to construct the event graphs.

## Implementation Overview

### Step 1: Wavelit Denoiser

Apply wavelet denoising to clean raw sensor channels before running existing threshold or extrema-based event detectors. Decompose the signal with `pywt.wavedec()`, threshold small coefficients (noise) with `pywt.threshold()`, and reconstruct with `pywt.waverec()`. This reduces false positives from noise and false negatives from overly conservative thresholds, making existing detection methods more robust without changing their logic.

### Step 2: Classifier

Extend the event classifier to label detected events as safety-state transitions from the Bishop & Bloomfield (1995) fault-error-failure model. Create a class representation of each subsystem that stores the subsystem name and other metadata, a list of `eventClassifier` methods for each event type (erronous, safe, dangerous, etc.). Maybe use a method reference or some other composable way to construct these classes. Refer to `examples/example_4/event_extractor.py` for source code.

reference: Each change point produced by the detection pipeline is currently just "the signal changed here" — the SHIP model provides a classification scheme that gives each event a safety-relevant label. A shift from nominal operating range to deviation is an error activation (OK → Erroneous), a self-correction back to nominal is error recovery (Erroneous → OK), entry into a degraded-but-safe mode is a fail-safe trip (Erroneous → Safe), and escalation beyond safety thresholds is a dangerous failure (Erroneous → Dangerous). The classifier uses the piecewise model fit before and after each change point to characterize the nature of the transition, with domain knowledge mapping model-change signatures to state transitions. Once classified, these events enable direct estimation of transition probabilities from the event log — error activation rates, containment effectiveness, and reliability growth trends — feeding quantitative evidence into safety cases.

### Step 3: Trace Generator

Temporal window method that takes an event of interest (EoI) and constructs a trace from the events infront (t_1) and the events behind (t_2). distance between t_1 and t_2 must be greater than 0, and t_1 and t_2 cannot be less than 0. Refer to `examples/example_4/case_generator.py`.

### Step 4: Analysis

Performance DFG Analysis: `examples/example_4/example_4_part_2.ipynb`
Markov DFG Analysis: `examples/example_4/example_4_part_2.ipynb`
Variant Analysis: `examples/example_4/example_4_part_2.ipynb`
Social Network Analysis: Reinterpret van der Aalst's SNA metrics in the context of system failure propagation, where subsystems are the performers and failure cases are the process instances. Handover-of-work metrics quantify how one subsystem's failure triggers another's. Subcontracting patterns (A → B → A) reveal feedback loops in failure chains. The working-together metric identifies common-cause failures — subsystems that frequently appear in the same failure cases likely share a vulnerability. Performer-by-activity similarity (via Hamming or Pearson distance on transition profiles) finds subsystems with shared failure patterns even without direct interaction. The result is a weighted, directed sociogram of subsystem relationships during failures that can also validate safety case independence assumptions — strong causal coupling between supposedly independent subsystems indicates a gap in the defence-in-depth argument.