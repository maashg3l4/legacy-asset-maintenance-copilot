import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embedder = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

MANUAL_TEXT = """
BEARING MAINTENANCE MANUAL - SECTION 4.2
Fault: Outer-Race Bearing Degradation
Symptoms: High vibration RMS (>0.25g), elevated kurtosis (>4.0).
Immediate Action: Schedule vibration inspection within 24 hours.
Inspection Procedure: Remove bearing housing. Inspect outer race for spalling, pitting, or discoloration.
Corrective Action: Replace bearing with SKF-6205-2RS. Apply high-temp grease.
Estimated Downtime: 2.0 hours.
Required Parts: 1x Bearing SKF-6205-2RS, 50g High-temp grease.
"""

chunks = [chunk.strip() for chunk in MANUAL_TEXT.split("\n\n") if chunk.strip()]
embeddings = embedder.encode(chunks)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings).astype('float32'))

def get_answer(query: str) -> str:
    query_vec = embedder.encode([query]).astype('float32')
    _, indices = index.search(query_vec, 1)
    context = chunks[indices[0][0]]
    
    prompt = f"""You are a maintenance copilot. Use ONLY the provided manual context to answer.
    Manual Context: {context}
    Technician Query: {query}
    Provide a concise, actionable answer."""
    
    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
            temperature=0.1,
            max_tokens=200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
