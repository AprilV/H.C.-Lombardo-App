#!/usr/bin/env python3
"""
Simple HuggingFace Text Classification Example
Using DistilBERT to classify a sample sentence
"""

from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

def main():
    print("HuggingFace Text Classification Example")
    print("=" * 50)
    
    # Step 1: Load model and tokenizer
    print("Loading DistilBERT model and tokenizer...")
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForSequenceClassification.from_pretrained(model_name)
    
    # Sample sentence to classify
    sample_sentence = "This movie is absolutely fantastic and entertaining!"
    print(f"\nSample sentence: '{sample_sentence}'")
    
    # Step 2: Tokenize input
    print("\nTokenizing input...")
    inputs = tokenizer(sample_sentence, return_tensors="pt")
    print(f"Input tokens: {tokenizer.tokenize(sample_sentence)}")
    print(f"Input IDs shape: {inputs['input_ids'].shape}")
    
    # Step 3: Pass through model
    print("\nPassing through model...")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
    
    # Step 4: Print result
    print("\nResults:")
    print(f"Raw logits: {logits[0].tolist()}")
    
    # Get prediction
    predicted_class = torch.argmax(logits, dim=-1).item()
    confidence = probabilities[0][predicted_class].item()
    
    # Map to labels
    labels = {0: "NEGATIVE", 1: "POSITIVE"}
    prediction = labels[predicted_class]
    
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
    
    # Show all probabilities
    print(f"\nAll probabilities:")
    for i, prob in enumerate(probabilities[0]):
        print(f"  {labels[i]}: {prob.item():.4f} ({prob.item()*100:.1f}%)")

if __name__ == "__main__":
    main()