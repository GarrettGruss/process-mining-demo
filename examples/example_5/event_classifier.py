"""EventClassifier: stateless detection methods for extracting discrete events from telemetry.

Ported from example_4/event_extractor.py (EventExtractor → EventClassifier). The
detect_change_points() method (ruptures-based) is removed — structural change detection
is handled by WaveletDenoiser (stretch goal). All other methods are preserved with their
original APIs.

Key difference from EventExtractor: detect_state_change_events handles boolean columns
correctly, emitting "{prefix} False->True" / "{prefix} True->False" activity labels
so the SHIP dispatcher can map them to error_activation / error_recovery automatically.
"""

import pandas as pd
from typing import List, Tuple


class EventClassifier:
    """Stateless event detection methods that operate on a telemetry DataFrame.

    Each method returns a DataFrame with columns: timestamp, activity, value.
    Methods have no knowledge of SHIP or subsystems — tagging is done by the dispatcher.
    """

    def __init__(self, df: pd.DataFrame):
        """Initialize with a telemetry DataFrame.

        Args:
            df: Telemetry DataFrame with all sensor channels and a 'time.absolute' column.
        """
        self.df = df

    def detect_threshold_events(
        self,
        column: str,
        threshold: float,
        condition: str,
        event_name: str,
        min_duration_rows: int = 1,
    ) -> pd.DataFrame:
        """Detect events where a column crosses a threshold (rising-edge only).

        Args:
            column: Column name to monitor.
            threshold: Threshold value.
            condition: Comparison operator ('>', '<', '>=', '<=', '==').
            event_name: Activity label for detected events.
            min_duration_rows: Minimum consecutive rows the condition must hold.

        Returns:
            DataFrame with columns: timestamp, activity, value.
        """
        ops = {
            ">": lambda s: s > threshold,
            "<": lambda s: s < threshold,
            ">=": lambda s: s >= threshold,
            "<=": lambda s: s <= threshold,
            "==": lambda s: s == threshold,
        }
        if condition not in ops:
            raise ValueError(f"Unknown condition: {condition!r}")

        mask = ops[condition](self.df[column])

        rising_edge = mask & ~mask.shift(1, fill_value=False)

        if min_duration_rows > 1:
            duration_check = pd.Series(False, index=self.df.index)
            for i in range(min_duration_rows):
                duration_check |= mask.shift(-i, fill_value=False)
            rising_edge = rising_edge & duration_check

        event_indices = self.df[rising_edge].index
        return pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"].values,
                "activity": event_name,
                "value": self.df.loc[event_indices, column].values,
            }
        ).reset_index(drop=True)

    def detect_state_change_events(
        self,
        column: str,
        event_name_prefix: str,
        ignore_nan: bool = True,
    ) -> pd.DataFrame:
        """Detect every value transition in a column.

        Activity labels:
        - Boolean columns: "{prefix} False->True" / "{prefix} True->False"
        - Numeric columns: "{prefix} {old:.0f}->{new:.0f}"
        - First row: "{prefix} Start" (no previous value available)

        Args:
            column: Column name to monitor.
            event_name_prefix: Prefix used to build activity label strings.
            ignore_nan: Skip transitions involving NaN values.

        Returns:
            DataFrame with columns: timestamp, activity, value.
        """
        col = self.df[column]
        if ignore_nan:
            changed = (col != col.shift(1)) & col.notna() & col.shift(1).notna()
        else:
            changed = col != col.shift(1)

        event_indices = self.df[changed].index
        if len(event_indices) == 0:
            return pd.DataFrame(columns=["timestamp", "activity", "value"])

        prev_values = col.shift(1)
        is_bool = pd.api.types.is_bool_dtype(col)
        first_idx = self.df.index[0]

        def _label(idx) -> str:
            if idx == first_idx:
                return f"{event_name_prefix} Start"
            prev = prev_values.loc[idx]
            curr = col.loc[idx]
            if is_bool:
                return f"{event_name_prefix} {prev}->{curr}"
            return f"{event_name_prefix} {prev:.0f}->{curr:.0f}"

        return pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"].values,
                "activity": [_label(idx) for idx in event_indices],
                "value": col.loc[event_indices].values,
            }
        ).reset_index(drop=True)

    def detect_combined_condition_events(
        self,
        conditions: List[Tuple[str, str, float]],
        event_name: str,
        mode: str = "all",
    ) -> pd.DataFrame:
        """Detect events where multiple column conditions are simultaneously satisfied.

        Args:
            conditions: List of (column, operator, threshold) tuples.
            event_name: Activity label for detected events.
            mode: 'all' (AND all conditions) or 'any' (OR any condition).

        Returns:
            DataFrame with columns: timestamp, activity, value.
        """
        ops = {
            ">": lambda s, t: s > t,
            "<": lambda s, t: s < t,
            ">=": lambda s, t: s >= t,
            "<=": lambda s, t: s <= t,
            "==": lambda s, t: s == t,
        }
        masks = [ops[op](self.df[col], thr) for col, op, thr in conditions]

        if mode == "all":
            combined = masks[0].copy()
            for m in masks[1:]:
                combined &= m
        else:
            combined = masks[0].copy()
            for m in masks[1:]:
                combined |= m

        rising_edge = combined & ~combined.shift(1, fill_value=False)
        event_indices = self.df[rising_edge].index

        return pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"].values,
                "activity": event_name,
                "value": float("nan"),
            }
        ).reset_index(drop=True)

    def detect_local_extrema_events(
        self,
        column: str,
        event_name_max: str,
        event_name_min: str,
        window_size: int = 10,
        prominence: float = 0.1,
    ) -> pd.DataFrame:
        """Detect local maxima and minima in a column.

        Args:
            column: Column to analyse.
            event_name_max: Activity label for local maxima.
            event_name_min: Activity label for local minima.
            window_size: Minimum distance between peaks (rows).
            prominence: Minimum peak prominence (same units as column).

        Returns:
            DataFrame with columns: timestamp, activity, value.
        """
        from scipy.signal import find_peaks

        values = self.df[column].fillna(0).values

        peaks_max, _ = find_peaks(values, distance=window_size, prominence=prominence)
        peaks_min, _ = find_peaks(-values, distance=window_size, prominence=prominence)

        events_max = pd.DataFrame(
            {
                "timestamp": self.df.iloc[peaks_max]["time.absolute"].values,
                "activity": event_name_max,
                "value": self.df.iloc[peaks_max][column].values,
            }
        )
        events_min = pd.DataFrame(
            {
                "timestamp": self.df.iloc[peaks_min]["time.absolute"].values,
                "activity": event_name_min,
                "value": self.df.iloc[peaks_min][column].values,
            }
        )

        return (
            pd.concat([events_max, events_min], ignore_index=True)
            .sort_values("timestamp")
            .reset_index(drop=True)
        )
