#!/usr/bin/env python3
"""
Simple HuggingFace BERT Classification Script
Alternative using BERT model for text classification
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def main():
    # Load HuggingFace BERT model (alternative to Gemma)
    print("Loading BERT model and tokenizer...")
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Input sentence
    sentence = "This new phone is absolutely amazing and works perfectly!"
    print(f"Input: '{sentence}'")
    
    # Tokenize sentence
    print("Tokenizing...")
    inputs = tokenizer(sentence, return_tensors="pt")
    print(f"Tokens: {tokenizer.tokenize(sentence)}")
    
    # Get model output
    print("Running inference...")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    
    # Print logits
    print(f"Output logits: {[f'{x:.2f}' for x in logits[0].tolist()]}")
    
    # Classification result
    prediction = torch.argmax(logits, dim=-1).item()
    probabilities = torch.softmax(logits, dim=-1)
    confidence = probabilities[0][prediction].item()
    
    # Labels for 5-star system
    labels = ["1-star", "2-star", "3-star", "4-star", "5-star"]
    
    print(f"Classification: {labels[prediction]}")
    print(f"Confidence: {confidence:.3f} ({confidence*100:.1f}%)")

if __name__ == "__main__":
    main()