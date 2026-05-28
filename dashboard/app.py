import pandas as pd
import plotly.express as px
import streamlit as st

from config import FILES


st.set_page_config(
    page_title="NASA Battery Health Dashboard",
    page_icon="🔋",
    layout="wide",
)


@st.cache_data
def load_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_data() -> dict[str, pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}

    for name, path in FILES.items():
        if path.exists():
            data[name] = load_parquet(str(path))
        else:
            data[name] = pd.DataFrame()

    return data

COLUMN_LABELS = {
    "battery_id": "Battery",
    "life_stage": "Life stage",
    "cycle_index": "Cycle index",
    "discharge_cycle_number": "Discharge cycle",
    "capacity_ah": "Capacity (Ah)",
    "initial_capacity_ah": "Initial capacity (Ah)",
    "previous_capacity_ah": "Previous capacity (Ah)",
    "first_capacity_ah": "Initial capacity (Ah)",
    "final_capacity_ah": "Final capacity (Ah)",
    "capacity_loss_ah": "Capacity loss (Ah)",
    "capacity_loss_percent": "Capacity loss (%)",
    "initial_soh": "Initial SOH",
    "final_soh": "Final SOH",
    "initial_soh_percent": "Initial SOH (%)",
    "final_soh_percent": "Final SOH (%)",
    "min_soh_percent": "Minimum SOH (%)",
    "avg_soh_percent": "Average SOH (%)",
    "soh": "SOH",
    "eol_flag": "EOL reached",
    "eol_cycle": "EOL cycle",
    "reached_eol": "Reached EOL",
    "cycle_below_80_soh": "First cycle below 80% SOH",
    "capacity_at_eol_ah": "Capacity at EOL (Ah)",
    "soh_at_eol_percent": "SOH at EOL (%)",
    "rul_available": "RUL available",
    "health_rank": "Health rank",
    "total_discharge_cycles": "Total discharge cycles",
    "avg_degradation_rate_per_cycle": "Average degradation per cycle",
    "avg_discharge_duration_seconds": "Average discharge duration (s)",
    "duration_loss_percent": "Duration loss (%)",
    "duration_loss_seconds": "Duration loss (s)",
    "duration_seconds": "Duration (s)",
    "initial_duration_seconds": "Initial duration (s)",
    "final_duration_seconds": "Final duration (s)",
    "avg_duration_seconds": "Average duration (s)",
    "corr_duration_capacity": "Duration vs capacity correlation",
    "corr_duration_soh": "Duration vs SOH correlation",
    "avg_capacity_ah": "Average capacity (Ah)",
    "avg_working_temperature": "Average working temperature (°C)",
    "max_working_temperature": "Maximum working temperature (°C)",
    "avg_temperature": "Average temperature (°C)",
    "max_temperature": "Maximum temperature (°C)",
    "avg_temperature_delta_to_ambient": "Average temperature above ambient (°C)",
    "temperature_delta_to_ambient": "Temperature above ambient (°C)",
    "temperature_change_within_stage": "Temperature change within stage (°C)",
    "delta_to_ambient_change_within_stage": "Ambient-adjusted temperature change (°C)",
    "avg_start_voltage": "Average start voltage (V)",
    "avg_end_voltage": "Average end voltage (V)",
    "avg_voltage": "Average voltage (V)",
    "avg_voltage_drop": "Average voltage drop (V)",
    "voltage_drop": "Voltage drop (V)",
    "voltage_drop_change_within_stage": "Voltage drop improvement within stage (V)",
    "correlation_voltage_drop_capacity": "Voltage drop vs capacity correlation",
    "correlation_voltage_drop_soh": "Voltage drop vs SOH correlation",
    "relative_capacity_drop_percent": "Relative capacity drop (%)",
    "relative_capacity_change_percent": "Relative capacity change (%)",
    "absolute_capacity_drop_ah": "Capacity drop (Ah)",
    "absolute_capacity_change_ah": "Capacity change (Ah)",
    "early_avg_capacity_ah": "Early average capacity (Ah)",
    "late_avg_capacity_ah": "Late average capacity (Ah)",
    "early_to_late_capacity_change_ah": "Early-to-late capacity change (Ah)",
    "early_to_late_capacity_change_percent": "Early-to-late capacity change (%)",
    "rolling_capacity_5": "Rolling capacity average",
    "rolling_soh_5": "Rolling SOH average",
    "capacity_fade_from_previous_percent": "Capacity change from previous cycle (%)",
    "capacity_fade_from_initial_percent": "Capacity change from initial cycle (%)",
    "degradation_acceleration_percent": "Degradation acceleration (%)",
    "absolute_capacity_drop_percent": "Absolute capacity drop (%)",
    "scope": "Scope",
    "x_metric": "First metric",
    "y_metric": "Second metric",
    "correlation_method": "Correlation method",
    "correlation_value": "Correlation value",
    "sample_count": "Sample count",
    "interpretation": "Interpretation",
    "total_cycles": "Total cycles",
    "valid_cycles": "Valid cycles",
    "invalid_cycles": "Invalid cycles",
    "quality_score_percent": "Quality score (%)",
    "invalid_discharge_cycles": "Invalid discharge cycles",
    "invalid_impedance_cycles": "Invalid impedance cycles",
    "top_error_code": "Most common error",
    "usable_for_health_analytics": "Usable for health analytics",
    "dataset_name": "Dataset",
    "file_path": "File path",
    "required_for_mvp": "Required for MVP",
    "dashboard_section": "Dashboard section",
    "grain": "Data grain",
    "description": "Description",
}


