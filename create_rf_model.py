#!/usr/bin/env python3
"""
Train and save the RandomForest model for use in run.sh
"""

import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame with extensive feature engineering
rows = []
for case in data:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    # Basic features
    row = {
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'output': output
    }
    
    # Derived features
    row['miles_per_day'] = miles / days if days > 0 else miles
    row['receipts_per_day'] = receipts / days if days > 0 else receipts
    row['total_input'] = days + miles + receipts
    
    # Categorical features
    row['is_1_day'] = int(days == 1)
    row['is_2_day'] = int(days == 2)
    row['is_3_day'] = int(days == 3)
    row['is_4_day'] = int(days == 4)
    row['is_5_day'] = int(days == 5)
    row['is_weekend'] = int(days in [2, 3])
    
    # Receipt features
    row['log_receipts'] = np.log1p(receipts)
    row['sqrt_receipts'] = np.sqrt(receipts)
    row['receipts_squared'] = receipts ** 2
    row['receipts_cubed'] = receipts ** 3
    
    # Rounding features
    receipt_str = f"{receipts:.2f}"
    row['ends_49'] = int(receipt_str.endswith('49'))
    row['ends_99'] = int(receipt_str.endswith('99'))
    row['ends_00'] = int(receipt_str.endswith('00'))
    row['last_digit'] = int(receipt_str[-1])
    row['second_last_digit'] = int(receipt_str[-2])
    
    # Mileage tiers
    row['tier1_miles'] = min(miles, 100)
    row['tier2_miles'] = max(0, min(miles - 100, 300))
    row['tier3_miles'] = max(0, miles - 400)
    
    # Efficiency features
    mpd = row['miles_per_day']
    row['efficiency_bonus'] = int(180 <= mpd <= 220)
    row['high_efficiency'] = int(mpd > 200)
    row['low_efficiency'] = int(mpd < 50)
    
    # Spending categories
    rpd = row['receipts_per_day']
    row['low_spend'] = int(rpd < 100)
    row['medium_spend'] = int(100 <= rpd < 300)
    row['high_spend'] = int(300 <= rpd < 500)
    row['very_high_spend'] = int(rpd >= 500)
    
    # Interaction features
    row['days_x_miles'] = days * miles
    row['days_x_receipts'] = days * receipts
    row['miles_x_receipts'] = miles * receipts
    row['efficiency_x_receipts'] = row['miles_per_day'] * receipts
    
    # Ratio features
    row['miles_to_receipts'] = miles / (receipts + 1)
    row['receipts_to_miles'] = receipts / (miles + 1)
    row['days_to_miles'] = days / (miles + 1)
    
    rows.append(row)

df = pd.DataFrame(rows)

# Select features for modeling
feature_cols = [col for col in df.columns if col != 'output']
X = df[feature_cols]
y = df['output']

print("Training RandomForest model...")

# Train the model
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)
rf.fit(X, y)

# Get predictions
y_pred = rf.predict(X)
mae = np.mean(np.abs(y - y_pred))
print(f"Training MAE: ${mae:.2f}")

# Save the model and feature names
model_data = {
    'model': rf,
    'feature_cols': feature_cols
}

