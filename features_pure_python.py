
def create_features(days, miles, receipts):
    """Create all 38 features exactly as used in training"""
    import math
    
    # Basic features
    features = {}
    features['days'] = float(days)
    features['miles'] = float(miles)
    features['receipts'] = float(receipts)
    
    # Derived features
    features['miles_per_day'] = miles / days if days > 0 else miles
    features['receipts_per_day'] = receipts / days if days > 0 else receipts
    features['total_input'] = days + miles + receipts
    
    # Categorical features
    features['is_1_day'] = float(days == 1)
    features['is_2_day'] = float(days == 2)
    features['is_3_day'] = float(days == 3)
    features['is_4_day'] = float(days == 4)
    features['is_5_day'] = float(days == 5)
    features['is_weekend'] = float(days in [2, 3])
    
    # Receipt features
    features['log_receipts'] = math.log1p(receipts)
    features['sqrt_receipts'] = math.sqrt(receipts)
    features['receipts_squared'] = receipts ** 2
    features['receipts_cubed'] = receipts ** 3
    
    # Rounding features
    receipt_str = f"{receipts:.2f}"
    features['ends_49'] = float(receipt_str.endswith('49'))
    features['ends_99'] = float(receipt_str.endswith('99'))
    features['ends_00'] = float(receipt_str.endswith('00'))
    features['last_digit'] = float(int(receipt_str[-1]))
    features['second_last_digit'] = float(int(receipt_str[-2]))
    
    # Mileage tiers
    features['tier1_miles'] = min(miles, 100)
    features['tier2_miles'] = max(0, min(miles - 100, 300))
    features['tier3_miles'] = max(0, miles - 400)
    
    # Efficiency features
    mpd = features['miles_per_day']
    features['efficiency_bonus'] = float(180 <= mpd <= 220)
    features['high_efficiency'] = float(mpd > 200)
    features['low_efficiency'] = float(mpd < 50)
    
    # Spending categories
    rpd = features['receipts_per_day']
    features['low_spend'] = float(rpd < 100)
    features['medium_spend'] = float(100 <= rpd < 300)
    features['high_spend'] = float(300 <= rpd < 500)
    features['very_high_spend'] = float(rpd >= 500)
    
    # Interaction features
    features['days_x_miles'] = days * miles
    features['days_x_receipts'] = days * receipts
    features['miles_x_receipts'] = miles * receipts
    features['efficiency_x_receipts'] = features['miles_per_day'] * receipts
    
    # Ratio features
    features['miles_to_receipts'] = miles / (receipts + 1)
    features['receipts_to_miles'] = receipts / (miles + 1)
    features['days_to_miles'] = days / (miles + 1)
    
    # Return as list in the exact order expected by the model
    feature_names = ['days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day', 'total_input', 'is_1_day', 'is_2_day', 'is_3_day', 'is_4_day', 'is_5_day', 'is_weekend', 'log_receipts', 'sqrt_receipts', 'receipts_squared', 'receipts_cubed', 'ends_49', 'ends_99', 'ends_00', 'last_digit', 'second_last_digit', 'tier1_miles', 'tier2_miles', 'tier3_miles', 'efficiency_bonus', 'high_efficiency', 'low_efficiency', 'low_spend', 'medium_spend', 'high_spend', 'very_high_spend', 'days_x_miles', 'days_x_receipts', 'miles_x_receipts', 'efficiency_x_receipts', 'miles_to_receipts', 'receipts_to_miles', 'days_to_miles']
    return [features[name] for name in feature_names]
