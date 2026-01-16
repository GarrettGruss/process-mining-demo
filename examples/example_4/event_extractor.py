"""The event extractor contains various methods to generate discrete events from telemetry data."""

"""Event Extraction from FSAE Telemetry Data

This module extracts discrete events from continuous telemetry data based on
threshold conditions and state changes.

Considerations: Raw threshold-based methods on noisy telemetry can generate
spurious events. Consider adding hysteresis (different thresholds for entering vs. exiting 
a state) or minimum dwell times to avoid event flooding. Threshold-based detection works 
well for known failure modes but struggles with gradual drift or context-dependent anomalies.

"""

import pandas as pd
from typing import List, Tuple


class EventExtractor:
    """Extract events from telemetry dataframe based on defined conditions."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with telemetry dataframe.

        Args:
            df: Telemetry dataframe with all sensor channels
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
        """Detect events where a column crosses a threshold.

        Args:
            column: Column name to monitor
            threshold: Threshold value
            condition: Comparison operator ('>', '<', '>=', '<=', '==')
            event_name: Name of the event
            min_duration_rows: Minimum number of consecutive rows to confirm event

        Returns:
            DataFrame with columns: timestamp, event_name, value, lap
        """
        # Create boolean mask based on condition
        if condition == ">":
            mask = self.df[column] > threshold
        elif condition == "<":
            mask = self.df[column] < threshold
        elif condition == ">=":
            mask = self.df[column] >= threshold
        elif condition == "<=":
            mask = self.df[column] <= threshold
        elif condition == "==":
            mask = self.df[column] == threshold
        else:
            raise ValueError(f"Unknown condition: {condition}")

        # Find rising edges (transitions from False to True)
        rising_edge = mask & ~mask.shift(1).fillna(False)

        # Filter by minimum duration if specified
        if min_duration_rows > 1:
            # Check if condition stays true for min_duration_rows
            duration_check = pd.Series(False, index=self.df.index)
            for i in range(min_duration_rows):
                duration_check |= mask.shift(-i).fillna(False)
            rising_edge = rising_edge & duration_check

        # Extract events
        event_indices = self.df[rising_edge].index
        events_df = pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"],
                "activity": event_name,
                "value": self.df.loc[event_indices, column],
            }
        )

        return events_df.reset_index(drop=True)

    def detect_state_change_events(
        self, column: str, event_name_prefix: str, ignore_nan: bool = True
    ) -> pd.DataFrame:
        """Detect when a column value changes (e.g., gear shifts, calibration changes).

        Args:
            column: Column name to monitor
            event_name_prefix: Prefix for event name (will append old->new values)
            ignore_nan: Whether to ignore NaN values

        Returns:
            DataFrame with event details
        """
        # Find where values change
        if ignore_nan:
            value_changed = (
                (self.df[column] != self.df[column].shift(1))
                & self.df[column].notna()
                & self.df[column].shift(1).notna()
            )
        else:
            value_changed = self.df[column] != self.df[column].shift(1)

        event_indices = self.df[value_changed].index

        events_df = pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"],
                "activity": [
                    f"{event_name_prefix} {self.df.loc[idx - 1, column]:.0f}->{self.df.loc[idx, column]:.0f}"
                    if idx > self.df.index[0]
                    else f"{event_name_prefix} Start"
                    for idx in event_indices
                ],
                "value": self.df.loc[event_indices, column],
            }
        )

        return events_df.reset_index(drop=True)

    def detect_combined_condition_events(
        self,
        conditions: List[Tuple[str, str, float]],
        event_name: str,
        mode: str = "all",
    ) -> pd.DataFrame:
        """Detect events based on multiple conditions.

        Args:
            conditions: List of (column, operator, threshold) tuples
            event_name: Name of the event
            mode: 'all' (AND) or 'any' (OR) for combining conditions

        Returns:
            DataFrame with event details
        """
        masks = []
        for column, operator, threshold in conditions:
            if operator == ">":
                masks.append(self.df[column] > threshold)
            elif operator == "<":
                masks.append(self.df[column] < threshold)
            elif operator == ">=":
                masks.append(self.df[column] >= threshold)
            elif operator == "<=":
                masks.append(self.df[column] <= threshold)
            elif operator == "==":
                masks.append(self.df[column] == threshold)

        # Combine masks
        if mode == "all":
            combined_mask = pd.Series(True, index=self.df.index)
            for mask in masks:
                combined_mask &= mask
        else:  # 'any'
            combined_mask = pd.Series(False, index=self.df.index)
            for mask in masks:
                combined_mask |= mask

        # Find rising edges
        rising_edge = combined_mask & ~combined_mask.shift(1).fillna(False)
        event_indices = self.df[rising_edge].index

        events_df = pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"],
                "activity": event_name,
                "value": None,
            }
        )

        return events_df.reset_index(drop=True)

    def detect_local_extrema_events(
        self,
        column: str,
        event_name_max: str,
        event_name_min: str,
        window_size: int = 10,
        prominence: float = 0.1,
    ) -> pd.DataFrame:
        """Detect local maxima and minima (e.g., corner apex).

        Args:
            column: Column to analyze
            event_name_max: Name for maximum events
            event_name_min: Name for minimum events
            window_size: Size of window for local comparison
            prominence: Minimum prominence (difference from neighbors)

        Returns:
            DataFrame with event details
        """
        from scipy.signal import find_peaks

        values = self.df[column].fillna(0).values

        # Find peaks (maxima)
        peaks_max, _ = find_peaks(values, distance=window_size, prominence=prominence)
        # Find valleys (minima)
        peaks_min, _ = find_peaks(-values, distance=window_size, prominence=prominence)

        # Create events for maxima
        events_max = pd.DataFrame(
            {
                "timestamp": self.df.iloc[peaks_max]["time.absolute"].values,
                "activity": event_name_max,
                "value": self.df.iloc[peaks_max][column].values,
            }
        )

        # Create events for minima
        events_min = pd.DataFrame(
            {
                "timestamp": self.df.iloc[peaks_min]["time.absolute"].values,
                "activity": event_name_min,
                "value": self.df.iloc[peaks_min][column].values,
            }
        )

        return pd.concat([events_max, events_min], ignore_index=True).sort_values(
            "timestamp"
        )