VALUE_LABELS = {
    "early": "Early",
    "middle": "Middle",
    "late": "Late",
    "all": "All",
    "all_batteries": "All batteries",
    "battery": "Single battery",
    "pearson": "Pearson",
    "strong_positive": "Strong positive",
    "moderate_positive": "Moderate positive",
    "weak_positive": "Weak positive",
    "very_weak_positive": "Very weak positive",
    "strong_negative": "Strong negative",
    "moderate_negative": "Moderate negative",
    "weak_negative": "Weak negative",
    "very_weak_negative": "Very weak negative",
    "not_enough_data": "Not enough data",
}


def natural_label(name: str) -> str:
    if name in COLUMN_LABELS:
        return COLUMN_LABELS[name]

    return name.replace("_", " ").title()


def natural_value(value):
    if isinstance(value, str):
        return VALUE_LABELS.get(value, value.replace("_", " ").title())

    return value


def display_dataframe(df: pd.DataFrame) -> None:
    display = df.copy()

    for column in display.columns:
        if display[column].dtype == "object":
            display[column] = display[column].map(natural_value)

    display = display.rename(
        columns={column: natural_label(column) for column in display.columns}
    )

    st.dataframe(display, use_container_width=True)


def plot_labels(df: pd.DataFrame) -> dict[str, str]:
    return {column: natural_label(column) for column in df.columns}


