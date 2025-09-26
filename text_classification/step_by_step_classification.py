#!/usr/bin/env python3
"""
Step-by-Step Text Classification with HuggingFace Transformers
Manual implementation showing tokenization, model inference, and logit processing
"""

# Step 1: Import required libraries
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

def main():
    print("=" * 60)
    print("STEP-BY-STEP TEXT CLASSIFICATION WITH HUGGINGFACE")
    print("=" * 60)
    
    # Step 2: Load a text model and tokenizer from HuggingFace
    print("\nStep 2: Loading model and tokenizer...")
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    print(f"Model: {model_name}")
    
    # Load tokenizer and model separately for manual control
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Get model info
    print(f"Model type: {type(model).__name__}")
    print(f"Number of parameters: {model.num_parameters():,}")
    print(f"Model labels: {model.config.id2label}")
    
    # Sample text inputs
    sample_texts = [
        "I absolutely love this movie! It's fantastic!",
        "This product is terrible and disappointing.",
        "The weather is nice today.",
        "I'm so excited about this new opportunity!"
    ]
    
    print(f"\nProcessing {len(sample_texts)} sample texts...")
    print("-" * 60)
    
    # Process each text
    for i, text in enumerate(sample_texts, 1):
        print(f"\nSAMPLE {i}: {text}")
        print("=" * 50)
        
        # Step 3: Tokenize a sample text input
        print("Step 3: Tokenizing input text...")
        
        # Tokenize the text (manual approach)
        inputs = tokenizer(
            text,
            return_tensors="pt",  # Return PyTorch tensors
            padding=True,
            truncation=True,
            max_length=512,
            return_attention_mask=True
        )
        
        print(f"Input IDs shape: {inputs['input_ids'].shape}")
        print(f"Input IDs: {inputs['input_ids'][0].tolist()[:10]}... (first 10 tokens)")
        print(f"Attention mask: {inputs['attention_mask'][0].tolist()[:10]}... (first 10)")
        
        # Decode some tokens to show tokenization
        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        print(f"Tokens: {tokens[:10]}... (first 10)")
        
        # Step 4: Run the model and get prediction logits
        print("\nStep 4: Running model inference...")
        
        with torch.no_grad():  # Disable gradient computation for inference
            outputs = model(**inputs)
            logits = outputs.logits
        
        print(f"Raw logits: {logits[0].tolist()}")
        print(f"Logits shape: {logits.shape}")
        
        # Convert logits to probabilities using softmax
        probabilities = torch.softmax(logits, dim=-1)
        print(f"Probabilities: {probabilities[0].tolist()}")
        
        # Step 5: Print or decode the output
        print("\nStep 5: Decoding and interpreting output...")
        
        # Get predicted class
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        predicted_label = model.config.id2label[predicted_class_id]
        confidence = probabilities[0][predicted_class_id].item()
        
        print(f"Predicted class ID: {predicted_class_id}")
        print(f"Predicted label: {predicted_label}")
        print(f"Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
        
        # Show all class probabilities
        print("\nAll class probabilities:")
        for class_id, prob in enumerate(probabilities[0]):
            label = model.config.id2label[class_id]
            print(f"  {label}: {prob.item():.4f} ({prob.item()*100:.1f}%)")
        
        print("-" * 50)

if __name__ == "__main__":
    main()