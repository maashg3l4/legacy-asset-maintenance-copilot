import paho.mqtt.client as mqtt
import json, numpy as np, os, time, random
from groq import Groq, RateLimitError

# ⚠️ PASTE YOUR REAL KEY HERE
groq_client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")

FALLBACK_MODELS = ["openai/gpt-oss-20b", "llama-3.1-8b-instant"]

anomaly_streak = 0
current_state = "NORMAL"

def call_groq_with_fallback(rms, kurtosis_val, client):
    prompt = f"Context: Outer-race bearing degradation. Evidence: RMS={rms:.3f}, Kurtosis={kurtosis_val:.3f}. Output strict JSON with keys: hypothesis, severity, actions, parts, downtime."
    
    for model_name in FALLBACK_MODELS:
        try:
            completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a maintenance copilot. Output strict JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=model_name,
                response_format={"type": "json_object"}
            )
            alert_json = json.loads(completion.choices[0].message.content)
            client.publish("aegisvision/factory/motor_01/alerts", json.dumps(alert_json))
            print(f"✅ Groq Success with {model_name}")
            return
        except RateLimitError:
            print(f"⏳ Rate limit on {model_name}, falling back...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            
    # Hard fallback if all models fail
    print("❌ All models failed. Using hardcoded fallback.")
    fallback_json = {"hypothesis": "Outer-race bearing degradation", "severity": "HIGH", "actions": ["Inspect bearing"], "parts": ["SKF-6205-2RS"]}
    client.publish("aegisvision/factory/motor_01/alerts", json.dumps(fallback_json))

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("aegisvision/factory/motor_01/vibration")

def on_message(client, userdata, msg):
    global anomaly_streak, current_state
    payload = json.loads(msg.payload.decode())
    features = np.array([payload["features"]])
    rms = float(features[0][0])
    kurtosis_val = float(features[0][1])
    
    client.publish("aegisvision/factory/motor_01/telemetry", json.dumps({"rms": rms, "kurtosis": kurtosis_val}))

    if rms > 0.20:
        anomaly_streak += 1
    else:
        anomaly_streak = 0

    if anomaly_streak >= 3 and current_state != "CRITICAL":
        current_state = "CRITICAL"
        call_groq_with_fallback(rms, kurtosis_val, client)
    elif anomaly_streak == 0 and current_state == "CRITICAL":
        current_state = "NORMAL"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
