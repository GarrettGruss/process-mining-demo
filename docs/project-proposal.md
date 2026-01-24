# Event-Driven Process Mining for Failure Cascade Detection in Vehicle Telemetry Systems

## Abstract

Modern motorsports teams generate gigabytes of telemetry data per race, yet analysis of this data is still predominantly a manual operation. Engineers groom and manipulate the data by hand to identify anomalies within the stream of sensor data, manually classifying discrete system failures and reconstructing the sequence of events leading to system failure or events of interest. This process is time-consuming, fault-prone, and lacks scalability.

In this project, we propose the application of process mining techniques from the business intelligence world for discovery and analysis of discrete system events and states on vehicle telemetry data. We present a methdology of event classification using threshold and signal process algorithms. These events are organized into temporal traces using a time-window approach centered on an event of interest. To construct the event graphs, we utilize the PM4PY library to construct Directly-Follows Graphs (DFGs) that visualize event relationships, transition probabilities, and timing characteristics.

## Background Information

### The Challenge of Telemetry Analysis

Motorsports teams generate gigabytes of telemetry data per session using data acquisition systems such as AiM and MoTeC. These systems capture dozens to hundreds of sensor channels at high frequencies, producing rich datasets that document multiple aspects of vehicle behavior. However, current analysis tools focus primarily on individual sensor visualization—engineers examine time-series plots, overlay channels, and manually search for correlations between sensor readings and vehicle behavior.

Diagnosing failures in this environment requires expert knowledge to correlate multiple sensors and reconstruct the sequence of events leading to an issue. When a failure occurs, engineers must manually trace backward through the data, identifying which events preceded the failure and hypothesizing causal relationships. This approach becomes increasingly difficult when failures involve cascading effects across multiple subsystems, where a minor fault in one component triggers a chain reaction affecting others.

### Process Mining: A Solution from Business Intelligence

Process mining is a family of techniques developed by a Dutch computer scientist by the name of Wil van der Aalst for the analysis of business and manufacturing workflows. While this methodology has proven useful in the business domain, it remains underutilized in time-series telemetry data due to the requirement of discrete events. This project address that gap by introducing a methodology to transform continuous telemetry data into discrete system events suitable for process mining and analysis.

### Target Use Cases

This methodology targets several valuable analysis patterns:

1. **Fault Tree Analysis**: Identify how failures cascade across a system by observing how minor events escalate into major failures. Process mining reveals the statistical patterns of failure propagation across many instances.

2. **Event Tree Analysis**: Discover which system events are related to each other, enabling engineers to understand the forward consequences of specific conditions or actions.

3. **Variant Analysis**: Identify the nominal sequence of events during normal operation and contrast it with non-nominal or defect paths, highlighting where behavior diverges from expectations.

## Implementation Approach

### Event Classification

In the event classification stage, continuous sensor telemetry is classified into discrete events using an `EventExtractor` class. The extractor supports threshold-based detection to detect when a sensor value crosses a defined limit (ex: brake pressure > 50 PSI creates a "brake applied" event), combined condition detection (ex: high brake pressure and high deceleration creates a "hard braking" event), and local extrema detection using `scipy` to identify peaks and valleys in sensor data (ex: maximum lateral g-force creates a "corner apex" event). Each algorithm is configurable and includes debounding to prevent event creation from sensor noise. The output is a structured list of events and their timestamp.

### Time-Window Trace Construction

The process mining algorithms requires events to be organized by a trace id representing each workflow occurance. The `CaseGenerator` class implements a temporal trace to draw a time-window around an event of interest (ex: "bumpstop hit" or "full throttle" event),  constructing a local trace. When events occur in rapid succession and the windows overlap, events are copied to maintain a complete trace. The output of this stage is a list of event traces ready for process discovery and analysis.

### Process Mining Analysis

Once the event trace log is constructed, event discovery can be performing using the PM4PY library. Directly-Follows Graphs (DFG) are generated, showing the order of events, the average timing between events, and the transition counts between states. Variant analysis can also be performed to identify all unique event sequences across cases, ranking them by frequency to identify nominal system behavior and alternative paths. Standard process mining metrics such as cycle time, lead time, and event frequencies can also be generated to provide quantitative characterization of the discovered patterns.

## Data Collection and Analysis

### Dataset

