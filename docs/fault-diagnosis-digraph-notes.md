# Fault Diagnosis of Automobile Systems Using Fault Tree Based on Digraph Modeling — James, Gandhi & Deshmukh (2017)

Published in Int J Syst Assur Eng Manag (Springer). Extends the Lapp & Powers (1977) digraph-based fault tree synthesis method from chemical/process systems to automobile systems. Demonstrated on a hydraulic power steering system.

## Problem

Fault diagnosis in automobiles is complex and traditionally relies on:
- **Diagnostic Trouble Codes (DTCs)** — indicate potential root causes but can't pinpoint the exact faulty component
- **Repair manuals** — don't convey failure propagation paths or inter-component relationships
- **Technician experience** — subjective, inconsistent, hard to systematize

Conventional fault tree construction is manual, time-consuming, subjective (different analysts produce different trees), and fails to capture **control loops** and **system structure** explicitly.

## Core idea: structure-aware fault trees via digraphs

The key insight is that a system's **physical structure** — its subsystems, components, parameters, and their interconnections — should be the basis for fault tree construction. A **digraph** (directed graph) captures this structure explicitly:

- **Nodes** = system parameters (pressure, temperature, mass flow rate, etc.) and failure events
- **Directed edges** = causal relationships between parameters, annotated with **gain values**:
  - `0` = no change
  - `±1` = moderate increase/decrease
  - `±10` = large increase/decrease (e.g. component failure)

The digraph encodes both **normal operating conditions** and **failed conditions** for every subsystem/component, based on input-output parameter relationships.

## Methodology

### Step 1: Fault tree diagram development

1. **Decompose the system** into subsystems, assemblies, components. Identify input/output parameters for each.
2. **Model input-output interrelationships** in tabular form — gain values (0, ±1, ±10) for normal and failed conditions. Include sub-failures and lower-level failures down to root causes.
3. **Build component digraphs** from the tables — one digraph per subsystem/assembly/component, capturing both normal and failure behaviour.
4. **Combine into a system digraph** by connecting component digraphs according to the physical system topology.
5. **Identify feedback and feedforward loops** in the system digraph. These are critical because they represent control loops that conventional fault tree methods can't handle.
6. **Identify the top event** — the symptom or undesired event (e.g. "loss of power" in the steering system).
7. **Trace input nodes** to the top event node and connect them via OR gates (if not in a loop) or generalized operators (if in a feedback/feedforward loop).
8. **Check consistency** — mutually exclusive events (e.g. simultaneous increase and decrease of the same parameter) cannot co-occur. Delete inconsistent events.
9. **Repeat** steps 7-8 for each stage of the tree until only primal/basic events remain.

### Step 2: Fault diagnosis using the tree

1. Start with the **top event** (failure symptom).
2. Identify the gate below it:
   - **OR gate**: any input event could be the cause. Check the highest-probability event first.
   - **AND gate**: all input events are contributing. Order of checking matters for efficiency.
3. Traverse the tree top-down, testing each event, until primal (root cause) events are reached.

## Handling control loops

A major advantage over conventional methods. Two types:

### Negative feedback loops
A path that starts and ends at the same node, where the product of normal gains is negative (i.e. the loop acts to correct disturbances). A disturbance can propagate through when:
- The external disturbance is too **large** for the loop to cancel
- The **control loop parameters themselves** cause the disturbance
- **Combined effect** of external disturbance and control loop failure

### Negative feedforward loops
Two or more paths between nodes with opposing gain signs — one causative path (net positive gain) and one corrective path (net negative gain). Fails when:
- The disturbance enters at a node **other than the sensor node**
- Loop devices are **inactive or reversed**

Both loop types get **generalized operators** (special fault tree sub-structures) rather than simple OR/AND gates.

## Hydraulic power steering example

The paper demonstrates the full methodology on a hydraulic power steering system with:
- **Two main subsystems**: hydraulic system (oil tank, vane pump, steering unit, return filter, pressure relief valve) and cooling system (cooler, temperature sensor, controller, coolant valve, coolant pump)
- **Critical parameters**: Pressure (P), Mass flow rate (M), Temperature (T) of hydraulic oil and coolant
- **One negative feedback control loop**: T4-P8-P9-M12-T4 (temperature control loop for hydraulic oil)
- **Top event**: "Loss of power" = P2(−1), i.e. reduced pressure at the steering unit input

