# Prompt

Your project proposal should be around 3-5 double-spaced pages in length that should include the following:

- A proper title (not just project for CS 8317)
- A proper abstract written as an executive summary clearly identifying the problem that you are going to address with some basic background information, the solution strategy you intend to use:
  - Which implementation approach is being taken
  - Which analysis/modeling technique to be used?
- A rough schedule
- For application-type projects, in addition to the above, you also need to discuss:
  - Data collection
  - Data analysis of result to be performed
- Follow up actions

Length Target
- Abstract: 0.5 pages
- Background: 0.75 pages
- Implementation: 1.5 pages
- Data Collection/Analysis: 1 page
- Visualization: 0.5 pages
- Schedule/Milestones: 0.5 pages
- Challenges: 0.25 pages = ~5 pages total

# Event-Driven Process Mining for Failure Cascade Detection in Vehicle Telemetry Systems

## Abstract

### Claude notes
Background (1-2 sentences):
- Current state: Manual investigation of telemetry anomalies
- Problem: Time-consuming, error-prone, difficult to identify failure cascades

Proposed Solution (2-3 sentences):
- Extract discrete events from continuous telemetry using threshold detection and signal processing
- Construct temporal traces using time-windowed case generation around critical events
- Apply process mining (PM4PY) to generate Directly-Follows Graphs (DFG) showing event relationships and timing

Expected Outcomes (1-2 sentences):
- Automated visualization of failure cascades (Fault Tree Analysis)
- Identification of nominal vs. anomalous event sequences (variant analysis)
- Quantifiable performance metrics (cycle time, event frequencies)
Dataset (1 sentence):
- Validation using 2016 FSAE endurance race telemetry (190k+ sensor samples, 22 laps, 32+ minutes)

### My notes

Explain how the traditional method to analyze telemetry data is by observing anomalies in the data, and then investigating the system state before and after the anomaly. Reconstructing the state of the system leading to a failure is manual and time consuming. We introduce a methdology to extract discrete events from telemetry data and reconstruct event traces using a time-window approach. We then perform a process mining operation on the discrete events to reconstruct a markov chain and timing graph of the events.

This methodology can be used to generate graphs for:
- Fault Tree Analysis to identify how failures cascade across a system (ex: from a minor fault to system failure)
- Event Tree Analysis to identify which events are related to each other for system debugging or analysis
- variant analysis to identify the nominal path of events, and the non-nominal or defect paths.

## Background Information

### Claude Notes
Why this matters:
- Motorsport teams analyze gigabytes of telemetry per session
- Current tools (MoTeC, AIM) focus on individual sensor visualization
- Failure diagnosis requires expert knowledge to correlate multiple sensors
- Process mining has proven effective in business processes but underutilized in time-series domains

Related Work:
- Process mining in manufacturing (predictive maintenance)
- Anomaly detection in telemetry (traditional ML approaches)
- Gap: No established methodology for extracting process models from continuous sensor data

## Implementation Approach

### Claude Notes
Current section is too brief. Add: Event Extraction Algorithms:
- Threshold-based detection (e.g., brake pressure > 50 psi = "Brake Applied")
- State change detection (e.g., gear shifts)
- Combined condition events (e.g., hard braking = high brake pressure AND high deceleration)
- Local extrema detection using scipy.signal.find_peaks (e.g., corner apex = max lateral g)

Time-Window Trace Construction:
- Trigger event selection (e.g., "Full Throttle", "Bumpstop Hit")
- Configurable window parameters (time_before, time_after)
- Handling overlapping windows (events copied to multiple cases)
- Case ID assignment and temporal ordering

Process Mining Techniques:
- Performance DFG: Shows average time between events
- Markov Chain DFG: Shows frequency/probability of transitions
- Variant Analysis: Identifies unique event sequences
- Statistical metrics: Cycle time, lead time, flow rate

### My Notes

- The dataset being used is the telemetry log of a [2016 FSAE endurance vehicle](https://huggingface.co/datasets/nominal-io/UCONN_FSAE_2016_Endurance). Note, if a different log should be used, there are [more options](https://huggingface.co/datasets?search=telemetry) on hugging face.
- Need to write code to extract events (and document which algorithms are being used). Potential use of algorithms for classification of events from the telemetry data.
- Need to write code to construct time-window traces
- Need to create a plotting function to display variants

## Data Collection and Analysis

### Claude Notes
Data Collection:
- Source: UCONN FSAE 2016 Endurance dataset on HuggingFace
- Format: AiM CSV telemetry (190,587 rows)
- Sampling rate: 100 Hz
- Channels: 75+ (suspension, acceleration, engine, GPS, etc.)
- Duration: ~32 minutes (1905 seconds), 22 laps

Data Preprocessing:
- Parse AiM metadata (venue, vehicle, timestamps)
- Type conversion and validation using Pandera
- Lap detection via time resets
- Absolute timestamp calculation
- Missing data handling

Event Extraction Validation:
- Expected: 8000+ discrete events from continuous data
- Event categories: Lap transitions, gear shifts, braking, cornering, suspension, engine
- Quality metrics: Event frequency distribution, temporal consistency

Analysis Metrics:
- Number of unique process variants
- Most common event sequences (top 10)
- Timing relationships between critical events
- Anomaly identification (deviations from nominal paths)

## Visualization Strategy (Expand)

### Claude Notes
Output Artifacts:
- Performance DFG - Network graph with timing annotations
- Markov DFG - Network graph with frequency annotations
- Chevron Workflow Diagrams - Color-coded event sequences for top variants
- Statistical Dashboards - Event distribution, case summaries

## Expected Contributions

### Claude Notes
Methodological:
- Reusable framework for extracting discrete events from continuous sensor data
- Time-window case generation approach applicable to any telemetry source
- Integration of signal processing with process mining

Practical:
- Automated fault cascade visualization
- Driver behavior pattern identification
- Performance optimization insights for FSAE teams

Technical:
- Open-source Python implementation (EventExtractor, CaseGenerator classes)
- Extensible to other domains: aircraft telemetry, industrial IoT, medical monitoring

## Follow-up Actions

## Claude Notes
Immediate (Week 1-2):
- Literature review: Process mining in time-series contexts
- Implement and validate EventExtractor class
- Document threshold selection methodology

Mid-term (Week 3-5):
- Implement CaseGenerator with time-window logic
- Generate preliminary DFGs for multiple trigger events
- Perform variant analysis and identify patterns

Final (Week 6-7):
- Create chevron visualization functions
- Statistical validation of discovered patterns
- Document findings and prepare presentation

Future Extensions:
- Real-time event detection for live telemetry
- Machine learning for automatic threshold tuning
- Comparative analysis across multiple race sessions
- Integration with existing motorsport tools

## Schedule

Consider combining with follow up actions.

- Start on 1/23/26
- (Hard Deliverable) Literature Research due 1/30/26
- (Hard Deliverable) Project Progress and Preliminary Analysis due 2/20/26
- (Hard Deliverable) Project Presentation due 3/5/26
- (Hard Deliverable) Project Report due 3/6/26

## Challenges & Risk Mitigation

### Claude Notes
Potential Challenges:
- Threshold selection - Risk of spurious events or missing events
    - Mitigation: Sensitivity analysis, expert validation
- Time-window sizing - Windows too small miss context, too large create noise
    - Mitigation: Multiple window sizes, comparative analysis
- Scalability - Large telemetry files may cause memory issues
    - Mitigation: Chunked processing, sampling strategies
- Interpretability - DFGs may be too complex with many event types
    - Mitigation: Event filtering, hierarchical abstraction