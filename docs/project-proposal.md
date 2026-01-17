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

# Event Driven Analysis of Telemetry Data using Process Mining

## Abstract

Explain how the traditional method to analyze telemetry data is by observing anomalies in the data, and then investigating the system state before and after the anomaly. Reconstructing the state of the system leading to a failure is manual and time consuming. We introduce a methdology to extract discrete events from telemetry data and reconstruct event traces using a time-window approach. We then perform a process mining operation on the discrete events to reconstruct a markov chain and timing graph of the events.

This methodology can be used to generate graphs for:
- Fault Tree Analysis to identify how failures cascade across a system (ex: from a minor fault to system failure)
- Event Tree Analysis to identify which events are related to each other for system debugging or analysis
- variant analysis to identify the nominal path of events, and the non-nominal or defect paths.

## Schedule

- Start on 1/23/26
- (Hard Deliverable) Literature Research due 1/30/26
- (Hard Deliverable) Project Progress and Preliminary Analysis due 2/20/26
- (Hard Deliverable) Project Presentation due 3/5/26
- (Hard Deliverable) Project Report due 3/6/26

## Implementation Details

- The dataset being used is the telemetry log of a [2016 FSAE endurance vehicle](https://huggingface.co/datasets/nominal-io/UCONN_FSAE_2016_Endurance). Note, if a different log should be used, there are [more options](https://huggingface.co/datasets?search=telemetry) on hugging face.
- Need to write code to extract events (and document which algorithms are being used)
- Need to write code to construct time-window traces
- Need to create a plotting function to display variants