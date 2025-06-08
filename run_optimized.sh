#!/bin/bash

# Black Box Legacy Reimbursement System - Optimized GradientBoosting Solution
# Using enhanced features and GradientBoosting for better accuracy
# Expected score: ~4000-4500 (improved from 5363)

# Validate arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

# Input validation
if ! [[ "$1" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$2" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$3" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

# Use the optimized GradientBoosting model for prediction
exec python3 predict_optimized.py "$1" "$2" "$3" 