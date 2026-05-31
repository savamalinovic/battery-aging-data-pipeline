# NASA Battery Cloud Pipeline

Data pipeline and Streamlit dashboard for processing NASA Li-ion Battery Aging data.

The project ingests a nested ZIP dataset, extracts MATLAB `.mat` battery files, builds cleaned Parquet tables, filters implausible health cycles, calculates battery health analytics, and visualizes the results in a Streamlit dashboard.

## What the project does

The pipeline:

1. downloads the NASA battery dataset archive,
2. extracts nested ZIP files,
3. extracts all `.mat` battery files,
4. parses charge, discharge, and impedance cycles,
5. builds cleaned cycle-level Parquet outputs,
6. filters implausible discharge cycles for SOH/degradation analytics,
7. calculates battery health, SOH, EOL, degradation, temperature, voltage, duration, correlation, and data quality metrics,
8. creates dashboard-ready Parquet files,
9. serves a local Streamlit dashboard.

## Important health filtering note

The full dataset contains batteries tested under different experimental conditions. Some batteries contain implausible discharge capacity values, including extremely low values, zero values, unrealistically high values, and large cycle-to-cycle jumps.

The project keeps all cleaned discharge cycles in:

```text
data/cleaned/discharge_cycles.parquet