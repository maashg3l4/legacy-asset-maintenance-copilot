import numpy as np
from scipy.stats import ks_2samp
import json

# Baseline distribution (from training)
BASELINE_RMS = np.random.normal(0.12, 0.02, 1000)

def check_drift(latest_rms_values: list) -> bool:
    """
    Detects data drift using the KS test.
    Returns True if drift is detected (p-value < 0.05).
    """
    if len(latest_rms_values) < 50:
        return False
        
    stat, p_value = ks_2samp(BASELINE_RMS, latest_rms_values)
    
    if p_value < 0.05:
        print(f"⚠️ DRIFT DETECTED! KS stat: {stat:.4f}, p-value: {p_value:.4f}")
        # Trigger retraining pipeline here
        return True
    return False
