import streamlit as st
import pandas as pd
import joblib
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

def get_live_time(timezone_name="America/New_York"):
    now = datetime.now(ZoneInfo(timezone_name))
    return now


def get_live_weather(latitude=33.7537, longitude=-84.3863):
    # Atlanta coordinates by default
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,precipitation,weather_code,cloud_cover"
        "&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["current"]

        weather_code = data.get("weather_code", 0)
        precipitation = data.get("precipitation", 0)
        cloud_cover = data.get("cloud_cover", 0)

        # Simple mapping into your model's categories
        if precipitation and precipitation > 0:
            weather_label = "rainy"
        elif cloud_cover is not None and cloud_cover >= 60:
            weather_label = "cloudy"
        else:
            weather_label = "sunny"

        return {
            "weather_label": weather_label,
            "temperature": data.get("temperature_2m"),
            "precipitation": precipitation,
            "cloud_cover": cloud_cover,
            "weather_code": weather_code,
            "success": True
        }
    except Exception:
        return {
            "weather_label": "sunny",
            "temperature": None,
            "precipitation": None,
            "cloud_cover": None,
            "weather_code": None,
            "success": False
        }


def derive_meal_period_and_window(current_hour):
    if 7 <= current_hour <= 10:
        return "breakfast", 1, "Opening Window"
    elif 11 <= current_hour <= 14:
        if current_hour <= 12:
            return "lunch", 1, "Opening Window"
        elif current_hour == 13:
            return "lunch", 2, "Peak Service"
        else:
            return "lunch", 3, "Closing Window"
    elif 17 <= current_hour <= 20:
        if current_hour <= 18:
            return "dinner", 1, "Opening Window"
        elif current_hour == 19:
            return "dinner", 2, "Peak Service"
        else:
            return "dinner", 3, "Closing Window"
    else:
        return "lunch", 2, "Peak Service"

st.set_page_config(page_title="BuffetFlow", layout="wide")

# Load trained models
taken_model = joblib.load("taken_model.pkl")
waste_model = joblib.load("waste_model.pkl")
traffic_model = joblib.load("traffic_model.pkl")

st.title("BuffetFlow")
st.subheader("Smarter buffet refill decisions, less food waste")
st.info(
    "BuffetFlow supports pre-service planning and live refill decisions "
    "to reduce buffet waste before it happens."
)

# Sidebar inputs
st.sidebar.header("Dining Scenario")

if st.sidebar.button("Refresh Live Data"):
    st.rerun()
time_source = st.sidebar.radio(
    "Time Source",
    ["Live Clock", "Manual"]
)

weather_source = st.sidebar.radio(
    "Weather Source",
    ["Live Weather", "Manual"]
)

input_mode = st.sidebar.radio(
    "Prep Input Mode",
    ["Quick Demo", "Manual Input"]
)

traffic_mode = st.sidebar.radio(
    "Traffic Source",
    ["Predicted", "Manual Override"]
)

scenario_preset = st.sidebar.selectbox(
    "Scenario Preset",
    ["Custom", "Normal Lunch", "Peak Lunch Rush", "Rainy Slow Period", "Closing Time"]
)

live_now = get_live_time("America/New_York")

st.markdown(
    f"**Live Local Time:** {live_now.strftime('%Y-%m-%d %I:%M %p')} | "
    f"**Time Source:** {time_source} | **Weather Source:** {weather_source}"
)

if time_source == "Live Clock":
    day = live_now.strftime("%a")
    meal, hour_block, service_window = derive_meal_period_and_window(live_now.hour)

    st.sidebar.markdown(f"**Live Day:** {day}")
    st.sidebar.markdown(f"**Live Time:** {live_now.strftime('%I:%M %p')}")
    st.sidebar.markdown(f"**Detected Meal Period:** {meal.title()}")
    st.sidebar.markdown(f"**Detected Hour Block:** {hour_block}")
