"""Time Window Case Generator

This class generates process mining cases by creating time windows around
events of interest. Events can belong to multiple cases if time windows overlap.
"""

import pandas as pd
from typing import Optional, List, Union


class CaseGenerator:
    """Generate case IDs based on time windows around specific events."""

    def __init__(self, event_log: pd.DataFrame):
        """Initialize with an event log dataframe.

        Args:
            event_log: DataFrame with columns including 'timestamp', 'activity'
        """
        self.event_log = event_log.copy()

        # Ensure timestamp is available
        if "timestamp" not in self.event_log.columns:
            raise ValueError("event_log must contain 'timestamp' column")

        # Convert timestamp to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(self.event_log["timestamp"]):
            self.event_log["timestamp"] = pd.to_datetime(self.event_log["timestamp"])

        # Ensure events are sorted by time
        self.event_log = self.event_log.sort_values("timestamp").reset_index(drop=True)

        print(f"TimeWindowCaseGenerator initialized with {len(self.event_log)} events")

    def generate_cases_time_window(
        self,
        trigger_event: Union[str, List[str]],
        time_before: float,
        time_after: float,
        case_prefix: str = "Case",
    ) -> pd.DataFrame:
        """Generate cases based on time windows around trigger events.

        This method finds all occurrences of the trigger event(s) and creates a time
        window around each occurrence. All events within each time window are assigned
        to that case. Events can appear in multiple cases if windows overlap.

        Args:
            trigger_event: Activity name(s) to use as trigger. Can be a string or list of strings.
            time_before: Time window before the trigger event (in seconds)
            time_after: Time window after the trigger event (in seconds)
            case_prefix: Prefix for case IDs (default: "Case")

        Returns:
            New DataFrame with events assigned to time window cases.
            Each row represents an event-case assignment.
        """
        # Convert single trigger to list
        if isinstance(trigger_event, str):
            trigger_events = [trigger_event]
        else:
            trigger_events = trigger_event

        # Find all trigger event occurrences
        trigger_mask = self.event_log["activity"].isin(trigger_events)
        trigger_occurrences = self.event_log[trigger_mask].copy()

        if len(trigger_occurrences) == 0:
            print(f"Warning: No events found matching trigger: {trigger_events}")
            return pd.DataFrame()

        print(f"Found {len(trigger_occurrences)} trigger event occurrences")
        print(f"Time window: -{time_before}s to +{time_after}s around each trigger")

        # Create cases for each trigger occurrence
        case_events = []

        for idx, (trigger_idx, trigger_row) in enumerate(
            trigger_occurrences.iterrows()
        ):
            case_id = f"{case_prefix}_{idx + 1:04d}"
            trigger_time = trigger_row["timestamp"]

            # Define time window using timedelta
            window_start = trigger_time - pd.Timedelta(seconds=time_before)
            window_end = trigger_time + pd.Timedelta(seconds=time_after)

            # Find all events within this time window
            in_window = (self.event_log["timestamp"] >= window_start) & (
                self.event_log["timestamp"] <= window_end
            )

            window_events = self.event_log[in_window].copy()

            # Add case information
            window_events["case_id"] = case_id
            window_events["trigger_event"] = trigger_row["activity"]
            window_events["trigger_time"] = trigger_time
            window_events["window_start"] = window_start
            window_events["window_end"] = window_end
            window_events["time_relative_to_trigger"] = (
                window_events["timestamp"] - trigger_time
            ).dt.total_seconds()
            window_events["is_trigger"] = window_events.index == trigger_idx

            case_events.append(window_events)

        # Combine all cases into a single dataframe
        result_df = pd.concat(case_events, ignore_index=True)

        # Sort by case_id and then by time within each case
        result_df = result_df.sort_values(["case_id", "timestamp"]).reset_index(
            drop=True
        )

        # Add sequence number within each case
        result_df["event_sequence"] = result_df.groupby("case_id").cumcount() + 1

        print(f"\nGenerated {len(trigger_occurrences)} cases")
        print(f"Total event-case assignments: {len(result_df)}")
        print(
            f"Average events per case: {len(result_df) / len(trigger_occurrences):.1f}"
        )

        # Calculate overlap statistics
        original_events = len(self.event_log)
        unique_events_in_cases = result_df.index.nunique()

        if original_events > 0:
            overlap_ratio = (
                len(result_df) / unique_events_in_cases
                if unique_events_in_cases > 0
                else 0
            )
            print(
                f"Event overlap ratio: {overlap_ratio:.2f}x (events appear in multiple cases)"
            )

        return result_df