def chart_data(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()

    for column in display.columns:
        if display[column].dtype == "object":
            display[column] = display[column].map(natural_value)

    return display


def show_overview(data: dict[str, pd.DataFrame]) -> None:
    st.header("Overview")

    battery_health = data["battery_health_summary"]
    soh_eol = data["soh_eol_summary"]

    if battery_health.empty:
        st.warning("battery_health_summary.parquet is missing or empty.")
        return

    battery_count = battery_health["battery_id"].nunique()
    avg_final_soh = battery_health["final_soh"].mean() * 100
    reached_eol_count = battery_health["reached_eol"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Batteries", int(battery_count))
    col2.metric("Average final SOH", f"{avg_final_soh:.2f}%")
    col3.metric("Reached EOL", int(reached_eol_count))

    st.markdown(
        """
        **SOH (State of Health)** shows how much usable capacity a battery has left
        compared with its first measured discharge capacity. In this project,
        the first discharge cycle starts at 100% SOH for each battery.

        **EOL (End of Life)** is reached when SOH first falls to 70% or lower.
        The project uses the first crossing rule, meaning the EOL cycle is the
        first discharge cycle where the battery reaches that threshold, even if
        later measurements temporarily recover above 70%.
        """
    )

    st.subheader("Battery health ranking")

    battery_health_display = battery_health.rename(
        columns={
            "battery_id": "Battery",
            "first_capacity_ah": "Initial capacity (Ah)",
            "final_capacity_ah": "Final capacity (Ah)",
            "capacity_loss_ah": "Capacity loss (Ah)",
            "capacity_loss_percent": "Capacity loss (%)",
            "initial_soh": "Initial SOH",
            "final_soh": "Final SOH",
            "total_discharge_cycles": "Total discharge cycles",
            "cycle_below_80_soh": "First cycle below 80% SOH",
            "eol_cycle": "EOL cycle",
            "reached_eol": "Reached EOL",
            "avg_degradation_rate_per_cycle": "Average degradation per cycle",
            "avg_discharge_duration_seconds": "Average discharge duration (s)",
            "duration_loss_percent": "Duration loss (%)",
            "health_rank": "Health rank",
        }
    )

    display_dataframe(battery_health_display)

    fig = px.bar(
        chart_data(battery_health),
        x="battery_id",
        y="final_soh",
        text="health_rank",
        title="Final SOH by battery",
        labels=plot_labels(battery_health),
    )
    st.plotly_chart(fig, use_container_width=True)

    if not soh_eol.empty:
        st.subheader("SOH and EOL summary")

        soh_eol_display = soh_eol.rename(
            columns={
                "battery_id": "Battery",
                "initial_soh_percent": "Initial SOH (%)",
                "final_soh_percent": "Final SOH (%)",
                "min_soh_percent": "Minimum SOH (%)",
                "avg_soh_percent": "Average SOH (%)",
                "cycle_below_80_soh": "First cycle below 80% SOH",
                "eol_cycle": "EOL cycle",
                "capacity_at_eol_ah": "Capacity at EOL (Ah)",
                "soh_at_eol_percent": "SOH at EOL (%)",
                "rul_available": "RUL available",
            }
        )

        display_dataframe(soh_eol_display)
        

def show_degradation(data: dict[str, pd.DataFrame]) -> None:
    st.header("Capacity degradation")

    degradation = data["degradation_summary"]
    rolling = data["rolling_degradation_summary"]

    if degradation.empty:
        st.warning("degradation_summary.parquet is missing or empty.")
        return

    st.subheader("Battery-level degradation summary")
    display_dataframe(degradation)

    fig = px.bar(
        chart_data(degradation),
        x="battery_id",
        y="relative_capacity_drop_percent",
        title="Relative capacity drop by battery",
        labels=plot_labels(degradation),
    )
    st.plotly_chart(fig, use_container_width=True)

    if not rolling.empty:
        st.subheader("Rolling capacity trend")

        fig = px.line(
            chart_data(rolling),
            x="discharge_cycle_number",
            y="rolling_capacity_5",
            color="battery_id",
            title="Rolling capacity average over discharge cycles",
            labels=plot_labels(rolling),
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = px.line(
            chart_data(rolling),
            x="discharge_cycle_number",
            y="rolling_soh_5",
            color="battery_id",
            title="Rolling SOH average over discharge cycles",
            labels=plot_labels(rolling),
        )
        st.plotly_chart(fig, use_container_width=True)


def show_life_stage(data: dict[str, pd.DataFrame]) -> None:
    st.header("Life stage comparison")

    life_stage = data["life_stage_summary"]

    if life_stage.empty:
        st.warning("life_stage_summary.parquet is missing or empty.")
        return

    display_dataframe(life_stage)

    fig = px.bar(
        chart_data(life_stage),
        x="battery_id",
        y="avg_capacity_ah",
        color="life_stage",
        barmode="group",
        title="Average capacity by life stage",
        labels=plot_labels(life_stage),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        chart_data(life_stage),
        x="battery_id",
        y="avg_soh_percent",
        color="life_stage",
        barmode="group",
        title="Average SOH by life stage",
        labels=plot_labels(life_stage),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_temperature(data: dict[str, pd.DataFrame]) -> None:
    st.header("Temperature behavior")

    temperature = data["temperature_summary"]

    if temperature.empty:
        st.warning("temperature_summary.parquet is missing or empty.")
        return

    display_dataframe(temperature)

    stage_rows = temperature[temperature["life_stage"] != "all"]

    fig = px.bar(
        chart_data(stage_rows),
        x="battery_id",
        y="avg_working_temperature",
        color="life_stage",
        barmode="group",
        title="Average working temperature by life stage",
        labels=plot_labels(stage_rows),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        chart_data(stage_rows),
        x="battery_id",
        y="avg_temperature_delta_to_ambient",
        color="life_stage",
        barmode="group",
        title="Average temperature delta to ambient by life stage",
        labels=plot_labels(stage_rows),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        chart_data(temperature),
        x="battery_id",
        y="temperature_change_within_stage",
        color="life_stage",
        barmode="group",
        title="Temperature change within stage",
        labels=plot_labels(temperature),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_voltage(data: dict[str, pd.DataFrame]) -> None:
    st.header("Voltage behavior")

    voltage = data["voltage_summary"]

    if voltage.empty:
        st.warning("voltage_summary.parquet is missing or empty.")
        return

    display_dataframe(voltage)

    stage_rows = voltage[voltage["life_stage"] != "all"]

    fig = px.bar(
        chart_data(stage_rows),
        x="battery_id",
        y="avg_voltage_drop",
        color="life_stage",
        barmode="group",
        title="Average voltage drop by life stage",
        labels=plot_labels(stage_rows),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        chart_data(voltage),
        x="battery_id",
        y="voltage_drop_change_within_stage",
        color="life_stage",
        barmode="group",
        title="Voltage drop change within stage",
        labels=plot_labels(voltage),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_duration(data: dict[str, pd.DataFrame]) -> None:
    st.header("Discharge duration")

    duration = data["discharge_duration_summary"]
    discharge_cycles = data["discharge_cycles"]

    if duration.empty:
        st.warning("discharge_duration_summary.parquet is missing or empty.")
        return

    display_dataframe(duration)

    fig = px.bar(
        chart_data(duration),
        x="battery_id",
        y="duration_loss_percent",
        title="Discharge duration loss by battery",
        labels=plot_labels(duration),
    )
    st.plotly_chart(fig, use_container_width=True)

    if not discharge_cycles.empty:
        fig = px.scatter(
            chart_data(discharge_cycles),
            x="capacity_ah",
            y="duration_seconds",
            color="battery_id",
            title="Discharge duration vs capacity",
            labels=plot_labels(discharge_cycles),
        )
        st.plotly_chart(fig, use_container_width=True)


def show_correlations(data: dict[str, pd.DataFrame]) -> None:
    st.header("Correlations")

    correlations = data["correlation_summary"]

    if correlations.empty:
        st.warning("correlation_summary.parquet is missing or empty.")
        return

    st.markdown(
        """
        Correlations show how strongly two metrics move together.

        Values close to **+1** mean both metrics usually increase together.
        Values close to **-1** mean one metric usually increases while the other decreases.
        Values close to **0** mean there is little linear relationship.
        """
    )

    display_dataframe(correlations)

    available_scopes = correlations["battery_id"].unique().tolist()

    selected_scope = st.selectbox(
        "Correlation scope",
        options=available_scopes,
        format_func=natural_value,
    )

    selected = correlations[
        correlations["battery_id"] == selected_scope
    ].copy()

    selected["First metric"] = selected["x_metric"].map(natural_label)
    selected["Second metric"] = selected["y_metric"].map(natural_label)

    heatmap = selected.pivot_table(
        index="Second metric",
        columns="First metric",
        values="correlation_value",
        aggfunc="mean",
    )

    fig = px.imshow(
        heatmap,
        text_auto=".2f",
        aspect="auto",
        zmin=-1,
        zmax=1,
        title="Correlation heatmap",
        labels={
            "x": "First metric",
            "y": "Second metric",
            "color": "Correlation",
        },
    )

    st.plotly_chart(fig, use_container_width=True)

def show_data_quality(data: dict[str, pd.DataFrame]) -> None:
    st.header("Data quality")

    quality = data["data_quality_summary"]
    invalid = data["invalid_cycles"]
    manifest = data["dashboard_manifest"]

    if quality.empty:
        st.warning("data_quality_summary.parquet is missing or empty.")
        return

    st.subheader("Quality summary")
    display_dataframe(quality)

    fig = px.bar(
        chart_data(quality),
        x="battery_id",
        y="quality_score_percent",
        title="Data quality score by battery",
        labels=plot_labels(quality),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Invalid cycles")
    display_dataframe(invalid)

    if not manifest.empty:
        st.subheader("Dashboard manifest")
        display_dataframe(manifest)


def main() -> None:
    st.title("NASA Battery Health Dashboard")

    st.markdown(
        """
        This dashboard is based on processed NASA Li-ion Battery Aging data.
        It shows battery health, capacity degradation, SOH/EOL behavior,
        temperature behavior, voltage behavior, discharge duration, correlations,
        and data quality.
        """
    )

    data = load_data()

    tabs = st.tabs(
        [
            "Overview",
            "Degradation",
            "Life Stage",
            "Temperature",
            "Voltage",
            "Duration",
            "Correlations",
            "Data Quality",
        ]
    )

    with tabs[0]:
        show_overview(data)

    with tabs[1]:
        show_degradation(data)

    with tabs[2]:
        show_life_stage(data)

    with tabs[3]:
        show_temperature(data)

    with tabs[4]:
        show_voltage(data)

    with tabs[5]:
        show_duration(data)

    with tabs[6]:
        show_correlations(data)

    with tabs[7]:
        show_data_quality(data)


if __name__ == "__main__":
    main()
