# Legacy Asset Maintenance Copilot

**A Multimodal Predictive Maintenance System for Legacy Industrial Assets**

This project aims to bridge the gap between modern AI and aging industrial infrastructure. Instead of relying on clean, curated datasets, this system is designed to handle the messy reality of legacy equipment: noisy sensors, missing data, and disconnected maintenance records.

## 🎯 Project Goal
To build an explainable, human-in-the-loop maintenance decision system that answers:
- *What* is abnormal?
- *Which* component is affected?
- *How urgent* is it?
- *What evidence* supports the decision?
- *What action* should be taken?

## 🏗️ Architecture (High-Level)
The system follows a layered architecture:
1.  **Edge Simulation:** Python scripts replaying public datasets (CWRU, NASA IMS) via MQTT.
2.  **Data Pipeline:** MQTT Broker → FastAPI → Time-Series Database (InfluxDB).
3.  **AI Core:** Anomaly Detection (Isolation Forest, Autoencoders) + Rule-Based Logic.
4.  **Application:** Streamlit Dashboard with Technician Feedback Loop.

*(Detailed architecture diagrams will be added in Phase 2)*

## 📊 Week 1 Progress: Data Foundation
**Objective:** Validate the ability to load, process, and extract features from the CWRU Bearing Dataset.

**Key Findings:**
- Successfully loaded normal (`97.mat`) and faulty (`105.mat`) baseline signals.
- Extracted time-domain features: **RMS** and **Kurtosis**.
- *Observation:* The faulty signal exhibits significantly higher Kurtosis, indicating sharp impulses characteristic of bearing defects.

**Initial Results:**
| Signal Type | RMS | Kurtosis |
| :--- | :--- | :--- |
| Normal | (Your Value) | (Your Value) |
| Faulty | (Your Value) | (Your Value) |

*(The plot generated in Colab will be inserted here)*

## 🛠️ Tech Stack (Planned)
- **Data & AI:** Python, Scikit-learn, PyTorch, SciPy
- **Backend:** FastAPI, MQTT (Mosquitto)
- **Database:** InfluxDB / TimescaleDB
- **Frontend:** Streamlit
- **Deployment:** Hugging Face Spaces / Oracle Cloud Free Tier

## 🚀 Future Roadmap
- **Week 2:** Simulate live MQTT stream from CWRU data.
- **Week 3:** Train Isolation Forest for unsupervised anomaly detection.
- **Week 4:** Build Streamlit dashboard for real-time monitoring.

## ⚠️ Honest Limitations
- Public datasets do not fully represent real factory conditions.
- The system will initially be validated in "shadow mode" (read-only).
- This is a portfolio project demonstrating production engineering principles, not a commercial product.
