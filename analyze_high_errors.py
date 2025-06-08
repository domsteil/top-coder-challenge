import json

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# High error cases from the evaluation
high_error_cases = [684, 152, 367, 996, 548]

print("High Error Cases Analysis:")
print("=" * 80)

for case_id in high_error_cases:
    case = cases[case_id]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    # Calculate ratios and features
    miles_per_day = miles / days if days > 0 else miles
    receipts_per_day = receipts / days if days > 0 else receipts
    total_input = days + miles + receipts
    receipt_ends_49 = str(receipts).endswith('49')
    receipt_ends_99 = str(receipts).endswith('99')
    
    print(f"\nCase {case_id}:")
    print(f"  Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
    print(f"  Expected: ${expected:.2f}")
    print(f"  Miles/day: {miles_per_day:.1f}")
    print(f"  Receipts/day: ${receipts_per_day:.2f}")
    print(f"  Total input: {total_input:.0f}")
    print(f"  Receipt ends .49: {receipt_ends_49}")
    print(f"  Receipt ends .99: {receipt_ends_99}")
    
    # Calculate what percentage of total input the reimbursement is
    reimb_ratio = expected / total_input if total_input > 0 else 0
    print(f"  Reimbursement/Total Input: {reimb_ratio:.3f}")

# Look for patterns in all .49 and .99 cases
print("\n\nAll .49 and .99 Receipt Cases:")
print("=" * 80)

count_49 = 0
count_99 = 0
for i, case in enumerate(cases):
    receipts = case['input']['total_receipts_amount']
    receipt_str = f"{receipts:.2f}"
    if receipt_str.endswith('49') or receipt_str.endswith('99'):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        expected = case['expected_output']
        total_input = days + miles + receipts
        reimb_ratio = expected / total_input if total_input > 0 else 0
        
        if receipt_str.endswith('49'):
            count_49 += 1
        else:
            count_99 += 1
            
        if i < 20:  # Show first 20 cases
            print(f"Case {i}: {days}d, {miles}mi, ${receipts:.2f} -> ${expected:.2f} (ratio: {reimb_ratio:.3f})")

print(f"\nTotal .49 cases: {count_49}")
print(f"Total .99 cases: {count_99}") 