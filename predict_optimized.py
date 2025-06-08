#!/usr/bin/env python3
import sys
import numpy as np
import pickle

def create_enhanced_features(days, miles, receipts):
    """Create enhanced feature set with 62 features"""
    features = {}
    
    # Basic features
    features['days'] = days
    features['miles'] = miles
    features['receipts'] = receipts
    
    # Derived features
    features['miles_per_day'] = miles / days if days > 0 else miles
    features['receipts_per_day'] = receipts / days if days > 0 else receipts
    features['total_input'] = days + miles + receipts
    
    # Day indicators (1-14)
    for d in range(1, 15):
        features[f'is_{d}_day'] = int(days == d)
    
    # Receipt features
    features['log_receipts'] = np.log1p(receipts)
    features['sqrt_receipts'] = np.sqrt(receipts)
    features['receipts_squared'] = receipts ** 2
    features['receipts_cubed'] = receipts ** 3
    
    # Enhanced rounding features
    receipt_str = f"{receipts:.2f}"
    features['ends_49'] = int(receipt_str.endswith('49'))
    features['ends_99'] = int(receipt_str.endswith('99'))
    features['ends_00'] = int(receipt_str.endswith('00'))
    
    # Granular ending patterns
    for digit in range(10):
        features[f'last_digit_{digit}'] = int(receipt_str[-1] == str(digit))
    
    # Penalty interaction features
    features['ends_49_x_receipts'] = features['ends_49'] * receipts
    features['ends_99_x_receipts'] = features['ends_99'] * receipts
    features['ends_49_x_log_receipts'] = features['ends_49'] * features['log_receipts']
    features['ends_99_x_log_receipts'] = features['ends_99'] * features['log_receipts']
    
    # Mileage features
    features['tier1_miles'] = min(miles, 100)
    features['tier2_miles'] = max(0, min(miles - 100, 300))
    features['tier3_miles'] = max(0, miles - 400)
    features['miles_squared'] = miles ** 2
    features['log_miles'] = np.log1p(miles)
    features['sqrt_miles'] = np.sqrt(miles)
    
    # Efficiency features
    mpd = features['miles_per_day']
    features['efficiency_bonus'] = int(180 <= mpd <= 220)
    features['efficiency_penalty'] = int(mpd > 300)
    
    # Spending categories
    rpd = features['receipts_per_day']
    features['very_low_spend'] = int(rpd < 50)
    features['low_spend'] = int(50 <= rpd < 100)
    features['medium_spend'] = int(100 <= rpd < 300)
    features['high_spend'] = int(300 <= rpd < 500)
    features['very_high_spend'] = int(rpd >= 500)
    features['extreme_spend'] = int(rpd >= 700)
    
    # Polynomial features
    features['days_squared'] = days ** 2
    features['days_x_miles_squared'] = days * miles ** 2
    features['days_squared_x_miles'] = days ** 2 * miles
    features['days_x_receipts_squared'] = days * receipts ** 2
    
    # Ratio features
    total = days + miles + receipts + 1
    features['receipts_to_total'] = receipts / total
    features['miles_to_total'] = miles / total
    features['days_to_total'] = days / total
    
    return features

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: predict_optimized.py <days> <miles> <receipts>", file=sys.stderr)
        sys.exit(1)
    
    days = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])
    
    # Load optimized model
    with open('optimized_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    model = model_data['model']
    feature_cols = model_data['feature_cols']
    corrections = model_data.get('corrections', {})
    
    # Create features
    features = create_enhanced_features(days, miles, receipts)
    
    # Create feature array in correct order
    X = np.array([[features[col] for col in feature_cols]])
    
    # Predict
    prediction = model.predict(X)[0]
    
    # Apply corrections if any
    receipt_str = f"{receipts:.2f}"
    if receipt_str.endswith('49') and 'ends_49' in corrections:
        prediction += corrections['ends_49']
    elif receipt_str.endswith('99') and 'ends_99' in corrections:
        prediction += corrections['ends_99']
    
    # Ensure non-negative
    prediction = max(0, prediction)
    
    print(f"{prediction:.2f}") 