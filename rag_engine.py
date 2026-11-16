import os, time, random
from groq import Groq, RateLimitError, APIError
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embedder = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# --- FALLBACK MODELS (Ordered by TPD) ---
FALLBACK_MODELS = [
    "openai/gpt-oss-20b",          # Primary: 200K TPD
    "llama-3.1-8b-instant",        # Secondary: 500K TPD
    "llama-3.3-70b-versatile"      # Tertiary: 100K TPD
]

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

def call_llm_with_fallback(prompt: str) -> str:
    """Tries models in order with exponential backoff on rate limits."""
    for model_name in FALLBACK_MODELS:
        for attempt in range(3):  # 3 retries per model
            try:
                completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_name,
                    temperature=0.1,
                    max_tokens=200
                )
                return completion.choices[0].message.content
            except RateLimitError as e:
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ Rate limit hit on {model_name}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"❌ Error with {model_name}: {e}")
                break  # Move to next model
    return "System busy. Please try again later."

def get_answer(query: str) -> str:
    query_vec = embedder.encode([query]).astype('float32')
    _, indices = index.search(query_vec, 1)
    context = chunks[indices[0][0]]
    
    prompt = f"""You are a maintenance copilot. Use ONLY the provided manual context to answer.
    Manual Context: {context}
    Technician Query: {query}
    Provide a concise, actionable answer."""
    
    return call_llm_with_fallback(prompt)
