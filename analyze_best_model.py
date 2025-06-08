import json
import subprocess

# Load public cases
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

# Test our best model on all cases
errors_by_category = {
    'short_low_receipts': [],
    'short_high_receipts': [],
    'medium_low_receipts': [],
    'medium_high_receipts': [],
    'long_low_receipts': [],
    'long_high_receipts': []
}

print("Analyzing best model performance by category...")
print("=" * 80)

for i, case in enumerate(public_cases):
    days = case['input']['trip_duration_days']
    receipts = case['input']['total_receipts_amount']
    
    # Categorize
    if days <= 3:
        trip_type = 'short'
    elif days <= 7:
        trip_type = 'medium'
    else:
        trip_type = 'long'
    
    if receipts <= 500:
        receipt_level = 'low_receipts'
    else:
        receipt_level = 'high_receipts'
    
    category = f"{trip_type}_{receipt_level}"
    
    # Run model
    result = subprocess.run(
        ['./run.sh', 
         str(case['input']['trip_duration_days']), 
         str(case['input']['miles_traveled']), 
         f"{case['input']['total_receipts_amount']:.2f}"],
        capture_output=True,
        text=True
    )
    
    got = float(result.stdout.strip())
    expected = case['expected_output']
    error = abs(got - expected)
    
    errors_by_category[category].append(error)
    
    if i % 100 == 0:
        print(f"Processed {i} cases...")

# Analyze results
print("\n\nResults by Category:")
print("=" * 80)

for category, errors in errors_by_category.items():
    if errors:
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        errors_over_100 = sum(1 for e in errors if e > 100)
        errors_over_500 = sum(1 for e in errors if e > 500)
        
        print(f"\n{category}:")
        print(f"  Count: {len(errors)}")
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Max error: ${max_error:.2f}")
        print(f"  Errors > $100: {errors_over_100} ({errors_over_100/len(errors)*100:.1f}%)")
        print(f"  Errors > $500: {errors_over_500} ({errors_over_500/len(errors)*100:.1f}%)")

# Find the worst cases in each category
print("\n\nWorst cases by category:")
print("=" * 80)

for category, errors in errors_by_category.items():
    if errors:
        # Find index of max error
        max_error_idx = errors.index(max(errors))
        
        # Find the corresponding case
        case_idx = 0
        for i, case in enumerate(public_cases):
            days = case['input']['trip_duration_days']
            receipts = case['input']['total_receipts_amount']
            
            if days <= 3:
                trip_type = 'short'
            elif days <= 7:
                trip_type = 'medium'
            else:
                trip_type = 'long'
            
            if receipts <= 500:
                receipt_level = 'low_receipts'
            else:
                receipt_level = 'high_receipts'
            
            if f"{trip_type}_{receipt_level}" == category:
                if case_idx == max_error_idx:
                    print(f"\n{category} worst case:")
                    print(f"  Days: {case['input']['trip_duration_days']}")
                    print(f"  Miles: {case['input']['miles_traveled']}")
                    print(f"  Receipts: ${case['input']['total_receipts_amount']:.2f}")
                    print(f"  Expected: ${case['expected_output']:.2f}")
                    print(f"  Error: ${max(errors):.2f}")
                    break
                case_idx += 1 