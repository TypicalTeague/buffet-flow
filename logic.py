import pandas as pd

from config import HIGH_DEMAND_ITEMS, ITEM_BASE_RATIOS, MEAL_MULTIPLIERS


def get_refill_action(item_name: str, prep_amount: int, expected_traffic: int,
                      predicted_taken: float, predicted_waste: float, hour_block: int) -> tuple[str, float, float, float]:
    waste_ratio = predicted_waste / prep_amount if prep_amount > 0 else 0
    take_ratio = predicted_taken / prep_amount if prep_amount > 0 else 0
    coverage_ratio = prep_amount / predicted_taken if predicted_taken > 0 else 1

    high_traffic_low_prep = expected_traffic > 300 and prep_amount < 40
    moderate_traffic_low_prep = expected_traffic > 220 and prep_amount < 30
    near_sellout = predicted_taken >= prep_amount * 0.9
    strong_demand = take_ratio >= 0.8
    moderate_demand = take_ratio >= 0.65

    if item_name in HIGH_DEMAND_ITEMS and expected_traffic > 300 and prep_amount < 50:
        action = "Increase batch now"
    elif high_traffic_low_prep:
        action = "Increase batch now"
    elif moderate_traffic_low_prep:
        action = "Full refill"
    elif near_sellout:
        action = "Full refill"
    elif item_name in HIGH_DEMAND_ITEMS and moderate_demand and hour_block != 3:
        action = "Full refill"
    elif coverage_ratio < 0.6:
        action = "Increase batch now"
    elif coverage_ratio < 0.85:
        action = "Full refill"
    elif hour_block == 3 and waste_ratio > 0.20:
        action = "Stop refill"
    elif waste_ratio > 0.20:
        action = "Half refill"
    elif strong_demand and waste_ratio < 0.18:
        action = "Full refill"
    else:
        action = "Limited refill"

    return action, waste_ratio, take_ratio, coverage_ratio


def get_recommended_start(item_name: str, meal: str, expected_traffic: int) -> int:
    meal_multiplier = MEAL_MULTIPLIERS[meal]
    item_base_ratio = ITEM_BASE_RATIOS[item_name]
    return round(expected_traffic * item_base_ratio * meal_multiplier)


def get_risk_level(predicted_waste: float, coverage_ratio: float) -> str:
    if predicted_waste > 20 or coverage_ratio < 0.7:
        return "High"
    if predicted_waste > 10 or coverage_ratio < 0.9:
        return "Medium"
    return "Low"


def build_results_df(items: dict, *, day: str, meal: str, hour_block: int, weather: str,
                     special_event: int, expected_traffic: int, taken_model, waste_model,
                     predict_item_func) -> pd.DataFrame:
    results = []

    for item_name, prep_amount in items.items():
        predicted_taken, predicted_waste = predict_item_func(
            taken_model,
            waste_model,
            day=day,
            meal=meal,
            hour_block=hour_block,
            weather=weather,
            special_event=special_event,
            expected_traffic=expected_traffic,
            item_name=item_name,
            prep_amount=prep_amount,
        )

        refill_action, waste_ratio, _, coverage_ratio = get_refill_action(
            item_name=item_name,
            prep_amount=prep_amount,
            expected_traffic=expected_traffic,
            predicted_taken=predicted_taken,
            predicted_waste=predicted_waste,
            hour_block=hour_block,
        )

        recommended_start = get_recommended_start(item_name, meal, expected_traffic)
        risk_level = get_risk_level(predicted_waste, coverage_ratio)

        results.append({
            "Item": item_name.title(),
            "Prep Amount": prep_amount,
            "Recommended Start": recommended_start,
            "Predicted Taken": round(predicted_taken, 1),
            "Predicted Waste": round(predicted_waste, 1),
            "Waste Ratio": round(waste_ratio, 2),
            "Coverage Ratio": round(coverage_ratio, 2),
            "Risk Level": risk_level,
            "Refill Action": refill_action,
        })

    return pd.DataFrame(results)


def summarize_results(results_df: pd.DataFrame) -> dict:
    high_risk_items = results_df[results_df["Risk Level"] == "High"]["Item"].tolist()
    priority_refill_items = results_df[
        results_df["Refill Action"].isin(["Increase batch now", "Full refill"])
    ]["Item"].tolist()

    total_predicted_waste = results_df["Predicted Waste"].sum()
    optimized_waste = total_predicted_waste * 0.8
    waste_reduction = total_predicted_waste - optimized_waste
    estimated_cost_savings = waste_reduction * 0.75
    estimated_co2_saved = waste_reduction * 2.5

    return {
        "high_risk_items": high_risk_items,
        "priority_refill_items": priority_refill_items,
        "total_predicted_waste": total_predicted_waste,
        "optimized_waste": optimized_waste,
        "waste_reduction": waste_reduction,
        "estimated_cost_savings": estimated_cost_savings,
        "estimated_co2_saved": estimated_co2_saved,
    }