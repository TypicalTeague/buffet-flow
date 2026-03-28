SERVICE_WINDOWS = {
    1: "Opening Window",
    2: "Peak Service",
    3: "Closing Window",
}

SCENARIO_PRESETS = [
    "Custom",
    "Normal Lunch",
    "Peak Lunch Rush",
    "Rainy Slow Period",
    "Closing Time",
]

HIGH_DEMAND_ITEMS = ["chicken", "pasta"]

ITEM_SELECT_OPTIONS = {
    "chicken": [40, 60, 80, 100, 120, 150],
    "rice": [30, 50, 70, 90, 110, 130],
    "pasta": [30, 50, 70, 95, 120, 140],
    "vegetables": [20, 40, 60, 70, 90, 110],
    "dessert": [20, 40, 50, 60, 80, 100],
}

ITEM_DEFAULTS = {
    "chicken": 100,
    "rice": 90,
    "pasta": 95,
    "vegetables": 70,
    "dessert": 60,
}

MEAL_MULTIPLIERS = {
    "breakfast": 0.8,
    "lunch": 1.0,
    "dinner": 0.9,
}

ITEM_BASE_RATIOS = {
    "chicken": 0.28,
    "rice": 0.24,
    "pasta": 0.26,
    "vegetables": 0.18,
    "dessert": 0.16,
}

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
MEALS = ["breakfast", "lunch", "dinner"]
WEATHER_OPTIONS = ["sunny", "cloudy", "rainy"]