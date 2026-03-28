import streamlit as st

from config import SERVICE_WINDOWS
from live_data import get_live_time, get_live_weather, derive_meal_period_and_window
from logic import build_results_df, summarize_results
from models import load_models, predict_item, predict_traffic
from ui import (
    render_header,
    render_item_inputs,
    render_manual_time_inputs,
    render_manual_weather_input,
    render_metrics,
    render_operational_summary,
    render_sidebar,
    render_special_event_input,
    render_tables,
    render_top_summary,
)

st.set_page_config(page_title="BuffetFlow", layout="wide")


def apply_scenario_preset(scenario_preset, meal, hour_block, weather, special_event):
    if scenario_preset == "Normal Lunch":
        meal = "lunch"
        hour_block = 2
        weather = "sunny"
        special_event = 0
    elif scenario_preset == "Peak Lunch Rush":
        meal = "lunch"
        hour_block = 2
        weather = "sunny"
        special_event = 1
    elif scenario_preset == "Rainy Slow Period":
        meal = "lunch"
        hour_block = 1
        weather = "rainy"
        special_event = 0
    elif scenario_preset == "Closing Time":
        meal = "dinner"
        hour_block = 3
        weather = "cloudy"
        special_event = 0

    service_window = SERVICE_WINDOWS[hour_block]
    return meal, hour_block, weather, special_event, service_window


def main():
    taken_model, waste_model, traffic_model = load_models()
    render_header()

    live_now = get_live_time("America/New_York")
    time_source, weather_source, input_mode, traffic_mode, scenario_preset = render_sidebar(live_now)

    if time_source == "Live Clock":
        day = live_now.strftime("%a")
        meal, hour_block, service_window = derive_meal_period_and_window(live_now.hour)
        st.sidebar.markdown(f"**Live Day:** {day}")
        st.sidebar.markdown(f"**Live Time:** {live_now.strftime('%I:%M %p')}")
        st.sidebar.markdown(f"**Detected Meal Period:** {meal.title()}")
        st.sidebar.markdown(f"**Detected Hour Block:** {hour_block}")
    else:
        day, meal, hour_block, service_window = render_manual_time_inputs()

    if weather_source == "Live Weather":
        live_weather = get_live_weather()
        weather = live_weather["weather_label"]
        st.sidebar.markdown(f"**Detected Weather:** {weather.title()}")

        if live_weather["temperature"] is not None:
            st.sidebar.markdown(f"**Temperature:** {live_weather['temperature']}°C")

        if not live_weather["success"]:
            st.sidebar.warning("Live weather unavailable. Using fallback weather label.")
    else:
        weather = render_manual_weather_input()

    special_event = render_special_event_input()

    meal, hour_block, weather, special_event, service_window = apply_scenario_preset(
        scenario_preset, meal, hour_block, weather, special_event
    )

    predicted_traffic = predict_traffic(
        traffic_model,
        day=day,
        meal=meal,
        hour_block=hour_block,
        weather=weather,
        special_event=special_event,
    )

    manual_traffic = None
    if traffic_mode == "Manual Override":
        manual_traffic = st.sidebar.number_input(
            "Manual Traffic Override",
            min_value=0,
            max_value=1000,
            value=220,
            step=5,
        )

    expected_traffic = manual_traffic if traffic_mode == "Manual Override" else predicted_traffic
    items = render_item_inputs(input_mode)

    render_top_summary(
        day=day,
        meal=meal,
        service_window=service_window,
        weather=weather,
        special_event=special_event,
        predicted_traffic=predicted_traffic,
        expected_traffic=expected_traffic,
    )

    results_df = build_results_df(
        items,
        day=day,
        meal=meal,
        hour_block=hour_block,
        weather=weather,
        special_event=special_event,
        expected_traffic=expected_traffic,
        taken_model=taken_model,
        waste_model=waste_model,
        predict_item_func=predict_item,
    )

    summary = summarize_results(results_df)
    render_operational_summary(summary)
    render_metrics(summary)
    render_tables(results_df)


if __name__ == "__main__":
    main()