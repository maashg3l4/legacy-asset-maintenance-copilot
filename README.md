# ⚙️ Legacy Asset Maintenance Copilot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-660066?logo=mqtt&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq-f55036)
![ML](https://img.shields.io/badge/ML-Isolation%20Forest-green)

**Live Demo:** [https://legacy-asset-maintenance-copilot-4.streamlit.app/](https://legacy-asset-maintenance-copilot-4.streamlit.app/)

## 🎯 The Problem
Legacy industrial machines lack modern sensors, and unplanned downtime costs factories millions. Most AI projects fail in production because they focus only on model accuracy, ignoring the realities of **alarm fatigue**, **operational context**, and **technician trust**.

## 🏛️ The Solution
An end-to-end, event-driven **Prescriptive Maintenance System**. It ingests raw vibration telemetry, detects anomalies, and uses an LLM to generate actionable maintenance reports for technicians.

### 🔄 System Architecture
```mermaid
flowchart LR
    %% Subgraphs for Enterprise Look
    subgraph Edge [🏭 Edge Layer]
        S[Sensor Simulator
(Colab)]
    end

    subgraph Cloud [☁️ Cloud Backend]
        M(MQTT Broker
HiveMQ)
        I{Anomaly Engine
Isolation Forest}
        L[GenAI Copilot
Groq Llama-3]
    end

    subgraph Frontend [💻 Frontend]
        D[Streamlit Dashboard
Cloud]
    end

    %% Connections
    S -- Telemetry --> M
    M -- Data Stream --> I
    I -- Anomaly Detected --> L
    L -- JSON Alert --> M
    M -- Live Updates --> D

    %% Node Styling (World-Class Colors)
    style S fill:#333,stroke:#fff,stroke-width:2px,color:#fff
    style M fill:#660066,stroke:#fff,stroke-width:2px,color:#fff
    style I fill:#FF4B4B,stroke:#fff,stroke-width:2px,color:#fff
    style L fill:#f55036,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#00BFFF,stroke:#fff,stroke-width:2px,color:#fff
```

## ✨ Key Features
* **📡 Real-Time Telemetry:** Streams continuous vibration data (RMS & Kurtosis) over MQTT.
* **🧠 Hybrid Anomaly Detection:** Uses an Isolation Forest for statistical anomaly detection, gated by physics-based rules (`RMS > 0.20`) to eliminate false positives.
* **🤖 GenAI Copilot (Groq):** When an anomaly is confirmed, it calls the Groq API to generate a strict JSON maintenance plan (Hypothesis, Severity, Actions, Parts).
* **💬 RAG Chatbot:** An embedded Retrieval-Augmented Generation chatbot allows technicians to query a maintenance manual. It uses **FAISS** and **SentenceTransformers** to ensure answers are grounded in actual documentation.
* **🛡️ Rate-Limit Resilience:** Implements a model fallback system to handle API rate limits gracefully.

## 🚨 Honest Limitations (Engineering Transparency)
1. **Simulated Data:** The current `publisher.py` uses a physics-inspired synthetic data generator (exponential degradation). It does not yet connect to physical hardware (e.g., ESP32 + MPU6050).
2. **Cloud Dependency:** The backend runs in Google Colab. If the Colab runtime disconnects, the data stream stops.
3. **Binary Status:** The system detects 'Anomaly vs. Normal'. It does not yet predict Remaining Useful Life (RUL) in hours.

## 🛠️ Tech Stack
* **Backend:** Python, Paho-MQTT, Scikit-learn
* **LLM Integration:** Groq API (`openai/gpt-oss-20b`)
* **RAG Pipeline:** FAISS, SentenceTransformers (`all-MiniLM-L6-v2`)
* **Frontend:** Streamlit, Plotly, Pandas
* **Deployment:** Streamlit Community Cloud, HiveMQ (Public Broker)

## 🚀 How to Run Locally
1. Clone the repo: `git clone https://github.com/maashg3l4/legacy-asset-maintenance-copilot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API Key to `inference_engine.py` or set it as an environment variable.
4. Run the Streamlit app: `streamlit run app.py`
5. Run the publisher (e.g., in a separate terminal/Colab): `python publisher.py`

---
*Built with a focus on Industrial IoT, MLOps principles, and Human-in-the-Loop AI.*