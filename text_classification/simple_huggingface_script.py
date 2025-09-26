#!/usr/bin/env python3
"""
Simple HuggingFace Text Classification Script
Loads DistilBERT, tokenizes a sentence, and prints logits/classification result
"""

from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Load HuggingFace DistilBERT model and tokenizer
print("Loading DistilBERT model and tokenizer...")
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name)

# Input sentence to classify
sentence = "I really enjoyed this movie, it was fantastic!"
print(f"\nInput sentence: '{sentence}'")

# Tokenize the sentence
print("\nTokenizing sentence...")
inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
tokens = tokenizer.tokenize(sentence)
print(f"Tokens: {tokens}")

# Get model predictions
print("\nGetting model predictions...")
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)

# Print output logits
print(f"\nOutput logits: {logits[0].tolist()}")

# Print classification result
predicted_class = torch.argmax(logits, dim=-1).item()
confidence = probabilities[0][predicted_class].item()

labels = {0: "NEGATIVE", 1: "POSITIVE"}
result = labels[predicted_class]

print(f"\nClassification Result:")
print(f"- Prediction: {result}")
print(f"- Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
print(f"- Probabilities: NEGATIVE={probabilities[0][0]:.4f}, POSITIVE={probabilities[0][1]:.4f}")