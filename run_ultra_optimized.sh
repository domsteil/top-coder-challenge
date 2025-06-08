#!/bin/bash

# Black Box Legacy Reimbursement System - Ultra-Optimized Version
# Aggressive feature engineering and multi-layer corrections
# Target score: ~3000

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$2" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$3" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

python3 predict_ultra_optimized.py "$1" "$2" "$3" 