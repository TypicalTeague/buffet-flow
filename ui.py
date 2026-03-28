import streamlit as st

from config import (
    ITEM_DEFAULTS,
    ITEM_SELECT_OPTIONS,
    MEALS,
    SCENARIO_PRESETS,
    SERVICE_WINDOWS,
    WEATHER_OPTIONS,
    WEEKDAYS,
)


def render_header():
    st.title("BuffetFlow")
    st.subheader("Smarter buffet refill decisions, less food waste")
    st.info(
        "BuffetFlow supports pre-service planning and live refill decisions "
        "to reduce buffet waste before it happens."
    )


def render_top_summary(day, meal, service_window, weather, special_event, predicted_traffic, expected_traffic):
    st.markdown(
        f"**Scenario:** {day} | {meal.title()} | {service_window} | "
        f"Weather: {weather.title()} | Event: {'Yes' if special_event == 1 else 'No'}"
    )
    st.markdown(
        f"**Predicted Traffic:** {predicted_traffic} | "
        f"**Traffic Used by System:** {expected_traffic}"
    )
    st.markdown("Use the controls on the left to simulate a buffet dining scenario.")


def render_operational_summary(summary: dict):
    summary_parts = []

    if summary["high_risk_items"]:
        summary_parts.append("High risk: " + ", ".join(summary["high_risk_items"]))
    if summary["priority_refill_items"]:
        summary_parts.append("Priority refill: " + ", ".join(summary["priority_refill_items"]))

    if summary_parts:
        st.warning(" | ".join(summary_parts))
    else:
        st.success("No high-risk items detected in this scenario.")


def render_metrics(summary: dict):
    st.markdown("## Overview")
    st.caption("Projected impact for the selected buffet scenario.")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Predicted Total Waste", f"{summary['total_predicted_waste']:.1f}")
    col2.metric("Estimated Waste After Optimization", f"{summary['optimized_waste']:.1f}")
    col3.metric("Estimated Waste Reduction", f"{summary['waste_reduction']:.1f}")
    col4.metric("Estimated Cost Savings", f"${summary['estimated_cost_savings']:.2f}")
    col5.metric("Estimated CO2 Avoided", f"{summary['estimated_co2_saved']:.1f} lbs")


def render_tables(results_df):
    st.markdown("## Pre-Service Plan")
    st.caption("Recommended starting batch sizes before service begins.")
    pre_service_df = results_df[["Item", "Recommended Start", "Risk Level"]].sort_values(
        "Recommended Start", ascending=False
    )
    st.dataframe(pre_service_df, use_container_width=True)

    st.markdown("## Live Refill Guidance")
    st.caption("Operational actions to take during service based on predicted demand and waste.")
    live_df = results_df[
        ["Item", "Prep Amount", "Predicted Taken", "Predicted Waste", "Coverage Ratio", "Refill Action"]
    ].sort_values("Predicted Waste", ascending=False)
    st.dataframe(live_df, use_container_width=True)

    st.markdown("## Highest Waste-Risk Items")
    st.caption("Items most likely to contribute to avoidable waste in this service window.")
    waste_chart = results_df.set_index("Item")["Predicted Waste"]
    st.bar_chart(waste_chart)


def render_sidebar(live_now, time_source_default="Live Clock", weather_source_default="Live Weather"):
    st.sidebar.header("Dining Scenario")

    if st.sidebar.button("Refresh Live Data"):
        st.rerun()

    time_source = st.sidebar.radio("Time Source", ["Live Clock", "Manual"], index=0 if time_source_default == "Live Clock" else 1)
    weather_source = st.sidebar.radio("Weather Source", ["Live Weather", "Manual"], index=0 if weather_source_default == "Live Weather" else 1)
    input_mode = st.sidebar.radio("Prep Input Mode", ["Quick Demo", "Manual Input"])
    traffic_mode = st.sidebar.radio("Traffic Source", ["Predicted", "Manual Override"])
    scenario_preset = st.sidebar.selectbox("Scenario Preset", SCENARIO_PRESETS)

    st.markdown(
        f"**Live Local Time:** {live_now.strftime('%Y-%m-%d %I:%M %p')} | "
        f"**Time Source:** {time_source} | **Weather Source:** {weather_source}"
    )

    return time_source, weather_source, input_mode, traffic_mode, scenario_preset


def render_manual_time_inputs():
    day = st.sidebar.selectbox("Day of Week", WEEKDAYS)
    meal = st.sidebar.selectbox("Meal Period", MEALS)
    hour_block = st.sidebar.selectbox("Hour Block", [1, 2, 3])
    service_window = SERVICE_WINDOWS[hour_block]
    return day, meal, hour_block, service_window


def render_manual_weather_input():
    return st.sidebar.selectbox("Weather", WEATHER_OPTIONS)


def render_special_event_input():
    return st.sidebar.selectbox("Special Event", [0, 1])


def render_item_inputs(input_mode: str) -> dict:
    st.sidebar.markdown("### Prep Amounts by Item")

    if input_mode == "Quick Demo":
        return {
            item: st.sidebar.selectbox(
                f"{item.title()} Prep Amount",
                ITEM_SELECT_OPTIONS[item],
                index=3
            )
            for item in ITEM_SELECT_OPTIONS
        }

    return {
        item: st.sidebar.number_input(
            f"{item.title()} Prep Amount",
            min_value=0,
            max_value=500,
            value=ITEM_DEFAULTS[item],
            step=5,
        )
        for item in ITEM_DEFAULTS
    }