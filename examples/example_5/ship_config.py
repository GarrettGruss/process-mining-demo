"""SHIP_EVENTS: flat config list mapping detection method calls to subsystems and SHIP transitions.

Two config shapes:

  State-change pattern (two SHIP transitions from one detection):
    {
        "subsystem": str,
        "method": "detect_state_change_events",
        "derived_column": (column, operator, threshold),   # dispatcher computes boolean
        "args": {"event_name_prefix": str},               # column injected by dispatcher
    }
    The dispatcher builds False->True → error_activation and True->False → error_recovery
    automatically from the prefix. No transition_type field is needed.

  Simple pattern (one SHIP transition):
    {
        "subsystem": str,
        "transition_type": str,                            # "error_activation" | "error_recovery"
        "method": str,                                     # any EventClassifier method name
        "args": {method keyword arguments},
    }

Threshold values below are calibrated starting points.  Run the data-exploration cells in
example_5.ipynb to validate and adjust them for the specific dataset.
"""

SHIP_EVENTS = [
    # ── SUSPENSION ────────────────────────────────────────────────────────────────────────
    # Bumpstop contact: unit > 0 means the bumpstop is engaged.
    # State-change gives both the hit (False→True) and release (True→False).
    {
        "subsystem": "Suspension",
        "method": "detect_state_change_events",
        "derived_column": ("fl.bumpstop_unit", ">", 0.0),
        "args": {"event_name_prefix": "fl_bumpstop"},
    },
    {
        "subsystem": "Suspension",
        "method": "detect_state_change_events",
        "derived_column": ("fr.bumpstop_unit", ">", 0.0),
        "args": {"event_name_prefix": "fr_bumpstop"},
    },
    {
        "subsystem": "Suspension",
        "method": "detect_state_change_events",
        "derived_column": ("rl.bumpstop_unit", ">", 0.0),
        "args": {"event_name_prefix": "rl_bumpstop"},
    },
    {
        "subsystem": "Suspension",
        "method": "detect_state_change_events",
        "derived_column": ("rr.bumpstop_unit", ">", 0.0),
        "args": {"event_name_prefix": "rr_bumpstop"},
    },
    # Roll event: body roll exceeds threshold.
    # NOTE: roll angle_unit is unpopulated (always 0.0) in the endurance dataset —
    # this entry will produce 0 events but is retained for completeness.
    {
        "subsystem": "Suspension",
        "method": "detect_state_change_events",
        "derived_column": ("roll angle_unit", ">", 3.0),
        "args": {"event_name_prefix": "roll_event"},
    },

    # ── BRAKES ────────────────────────────────────────────────────────────────────────────
    # Wheel lockup: individual wheel speed drops near zero while the car is moving.
    # Front-left
    {
        "subsystem": "Brakes",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.speed.fl_mph", "<", 1.0),
                ("f88.v.speed_mph", ">", 5.0),
            ],
            "event_name": "wheel_lockup_fl",
        },
    },
    # Front-right
    {
        "subsystem": "Brakes",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.speed.fr_mph", "<", 1.0),
                ("f88.v.speed_mph", ">", 5.0),
            ],
            "event_name": "wheel_lockup_fr",
        },
    },
    # Rear-left
    {
        "subsystem": "Brakes",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.speed.rl_mph", "<", 1.0),
                ("f88.v.speed_mph", ">", 5.0),
            ],
            "event_name": "wheel_lockup_rl",
        },
    },
    # Rear-right
    {
        "subsystem": "Brakes",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.speed.rr_mph", "<", 1.0),
                ("f88.v.speed_mph", ">", 5.0),
            ],
            "event_name": "wheel_lockup_rr",
        },
    },

    # ── ENGINE ────────────────────────────────────────────────────────────────────────────
    # Engine overheating: coolant temp exceeds threshold.
    # Calibrated from data: max is 168 °F, 95th pct is 164 °F, mean is 148 °F.
    # 160 °F catches high-temp excursions without triggering on normal operating range.
    {
        "subsystem": "Engine",
        "method": "detect_state_change_events",
        "derived_column": ("f88.ect1_°f", ">", 160),
        "args": {"event_name_prefix": "engine_overheating"},
    },
    # Engine lugging: throttle open but RPM low — indicates wrong gear or driver error.
    {
        "subsystem": "Engine",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.rpm_rpm", "<", 3000),
                ("f88.tps1_%", ">", 70),
            ],
            "event_name": "engine_lugging",
        },
    },

    # ── LUBRICATION ───────────────────────────────────────────────────────────────────────
    # Low oil pressure: below threshold is a safety concern.
    # Calibrated from data: mean is 30 psi, but pressure drops during idle/startup.
    # 5 psi represents a genuinely dangerous low-pressure event (distinct from idle noise).
    {
        "subsystem": "Lubrication",
        "method": "detect_state_change_events",
        "derived_column": ("f88.oil.p1_psi", "<", 5),
        "args": {"event_name_prefix": "low_oil_pressure"},
    },
    # Oil pressure spike: above 80 psi may indicate a stuck relief valve or blockage.
    {
        "subsystem": "Lubrication",
        "method": "detect_state_change_events",
        "derived_column": ("f88.oil.p1_psi", ">", 80),
        "args": {"event_name_prefix": "oil_pressure_spike"},
    },

    # ── ELECTRICAL ────────────────────────────────────────────────────────────────────────
    # Low battery: voltage drop risks ECU brownout.
    # Calibrated from data: range is 12.9–15.0 V (very stable alternator).
    # 13.2 V catches brief voltage sag events (below 1st percentile min of 12.9 V
    # is not reachable in this dataset, so this threshold catches relative sags).
    {
        "subsystem": "Electrical",
        "method": "detect_state_change_events",
        "derived_column": ("battery_v", "<", 13.2),
        "args": {"event_name_prefix": "low_battery"},
    },
    # GPS lock degraded: fewer satellites degrades position accuracy.
    # Calibrated from data: range is 7–11 satellites.  Threshold < 8 catches the
    # minimum observed (7 sat) as a brief degradation event.
    {
        "subsystem": "Electrical",
        "method": "detect_state_change_events",
        "derived_column": ("gps.nsat_#", "<", 8),
        "args": {"event_name_prefix": "gps_degraded"},
    },

    # ── DRIVETRAIN ────────────────────────────────────────────────────────────────────────
    # Over-rev: RPM above rev limiter region while at speed.
    # Calibrated from data: max RPM is 12826.  12000+ at speed > 30 mph suggests
    # the engine is approaching the limiter in a gear where it shouldn't be.
    {
        "subsystem": "Drivetrain",
        "transition_type": "error_activation",
        "method": "detect_combined_condition_events",
        "args": {
            "conditions": [
                ("f88.rpm_rpm", ">", 12000),
                ("f88.v.speed_mph", ">", 30),
            ],
            "event_name": "drivetrain_overrev",
        },
    },
]
