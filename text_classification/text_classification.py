#!/usr/bin/env python3
"""
Text Classification with HuggingFace Transformers
Simple example using a pre-trained sentiment analysis model
"""

from transformers import pipeline
import torch

def main():
    print("Loading pre-trained text classification model...")
    print(f"PyTorch version: {torch.__version__}")
    
    # Load a pre-trained sentiment analysis pipeline
    # This uses a BERT-based model fine-tuned for sentiment analysis
    classifier = pipeline(
        "text-classification",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        top_k=None  # Return all scores
    )
    
    # Sample texts for inference
    sample_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is the worst experience I've ever had. Terrible!",
        "The weather is okay today, nothing special.",
        "I'm excited about the new features in this update!",
        "The service was disappointing and slow."
    ]
    
    print("\n" + "="*60)
    print("RUNNING TEXT CLASSIFICATION INFERENCE")
    print("="*60)
    
    # Run inference on sample texts
    for i, text in enumerate(sample_texts, 1):
        print(f"\nSample {i}: {text}")
        print("-" * 50)
        
        # Get predictions
        results = classifier(text)
        
        # Display results - results is a list containing one prediction set
        prediction_scores = results[0] if isinstance(results, list) and len(results) > 0 else results
        
        # If top_k=None, we get all scores as a list
        if isinstance(prediction_scores, list):
            for result in prediction_scores:
                label = result['label']
                score = result['score']
                print(f"  {label}: {score:.4f} ({score*100:.1f}%)")
            
            # Get the top prediction
            top_prediction = max(prediction_scores, key=lambda x: x['score'])
            print(f"  → Prediction: {top_prediction['label']} (confidence: {top_prediction['score']*100:.1f}%)")
        else:
            # Single prediction
            label = prediction_scores['label']
            score = prediction_scores['score']
            print(f"  {label}: {score:.4f} ({score*100:.1f}%)")
            print(f"  → Prediction: {label} (confidence: {score*100:.1f}%)")

if __name__ == "__main__":
    main()