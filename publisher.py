import numpy as np, json, time, paho.mqtt.client as mqtt
from scipy.stats import kurtosis

pub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
pub_client.connect("broker.hivemq.com", 1883, 60)
i = 0
print("Publisher started...")
while True:
    # 40k Normal, then 40k Faulty
    window = np.random.normal(0, 0.12 if (i // 40000) % 2 == 0 else 0.3, 1024)
    rms = float(np.sqrt(np.mean(window**2)))
    kurt = float(kurtosis(window))
    pub_client.publish("aegisvision/factory/motor_01/vibration", json.dumps({"sensor_id": "MOTOR-01", "features": [rms, kurt, 0.0, 0.0]}))
    i += 512
    time.sleep(0.05)
