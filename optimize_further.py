#!/usr/bin/env python3
"""
Explore further optimizations for the RandomForest model
"""

import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score
import pickle

print("Loading data and analyzing optimization opportunities...")

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Analyze the high-error patterns
high_error_patterns = {
    'ends_49': 0,
    'ends_99': 0,
    'high_receipts': 0,
    'very_high_receipts': 0,
    'high_daily_spend': 0
}

for case in data:
    receipts = case['input']['total_receipts_amount']
    days = case['input']['trip_duration_days']
    receipt_str = f"{receipts:.2f}"
    
    if receipt_str.endswith('49'):
        high_error_patterns['ends_49'] += 1
    elif receipt_str.endswith('99'):
        high_error_patterns['ends_99'] += 1
    
    if receipts > 1400:
        high_error_patterns['high_receipts'] += 1
    if receipts > 2000:
        high_error_patterns['very_high_receipts'] += 1
    
    if receipts / days > 500:
        high_error_patterns['high_daily_spend'] += 1

print("\nHigh-error pattern frequencies in public data:")
for pattern, count in high_error_patterns.items():
    print(f"  {pattern}: {count} cases ({count/len(data)*100:.1f}%)")

# Create enhanced features
print("\n" + "="*60)
print("OPTIMIZATION STRATEGY 1: Enhanced Feature Engineering")
print("="*60)

rows = []
for case in data:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    row = {
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'output': output
    }
    
    # All existing features from before
    row['miles_per_day'] = miles / days if days > 0 else miles
    row['receipts_per_day'] = receipts / days if days > 0 else receipts
    row['total_input'] = days + miles + receipts
    
    # Day indicators
    for d in range(1, 15):
        row[f'is_{d}_day'] = int(days == d)
    
    # Receipt features
    row['log_receipts'] = np.log1p(receipts)
    row['sqrt_receipts'] = np.sqrt(receipts)
    row['receipts_squared'] = receipts ** 2
    row['receipts_cubed'] = receipts ** 3
    
    # Enhanced rounding features
    receipt_str = f"{receipts:.2f}"
    row['ends_49'] = int(receipt_str.endswith('49'))
    row['ends_99'] = int(receipt_str.endswith('99'))
    row['ends_00'] = int(receipt_str.endswith('00'))
    
    # NEW: More granular ending patterns
    for digit in range(10):
        row[f'last_digit_{digit}'] = int(receipt_str[-1] == str(digit))
    
    # NEW: Penalty interaction features
    row['ends_49_x_receipts'] = row['ends_49'] * receipts
    row['ends_99_x_receipts'] = row['ends_99'] * receipts
    row['ends_49_x_log_receipts'] = row['ends_49'] * row['log_receipts']
    row['ends_99_x_log_receipts'] = row['ends_99'] * row['log_receipts']
    
    # Mileage features
    row['tier1_miles'] = min(miles, 100)
    row['tier2_miles'] = max(0, min(miles - 100, 300))
    row['tier3_miles'] = max(0, miles - 400)
    
    # NEW: More mileage features
    row['miles_squared'] = miles ** 2
    row['log_miles'] = np.log1p(miles)
    row['sqrt_miles'] = np.sqrt(miles)
    
    # Efficiency features
    mpd = row['miles_per_day']
    row['efficiency_bonus'] = int(180 <= mpd <= 220)
    row['efficiency_penalty'] = int(mpd > 300)
    
    # Spending categories with more granularity
    rpd = row['receipts_per_day']
    row['very_low_spend'] = int(rpd < 50)
    row['low_spend'] = int(50 <= rpd < 100)
    row['medium_spend'] = int(100 <= rpd < 300)
    row['high_spend'] = int(300 <= rpd < 500)
    row['very_high_spend'] = int(rpd >= 500)
    row['extreme_spend'] = int(rpd >= 700)
    
    # NEW: Polynomial features for key interactions
    row['days_squared'] = days ** 2
    row['days_x_miles_squared'] = days * miles ** 2
    row['days_squared_x_miles'] = days ** 2 * miles
    row['days_x_receipts_squared'] = days * receipts ** 2
    
    # NEW: Ratio features
    row['receipts_to_total'] = receipts / (days + miles + receipts + 1)
    row['miles_to_total'] = miles / (days + miles + receipts + 1)
    row['days_to_total'] = days / (days + miles + receipts + 1)
    
    rows.append(row)