else:
    day = st.sidebar.selectbox("Day of Week", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    meal = st.sidebar.selectbox("Meal Period", ["breakfast", "lunch", "dinner"])
    hour_block = st.sidebar.selectbox("Hour Block", [1, 2, 3])

    service_window = {
        1: "Opening Window",
        2: "Peak Service",
        3: "Closing Window"
    }[hour_block]

if weather_source == "Live Weather":
    live_weather = get_live_weather()
    weather = live_weather["weather_label"]

    st.sidebar.markdown(f"**Detected Weather:** {weather.title()}")

    if live_weather["temperature"] is not None:
        st.sidebar.markdown(f"**Temperature:** {live_weather['temperature']}°C")

    if not live_weather["success"]:
        st.sidebar.warning("Live weather unavailable. Using fallback weather label.")
else:
    weather = st.sidebar.selectbox("Weather", ["sunny", "cloudy", "rainy"])

special_event = st.sidebar.selectbox("Special Event", [0, 1])

# Apply presets
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
service_window = {
    1: "Opening Window",
    2: "Peak Service",
    3: "Closing Window"
}[hour_block]
service_window = {
    1: "Opening Window",
    2: "Peak Service",
    3: "Closing Window"
}[hour_block]

# Predict traffic from context
traffic_input = pd.DataFrame([{
    "day_of_week": day,
    "meal_period": meal,
    "hour_block": hour_block,
    "weather": weather,
    "special_event": special_event
}])

predicted_traffic = round(float(traffic_model.predict(traffic_input)[0]))

manual_traffic = None
if traffic_mode == "Manual Override":
    manual_traffic = st.sidebar.number_input(
        "Manual Traffic Override",
        min_value=0,
        max_value=1000,
        value=220,
        step=5
    )

expected_traffic = manual_traffic if traffic_mode == "Manual Override" else predicted_traffic

st.sidebar.markdown("### Prep Amounts by Item")

if input_mode == "Quick Demo":
    items = {
        "chicken": st.sidebar.selectbox("Chicken Prep Amount", [40, 60, 80, 100, 120, 150], index=3),
        "rice": st.sidebar.selectbox("Rice Prep Amount", [30, 50, 70, 90, 110, 130], index=3),
        "pasta": st.sidebar.selectbox("Pasta Prep Amount", [30, 50, 70, 95, 120, 140], index=3),
        "vegetables": st.sidebar.selectbox("Vegetables Prep Amount", [20, 40, 60, 70, 90, 110], index=3),
        "dessert": st.sidebar.selectbox("Dessert Prep Amount", [20, 40, 50, 60, 80, 100], index=3),
    }
else:
    items = {
        "chicken": st.sidebar.number_input("Chicken Prep Amount", min_value=0, max_value=500, value=100, step=5),
        "rice": st.sidebar.number_input("Rice Prep Amount", min_value=0, max_value=500, value=90, step=5),
        "pasta": st.sidebar.number_input("Pasta Prep Amount", min_value=0, max_value=500, value=95, step=5),
        "vegetables": st.sidebar.number_input("Vegetables Prep Amount", min_value=0, max_value=500, value=70, step=5),
        "dessert": st.sidebar.number_input("Dessert Prep Amount", min_value=0, max_value=500, value=60, step=5),
    }

# Top-of-page scenario summary
st.markdown(
    f"**Scenario:** {day} | {meal.title()} | {service_window} | "
    f"Weather: {weather.title()} | Event: {'Yes' if special_event == 1 else 'No'}"
)
st.markdown(
    f"**Predicted Traffic:** {predicted_traffic} | "
    f"**Traffic Used by System:** {expected_traffic}"
)
st.markdown("Use the controls on the left to simulate a buffet dining scenario.")

results = []

for item_name, prep_amount in items.items():
    input_row = pd.DataFrame([{
        "day_of_week": day,
        "meal_period": meal,
        "hour_block": hour_block,
        "weather": weather,
        "special_event": special_event,
        "expected_traffic": expected_traffic,
        "item_name": item_name,
        "prep_amount": prep_amount
    }])

    predicted_taken = float(taken_model.predict(input_row)[0])
    predicted_waste = float(waste_model.predict(input_row)[0])

    waste_ratio = predicted_waste / prep_amount if prep_amount > 0 else 0
    take_ratio = predicted_taken / prep_amount if prep_amount > 0 else 0
    coverage_ratio = prep_amount / predicted_taken if predicted_taken > 0 else 1

    high_demand_items = ["chicken", "pasta"]

    high_traffic_low_prep = expected_traffic > 300 and prep_amount < 40
    moderate_traffic_low_prep = expected_traffic > 220 and prep_amount < 30
    near_sellout = predicted_taken >= prep_amount * 0.9
    strong_demand = take_ratio >= 0.8
    moderate_demand = take_ratio >= 0.65

    if item_name in high_demand_items and expected_traffic > 300 and prep_amount < 50:
        refill_action = "Increase batch now"
    elif high_traffic_low_prep:
        refill_action = "Increase batch now"
    elif moderate_traffic_low_prep:
        refill_action = "Full refill"
    elif near_sellout:
        refill_action = "Full refill"
    elif item_name in high_demand_items and moderate_demand and hour_block != 3:
        refill_action = "Full refill"
    elif coverage_ratio < 0.6:
        refill_action = "Increase batch now"
    elif coverage_ratio < 0.85:
        refill_action = "Full refill"
    elif hour_block == 3 and waste_ratio > 0.20:
        refill_action = "Stop refill"
    elif waste_ratio > 0.20:
        refill_action = "Half refill"
    elif strong_demand and waste_ratio < 0.18:
        refill_action = "Full refill"
    else:
        refill_action = "Limited refill"

    meal_multiplier = {
        "breakfast": 0.8,
        "lunch": 1.0,
        "dinner": 0.9
    }[meal]

    item_base_ratio = {
        "chicken": 0.28,
        "rice": 0.24,
        "pasta": 0.26,
        "vegetables": 0.18,
        "dessert": 0.16
    }[item_name]

    recommended_start = round(expected_traffic * item_base_ratio * meal_multiplier)

    if predicted_waste > 20 or coverage_ratio < 0.7:
        risk_level = "High"
    elif predicted_waste > 10 or coverage_ratio < 0.9:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    results.append({
        "Item": item_name.title(),
        "Prep Amount": prep_amount,
        "Recommended Start": recommended_start,
        "Predicted Taken": round(predicted_taken, 1),
        "Predicted Waste": round(predicted_waste, 1),
        "Waste Ratio": round(waste_ratio, 2),
        "Coverage Ratio": round(coverage_ratio, 2),
        "Risk Level": risk_level,
        "Refill Action": refill_action
    })

results_df = pd.DataFrame(results)

# Operational summary
high_risk_items = results_df[results_df["Risk Level"] == "High"]["Item"].tolist()
priority_refill_items = results_df[
    results_df["Refill Action"].isin(["Increase batch now", "Full refill"])
]["Item"].tolist()

summary_parts = []
if high_risk_items:
    summary_parts.append("High risk: " + ", ".join(high_risk_items))
if priority_refill_items:
    summary_parts.append("Priority refill: " + ", ".join(priority_refill_items))

if summary_parts:
    st.warning(" | ".join(summary_parts))
else:
    st.success("No high-risk items detected in this scenario.")

# Dashboard metrics
total_predicted_waste = results_df["Predicted Waste"].sum()
optimized_waste = total_predicted_waste * 0.8
waste_reduction = total_predicted_waste - optimized_waste
estimated_cost_savings = waste_reduction * 0.75
estimated_co2_saved = waste_reduction * 2.5

st.markdown("## Overview")
st.caption("Projected impact for the selected buffet scenario.")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Predicted Total Waste", f"{total_predicted_waste:.1f}")
col2.metric("Estimated Waste After Optimization", f"{optimized_waste:.1f}")
col3.metric("Estimated Waste Reduction", f"{waste_reduction:.1f}")
col4.metric("Estimated Cost Savings", f"${estimated_cost_savings:.2f}")
col5.metric("Estimated CO2 Avoided", f"{estimated_co2_saved:.1f} lbs")

st.markdown("## Pre-Service Plan")
st.caption("Recommended starting batch sizes before service begins.")
pre_service_df = results_df[["Item", "Recommended Start", "Risk Level"]].sort_values(
    "Recommended Start", ascending=False
)
st.dataframe(pre_service_df, use_container_width=True)

st.markdown("## Live Refill Guidance")
st.caption("Operational actions to take during service based on predicted demand and waste.")
live_df = results_df[[
    "Item",
    "Prep Amount",
    "Predicted Taken",
    "Predicted Waste",
    "Coverage Ratio",
    "Refill Action"
]].sort_values("Predicted Waste", ascending=False)
st.dataframe(live_df, use_container_width=True)

st.markdown("## Highest Waste-Risk Items")
st.caption("Items most likely to contribute to avoidable waste in this service window.")
waste_chart = results_df.set_index("Item")["Predicted Waste"]
st.bar_chart(waste_chart)