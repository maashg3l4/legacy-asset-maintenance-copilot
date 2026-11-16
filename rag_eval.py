import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from rag_engine import get_answer, embedder, index, chunks
import numpy as np

def run_ragas_evaluation():
    print("🧪 Running RAGAS Evaluation...")
    
    # Golden Dataset for Industrial Maintenance
    test_questions = [
        "What parts do I need for an outer-race bearing?",
        "What is the immediate action for high vibration?",
        "What is the estimated downtime for bearing replacement?"
    ]
    
    # Build the evaluation dataset
    eval_data = []
    for q in test_questions:
        # Retrieve context manually for RAGAS
        query_vec = embedder.encode([q]).astype('float32')
        _, indices = index.search(query_vec, 1)
        context = chunks[indices[0][0]]
        
        # Get the LLM answer
        answer = get_answer(q)
        
        eval_data.append({
            "question": q,
            "answer": answer,
            "contexts": [context],
            "ground_truth": "Reference answer here (optional for basic metrics)"
        })
        
    dataset = Dataset.from_list(eval_data)
    
    # Evaluate using Groq as the judge LLM
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=your_groq_judge_client  # You must configure a judge LLM
    )
    
    print("📊 RAGAS Scores:")
    print(result)
    return result

if __name__ == "__main__":
    run_ragas_evaluation()
