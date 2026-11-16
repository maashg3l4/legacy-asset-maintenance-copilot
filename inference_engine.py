import paho.mqtt.client as mqtt
import json, numpy as np, os, time
from groq import Groq

# ⚠️ PASTE YOUR REAL KEY HERE
groq_client = Groq(api_key="YOUR_GROQ_KEY_HERE")

# Switched to the high-limit model
MODEL_NAME = "llama-3.1-8b-instant" 

anomaly_streak = 0
current_state = "NORMAL"
last_api_call_time = 0  # Cooldown tracker
COOLDOWN_SECONDS = 60   # Wait 60s between API calls

def call_groq_api(rms, kurtosis_val, client):
    global last_api_call_time
    print(f"Calling Groq API for RMS={rms:.3f}...")
    
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a maintenance copilot. Output strict JSON with keys: hypothesis, severity, actions, parts, downtime."},
                {"role": "user", "content": f"Context: Outer-race bearing degradation. Evidence: RMS={rms:.3f}, Kurtosis={kurtosis_val:.3f}"}
            ],
            model=MODEL_NAME,
            response_format={"type": "json_object"}
        )
        alert_json = json.loads(completion.choices[0].message.content)
        print(f"✅ Groq Success with {MODEL_NAME}")
    except Exception as e:
        print(f"❌ GROQ ERROR: {e}")
        alert_json = {"hypothesis": "FALLBACK: Outer-race degradation", "severity": "HIGH", "actions": ["Inspect bearing"], "parts": ["SKF-6205-2RS"], "downtime": "2 hours"}
        
    client.publish("aegisvision/factory/motor_01/alerts", json.dumps(alert_json))
    last_api_call_time = time.time() # Reset cooldown timer

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("aegisvision/factory/motor_01/vibration")

def on_message(client, userdata, msg):
    global anomaly_streak, current_state, last_api_call_time
    payload = json.loads(msg.payload.decode())
    features = np.array([payload["features"]])
    rms = float(features[0][0])
    kurtosis_val = float(features[0][1])
    
    client.publish("aegisvision/factory/motor_01/telemetry", json.dumps({"rms": rms, "kurtosis": kurtosis_val}))

    if rms > 0.20:
        anomaly_streak += 1
    else:
        anomaly_streak = 0

    current_time = time.time()
    
    # Check if we are in an anomaly AND the cooldown has expired
    if anomaly_streak >= 3 and current_state != "CRITICAL" and (current_time - last_api_call_time > COOLDOWN_SECONDS):
        current_state = "CRITICAL"
        call_groq_api(rms, kurtosis_val, client)
        
    elif anomaly_streak == 0 and current_state == "CRITICAL":
        current_state = "NORMAL"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
