# Example 5: SHIP-Classified Process Mining on FSAE Telemetry

## What this example does

Applies process mining to FSAE vehicle telemetry to discover failure propagation patterns.
Raw telemetry is classified into discrete SHIP safety-state events, organized into time-windowed
cases, and analyzed via Directly-Follows Graphs (DFGs) using PM4Py.

**Pipeline:**
```
Raw Telemetry → SHIP Dispatcher → CaseGenerator → DFG / Variant Analysis
```

**Results (endurance dataset, 190,587 rows × 76 channels, ~31 min):**
- 801 SHIP events detected across 6 subsystems
- 404 cases generated (10,727 event-case assignments, avg 26.6 events/case)
- 218 unique variants, 95 DFG edges

## Files

| File | Purpose |
|---|---|
| `example_5.ipynb` | Main pipeline notebook — run top to bottom |
| `ship_config.py` | `SHIP_EVENTS` list: 16 config entries across 6 subsystems |
| `ship_dispatcher.py` | `dispatch_ship_events()` — iterates config, calls EventClassifier, tags output |
| `event_classifier.py` | Stateless detection methods (reused/renamed from example_4) |
| `wavelet_denoiser.py` | `WaveletDenoiser` — stretch goal, not wired into base pipeline |

**Reused from example_4:**
- `../example_4/case_generator.py` — `CaseGenerator` (unchanged)
- `../example_4/variant_visualization.py` — `visualize_chevron_variants`
- `../example_4/data/processed/FSAE_Endurance_Full_parsed.csv` — parsed telemetry input

**Generated outputs** (in `data/processed/`):
- `ship_events_timeline.png`, `ship_events_per_case.png`
- `ship_dfg.png`, `ship_dfg_performance.png`, `ship_dfg_activations.png`
- `ship_variants.png`

## Config shapes in SHIP_EVENTS

**State-change pattern** — one config entry, two SHIP transitions (activation + recovery):
```python
{
    "subsystem": "Engine",
    "method": "detect_state_change_events",
    "derived_column": ("f88.ect1_°f", ">", 160),   # dispatcher computes boolean
    "args": {"event_name_prefix": "engine_overheating"},
}
# Dispatcher builds: "engine_overheating False->True" → error_activation
#                    "engine_overheating True->False" → error_recovery
```

**Simple pattern** — one config entry, one SHIP transition:
```python
{
    "subsystem": "Brakes",
    "transition_type": "error_activation",
    "method": "detect_combined_condition_events",
    "args": {"conditions": [...], "event_name": "wheel_lockup_fl"},
}
```

## Key design decisions

- **Thresholds are data-calibrated**, not from specs. Design-spec values (220 °F coolant,
  11.5 V battery, 4-sat GPS) never fire against this dataset. See `overview.md` → Data Notes.
- **Missing columns are skipped** with `warnings.warn()` rather than raising. A partial config
  run is valid.
- **Lubrication dominates** (68% of events, 548/801). Consider subsystem filtering before
  variant analysis to avoid drowning rarer interactions.
- **`value` dtype is heterogeneous** (bool/float/NaN across detector methods) — a pandas
  FutureWarning on `pd.concat` is a known issue documented in the dispatcher.
- **`roll angle_unit` is always 0** in this dataset — its config entry is retained but
  produces no events.
- **`org:resource`** is set to `subsystem` in the PM4Py prep step, enabling SNA stretch goal
  without further changes.

## Known issue: pm4py.get_variants() return type

`pm4py.get_variants()` returns `dict[tuple[str], int]` (count, not a set) in some PM4Py
versions. The variant-sorting cell in the notebook uses `len(cases_set)` which breaks when
the value is an int. Workaround: use the count directly or sort with `lambda x: -x[1]`.

## Subsystem event counts (base pipeline)

| Subsystem | error_activation | error_recovery | Total |
|---|---|---|---|
| Suspension | 72 | 72 | 144 |
| Brakes | 3 | 0 | 3 |
| Engine | 45 | 44 | 89 |
| Lubrication | 274 | 274 | 548 |
| Electrical | 7 | 7 | 14 |
| Drivetrain | 3 | 0 | 3 |
| **Total** | **404** | **397** | **801** |

## Dependencies

```
pandas, pm4py, matplotlib, IPython
```

Stretch goal only: `pip install PyWavelets` (not required for base pipeline).

## Work remaining

- Subsystem-filtered DFG and oil-pressure threshold sensitivity analysis
- Window-size sensitivity analysis (currently 10 s pre / 30 s post)
- SNA sociogram (`org:resource` already populated — PM4Py SNA functions can be called directly)
- Fix `get_variants()` sort to handle int counts
