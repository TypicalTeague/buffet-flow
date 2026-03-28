import joblib
import pandas as pd


def load_models() -> tuple:
    taken_model = joblib.load("taken_model.pkl")
    waste_model = joblib.load("waste_model.pkl")
    traffic_model = joblib.load("traffic_model.pkl")
    return taken_model, waste_model, traffic_model


def predict_traffic(traffic_model, day: str, meal: str, hour_block: int, weather: str, special_event: int) -> int:
    traffic_input = pd.DataFrame([{
        "day_of_week": day,
        "meal_period": meal,
        "hour_block": hour_block,
        "weather": weather,
        "special_event": special_event,
    }])
    return round(float(traffic_model.predict(traffic_input)[0]))


def predict_item(taken_model, waste_model, *, day: str, meal: str, hour_block: int,
                 weather: str, special_event: int, expected_traffic: int,
                 item_name: str, prep_amount: int) -> tuple[float, float]:
    input_row = pd.DataFrame([{
        "day_of_week": day,
        "meal_period": meal,
        "hour_block": hour_block,
        "weather": weather,
        "special_event": special_event,
        "expected_traffic": expected_traffic,
        "item_name": item_name,
        "prep_amount": prep_amount,
    }])

    predicted_taken = float(taken_model.predict(input_row)[0])
    predicted_waste = float(waste_model.predict(input_row)[0])
    return predicted_taken, predicted_waste