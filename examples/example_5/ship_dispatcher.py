"""SHIP Dispatcher: routes telemetry through SHIP_EVENTS config and produces a tagged event log.

Usage:
    from examples.example_5.ship_config import SHIP_EVENTS
    from examples.example_5.ship_dispatcher import dispatch_ship_events

    event_log = dispatch_ship_events(df, SHIP_EVENTS)

Output DataFrame columns: timestamp, activity, subsystem, transition_type, value.
"""

import warnings
import operator as _op

import pandas as pd

from examples.example_5.event_classifier import EventClassifier


def dispatch_ship_events(
    df: pd.DataFrame,
    config: list[dict],
    wd=None,  # WaveletDenoiser | None
) -> pd.DataFrame:
    """Iterate over SHIP_EVENTS, call the appropriate detector, and tag results.

    Two config shapes are handled:

    State-change pattern (entry has "derived_column"):
        The dispatcher computes a boolean Series from the derived_column spec, injects it
        as a temporary column on a per-entry copy of the DataFrame, constructs a fresh
        EventClassifier, and calls detect_state_change_events.  Transition types are built
        programmatically from event_name_prefix:
            "{prefix} False->True" → error_activation
            "{prefix} True->False" → error_recovery

    Simple pattern (entry has "transition_type"):
        The dispatcher calls the configured method on the shared EventClassifier (or on
        a WaveletDenoiser instance when the method belongs to that class) and tags all
        resulting events with the given transition_type.

    Missing columns cause that entry to be skipped with a warning rather than crashing
    the entire pipeline.

    Args:
        df:     Raw (or denoised) telemetry DataFrame.
        config: List of event definition dicts (see ship_config.py).
        wd:     Optional WaveletDenoiser instance.  When provided, entries whose method
                name exists on the denoiser are routed to it instead of EventClassifier.

    Returns:
        DataFrame with columns: timestamp, activity, subsystem, transition_type, value,
        sorted ascending by timestamp.
    """
    _OPS = {
        ">": _op.gt,
        "<": _op.lt,
        ">=": _op.ge,
        "<=": _op.le,
        "==": _op.eq,
    }

    ec = EventClassifier(df)
    frames: list[pd.DataFrame] = []

    for entry in config:
        subsystem = entry["subsystem"]

        try:
            if "derived_column" in entry:
                col, op, val = entry["derived_column"]

                if col not in df.columns:
                    warnings.warn(
                        f"[SHIP Dispatcher] Column '{col}' not found in DataFrame — "
                        f"skipping entry '{entry['args'].get('event_name_prefix', '?')}'."
                    )
                    continue

                # Compute boolean series without mutating the shared DataFrame
                derived: pd.Series = _OPS[op](df[col], val)
                entry_df = df.copy(deep=False)
                prefix = entry["args"]["event_name_prefix"]
                temp_col = f"_derived_{prefix}"
                entry_df[temp_col] = derived

                entry_ec = EventClassifier(entry_df)
                args = {**entry["args"], "column": temp_col}
                events = getattr(entry_ec, entry["method"])(**args)

                # Map state-change labels → SHIP transition types
                tmap = {
                    f"{prefix} False->True": "error_activation",
                    f"{prefix} True->False": "error_recovery",
                }
                events["transition_type"] = events["activity"].map(tmap)
                events = events.dropna(subset=["transition_type"])

            else:
                # Simple pattern — validate columns before calling
                args = entry["args"]
                if "conditions" in args:
                    missing = [c for c, _, _ in args["conditions"] if c not in df.columns]
                    if missing:
                        warnings.warn(
                            f"[SHIP Dispatcher] Columns {missing} not found — "
                            f"skipping entry '{args.get('event_name', '?')}'."
                        )
                        continue
                elif "column" in args and args["column"] not in df.columns:
                    warnings.warn(
                        f"[SHIP Dispatcher] Column '{args['column']}' not found — "
                        f"skipping entry '{args.get('event_name', '?')}'."
                    )
                    continue

                target = wd if (wd is not None and hasattr(wd, entry["method"])) else ec
                events = getattr(target, entry["method"])(**args)
                events["transition_type"] = entry["transition_type"]

            events["subsystem"] = subsystem
            # KNOWN ISSUE: EventClassifier methods return heterogeneous value dtypes.
            # detect_state_change_events on a boolean-derived column produces bool values;
            # detect_threshold_events produces floats; detect_combined_condition_events
            # produces float("nan"). pd.concat below raises a FutureWarning because
            # mixing bool/object/float in the value column causes ambiguous dtype inference.
            # Current behavior is correct (pandas coerces to object), but a future pandas
            # release may change how all-NA or mixed-type columns are handled.
            #
            # FUTURE FIX: add a _validate_event_frame() helper (or a pandera schema) that
            # validates required columns (timestamp, activity, value) and casts value to
            # float64 via pd.to_numeric(..., errors="coerce") before appending. This would
            # eliminate the warning and ensure a stable numeric dtype for downstream analysis.
            frames.append(events)

        except Exception as exc:  # noqa: BLE001
            warnings.warn(
                f"[SHIP Dispatcher] Error processing entry for subsystem '{subsystem}' "
                f"({entry.get('args', {})}): {exc}"
            )

    if not frames:
        return pd.DataFrame(
            columns=["timestamp", "activity", "subsystem", "transition_type", "value"]
        )

    return (
        pd.concat(frames, ignore_index=True)
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