The resulting fault tree (Fig. 9) identifies 34 primal events as potential root causes, with "vane pump failure" as the most probable cause based on garage experience.

## Key contributions

- **Analyst-independent**: the digraph produces a unique fault tree from the system structure, eliminating subjectivity
- **Handles control loops**: conventional methods can't capture feedback/feedforward loops; this method handles them via generalized operators
- **Computer-amenable**: the tabular input-output relationships and digraph construction are systematic enough for automation
- **Multi-valued logic**: captures not just "failed/not-failed" but magnitude (±1 vs ±10) and direction of deviations
- **Qualitative focus**: determines all possible combinations of events leading to the top event; quantitative analysis (failure probabilities) is possible but not the focus here

## Relevance to process mining and sensor-based event detection

### Digraphs as causal models for event classification

The system digraph explicitly encodes **which parameters affect which other parameters, and how**. This is directly useful for event classification from sensor telemetry:

- When change-point detection (Guralnik) detects a deviation in parameter P2 (pressure), the digraph tells you which upstream parameters could have caused it (P1, T1, vane pump failure, etc.)
- The **gain values** (±1 vs ±10) provide a severity classification — a gain of ±10 indicates a component failure (mapping to the SHIP model's OK → Erroneous transition), while ±1 indicates a moderate deviation that may self-correct
- The digraph's **directed edges** define the causal propagation paths that social network analysis should recover from the event log

### Fault trees as event log schemas

The fault tree structure defines a **hierarchy of events** from symptoms (top events) down to root causes (primal events). This hierarchy can serve as the **activity taxonomy** for event logs:

- **Top events** = high-level process outcomes (e.g. "loss of power")
- **Intermediate events** = subsystem-level failures (e.g. "vane pump failure", "coolant line choked")
- **Primal events** = root causes (e.g. "belt broken", "bearing failure", "seal failure")

Each level of the fault tree corresponds to a different granularity of event for process mining. The OR/AND gate structure tells you whether events are alternative causes or co-occurring causes.

### Control loops and the self-healing state

The paper's treatment of feedback control loops connects directly to the SHIP safety case model's **Erroneous → OK** (self-healing) transition:

- A negative feedback loop that successfully corrects a disturbance = self-healing (Erroneous → OK)
- A disturbance that overwhelms the control loop = escalation (OK → Erroneous, potentially → Dangerous)
- The generalized operator for feedback loops provides the exact conditions under which self-healing fails — these are the conditions that should trigger safety-relevant events

### Parameter deviations as sensor-detectable events

The input-output tables define what **observable parameter changes** correspond to each failure mode. This provides a direct mapping from sensor telemetry to events:

| Observed parameter change | Digraph interpretation | Safety state transition |
|---|---|---|
| P2 moderate decrease (−1) | Upstream component degradation | OK → Erroneous (developing fault) |
| P2 large decrease (−10) | Component failure (e.g. vane pump) | OK → Erroneous (failure) |
| T4 increase (+1) with M12 decrease (−1) | Cooling system degradation | OK → Erroneous (thermal) |
| P2 returns to nominal after deviation | Control loop correction or maintenance | Erroneous → OK (recovery) |

Wavelet denoising would help distinguish real parameter deviations (±1, ±10) from sensor noise, ensuring change-point detection only fires on genuine fault-related transitions.

### Social network analysis on failure propagation

The system digraph defines the **expected causal structure** of the system. Social network analysis on the event log can validate or extend this:

- **Handover-of-work** metrics should recover the digraph's directed edges — if vane pump failure events are consistently followed by steering unit pressure loss events, this confirms the P1 → P2 causal link
- **Unexpected handover patterns** not present in the digraph may reveal undocumented failure propagation paths
- **Subcontracting patterns** (A → B → A) in the event log would indicate the feedback control loops that the digraph already models
- The digraph's gain values provide **expected severity** for each propagation path — if the observed event magnitude doesn't match the digraph's predicted gain, this may indicate an additional fault or a modeling error

### Automating fault tree construction from event logs

The paper's methodology is currently manual (requires engineering knowledge to build the input-output tables). Process mining could potentially **reverse-engineer** parts of this:

- Frequent pattern mining on event logs could discover which parameter deviations co-occur (AND gates) vs. which are alternatives (OR gates)
- Causal discovery from temporal event sequences could reconstruct the digraph's directed edges
- This would complement the engineering-driven approach with data-driven validation, or extend it to systems where the full structure isn't known
