## change point detection

Classic time-series problem where an abrupt change in a signal is logged as an event. Problem is detecting this change. See [Ruptures](https://pypi.org/project/ruptures/), a python library that implements some algorithms.

### "A priori" in change-point detection

In this context, "a priori" is used in the statistical sense — meaning "determined in advance, before looking at the data." Standard change-point detection approaches require two things to be fixed a priori:

1. **The number of change points** — you must decide beforehand how many events/transitions exist in the time series.
2. **The model to fit** between successive change points — typically assumed to be a known, stationary (usually linear) model.

Given these assumptions, the problem reduces to finding the best placement of a predetermined number of change points that minimizes the fitting error.

Guralnik & Srivastava (1999) remove both assumptions: the number of change points is discovered automatically via maximum likelihood with a stopping criterion, and the model for each segment is selected independently using basis functions and cross-validation.

## Guralnik & Srivastava (1999) — Event Detection from Time Series Data

### Problem

Sensor data produces continuous time series. Most pattern mining assumes you already have a discrete event sequence. This paper addresses the gap: how to automatically convert raw time series into events by detecting where the underlying behavior changes significantly.

### Core idea

Model the time series as a **piecewise function** — different segments each described by their own fitted model. A "change point" is a boundary between two segments where the model changes. Each change point becomes a discrete event.

### Model selection

For each segment, the algorithm selects the best-fitting model from a set of basis functions (e.g. polynomials: 1, t, t², t³). Model quality is evaluated using **leave-one-out cross-validation** to estimate expected risk, avoiding assumptions about the data distribution. Different segments can have different model types.

### Batch algorithm

For use when the full dataset is available before analysis begins.

- **Intuition**: repeatedly find the single best place to split a segment in two, until splitting no longer helps.
- **Procedure**: Start with the entire time series as one segment. Find the split point that minimizes the combined likelihood criteria of the two resulting segments. Recursively split each sub-segment the same way.
- **Stopping criterion**: stop when the relative improvement in likelihood between iteration k and k+1 falls below a stability threshold *s*. This prevents detecting spurious change points from noise. Setting s=0% means "stop only when likelihood starts getting worse"; higher values (e.g. 5%) are more conservative.
- **Strength**: global optimization over the full dataset, so it's robust to noise.

### Incremental algorithm

For use when data arrives in real-time and change points must be detected as they happen.

- **Intuition**: as each new data point arrives, check whether the data seen so far is better explained by one segment or two.
- **Procedure**: accumulate data points since the last detected change. For each new point, find the best candidate split and compare its likelihood to the no-split likelihood. If the relative improvement exceeds a threshold δ, report a change point and reset.
- **Strength**: works in real-time / streaming settings.
- **Weakness**: only local optimization (no future data), so it's less noise-tolerant than batch. At low signal-to-noise ratios it produces false positives and has higher detection latency.

### Experimental results

- **Synthetic data** (saw-tooth function with Gaussian noise): batch works well at signal-to-noise ratio h ≥ 8. Incremental works well at h ≥ 30.
- **Real traffic data** (highway loop detectors, 288 samples over 24 hours): compared against 4 human subjects doing visual inspection. The algorithm's segmentation had **better likelihood scores than all human subjects**, and the humans disagreed significantly with each other.
- Key finding: humans tend to segment smooth curves into piecewise straight lines — the algorithm avoids this bias.

## Bridging to process mining: from time series to event logs

Change-point detection is the **event generation** step that feeds into process mining. The connection works as follows:

### Generating events from sensor data

1. **Run change-point detection** on each sensor's time series. Each detected change point becomes a candidate event with a timestamp.
2. **Label events** based on the transition detected. The model fitted before and after the change point characterizes the nature of the change (e.g. "traffic went from increasing-linear to decreasing-quadratic" → "congestion peak"). Domain knowledge maps model transitions to meaningful activity names.
3. **Associate events with cases**. A case identifier ties events to a process instance (e.g. sensor location, machine ID, patient ID). All events from sensors monitoring the same entity/process instance share a case ID.
4. **Assign performers/originators** if applicable (e.g. which sensor, which subsystem, which operator was responsible).

### The resulting event log

Each row contains: **(case ID, activity, performer, timestamp)** — exactly the format that process mining and social network analysis expect. From here you can apply handover-of-work metrics, discover process models, build sociograms, etc.

### Why this matters

Without reliable event detection, the entire process mining pipeline is built on assumptions about when events occur. If events are generated from simple thresholds on poorly-understood phenomena, the resulting process models and social networks will be unreliable. Change-point detection provides a principled, data-driven alternative to manual threshold setting.

