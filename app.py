import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import os

st.set_page_config(page_title="Maintenance Copilot", layout="wide")

css = "<style>.metric-box { padding: 15px; border-radius: 10px; background-color: #1E2129; text-align: center; border: 1px solid #333; } .metric-val { font-size: 32px; font-weight: bold; color: #00BFFF; } .status-normal { color: #00FF00; font-weight: bold; font-size: 24px; } .status-critical { color: #FF4B4B; font-weight: bold; font-size: 24px; animation: blinker 1s linear infinite; } @keyframes blinker { 50% { opacity: 0; } } .alert-card { padding: 20px; border-radius: 10px; background-color: #2E1C1C; border-left: 5px solid #FF4B4B; margin-top: 20px; color: white;}</style>"
st.markdown(css, unsafe_allow_html=True)

st.title("⚙️ Legacy Asset Maintenance Copilot")
st.markdown("**Asset:** MOTOR-01 | **Location:** Plant A | **Mode:** Live Telemetry")

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Time", "RMS", "Kurtosis"])
if 'is_critical' not in st.session_state:
    st.session_state.is_critical = False

data_path = "latest_telemetry.json"
alert_path = "latest_alert.json"

# Read live data
if os.path.exists(data_path):
    with open(data_path, "r") as f:
        try:
            data = json.load(f)
            rms = data.get("rms", 0.0)
            kurt = data.get("kurtosis", 0.0)
            
            # If file exists, we know it's an alert
            if os.path.exists(alert_path):
                st.session_state.is_critical = True
                
            if rms < 0.15:
                 st.session_state.is_critical = False

            timestamp = datetime.now().strftime("%H:%M:%S")
            if len(st.session_state.history) == 0 or st.session_state.history.iloc[-1]["Time"] != timestamp:
                new_row = pd.DataFrame({"Time": [timestamp], "RMS": [rms], "Kurtosis": [kurt]})
                st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True).tail(50)
        except:
            pass

col1, col2, col3 = st.columns(3)
if not st.session_state.history.empty:
    latest = st.session_state.history.iloc[-1]
    col1.markdown(f'<div class="metric-box"><p>Live RMS Vibration</p><div class="metric-val">{latest["RMS"]:.3f}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-box"><p>Live Kurtosis</p><div class="metric-val">{latest["Kurtosis"]:.2f}</div></div>', unsafe_allow_html=True)
    
    if st.session_state.is_critical:
        col3.markdown('<div class="metric-box"><p>System Status</p><div class="status-critical">🚨 CRITICAL</div></div>', unsafe_allow_html=True)
    else:
        col3.markdown('<div class="metric-box"><p>System Status</p><div class="status-normal">✅ NORMAL</div></div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history["Time"], y=st.session_state.history["RMS"], mode='lines', name='RMS', line=dict(color='#00BFFF', width=2)))
    fig.update_layout(title="Vibration Trend (RMS)", template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20), yaxis_title="RMS (g)")
    st.plotly_chart(fig, use_container_width=True)
else:
    col1.markdown('<div class="metric-box"><p>Live RMS</p><div class="metric-val">--</div></div>', unsafe_allow_html=True)
    col2.markdown('<div class="metric-box"><p>Live Kurtosis</p><div class="metric-val">--</div></div>', unsafe_allow_html=True)
    col3.markdown('<div class="metric-box"><p>System Status</p><div class="status-normal">WAITING</div></div>', unsafe_allow_html=True)

if os.path.exists(alert_path) and st.session_state.is_critical:
    with open(alert_path, "r") as f:
        try:
            alert = json.load(f)
            st.markdown(f'<div class="alert-card"><h3>🚨 AI COPILOT DIAGNOSIS</h3><p><strong>Hypothesis:</strong> {alert.get("hypothesis", "N/A")}</p><p><strong>Severity:</strong> {alert.get("severity", "N/A")}</p><p><strong>Actions:</strong> {", ".join(alert.get("actions", []))}</p><p><strong>Parts:</strong> {", ".join(alert.get("parts", []))}</p></div>', unsafe_allow_html=True)
            if st.button("Acknowledge"):
                st.session_state.is_critical = False
                st.rerun()
        except:
            pass

time.sleep(1)
st.rerun()
