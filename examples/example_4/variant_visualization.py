"""Create chevron-style visualization for process variants."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def _draw_chevron_workflow(
    ax, variant_tuple, y_position, variant_count, variant_pct, max_events=15
):
    """Draw a single variant as a chevron/pipeline workflow.

    Args:
        ax: Matplotlib axis
        variant_tuple: Tuple of activity names
        y_position: Y-axis position for this variant
        variant_count: Number of cases with this variant
        variant_pct: Percentage of total cases
        max_events: Maximum number of events to display (truncate if longer)
    """
    # Truncate if too long
    activities = list(variant_tuple)[:max_events]
    truncated = len(variant_tuple) > max_events

    # Colors for different event types
    color_map = {
        "Full Throttle": "#FF4444",  # Red - the trigger
        "Brake": "#4444FF",  # Blue - braking events
        "Gear": "#44AA44",  # Green - gear shifts
        "Corner": "#FF8844",  # Orange - cornering
        "High Lateral": "#AA44AA",  # Purple - lateral load
        "Bumpstop": "#FFAA44",  # Yellow/orange - suspension
        "Low Oil": "#AA4444",  # Dark red - warnings
        "Lap": "#888888",  # Gray - lap events
    }

    def get_color(activity):
        """Get color based on activity type."""
        for key, color in color_map.items():
            if key in activity:
                return color
        return "#CCCCCC"  # Default gray

    # Layout parameters
    box_width = 1.5
    box_height = 0.6
    spacing = 0.3
    x_start = 0

    # Draw each event as a chevron/arrow box
    for i, activity in enumerate(activities):
        x_pos = x_start + i * (box_width + spacing)

        # Truncate long activity names
        display_name = activity if len(activity) <= 20 else activity[:17] + "..."

        # Create chevron-style box (fancy box with arrow style)
        color = get_color(activity)

        # Draw the box
        box = FancyBboxPatch(
            (x_pos, y_position - box_height / 2),
            box_width,
            box_height,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor="black",
            linewidth=1.5,
            alpha=0.8,
        )
        ax.add_patch(box)

        # Add text
        ax.text(
            x_pos + box_width / 2,
            y_position,
            display_name,
            ha="center",
            va="center",
            fontsize=7,
            weight="bold",
            color="white",
            wrap=True,
        )

        # Draw arrow to next event
        if i < len(activities) - 1:
            arrow = FancyArrowPatch(
                (x_pos + box_width, y_position),
                (x_pos + box_width + spacing, y_position),
                arrowstyle="->",
                color="black",
                linewidth=2,
                mutation_scale=15,
            )
            ax.add_patch(arrow)

    # Add truncation indicator
    if truncated:
        x_pos = x_start + len(activities) * (box_width + spacing)
        ax.text(
            x_pos,
            y_position,
            f"... +{len(variant_tuple) - max_events} more",
            ha="left",
            va="center",
            fontsize=8,
            style="italic",
            color="gray",
        )

    # Add variant label on the left
    ax.text(
        -0.5,
        y_position,
        f"{variant_count} cases\n({variant_pct}%)",
        ha="right",
        va="center",
        fontsize=8,
        weight="bold",
    )


def visualize_chevron_variants(
    variant_stats_df, max_variants=10, max_events_per_variant=12
):
    """Create chevron visualization for top variants.

    Args:
        variant_stats_df: DataFrame with variant statistics
        max_variants: Maximum number of variants to display
        max_events_per_variant: Maximum events to show per variant
    """
    # Select top variants
    top_variants = variant_stats_df.head(max_variants)

    # Calculate figure size based on number of variants
    fig_height = max(8, len(top_variants) * 1.2)
    fig_width = 16

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Draw each variant
    for i, (idx, row) in enumerate(top_variants.iterrows()):
        y_pos = len(top_variants) - i - 1  # Reverse order (top variant at top)
        _draw_chevron_workflow(
            ax,
            row["Variant"],
            y_pos,
            row["Count"],
            row["Percentage"],
            max_events=max_events_per_variant,
        )

    # Set axis limits and labels
    ax.set_xlim(-2, max_events_per_variant * 2)
    ax.set_ylim(-1, len(top_variants))
    ax.set_aspect("equal", adjustable="datalim")

    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add title
    plt.title(
        f"Top {len(top_variants)} Process Variants - Chevron Workflow View",
        fontsize=14,
        weight="bold",
        pad=20,
    )

    # Add legend
    legend_elements = [
        mpatches.Patch(color=color, label=label, alpha=0.8)
        for label, color in [
            ("Full Throttle (Trigger)", "#FF4444"),
            ("Braking Events", "#4444FF"),
            ("Gear Shifts", "#44AA44"),
            ("Corner Events", "#FF8844"),
            ("High Lateral Load", "#AA44AA"),
            ("Suspension Events", "#FFAA44"),
            ("Warnings", "#AA4444"),
            ("Other", "#CCCCCC"),
        ]
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    return fig
