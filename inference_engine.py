import paho.mqtt.client as mqtt
import json, numpy as np, time, os
from groq import Groq

# ⚠️ PUT YOUR API KEY HERE
try:
    groq_client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
except:
    groq_client = None

anomaly_streak = 0
current_state = "NORMAL"

def call_groq_api(rms, kurtosis_val):
    alert_json = {}
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a maintenance copilot. Output strict JSON with keys: hypothesis, severity, actions, parts, downtime."},
                    {"role": "user", "content": f"Context: Outer-race bearing degradation. Evidence: RMS={rms:.3f}, Kurtosis={kurtosis_val:.3f}"}
                ],
                model="openai/gpt-oss-20b",
                response_format={"type": "json_object"}
            )
            alert_json = json.loads(completion.choices[0].message.content)
        except Exception as e:
            print("Groq Error:", e)
            
    if not alert_json:
        alert_json = {
            "hypothesis": "Outer-race bearing degradation",
            "severity": "HIGH",
            "actions": ["Schedule inspection within 24 hours", "Check lubrication"],
            "parts": ["Bearing SKF-6205-2RS"],
            "downtime": "2.0 hours"
        }
        
    with open("latest_alert.json", "w") as f:
        json.dump(alert_json, f)

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("aegisvision/factory/motor_01/vibration")

def on_message(client, userdata, msg):
    global anomaly_streak, current_state
    payload = json.loads(msg.payload.decode())
    features = np.array([payload["features"]])
    rms = float(features[0][0])
    kurtosis_val = float(features[0][1])
    
    with open("latest_telemetry.json", "w") as f:
        json.dump({"rms": rms, "kurtosis": kurtosis_val}, f)

    if rms > 0.20:
        anomaly_streak += 1
    else:
        anomaly_streak = 0

    if anomaly_streak >= 3 and current_state != "CRITICAL":
        current_state = "CRITICAL"
        call_groq_api(rms, kurtosis_val)
        
    elif anomaly_streak == 0 and current_state == "CRITICAL":
        current_state = "NORMAL"
        if os.path.exists("latest_alert.json"):
            os.remove("latest_alert.json")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
