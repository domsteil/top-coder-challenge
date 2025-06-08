#!/usr/bin/env python3
"""
Phase 1: Stop guess-and-twiddle; fit the public data mechanically
Goal: Use linear regression to discover the true weights and relationships
"""

import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from decimal import Decimal as D

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
rows = []
for case in data:
    row = {
        'days': case['input']['trip_duration_days'],
        'miles': case['input']['miles_traveled'],
        'receipts': case['input']['total_receipts_amount'],
        'legacy_output': case['expected_output']
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Derive all features mentioned in interviews
df['miles_per_day'] = df['miles'] / df['days']
df['receipts_per_day'] = df['receipts'] / df['days']
df['is_five_day'] = (df['days'] == 5).astype(int)
df['is_short_trip'] = (df['days'] <= 3).astype(int)
df['is_medium_trip'] = ((df['days'] > 3) & (df['days'] <= 7)).astype(int)
df['is_long_trip'] = (df['days'] > 7).astype(int)
df['low_receipt_flag'] = ((df['receipts'] > 0) & (df['receipts'] <= 50)).astype(int)

# Rounding flags
df['rounding_49_flag'] = df['receipts'].apply(lambda x: 1 if f"{x:.2f}".endswith('49') else 0)
df['rounding_99_flag'] = df['receipts'].apply(lambda x: 1 if f"{x:.2f}".endswith('99') else 0)
df['rounding_49_99_flag'] = df['rounding_49_flag'] | df['rounding_99_flag']

# Mileage tiers
df['tier1_miles'] = df['miles'].apply(lambda x: min(x, 100))
df['tier2_miles'] = df['miles'].apply(lambda x: max(0, min(x - 100, 300)))  # 101-400
df['tier3_miles'] = df['miles'].apply(lambda x: max(0, x - 400))  # 401+

# Additional features
df['log_receipts'] = np.log1p(df['receipts'])  # log(receipts + 1) to handle zeros
df['sqrt_receipts'] = np.sqrt(df['receipts'])
df['receipts_squared'] = df['receipts'] ** 2
df['high_daily_spend'] = (df['receipts_per_day'] > 450).astype(int)
df['very_high_daily_spend'] = (df['receipts_per_day'] > 500).astype(int)
df['extreme_receipts'] = (df['receipts'] > 2000).astype(int)

# Efficiency bonus indicators
df['efficiency_bonus'] = ((df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)).astype(int)
df['efficiency_bonus_narrow'] = ((df['miles_per_day'] >= 185) & (df['miles_per_day'] <= 215)).astype(int)

# Interaction terms
df['days_x_receipts'] = df['days'] * df['receipts']
df['five_day_x_receipts'] = df['is_five_day'] * df['receipts']
df['high_spend_x_days'] = df['high_daily_spend'] * df['days']

print("Dataset shape:", df.shape)
print("\nFirst few rows:")
print(df.head())

# Prepare features for regression
feature_cols = [
    'days', 'tier1_miles', 'tier2_miles', 'tier3_miles',
    'receipts', 'log_receipts', 'sqrt_receipts',
    'receipts_per_day', 'miles_per_day',
    'is_five_day', 'is_short_trip', 'is_medium_trip', 'is_long_trip',
    'low_receipt_flag', 'rounding_49_99_flag',
    'high_daily_spend', 'very_high_daily_spend', 'extreme_receipts',
    'efficiency_bonus', 'efficiency_bonus_narrow',
    'days_x_receipts', 'five_day_x_receipts', 'high_spend_x_days'
]

X = df[feature_cols]
y = df['legacy_output']

# Fit linear regression
model = LinearRegression()
model.fit(X, y)

# Get predictions
y_pred = model.predict(X)
mae = np.mean(np.abs(y - y_pred))
print(f"\nLinear Regression MAE: ${mae:.2f}")

# Examine coefficients
coef_df = pd.DataFrame({
    'feature': feature_cols,
    'coefficient': model.coef_
}).sort_values('coefficient', key=abs, ascending=False)

print("\nTop 15 Most Important Features (by absolute coefficient):")
print(coef_df.head(15).to_string(index=False))

print(f"\nIntercept: {model.intercept_:.2f}")

# Analyze specific insights
print("\n" + "="*60)
print("KEY INSIGHTS FROM REGRESSION:")
print("="*60)

# Mileage rates
tier1_coef = coef_df[coef_df['feature'] == 'tier1_miles']['coefficient'].values[0]
tier2_coef = coef_df[coef_df['feature'] == 'tier2_miles']['coefficient'].values[0]
tier3_coef = coef_df[coef_df['feature'] == 'tier3_miles']['coefficient'].values[0]

print(f"\nMileage Rates:")
print(f"  Tier 1 (0-100): ${tier1_coef:.3f}/mile")
print(f"  Tier 2 (101-400): ${tier2_coef:.3f}/mile")
print(f"  Tier 3 (401+): ${tier3_coef:.3f}/mile")

# Per diem
days_coef = coef_df[coef_df['feature'] == 'days']['coefficient'].values[0]
print(f"\nBase per diem component: ${days_coef:.2f}/day")

# Receipt handling
receipts_coef = coef_df[coef_df['feature'] == 'receipts']['coefficient'].values[0]
log_receipts_coef = coef_df[coef_df['feature'] == 'log_receipts']['coefficient'].values[0]
receipts_per_day_coef = coef_df[coef_df['feature'] == 'receipts_per_day']['coefficient'].values[0]

print(f"\nReceipt handling:")
print(f"  Linear receipts coefficient: {receipts_coef:.4f}")
print(f"  Log receipts coefficient: {log_receipts_coef:.2f}")
print(f"  Receipts per day coefficient: {receipts_per_day_coef:.4f}")

# Special bonuses/penalties
five_day_coef = coef_df[coef_df['feature'] == 'is_five_day']['coefficient'].values[0]
low_receipt_coef = coef_df[coef_df['feature'] == 'low_receipt_flag']['coefficient'].values[0]
rounding_coef = coef_df[coef_df['feature'] == 'rounding_49_99_flag']['coefficient'].values[0]
efficiency_coef = coef_df[coef_df['feature'] == 'efficiency_bonus']['coefficient'].values[0]

print(f"\nSpecial adjustments:")
print(f"  5-day bonus: ${five_day_coef:.2f}")
print(f"  Low receipt penalty: ${low_receipt_coef:.2f}")
print(f"  Rounding bug bonus: ${rounding_coef:.2f}")
print(f"  Efficiency bonus effect: ${efficiency_coef:.2f}")

# High spending penalties
high_spend_coef = coef_df[coef_df['feature'] == 'high_daily_spend']['coefficient'].values[0]
very_high_spend_coef = coef_df[coef_df['feature'] == 'very_high_daily_spend']['coefficient'].values[0]

print(f"\nHigh spending penalties:")
print(f"  High daily spend (>$450): ${high_spend_coef:.2f}")
print(f"  Very high daily spend (>$500): ${very_high_spend_coef:.2f}")

# Save results for Phase 2
results = {
    'mae': mae,
    'coefficients': coef_df.to_dict('records'),
    'intercept': model.intercept_
}

with open('phase1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Phase 1 complete! Results saved to phase1_results.json")
print(f"   Starting MAE: $171.09 → Regression MAE: ${mae:.2f}")
print(f"   Next: Use these coefficients to build deterministic rules in Phase 2") 