df = pd.DataFrame(rows)
feature_cols = [col for col in df.columns if col != 'output']
X = df[feature_cols]
y = df['output']

print(f"\nEnhanced feature set: {len(feature_cols)} features (up from 38)")

# Test different models
print("\n" + "="*60)
print("OPTIMIZATION STRATEGY 2: Advanced Models")
print("="*60)

models = {
    'RandomForest_100': RandomForestRegressor(
        n_estimators=100, max_depth=8, min_samples_leaf=5, random_state=42
    ),
    'RandomForest_200': RandomForestRegressor(
        n_estimators=200, max_depth=10, min_samples_leaf=3, random_state=42
    ),
    'GradientBoosting': GradientBoostingRegressor(
        n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
    ),
    'NeuralNet': MLPRegressor(
        hidden_layer_sizes=(100, 50, 25), max_iter=1000, random_state=42
    )
}

print("\nTraining and evaluating models...")
best_model = None
best_mae = float('inf')
best_name = None

for name, model in models.items():
    print(f"\n{name}:")
    model.fit(X, y)
    y_pred = model.predict(X)
    mae = np.mean(np.abs(y - y_pred))
    print(f"  Training MAE: ${mae:.2f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, 
                                scoring='neg_mean_absolute_error')
    cv_mae = -cv_scores.mean()
    print(f"  Cross-validation MAE: ${cv_mae:.2f}")
    
    if mae < best_mae:
        best_mae = mae
        best_model = model
        best_name = name

print(f"\n✨ Best model: {best_name} with MAE ${best_mae:.2f}")

# Analyze residuals for the best model
print("\n" + "="*60)
print("OPTIMIZATION STRATEGY 3: Residual Analysis & Post-processing")
print("="*60)

y_pred = best_model.predict(X)
df['predicted'] = y_pred
df['residual'] = y - y_pred
df['abs_residual'] = np.abs(df['residual'])

# Analyze residuals by pattern
print("\nAverage residuals by pattern:")
print(f"  Cases ending in .49: ${df[df['ends_49'] == 1]['residual'].mean():.2f}")
print(f"  Cases ending in .99: ${df[df['ends_99'] == 1]['residual'].mean():.2f}")
print(f"  High receipts (>$1400): ${df[df['receipts'] > 1400]['residual'].mean():.2f}")
print(f"  Very high receipts (>$2000): ${df[df['receipts'] > 2000]['residual'].mean():.2f}")

# Find systematic biases
print("\nSystematic biases to correct:")
corrections = {}

# If .49 endings are consistently under/over-predicted
if abs(df[df['ends_49'] == 1]['residual'].mean()) > 50:
    corrections['ends_49'] = df[df['ends_49'] == 1]['residual'].mean()
    print(f"  .49 endings: adjust by ${corrections['ends_49']:.2f}")

if abs(df[df['ends_99'] == 1]['residual'].mean()) > 50:
    corrections['ends_99'] = df[df['ends_99'] == 1]['residual'].mean()
    print(f"  .99 endings: adjust by ${corrections['ends_99']:.2f}")

# Save the optimized model
print("\n" + "="*60)
print("SAVING OPTIMIZED MODEL")
print("="*60)

model_data = {
    'model': best_model,
    'feature_cols': feature_cols,
    'corrections': corrections,
    'model_name': best_name
}

with open('optimized_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print(f"✅ Saved optimized model to optimized_model.pkl")
print(f"   Model: {best_name}")
print(f"   Features: {len(feature_cols)}")
print(f"   Expected improvement: ~{(52.64 - best_mae) / 52.64 * 100:.1f}%") 