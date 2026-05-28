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

    st.dataframe(battery_health_display, use_container_width=True)

    fig = px.bar(
        battery_health,
        x="battery_id",
        y="final_soh",
        text="health_rank",
        title="Final SOH by battery",
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

        st.dataframe(soh_eol_display, use_container_width=True)
        

def show_degradation(data: dict[str, pd.DataFrame]) -> None:
    st.header("Capacity degradation")

    degradation = data["degradation_summary"]
    rolling = data["rolling_degradation_summary"]

    if degradation.empty:
        st.warning("degradation_summary.parquet is missing or empty.")
        return

    st.subheader("Battery-level degradation summary")
    st.dataframe(degradation, use_container_width=True)

    fig = px.bar(
        degradation,
        x="battery_id",
        y="relative_capacity_drop_percent",
        title="Relative capacity drop by battery",
    )
    st.plotly_chart(fig, use_container_width=True)

    if not rolling.empty:
        st.subheader("Rolling capacity trend")

        fig = px.line(
            rolling,
            x="discharge_cycle_number",
            y="rolling_capacity_5",
            color="battery_id",
            title="Rolling capacity average over discharge cycles",
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = px.line(
            rolling,
            x="discharge_cycle_number",
            y="rolling_soh_5",
            color="battery_id",
            title="Rolling SOH average over discharge cycles",
        )
        st.plotly_chart(fig, use_container_width=True)


def show_life_stage(data: dict[str, pd.DataFrame]) -> None:
    st.header("Life stage comparison")

    life_stage = data["life_stage_summary"]

    if life_stage.empty:
        st.warning("life_stage_summary.parquet is missing or empty.")
        return

    st.dataframe(life_stage, use_container_width=True)

    fig = px.bar(
        life_stage,
        x="battery_id",
        y="avg_capacity_ah",
        color="life_stage",
        barmode="group",
        title="Average capacity by life stage",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        life_stage,
        x="battery_id",
        y="avg_soh_percent",
        color="life_stage",
        barmode="group",
        title="Average SOH by life stage",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_temperature(data: dict[str, pd.DataFrame]) -> None:
    st.header("Temperature behavior")

    temperature = data["temperature_summary"]

    if temperature.empty:
        st.warning("temperature_summary.parquet is missing or empty.")
        return

    st.dataframe(temperature, use_container_width=True)

    stage_rows = temperature[temperature["life_stage"] != "all"]

    fig = px.bar(
        stage_rows,
        x="battery_id",
        y="avg_working_temperature",
        color="life_stage",
        barmode="group",
        title="Average working temperature by life stage",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        stage_rows,
        x="battery_id",
        y="avg_temperature_delta_to_ambient",
        color="life_stage",
        barmode="group",
        title="Average temperature delta to ambient by life stage",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        temperature,
        x="battery_id",
        y="temperature_change_within_stage",
        color="life_stage",
        barmode="group",
        title="Temperature change within stage",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_voltage(data: dict[str, pd.DataFrame]) -> None:
    st.header("Voltage behavior")

    voltage = data["voltage_summary"]

    if voltage.empty:
        st.warning("voltage_summary.parquet is missing or empty.")
        return

    st.dataframe(voltage, use_container_width=True)

    stage_rows = voltage[voltage["life_stage"] != "all"]

    fig = px.bar(
        stage_rows,
        x="battery_id",
        y="avg_voltage_drop",
        color="life_stage",
        barmode="group",
        title="Average voltage drop by life stage",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        voltage,
        x="battery_id",
        y="voltage_drop_change_within_stage",
        color="life_stage",
        barmode="group",
        title="Voltage drop change within stage",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_duration(data: dict[str, pd.DataFrame]) -> None:
    st.header("Discharge duration")

    duration = data["discharge_duration_summary"]
    discharge_cycles = data["discharge_cycles"]

    if duration.empty:
        st.warning("discharge_duration_summary.parquet is missing or empty.")
        return

    st.dataframe(duration, use_container_width=True)

    fig = px.bar(
        duration,
        x="battery_id",
        y="duration_loss_percent",
        title="Discharge duration loss by battery",
    )
    st.plotly_chart(fig, use_container_width=True)

    if not discharge_cycles.empty:
        fig = px.scatter(
            discharge_cycles,
            x="capacity_ah",
            y="duration_seconds",
            color="battery_id",
            title="Discharge duration vs capacity",
        )
        st.plotly_chart(fig, use_container_width=True)


def show_correlations(data: dict[str, pd.DataFrame]) -> None:
    st.header("Correlations")

    correlations = data["correlation_summary"]

    if correlations.empty:
        st.warning("correlation_summary.parquet is missing or empty.")
        return

    st.dataframe(correlations, use_container_width=True)

    all_batteries = correlations[
        correlations["scope"] == "all_batteries"
    ].copy()

    all_batteries["metric_pair"] = (
        all_batteries["x_metric"] + " vs " + all_batteries["y_metric"]
    )

    fig = px.bar(
        all_batteries,
        x="metric_pair",
        y="correlation_value",
        title="Correlation values across all batteries",
    )
    fig.update_layout(xaxis_tickangle=-45)
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
    st.dataframe(quality, use_container_width=True)

    fig = px.bar(
        quality,
        x="battery_id",
        y="quality_score_percent",
        title="Data quality score by battery",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Invalid cycles")
    st.dataframe(invalid, use_container_width=True)

    if not manifest.empty:
        st.subheader("Dashboard manifest")
        st.dataframe(manifest, use_container_width=True)


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