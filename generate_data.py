import pandas as pd
import numpy as np

np.random.seed(42)

items = ["chicken", "rice", "pasta", "vegetables", "dessert"]
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
meal_periods = ["breakfast", "lunch", "dinner"]
weather_options = ["sunny", "rainy", "cloudy"]

rows = []

for week in range(4):
    for day in days:
        for meal in meal_periods:
            for hour_block in [1, 2, 3]:
                special_event = np.random.choice([0, 1], p=[0.85, 0.15])
                weather = np.random.choice(weather_options, p=[0.5, 0.2, 0.3])

                base_traffic = {
                    "breakfast": 120,
                    "lunch": 260,
                    "dinner": 220
                }[meal]

                if day in ["Mon", "Tue", "Wed", "Thu"]:
                    base_traffic += 20

                if weather == "rainy":
                    base_traffic -= 15

                if special_event == 1:
                    base_traffic += 40

                expected_traffic = max(80, int(np.random.normal(base_traffic, 20)))

                for item in items:
                    popularity = {
                        "chicken": 1.15,
                        "rice": 1.00,
                        "pasta": 1.10,
                        "vegetables": 0.75,
                        "dessert": 0.85
                    }[item]

                    waste_bias = {
                        "chicken": 0.08,
                        "rice": 0.18,
                        "pasta": 0.12,
                        "vegetables": 0.15,
                        "dessert": 0.10
                    }[item]

                    prep_amount = max(20, int(expected_traffic * popularity * np.random.uniform(0.25, 0.4)))
                    amount_taken = max(10, int(prep_amount * np.random.uniform(0.65, 0.98)))
                    plate_waste = max(0, int(amount_taken * np.random.uniform(waste_bias * 0.7, waste_bias * 1.3)))
                    amount_left_in_pan = max(0, prep_amount - amount_taken - np.random.randint(0, 8))

                    rows.append({
                        "week": week + 1,
                        "day_of_week": day,
                        "meal_period": meal,
                        "hour_block": hour_block,
                        "weather": weather,
                        "special_event": special_event,
                        "expected_traffic": expected_traffic,
                        "item_name": item,
                        "prep_amount": prep_amount,
                        "amount_taken": amount_taken,
                        "amount_left_in_pan": amount_left_in_pan,
                        "plate_waste": plate_waste
                    })

df = pd.DataFrame(rows)

df["consumed"] = df["amount_taken"] - df["plate_waste"]
df["waste_total"] = df["amount_left_in_pan"] + df["plate_waste"]
df["take_rate"] = df["amount_taken"] / df["prep_amount"]
df["waste_rate"] = df["waste_total"] / df["prep_amount"]

df.to_csv("buffet_data.csv", index=False)

print("Dataset created successfully.")
print(df.head())
print("\nShape:", df.shape)
print("\nSummary by item:")
print(df.groupby("item_name")[["prep_amount", "amount_taken", "waste_total"]].mean().round(2))