with open('rf_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("Model saved to rf_model.pkl")

# Create a standalone prediction script
prediction_script = '''#!/usr/bin/env python3
import sys
import numpy as np
import pickle

def create_features(days, miles, receipts):
    """Create all features for the model"""
    features = {}
    
    # Basic features
    features['days'] = days
    features['miles'] = miles
    features['receipts'] = receipts
    
    # Derived features
    features['miles_per_day'] = miles / days if days > 0 else miles
    features['receipts_per_day'] = receipts / days if days > 0 else receipts
    features['total_input'] = days + miles + receipts
    
    # Categorical features
    features['is_1_day'] = int(days == 1)
    features['is_2_day'] = int(days == 2)
    features['is_3_day'] = int(days == 3)
    features['is_4_day'] = int(days == 4)
    features['is_5_day'] = int(days == 5)
    features['is_weekend'] = int(days in [2, 3])
    
    # Receipt features
    features['log_receipts'] = np.log1p(receipts)
    features['sqrt_receipts'] = np.sqrt(receipts)
    features['receipts_squared'] = receipts ** 2
    features['receipts_cubed'] = receipts ** 3
    
    # Rounding features
    receipt_str = f"{receipts:.2f}"
    features['ends_49'] = int(receipt_str.endswith('49'))
    features['ends_99'] = int(receipt_str.endswith('99'))
    features['ends_00'] = int(receipt_str.endswith('00'))
    features['last_digit'] = int(receipt_str[-1])
    features['second_last_digit'] = int(receipt_str[-2])
    
    # Mileage tiers
    features['tier1_miles'] = min(miles, 100)
    features['tier2_miles'] = max(0, min(miles - 100, 300))
    features['tier3_miles'] = max(0, miles - 400)
    
    # Efficiency features
    mpd = features['miles_per_day']
    features['efficiency_bonus'] = int(180 <= mpd <= 220)
    features['high_efficiency'] = int(mpd > 200)
    features['low_efficiency'] = int(mpd < 50)
    
    # Spending categories
    rpd = features['receipts_per_day']
    features['low_spend'] = int(rpd < 100)
    features['medium_spend'] = int(100 <= rpd < 300)
    features['high_spend'] = int(300 <= rpd < 500)
    features['very_high_spend'] = int(rpd >= 500)
    
    # Interaction features
    features['days_x_miles'] = days * miles
    features['days_x_receipts'] = days * receipts
    features['miles_x_receipts'] = miles * receipts
    features['efficiency_x_receipts'] = features['miles_per_day'] * receipts
    
    # Ratio features
    features['miles_to_receipts'] = miles / (receipts + 1)
    features['receipts_to_miles'] = receipts / (miles + 1)
    features['days_to_miles'] = days / (miles + 1)
    
    return features

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: predict.py <days> <miles> <receipts>", file=sys.stderr)
        sys.exit(1)
    
    days = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])
    
    # Load model
    with open('rf_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    rf = model_data['model']
    feature_cols = model_data['feature_cols']
    
    # Create features
    features = create_features(days, miles, receipts)
    
    # Create feature array in correct order
    X = np.array([[features[col] for col in feature_cols]])
    
    # Predict
    prediction = rf.predict(X)[0]
    print(f"{prediction:.2f}")
'''

with open('predict.py', 'w') as f:
    f.write(prediction_script)

print("Prediction script saved to predict.py")

# Test a few cases
print("\nTesting predictions:")
test_cases = [
    (3, 93, 1.42),
    (1, 55, 3.60),
    (5, 516, 1878.49),
    (4, 69, 2321.49)
]

for days, miles, receipts in test_cases:
    features = create_features(days, miles, receipts)
    X_test = pd.DataFrame([features])[feature_cols]
    pred = rf.predict(X_test)[0]
    print(f"{days}d, {miles}mi, ${receipts:.2f} → Predicted: ${pred:.2f}")

def create_features(days, miles, receipts):
    """Helper function to create features"""
    features = {}
    features['days'] = days
    features['miles'] = miles
    features['receipts'] = receipts
    features['miles_per_day'] = miles / days if days > 0 else miles
    features['receipts_per_day'] = receipts / days if days > 0 else receipts
    features['total_input'] = days + miles + receipts
    features['is_1_day'] = int(days == 1)
    features['is_2_day'] = int(days == 2)
    features['is_3_day'] = int(days == 3)
    features['is_4_day'] = int(days == 4)
    features['is_5_day'] = int(days == 5)
    features['is_weekend'] = int(days in [2, 3])
    features['log_receipts'] = np.log1p(receipts)
    features['sqrt_receipts'] = np.sqrt(receipts)
    features['receipts_squared'] = receipts ** 2
    features['receipts_cubed'] = receipts ** 3
    receipt_str = f"{receipts:.2f}"
    features['ends_49'] = int(receipt_str.endswith('49'))
    features['ends_99'] = int(receipt_str.endswith('99'))
    features['ends_00'] = int(receipt_str.endswith('00'))
    features['last_digit'] = int(receipt_str[-1])
    features['second_last_digit'] = int(receipt_str[-2])
    features['tier1_miles'] = min(miles, 100)
    features['tier2_miles'] = max(0, min(miles - 100, 300))
    features['tier3_miles'] = max(0, miles - 400)
    mpd = features['miles_per_day']
    features['efficiency_bonus'] = int(180 <= mpd <= 220)
    features['high_efficiency'] = int(mpd > 200)
    features['low_efficiency'] = int(mpd < 50)
    rpd = features['receipts_per_day']
    features['low_spend'] = int(rpd < 100)
    features['medium_spend'] = int(100 <= rpd < 300)
    features['high_spend'] = int(300 <= rpd < 500)
    features['very_high_spend'] = int(rpd >= 500)
    features['days_x_miles'] = days * miles
    features['days_x_receipts'] = days * receipts
    features['miles_x_receipts'] = miles * receipts
    features['efficiency_x_receipts'] = features['miles_per_day'] * receipts
    features['miles_to_receipts'] = miles / (receipts + 1)
    features['receipts_to_miles'] = receipts / (miles + 1)
    features['days_to_miles'] = days / (miles + 1)
    return features 