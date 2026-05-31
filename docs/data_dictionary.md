# Data Dictionary

This document summarizes the main pipeline outputs.

## Cleaned outputs

### `data/cleaned/cycle_summary.parquet`

Grain: one row per raw cycle.

Main columns:

| Column | Meaning |
|---|---|
| `battery_id` | Battery identifier, for example B0005 |
| `cycle_index` | Original cycle index from the raw MATLAB file |
| `operation_type` | charge, discharge, or impedance |
| `start_time` | Operation start time parsed from MATLAB time vector |
| `ambient_temperature` | Ambient temperature recorded for the cycle |
| `duration_seconds` | Cycle duration from the internal Time array |
| `capacity_ah` | Discharge capacity in Ah, only available for discharge cycles |
| `soh` | Initial raw SOH value from cycle summary; health analytics later recalculate SOH after filtering |
| `avg_voltage` | Average measured voltage within the cycle |
| `start_voltage` | First measured voltage value |
| `end_voltage` | Last measured voltage value |
| `voltage_drop` | Start voltage minus end voltage |
| `avg_temperature` | Average measured working temperature |
| `max_temperature` | Maximum measured working temperature |
| `temperature_delta_to_ambient` | Average working temperature minus ambient temperature |
| `is_valid` | Whether the cycle passed raw structure validation |

### `data/cleaned/discharge_cycles.parquet`

Grain: one row per discharge cycle.

This table keeps all discharge cycles, including cycles that may later be excluded from health analytics.

Main columns:

| Column | Meaning |
|---|---|
| `battery_id` | Battery identifier |
| `discharge_cycle_number` | Sequential discharge cycle number per battery |
| `capacity_ah` | Raw discharge capacity |
| `duration_seconds` | Discharge duration |
| `voltage_drop` | Start voltage minus end voltage |
| `avg_temperature` | Average working temperature |
| `life_stage` | Life stage based on SOH at the time this table was built |
| `is_valid` | Raw validation flag |

### `data/cleaned/discharge_cycles_health.parquet`

Grain: one row per health-valid discharge cycle.

This is the main input for SOH, EOL, degradation, ranking, duration, voltage, temperature, and correlation analytics.

Bad cycles are removed before this table is built. Batteries with too many implausible cycles are excluded from this table completely.

Main columns:

| Column | Meaning |
|---|---|
| `battery_id` | Battery identifier |
| `discharge_cycle_number` | Re-numbered health-valid discharge cycle number |
| `original_discharge_cycle_number` | Original discharge cycle number before filtering |
| `capacity_ah` | Plausible discharge capacity |
| `reference_capacity_ah` | Maximum plausible capacity for that battery |
| `initial_capacity_ah` | First plausible discharge capacity after filtering |
| `previous_capacity_ah` | Previous plausible discharge capacity |
| `soh` | Capacity divided by reference capacity |
| `eol_flag` | True when SOH is less than or equal to 70% |
| `capacity_change_from_reference_percent` | Signed capacity change from reference capacity |
| `capacity_change_from_previous_percent` | Signed cycle-to-cycle capacity change |
| `life_stage` | early, middle, or late based on SOH |
| `rul_cycles_actual` | Placeholder for later RUL logic |

## Quality outputs

### `data/quality/invalid_cycles.parquet`

Grain: one row per raw validation issue.

Contains cycles that failed structural validation, such as missing fields, empty arrays, invalid capacity, or non-monotonic time.

### `data/quality/health_quality_summary.parquet`

Grain: one row per battery.

Explains whether a battery is usable for health analytics.

Main columns:

| Column | Meaning |
|---|---|
| `battery_id` | Battery identifier |
| `total_discharge_cycles` | Total discharge cycles before health filtering |
| `plausible_discharge_cycles` | Discharge cycles kept for health analytics |
| `excluded_discharge_cycles` | Discharge cycles excluded from health analytics |
| `bad_cycle_percent` | Percent of discharge cycles excluded |
| `usable_for_health_analytics` | Whether the battery is included in health analytics |
| `health_exclusion_reason` | Reason for excluding the battery, if excluded |

## Analytics outputs

### `data/analytics/battery_health_summary.parquet`

Grain: one row per battery.

Battery-level health KPIs: initial capacity, final capacity, capacity loss, final SOH, EOL, duration loss, degradation rate, and health rank.

### `data/analytics/degradation_summary.parquet`

Grain: one row per battery.

Battery-level capacity degradation summary.

### `data/analytics/rolling_degradation_summary.parquet`

Grain: one row per health-valid discharge cycle.

Rolling capacity and SOH metrics for trend charts.

### `data/analytics/soh_eol_summary.parquet`

Grain: one row per battery.

SOH and EOL metrics, including first cycle below 80% SOH and first EOL crossing at 70% SOH.

### `data/analytics/life_stage_summary.parquet`

Grain: one row per battery and life stage.

Aggregated capacity, SOH, duration, voltage, and temperature metrics for early, middle, and late life.

### `data/analytics/temperature_summary.parquet`

Grain: one row per battery and life stage, plus an `all` row.

Temperature behavior by life stage, including temperature change within stage and ambient-adjusted temperature change.

### `data/analytics/voltage_summary.parquet`

Grain: one row per battery and life stage, plus an `all` row.

Voltage behavior by life stage, including voltage drop and voltage-drop correlations.

### `data/analytics/discharge_duration_summary.parquet`

Grain: one row per battery.

Discharge duration loss and correlation with capacity/SOH.

### `data/analytics/correlation_summary.parquet`

Grain: one row per metric pair and scope.

Pearson correlations between temperature, capacity, SOH, duration, and voltage metrics.

### `data/analytics/data_quality_summary.parquet`

Grain: one row per battery.

Raw cycle-level quality score and invalid cycle counts.

## Dashboard output

### `data/dashboard/dashboard_manifest.parquet`

Grain: one row per dataset.

Index of all dashboard-ready files, their paths, grains, and dashboard sections.