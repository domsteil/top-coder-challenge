Testing specific high-error cases:
================================================================================

Case 684: 8d, 795mi, $1645.99
  Expected: $644.69
  Got: $810.67
  Error: $165.98
  Miles/day: 99.4
  Receipts/day: $205.75
  Expected/Total Input: 0.263
  ⚠️  Receipt ends in .99 - should be moderately penalized

Case 152: 4d, 69mi, $2321.49
  Expected: $322.00
  Got: $778.21
  Error: $456.21
  Miles/day: 17.2
  Receipts/day: $580.37
  Expected/Total Input: 0.134
  ⚠️  Receipt ends in .49 - should be heavily penalized

Case 367: 11d, 740mi, $1171.99
  Expected: $902.09
  Got: $1431.64
  Error: $529.55
  Miles/day: 67.3
  Receipts/day: $106.54
  Expected/Total Input: 0.469
  ⚠️  Receipt ends in .99 - should be moderately penalized

Case 996: 1d, 1082mi, $1809.49
  Expected: $446.94
  Got: $258.50
  Error: $188.44
  Miles/day: 1082.0
  Receipts/day: $1809.49
  Expected/Total Input: 0.155
  ⚠️  Receipt ends in .49 - should be heavily penalized

Case 548: 8d, 482mi, $1411.49
  Expected: $631.81
  Got: $988.91
  Error: $357.10
  Miles/day: 60.2
  Receipts/day: $176.44
  Expected/Total Input: 0.332
  ⚠️  Receipt ends in .49 - should be heavily penalized
