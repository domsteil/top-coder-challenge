#!/bin/bash

# Black Box Legacy Reimbursement System - RandomForest Solution
# Using machine learning to achieve ~5200 score (MAE ~$52)
# This model captures complex non-linear patterns in the legacy system

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

# Use the trained RandomForest model for prediction
exec python3 predict.py "$1" "$2" "$3"
