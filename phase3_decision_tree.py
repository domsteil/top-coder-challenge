#!/usr/bin/env python3
"""
Phase 3: Machine-fit the decision tree to capture non-linear patterns
This will reveal hidden splits and rules the regression missed
"""

import json
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
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

# Create all features
df['miles_per_day'] = df['miles'] / df['days']
df['receipts_per_day'] = df['receipts'] / df['days']
df['is_five_day'] = (df['days'] == 5).astype(int)
df['is_short_trip'] = (df['days'] <= 3).astype(int)
df['is_medium_trip'] = ((df['days'] > 3) & (df['days'] <= 7)).astype(int)
df['is_long_trip'] = (df['days'] > 7).astype(int)
df['low_receipt_flag'] = ((df['receipts'] > 0) & (df['receipts'] <= 50)).astype(int)
df['rounding_49_flag'] = df['receipts'].apply(lambda x: 1 if f"{x:.2f}".endswith('49') else 0)
df['rounding_99_flag'] = df['receipts'].apply(lambda x: 1 if f"{x:.2f}".endswith('99') else 0)
df['tier1_miles'] = df['miles'].apply(lambda x: min(x, 100))
df['tier2_miles'] = df['miles'].apply(lambda x: max(0, min(x - 100, 300)))
df['tier3_miles'] = df['miles'].apply(lambda x: max(0, x - 400))

# Key features for decision tree
feature_cols = ['days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day']
X = df[feature_cols]
y = df['legacy_output']

# Try different max_depths
print("Testing different tree depths:")
for depth in [3, 4, 5, 6]:
    tree = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=20, random_state=42)
    tree.fit(X, y)
    y_pred = tree.predict(X)
    mae = np.mean(np.abs(y - y_pred))
    print(f"  Depth {depth}: MAE = ${mae:.2f}")

# Use depth 4 as recommended
print("\nUsing depth=4 tree:")
tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=20, random_state=42)
tree.fit(X, y)

# Get predictions
y_pred = tree.predict(X)
mae = np.mean(np.abs(y - y_pred))
print(f"Decision Tree MAE: ${mae:.2f}")

# Export tree rules
tree_rules = export_text(tree, feature_names=feature_cols)
print("\nDecision Tree Rules:")
print(tree_rules)

# Analyze the tree structure more programmatically
def get_tree_rules(tree, feature_names):
    """Extract rules from decision tree"""
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]
    
    rules = []
    
    def recurse(node, depth, parent_rule=""):
        if tree_.feature[node] != -2:  # Not a leaf
            name = feature_name[node]
            threshold = tree_.threshold[node]
            
            # Left child (<=)
            left_rule = f"{parent_rule} & " if parent_rule else ""
            left_rule += f"({name} <= {threshold:.2f})"
            recurse(tree_.children_left[node], depth + 1, left_rule)
            
            # Right child (>)
            right_rule = f"{parent_rule} & " if parent_rule else ""
            right_rule += f"({name} > {threshold:.2f})"
            recurse(tree_.children_right[node], depth + 1, right_rule)
        else:  # Leaf node
            value = tree_.value[node][0][0]
            n_samples = tree_.n_node_samples[node]
            rules.append({
                'rule': parent_rule,
                'value': value,
                'samples': n_samples
            })
    
    recurse(0, 1)
    return rules

rules = get_tree_rules(tree, feature_cols)
print("\nExtracted Rules (sorted by impact):")
rules.sort(key=lambda x: x['samples'], reverse=True)
for i, rule in enumerate(rules[:15]):  # Show top 15 rules
    print(f"\nRule {i+1} (affects {rule['samples']} samples):")
    print(f"  IF {rule['rule']}")
    print(f"  THEN output = ${rule['value']:.2f}")

# Generate Python code for the decision tree
print("\n" + "="*60)
print("PYTHON IMPLEMENTATION OF DECISION TREE:")
print("="*60)

def generate_tree_code(tree, feature_names):
    """Generate Python code from decision tree"""
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]
    
    def recurse(node, depth=0):
        indent = "    " * depth
        
        if tree_.feature[node] != -2:  # Not a leaf
            name = feature_name[node]
            threshold = tree_.threshold[node]
            print(f"{indent}if {name} <= {threshold:.2f}:")
            recurse(tree_.children_left[node], depth + 1)
            print(f"{indent}else:  # {name} > {threshold:.2f}")
            recurse(tree_.children_right[node], depth + 1)
        else:  # Leaf
            value = tree_.value[node][0][0]
            print(f"{indent}return {value:.2f}")
    
    print("def calculate_reimbursement_tree(days, miles, receipts):")
    print("    miles_per_day = miles / days if days > 0 else miles")
    print("    receipts_per_day = receipts / days if days > 0 else receipts")
    print("    ")
    recurse(0, 1)

generate_tree_code(tree, feature_cols)

# Analyze residuals
residuals = y - y_pred
df['residual'] = residuals
df['abs_residual'] = np.abs(residuals)

print("\n" + "="*60)
print("RESIDUAL ANALYSIS:")
print("="*60)

# Find patterns in large residuals
large_residuals = df[df['abs_residual'] > 50].copy()
print(f"\nCases with residuals > $50: {len(large_residuals)}")

# Check for patterns
print("\nPatterns in large residuals:")
print("Average values for high-error cases:")
print(f"  Days: {large_residuals['days'].mean():.1f}")
print(f"  Miles: {large_residuals['miles'].mean():.1f}")
print(f"  Receipts: ${large_residuals['receipts'].mean():.2f}")
print(f"  Miles/day: {large_residuals['miles_per_day'].mean():.1f}")
print(f"  Receipts/day: ${large_residuals['receipts_per_day'].mean():.2f}")

# Check for rounding patterns
rounding_49_errors = df[df['rounding_49_flag'] == 1]['residual'].mean()
rounding_99_errors = df[df['rounding_99_flag'] == 1]['residual'].mean()
print(f"\nRounding pattern residuals:")
print(f"  .49 endings: average residual = ${rounding_49_errors:.2f}")
print(f"  .99 endings: average residual = ${rounding_99_errors:.2f}")

# Check 5-day trips
five_day_residual = df[df['is_five_day'] == 1]['residual'].mean()
print(f"\n5-day trips: average residual = ${five_day_residual:.2f}")

print("\n✅ Phase 3 complete!")
print(f"   Decision tree MAE: ${mae:.2f}")
print("   Next: Implement the tree rules and analyze remaining patterns in Phase 4") 