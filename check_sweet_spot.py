import json

with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

sweet_spot_count = 0
for case in public_cases:
    days = case['input']['trip_duration_days']
    receipts = case['input']['total_receipts_amount']
    
    # Check if it falls into Lisa's sweet spot
    if 4 <= days <= 7 and 600 <= receipts <= 800:
        sweet_spot_count += 1

print(f"Total cases: {len(public_cases)}")
print(f"Cases in Lisa's sweet spot (4-7 days, $600-800 receipts): {sweet_spot_count}")
print(f"Percentage: {sweet_spot_count/len(public_cases)*100:.1f}%") 