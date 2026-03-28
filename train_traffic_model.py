import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Load buffet dataset
df = pd.read_csv("buffet_data.csv")

# Each buffet row repeats the same traffic for multiple items
# We only want one row per service scenario
traffic_df = df[
    ["day_of_week", "meal_period", "hour_block", "weather", "special_event", "expected_traffic"]
].drop_duplicates()

X = traffic_df[["day_of_week", "meal_period", "hour_block", "weather", "special_event"]]
y = traffic_df["expected_traffic"]

categorical_features = ["day_of_week", "meal_period", "weather"]
numeric_features = ["hour_block", "special_event"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

traffic_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=200, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

traffic_model.fit(X_train, y_train)
preds = traffic_model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

joblib.dump(traffic_model, "traffic_model.pkl")

print("Traffic model trained successfully.")
print(f"Traffic model MAE: {mae:.2f}")
print("Saved as traffic_model.pkl")