This project uses the UCONN FSAE 2016 Endurance dataset, publicly available on HuggingFace. The dataset contains telemetry from a Formula SAE racecar during an endurance event, recorded by an AiM data acquisition system. The data comprises 190,587 rows sampled at 100 Hz, spanning approximately 32 minutes (1905 seconds) across 22 laps. Over 75 sensor channels capture suspension travel, acceleration (longitudinal, lateral, vertical), engine parameters (RPM, throttle position, temperatures), brake pressure, steering angle, GPS coordinates, and wheel speeds.

### Event Extraction Validation

From the continuous telemetry, we expect to extract 8,000+ discrete events across multiple categories: lap transitions (start/finish line crossings), gear shifts (approximately 20-30 per lap), braking events (brake application and release), cornering events (apex detection via lateral acceleration peaks), suspension events (bumpstop contacts, full droop), and engine events (redline hits, throttle cut). Validation involves verifying that event frequencies match expected ranges based on track characteristics and confirming temporal consistency—events should not occur faster than physically possible.

### Analysis Metrics

The process mining analysis will produce several quantitative outputs: the total number of unique process variants discovered, the frequency distribution of the top 10 most common event sequences, timing statistics for transitions between critical events (e.g., mean time from brake application to corner apex), and identification of anomalous variants that deviate significantly from nominal patterns. These metrics enable both aggregate characterization of driving behavior and identification of specific instances warranting detailed investigation.

## Visualization Strategy

The project produces several visualization artifacts to communicate discovered patterns. Directly-Follows Graphs are rendered as network diagrams where nodes represent event types and directed edges show observed transitions. The Performance DFG annotates edges with average inter-event timing, while the Frequency DFG displays transition counts or probabilities. Node sizing reflects event frequency, and edge thickness indicates transition strength. These graphs are generated using PM4PY's built-in visualization and exported as PNG or SVG.

Chevron Workflow Diagrams provide a linear representation of process variants. Each variant is displayed as a sequence of colored boxes (chevrons) representing events in order. The top variants are shown side-by-side, enabling visual comparison of common paths versus deviations. Color coding groups related event types (e.g., all braking events in red, all cornering events in blue) for rapid pattern recognition.

Statistical Dashboards summarize the event log characteristics: histograms of event type frequencies, box plots of case durations, and tables of variant statistics. These provide the quantitative context needed to interpret the process models and provide a high level overview of the analysis findings.

## Schedule and Milestones

The project spans seven weeks with the following deliverables and milestones:

**Phase 1: Foundation (Week 1-2, 1/23 - 2/5)**
- Complete literature review on process mining in time-series contexts
- Implement and validate the `EventExtractor` class with threshold-based detection
- Document threshold selection methodology and validate against known events
- **Deliverable: Literature Research (due 1/30/26)**

**Phase 2: Core Implementation (Week 3-5, 2/6 - 2/26)**
- Implement `CaseGenerator` with time-window trace construction
- Generate preliminary DFGs for multiple trigger event types
- Perform initial variant analysis and identify patterns in the FSAE dataset
- Iterate on event definitions based on discovered patterns
- **Deliverable: Project Progress and Preliminary Analysis (due 2/20/26)**

**Phase 3: Analysis and Documentation (Week 6-7, 2/27 - 3/6)**
- Create chevron visualization functions for variant display
- Conduct statistical validation of discovered patterns
- Prepare presentation materials and final report
- **Deliverable: Project Presentation (due 3/5/26)**
- **Deliverable: Project Report (due 3/6/26)**

**Future Extensions** (beyond project scope): Real-time event detection for live telemetry, machine learning for automatic threshold tuning, comparative analysis across multiple race sessions, and integration with existing motorsport analysis tools.

## Challenges & Risk Mitigation

Threshold selection risks generating spurious events from noise or missing genuine events from overly conservative limits. We mitigate this through sensitivity analysis across threshold ranges and validation against manually-identified events by domain experts.

Time-window sizing presents a tradeoff: windows too small miss relevant context, while windows too large introduce noise and blur causal relationships. We address this by testing multiple window sizes and comparing the resulting process models for stability and interpretability.

Interpretability challenges emerge when many event types create overly complex DFGs that are difficult to analyze. We mitigate this through event filtering to focus on relevant subsets, hierarchical abstraction grouping related events, and threshold-based edge filtering to show only significant transitions.