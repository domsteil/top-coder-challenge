#!/usr/bin/env python3
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
