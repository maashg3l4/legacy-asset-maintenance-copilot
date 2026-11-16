import paho.mqtt.client as mqtt
import json, numpy as np, time, os, joblib
from groq import Groq
from sklearn.ensemble import IsolationForest

# 1. Load the Real ML Model
# If the file doesn't exist, we train a quick one for the demo
if not os.path.exists("isolation_forest_v1.joblib"):
    print("Training Isolation Forest...")
    X_train = np.random.normal(0.12, 0.02, (500, 4))  # Normal baseline
    model = IsolationForest(contamination=0.05, random_state=42).fit(X_train)
    joblib.dump(model, "isolation_forest_v1.joblib")
else:
    model = joblib.load("isolation_forest_v1.joblib")

try:
    groq_client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
except:
    groq_client = None

anomaly_streak = 0
current_state = "NORMAL"

def call_groq_api(rms, kurtosis_val, client):
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
        alert_json = {"hypothesis": "Outer-race bearing degradation", "severity": "HIGH", "actions": ["Inspect bearing", "Check lubrication"], "parts": ["SKF-6205-2RS"]}
        
    client.publish("aegisvision/factory/motor_01/alerts", json.dumps(alert_json))

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("aegisvision/factory/motor_01/vibration")

def on_message(client, userdata, msg):
    global anomaly_streak, current_state
    payload = json.loads(msg.payload.decode())
    features = np.array([payload["features"]])
    rms = float(features[0][0])
    kurtosis_val = float(features[0][1])
    
    # Broadcast live telemetry for the dashboard
    client.publish("aegisvision/factory/motor_01/telemetry", json.dumps({"rms": rms, "kurtosis": kurtosis_val}))

    # --- LAYER 1: ML PREDICTION ---
    ml_pred = model.predict(features)[0]  # -1 = anomaly, 1 = normal
    is_ml_anomaly = (ml_pred == -1)

    # --- LAYER 2: HYBRID RULE (Operationally Relevant) ---
    is_rule_anomaly = (rms > 0.20)  # Physical threshold

    # Only trigger if BOTH agree (prevents false alarms)
    is_real_anomaly = is_ml_anomaly and is_rule_anomaly

    if is_real_anomaly:
        anomaly_streak += 1
    else:
        anomaly_streak = 0

    if anomaly_streak >= 3 and current_state != "CRITICAL":
        current_state = "CRITICAL"
        call_groq_api(rms, kurtosis_val, client)
        
    elif anomaly_streak == 0 and current_state == "CRITICAL":
        current_state = "NORMAL"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
