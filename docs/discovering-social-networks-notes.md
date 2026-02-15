# Discovering social networks from logs

Each metric assigns a weight W_{i,j} to the relationship between individuals i and j. If W_{i,j} exceeds a threshold τ, the pair is included in the sociogram. The result is a weighted graph (P, R, W) usable by SNA tools.

## Metrics based on (possible) causality

These metrics monitor how work moves among performers within individual cases. Two core metrics, each with 8 variants (16 total) derived from three refinement axes.

### Handover of Work

- **Handover of Work**: there is a handover of work from individual i to individual j if there are two subsequent activities where the first is completed by i and the second by j.
- **Calculation**: count of such successions from i to j, divided by the maximum number of possible successions in the log. This gives a relative weight between 0 and 1.

### Subcontracting

- **Subcontracting**: count the number of times individual j executed an activity in-between two activities executed by individual i (i → j → i pattern). This may indicate that work was subcontracted from i to j.
- **Calculation**: count of such in-between occurrences, divided by the maximum possible in-between occurrences in the log.

### Three refinement axes (apply to both metrics, yielding 8 variants each)

1. **Direct vs. indirect succession**: Direct (n=1) means the very next activity. Indirect (n>1) allows activities in-between, weighted by a "causality fall factor" β (0 < β < 1). Each additional step of distance is discounted by β^(n-1), so more distant transfers contribute less.
2. **Multiple transfers per case**: Either count every transfer within a case, or ignore duplicates (count at most once per case instance).
3. **Causal dependency**: Either count all arbitrary successions, or only those where a real causal dependency exists between the activities (derived from the process model, e.g. via the α-algorithm).

A "calculation depth factor" k bounds how far apart in a case to search, for computational efficiency.

## Metrics based on joint cases

- **Working together metric**: count how frequently two individuals are performing activities for the same case.
- **Calculation**: for performers p1 and p2, weight = (number of joint cases) / (number of cases p1 appeared in). This is **asymmetric** — p1's value toward p2 can differ from p2's toward p1, since they may participate in different total numbers of cases.

## Metrics based on joint activities

- Focus on what activities performers do, not whether they work on the same cases. The assumption is that people doing similar things have stronger relations than people doing completely different things.
- **Performer-by-activity matrix**: rows = performers, columns = activities, cells = frequency counts. Compare performers by measuring the distance between their row vectors.
- Three distance measures:
  - **Minkowski distance**: generalized distance with parameter n. n=1 is Manhattan distance, n=2 is Euclidean. Sensitive to volume differences between performers.
  - **Hamming distance**: binary comparison — only checks whether both performers have done an activity (ignores frequency). More robust to volume differences (e.g. full-time vs. part-time workers).
  - **Pearson's correlation coefficient**: measures linear correlation between activity profiles. Ranges from -1 to +1; similar profiles yield values near +1.
- A log-scale transform on the activity matrix can help when work volumes vary significantly.

## Metrics based on special event types

- The previous metrics assume events correspond to activity completions. But logs can also contain event types like: *schedule, assign, withdraw, reassign, start, suspend, resume, abort, complete, autoskip, manualskip*.
- **Reassignment metric**: count the number of times individual i reassigns work to individual j, divided by the maximum possible reassignments in the log. A variant ignores multiple reassignments within one case.
- If i frequently delegates work to j but not vice versa, it is likely that i is in a hierarchical relation with j. From an SNA point of view these observations are particularly interesting since they represent explicit power relations.

## Implications for event generation

To enable effective social network analysis, the system producing events must capture the right data. Each metric type places different demands on what an event contains.

### Minimum required fields per event

Every event must include at minimum:
1. **Case identifier** — which process instance this event belongs to (e.g. order ID, ticket number). Without this, no metric can be computed.
2. **Activity identifier** — which step in the process was performed (e.g. "review application", "approve claim"). Required by all metrics.
3. **Performer/originator** — who executed or initiated the activity. This is the basis for every social network link.
4. **Timestamp** — needed to establish ordering of events within a case. Without ordering, causality-based metrics (handover, subcontracting) cannot be computed.

### Additional fields that unlock specific metrics

- **Event type** (e.g. complete, reassign, start, suspend) — required for reassignment metrics and special event type analysis. If all events are logged as a single undifferentiated type, hierarchical/delegation patterns become invisible.
- **Causal dependency information** — either embedded in the log or derivable from a known process model. Enables the causal dependency refinement axis for handover and subcontracting metrics, filtering out coincidental successions from causally related ones.

### Event design considerations

- **Log completions, not just starts**: Causality metrics depend on knowing when work actually transfers. A "complete" event for one activity followed by a "start" event for the next gives the clearest handover signal.
- **Log reassignments explicitly**: If work is delegated or reassigned, emit a dedicated reassign event rather than silently changing the performer. Without this, hierarchical power relations cannot be detected.
- **Use consistent performer identifiers**: All metrics depend on reliably identifying individuals. Inconsistent naming (e.g. "J. Smith" vs "John Smith") will fragment the social network.
- **Use consistent activity identifiers**: Joint activity metrics build a performer-by-activity matrix. If the same activity has multiple names, the profiles become unreliable.
- **Ensure sufficient case volume**: The paper notes that logs may be incomplete — a person may not execute certain activities during the collection period by coincidence. More cases yield more reliable social networks.
- **Capture enough event types to distinguish phases**: Logging only "complete" events is sufficient for causality and joint case/activity metrics, but richer event types (assign, reassign, suspend, resume) reveal organizational dynamics that completion events alone cannot.
