#!/usr/bin/env python3
"""
Simple Text Classification with HuggingFace Transformers
Alternative approach using BERT model for sentiment analysis
"""

from transformers import pipeline
import torch

def main():
    print("Loading pre-trained BERT sentiment analysis model...")
    print(f"PyTorch version: {torch.__version__}")
    
    # Load a simpler sentiment analysis pipeline
    # Using the default sentiment analysis model
    classifier = pipeline("sentiment-analysis")
    
    # Sample texts for inference
    sample_texts = [
        "I absolutely love this new phone!",
        "This movie was terrible and boring.",
        "The food was okay, nothing extraordinary.",
        "Amazing customer service and fast delivery!",
        "I hate waiting in long lines."
    ]
    
    print("\n" + "="*50)
    print("SIMPLE SENTIMENT ANALYSIS")
    print("="*50)
    
    # Run inference on sample texts
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{i}. Text: {text}")
        
        # Get prediction
        result = classifier(text)[0]  # Get first result
        
        label = result['label']
        score = result['score']
        
        print(f"   Prediction: {label}")
        print(f"   Confidence: {score:.4f} ({score*100:.1f}%)")
        print("-" * 30)

if __name__ == "__main__":
    main()