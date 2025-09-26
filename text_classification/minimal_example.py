#!/usr/bin/env python3
"""
Minimal HuggingFace Classification Example
Clean 4-step implementation
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
print("1. Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# Tokenize input
print("2. Tokenizing input...")
sentence = "This product is incredible! Highly recommended."
inputs = tokenizer(sentence, return_tensors="pt")
print(f"   Sentence: '{sentence}'")

# Pass through model  
print("3. Passing through model...")
with torch.no_grad():
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=-1).item()
    confidence = torch.softmax(outputs.logits, dim=-1).max().item()

# Print result
print("4. Result:")
labels = ["NEGATIVE", "POSITIVE"]
print(f"   Prediction: {labels[prediction]}")
print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
print(f"   Raw logits: {outputs.logits[0].tolist()}")