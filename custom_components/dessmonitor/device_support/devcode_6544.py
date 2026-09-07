"""DessMonitor Data Collector (devcode 6544)"""

from __future__ import annotations

DEVICE_INFO = {
    "name": "DessMonitor Data Collector (devcode 6544)",
    "description": "DessMonitor data collector/gateway for split-phase inverters",
    "manufacturer": "DessMonitor",
    "known_inverters": ["ANENJI ANJ-HHS-11KW-48V"],
    "supported_features": [
        "real_time_monitoring",
        "energy_tracking",
        "battery_management",
        "solar_tracking",
        "parameter_control",
        "split_phase_output",
    ],
}

OUTPUT_PRIORITY_MAPPING: dict[str, str] = {
    "SUB": "Solar → Utility → Battery",
    "SBU": "Solar → Battery → Utility",
    "SUF": "Solar → Utility First",
}

CHARGER_PRIORITY_MAPPING: dict[str, str] = {
    "SOF": "Solar First",
    "SNU": "Solar and Utility",
    "OSO": "Only Solar",
    "SOR": "Solar or Utility",
}

OPERATING_MODE_MAPPING: dict[str, str] = {
    "Bypass Mode": "Grid Mode",
    "Line Mode": "Grid Mode",
    "Mains Mode": "Grid Mode",
    "Battery Mode": "Battery Mode",
    "Inverter Mode": "Off-grid Mode",
    "Standby": "Standby",
    "Fault": "Fault",
}

SENSOR_TITLE_MAPPINGS: dict[str, str] = {
    # Fix typos
    "INV Module Termperature": "Inverter Temperature",
    "DC Module Termperature": "DC Module Temperature",
    "Total Output Aparent Power": "Output Apparent Power",
    "devise serial number": "Device Serial Number",
    # Standardize output sensors
    "Output frequency": "Output Frequency",
    "Total Output Active Power": "Output Active Power",
    "Total Output Current": "Output Current",
    "Total Load Percentage": "Load Percent",
    # PV sensors
    "PV1 Current": "PV1 Charger Current",
    "PV1 Power": "PV1 Charger Power",
    "PV2 Current": "PV2 Charger Current",
    "PV2 Power": "PV2 Charger Power",
    "Total PV Power": "PV Power",
    "Total PV Charging Power": "PV Total Charger Power",
    "Total PV Charging Current": "PV Charging Current",
    # Energy sensors
    "Daily PV energy generation": "Energy Today",
    "Total PV energy generation": "Energy Total",
    # Priority sensors
    "Main Output Priority": "Output priority",
    "Current output priority": "Output priority",
    "Current charging priority": "Charger Source Priority",
}

# Configurable ranges documented in the ANJ-HHS-11KW-48V manual (LCD setting
# groups F0-F3), keyed by control field id as ``(min, max, step)``.
#
# The cloud API returns ``hint: null`` for every control on this collector, so
# without this table ``number`` entities fall back to a guessed range. Some of
# those guesses are wrong in both directions: "Min" controls keep Home
# Assistant's 0-100 default even though the device reports 120 (Eq timeout) and
# accepts up to 900, while a current control is capped at 200A when the
# hardware accepts 500A.
#
# Only the outer limits are encoded. The manual also defines cross-field limits
# (floating <= bulk voltage, utility charging current <= total charging
# current, and the Max[]/Min[] chains around the utility/battery switch-over
# points). Those are left to the inverter, which rejects an out-of-range write
# on its own; mirroring them here would mean five entities reading each other's
# state on every render for no added protection.
CONTROL_RANGES: dict[str, tuple[float, float, float]] = {
    # --- F1 AC output ---
    # F1-12 OP2 overload warning point.
    "bse_eybond_read_55429": (10.0, 100.0, 1.0),
    # --- F2 battery ---
    # F2-03 bulk (C.V) charging voltage.
    "bat_eybond_read_43991": (48.0, 62.0, 0.1),
    # F2-04 floating charging voltage.
    "bat_eybond_read_43992": (48.0, 62.0, 0.1),
    # F2-16 bulk charging time; 0 selects the inverter's automatic timing.
    "bat_eybond_read_43993": (0.0, 900.0, 5.0),
    # F2-09 total charging current (11kW model; the 8.5kW model tops out at 140A).
    "bat_eybond_read_43994": (10.0, 160.0, 1.0),
    # F2-10 utility charging current.
    "bat_eybond_read_43995": (5.0, 120.0, 1.0),
    # F2-25 max battery discharge current; 0 disables the limit.
    "bat_eybond_read_43996": (0.0, 500.0, 1.0),
    # F2-06 voltage point back to battery mode; 0 means "battery fully charged".
    "bat_eybond_read_43997": (0.0, 62.0, 0.1),
    # F2-05 voltage point back to utility.
    "bat_eybond_read_43998": (44.0, 57.2, 0.1),
    # F2-07/F2-08 off-grid cut-off voltage.
    "bat_eybond_read_43999": (40.0, 54.0, 0.1),
    # F2-05 utility switch-over as SOC (battery with communication).
    "bat_eybond_read_44000": (5.0, 96.0, 1.0),
    # F2-06 battery switch-back as SOC.
    "bat_eybond_read_44001": (10.0, 100.0, 1.0),
    # F2-07/F2-08 off-grid cut-off SOC.
    "bat_eybond_read_44002": (0.0, 95.0, 1.0),
    # F2-18 equalization voltage.
    "bat_eybond_read_44004": (48.0, 62.0, 0.1),
    # F2-19 equalization duration.
    "bat_eybond_read_44005": (0.0, 900.0, 5.0),
    # F2-20 equalization timeout.
    "bat_eybond_read_44006": (0.0, 900.0, 5.0),
    # F2-21 equalization interval.
    "bat_eybond_read_44007": (1.0, 90.0, 1.0),
    # F2-07 OP1 off-grid cut-off voltage.
    "bat_eybond_read_55431": (40.0, 54.0, 0.1),
    # F2-07 OP1 off-grid cut-off SOC.
    "bat_eybond_read_55433": (0.0, 95.0, 1.0),
}


VALUE_TRANSFORMATIONS: dict = {}

PARAMETER_SENSOR_NAMES: set[str] = set()

DEVCODE_CONFIG = {
    "device_info": DEVICE_INFO,
    "output_priority_mapping": OUTPUT_PRIORITY_MAPPING,
    "charger_priority_mapping": CHARGER_PRIORITY_MAPPING,
    "operating_mode_mapping": OPERATING_MODE_MAPPING,
    "sensor_title_mappings": SENSOR_TITLE_MAPPINGS,
    "value_transformations": VALUE_TRANSFORMATIONS,
    "control_ranges": CONTROL_RANGES,
    "parameter_sensor_names": PARAMETER_SENSOR_NAMES,
}
