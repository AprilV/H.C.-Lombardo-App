#!/usr/bin/env python3
"""
Ultra-Simple HuggingFace Script
Minimal code to demonstrate text classification
"""

from transformers import pipeline
import torch

print("Simple HuggingFace Text Classification")
print("=" * 40)

# Load model using pipeline (simplest approach)
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Input sentence
sentence = "This is an excellent product! I love it!"
print(f"Input: '{sentence}'")

# Get classification result
result = classifier(sentence)[0]
print(f"Result: {result}")

# For more detailed output, let's also show manual approach
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# Tokenize and get logits
inputs = tokenizer(sentence, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits

print(f"Logits: {logits[0].tolist()}")
print(f"Tokens: {tokenizer.tokenize(sentence)}")