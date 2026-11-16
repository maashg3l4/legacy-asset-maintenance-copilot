import streamlit as st
import paho.mqtt.client as mqtt
import json, pandas as pd, plotly.graph_objects as go
from datetime import datetime
import time, threading, queue
from rag_engine import get_answer

st.set_page_config(page_title="Maintenance Copilot", layout="wide")

css = "<style>.metric-box { padding: 15px; border-radius: 10px; background-color: #1E2129; text-align: center; border: 1px solid #333; } .metric-val { font-size: 32px; font-weight: bold; color: #00BFFF; } .status-normal { color: #00FF00; font-weight: bold; font-size: 24px; } .status-critical { color: #FF4B4B; font-weight: bold; font-size: 24px; animation: blinker 1s linear infinite; } @keyframes blinker { 50% { opacity: 0; } } .alert-card { padding: 20px; border-radius: 10px; background-color: #2E1C1C; border-left: 5px solid #FF4B4B; margin-top: 20px; color: white;}</style>"
st.markdown(css, unsafe_allow_html=True)
st.title("⚙️ Legacy Asset Maintenance Copilot")

if 'mqtt_queue' not in st.session_state:
    st.session_state.mqtt_queue = queue.Queue()
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Time", "RMS", "Kurtosis"])
if 'is_critical' not in st.session_state:
    st.session_state.is_critical = False
if 'latest_alert' not in st.session_state:
    st.session_state.latest_alert = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource
def start_mqtt(_q):
    def on_connect(client, userdata, flags, rc, properties):
        client.subscribe("aegisvision/factory/motor_01/telemetry")
        client.subscribe("aegisvision/factory/motor_01/alerts")
    def on_message(client, userdata, msg):
        _q.put((msg.topic, json.loads(msg.payload.decode())))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    return True

start_mqtt(st.session_state.mqtt_queue)

while not st.session_state.mqtt_queue.empty():
    topic, data = st.session_state.mqtt_queue.get_nowait()
    if "telemetry" in topic:
        rms = data.get("rms", 0.0)
        kurt = data.get("kurtosis", 0.0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if len(st.session_state.history) == 0 or st.session_state.history.iloc[-1]["Time"] != timestamp:
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame({"Time": [timestamp], "RMS": [rms], "Kurtosis": [kurt]})], ignore_index=True).tail(50)
        if rms < 0.18: st.session_state.is_critical = False
    elif "alerts" in topic:
        st.session_state.is_critical = True
        st.session_state.latest_alert = data

col1, col2, col3 = st.columns(3)
if not st.session_state.history.empty:
    latest = st.session_state.history.iloc[-1]
    col1.markdown(f'<div class="metric-box"><p>Live RMS</p><div class="metric-val">{latest["RMS"]:.3f}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-box"><p>Live Kurtosis</p><div class="metric-val">{latest["Kurtosis"]:.2f}</div></div>', unsafe_allow_html=True)
    status = "CRITICAL" if st.session_state.is_critical else "NORMAL"
    color = "status-critical" if st.session_state.is_critical else "status-normal"
    col3.markdown(f'<div class="metric-box"><p>Status</p><div class="{color}">{status}</div></div>', unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Scatter(x=st.session_state.history["Time"], y=st.session_state.history["RMS"], line=dict(color='#00BFFF', width=2))])
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

if st.session_state.latest_alert and st.session_state.is_critical:
    alert = st.session_state.latest_alert
    st.markdown(f'<div class="alert-card"><h3>🚨 AI COPILOT DIAGNOSIS</h3><p><strong>Hypothesis:</strong> {alert.get("hypothesis")}</p><p><strong>Actions:</strong> {", ".join(alert.get("actions", []))}</p></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("💬 Ask the Maintenance Copilot")
user_query = st.chat_input("Ask about bearing maintenance...")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.spinner("Thinking..."):
        answer = get_answer(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

time.sleep(1)
st.rerun()
