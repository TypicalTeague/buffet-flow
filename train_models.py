import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Load dataset
df = pd.read_csv("buffet_data.csv")

# Features to use
features = [
    "day_of_week",
    "meal_period",
    "hour_block",
    "weather",
    "special_event",
    "expected_traffic",
    "item_name",
    "prep_amount"
]

X = df[features]
y_taken = df["amount_taken"]
y_waste = df["waste_total"]

# Separate categorical and numeric columns
categorical_features = ["day_of_week", "meal_period", "weather", "item_name"]
numeric_features = ["hour_block", "special_event", "expected_traffic", "prep_amount"]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

# Model for amount_taken
taken_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=200, random_state=42))
])

# Model for waste_total
waste_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=200, random_state=42))
])

# Train/test split for amount_taken
X_train, X_test, y_train, y_test = train_test_split(X, y_taken, test_size=0.2, random_state=42)
taken_model.fit(X_train, y_train)
taken_preds = taken_model.predict(X_test)
taken_mae = mean_absolute_error(y_test, taken_preds)

# Train/test split for waste_total
X_train, X_test, y_train, y_test = train_test_split(X, y_waste, test_size=0.2, random_state=42)
waste_model.fit(X_train, y_train)
waste_preds = waste_model.predict(X_test)
waste_mae = mean_absolute_error(y_test, waste_preds)

# Save models
joblib.dump(taken_model, "taken_model.pkl")
joblib.dump(waste_model, "waste_model.pkl")

print("Models trained successfully.")
print(f"Taken model MAE: {taken_mae:.2f}")
print(f"Waste model MAE: {waste_mae:.2f}")
print("Saved as taken_model.pkl and waste_model.pkl")