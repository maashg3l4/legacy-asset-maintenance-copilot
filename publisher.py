import numpy as np, json, time, paho.mqtt.client as mqtt
from scipy.stats import kurtosis

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("broker.hivemq.com", 1883, 60)
print("📡 Publisher started (Realistic Degradation Curve)...")

i = 0
while True:
    # Simulate a 2-minute degradation cycle
    cycle_time = (i // 2000) % 120  # 0 to 120 seconds
    if cycle_time < 60:
        # Healthy Phase: Baseline RMS ~0.12
        rms_base = 0.12 + np.random.normal(0, 0.005)
    else:
        # Degrading Phase: Exponential rise from 0.12 to 0.30
        progress = (cycle_time - 60) / 60  # 0.0 to 1.0
        rms_base = 0.12 + (0.18 * (progress ** 2))  # Exponential curve
        rms_base += np.random.normal(0, 0.01)
    
    # Kurtosis spikes at onset (around progress=0.2) then falls
    if cycle_time >= 60 and cycle_time < 75:
        kurt = 5.0 + np.random.normal(0, 0.5)  # Spike
    elif cycle_time >= 75:
        kurt = 3.0 + np.random.normal(0, 0.2)  # Recovery
    else:
        kurt = 3.0 + np.random.normal(0, 0.2)  # Normal
        
    client.publish("aegisvision/factory/motor_01/vibration", json.dumps({"features": [float(rms_base), float(kurt), 0.0, 0.0]}))
    i += 1
    time.sleep(0.05)
