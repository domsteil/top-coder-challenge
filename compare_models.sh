#!/bin/bash

echo "Comparing all models on test cases:"
echo "==================================="
echo ""

echo "Test case 1: 3 days, 93 miles, \$1.42 receipts (Expected: \$364.51)"
echo "RandomForest (run.sh):      $(./run.sh 3 93 1.42 2>&1 | tail -1)"
echo "Decision Tree:              $(./run_decision_tree.sh 3 93 1.42)"
echo "Ultra-optimized:            $(./run_standalone.sh 3 93 1.42)"
echo ""

echo "Test case 2: 1 day, 55 miles, \$3.60 receipts (Expected: \$126.06)"
echo "RandomForest (run.sh):      $(./run.sh 1 55 3.60 2>&1 | tail -1)"
echo "Decision Tree:              $(./run_decision_tree.sh 1 55 3.60)"
echo "Ultra-optimized:            $(./run_standalone.sh 1 55 3.60)"
echo ""

echo "Test case 3: 5 days, 516 miles, \$1878.49 receipts (Expected: \$669.85)"
echo "RandomForest (run.sh):      $(./run.sh 5 516 1878.49 2>&1 | tail -1)"
echo "Decision Tree:              $(./run_decision_tree.sh 5 516 1878.49)"
echo "Ultra-optimized:            $(./run_standalone.sh 5 516 1878.49)"
echo ""

echo "Summary of expected scores:"
echo "- RandomForest:    ~5264 (MAE ~\$52.64)"
echo "- Decision Tree:   ~13161 (MAE ~\$132)"
echo "- Ultra-optimized: ~17209 (MAE ~\$172)" 