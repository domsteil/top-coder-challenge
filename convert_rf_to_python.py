#!/usr/bin/env python3
"""
Convert RandomForest model to pure Python code using m2cgen
This will create a self-contained solution with no external dependencies
"""

import pickle
import subprocess
import sys

# First, install m2cgen if not available
try:
    import m2cgen as m2c
except ImportError:
    print("Installing m2cgen...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "m2cgen"])
    import m2cgen as m2c

print("Loading RandomForest model...")
with open('rf_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

rf_model = model_data['model']
feature_cols = model_data['feature_cols']

print(f"Model info:")
print(f"  Type: {type(rf_model).__name__}")
print(f"  Features: {len(feature_cols)}")
print(f"  Trees: {rf_model.n_estimators}")
print(f"  Max depth: {rf_model.max_depth}")

# Convert to pure Python
print("\nConverting to pure Python code...")
code = m2c.export_to_python(rf_model)

# Save the generated code
with open('rf_pure_python.py', 'w') as f:
    f.write("# Auto-generated RandomForest model in pure Python\n")
    f.write("# No sklearn or external dependencies required\n\n")
    f.write(code)

print(f"✅ Saved pure Python model to rf_pure_python.py")
print(f"   File size: {len(code)} bytes")

# Create the feature engineering function that matches our training
feature_code = '''
def create_features(days, miles, receipts):
    """Create all 38 features exactly as used in training"""
    import math
    
    # Basic features
    features = {}
    features['days'] = float(days)
    features['miles'] = float(miles)
    features['receipts'] = float(receipts)
    
    # Derived features
    features['miles_per_day'] = miles / days if days > 0 else miles
    features['receipts_per_day'] = receipts / days if days > 0 else receipts
    features['total_input'] = days + miles + receipts
    
    # Categorical features
    features['is_1_day'] = float(days == 1)
    features['is_2_day'] = float(days == 2)
    features['is_3_day'] = float(days == 3)
    features['is_4_day'] = float(days == 4)
    features['is_5_day'] = float(days == 5)
    features['is_weekend'] = float(days in [2, 3])
    
    # Receipt features
    features['log_receipts'] = math.log1p(receipts)
    features['sqrt_receipts'] = math.sqrt(receipts)
    features['receipts_squared'] = receipts ** 2
    features['receipts_cubed'] = receipts ** 3
    
    # Rounding features
    receipt_str = f"{receipts:.2f}"
    features['ends_49'] = float(receipt_str.endswith('49'))
    features['ends_99'] = float(receipt_str.endswith('99'))
    features['ends_00'] = float(receipt_str.endswith('00'))
    features['last_digit'] = float(int(receipt_str[-1]))
    features['second_last_digit'] = float(int(receipt_str[-2]))
    
    # Mileage tiers
    features['tier1_miles'] = min(miles, 100)
    features['tier2_miles'] = max(0, min(miles - 100, 300))
    features['tier3_miles'] = max(0, miles - 400)
    
    # Efficiency features
    mpd = features['miles_per_day']
    features['efficiency_bonus'] = float(180 <= mpd <= 220)
    features['high_efficiency'] = float(mpd > 200)
    features['low_efficiency'] = float(mpd < 50)
    
    # Spending categories
    rpd = features['receipts_per_day']
    features['low_spend'] = float(rpd < 100)
    features['medium_spend'] = float(100 <= rpd < 300)
    features['high_spend'] = float(300 <= rpd < 500)
    features['very_high_spend'] = float(rpd >= 500)
    
    # Interaction features
    features['days_x_miles'] = days * miles
    features['days_x_receipts'] = days * receipts
    features['miles_x_receipts'] = miles * receipts
    features['efficiency_x_receipts'] = features['miles_per_day'] * receipts
    
    # Ratio features
    features['miles_to_receipts'] = miles / (receipts + 1)
    features['receipts_to_miles'] = receipts / (miles + 1)
    features['days_to_miles'] = days / (miles + 1)
    
    # Return as list in the exact order expected by the model
    feature_names = %s
    return [features[name] for name in feature_names]
''' % repr(feature_cols)

# Save feature engineering code
with open('features_pure_python.py', 'w') as f:
    f.write(feature_code)

print("\n✅ Saved feature engineering to features_pure_python.py")

# Create the complete self-contained solution
print("\nCreating self-contained run.sh...")

run_sh_content = '''#!/bin/bash

# Black Box Legacy Reimbursement System - Self-Contained RandomForest Solution
# Pure Python implementation with no external dependencies
# Expected score: ~5364 (MAE ~$52.64)

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+\\.?[0-9]*$ ]] || ! [[ "$2" =~ ^[0-9]+\\.?[0-9]*$ ]] || ! [[ "$3" =~ ^[0-9]+\\.?[0-9]*$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

python3 - <<'PYTHON_CODE' "$1" "$2" "$3"
import sys
import math

# ===== FEATURE ENGINEERING (must match training exactly) =====
''' + feature_code + '''

# ===== PURE PYTHON RANDOM FOREST MODEL =====
''' + code + '''

# ===== MAIN PREDICTION FUNCTION =====
def predict_reimbursement(days, miles, receipts):
    """Main prediction function with all adjustments"""
    
    # Get features
    features = create_features(days, miles, receipts)
    
    # Get base prediction from RandomForest
    prediction = score(features)
    
    # Apply known adjustments from analysis
    receipt_str = f"{receipts:.2f}"
    
    # Rounding bug bonus - discovered in analysis
    if receipt_str.endswith(("49", "99")):
        prediction += 5.01
    
    # Ensure non-negative and round to cents
    return round(max(0.0, prediction), 2)

# ===== ENTRY POINT =====
if __name__ == "__main__":
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = predict_reimbursement(days, miles, receipts)
        print(f"{result:.2f}")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

PYTHON_CODE
'''

with open('run_self_contained.sh', 'w') as f:
    f.write(run_sh_content)

print("✅ Created run_self_contained.sh")
print("\nNext steps:")
print("1. chmod +x run_self_contained.sh")
print("2. Test with: ./run_self_contained.sh 3 93 1.42")
print("3. Run full evaluation to verify score")
print("4. Replace run.sh with this self-contained version") 