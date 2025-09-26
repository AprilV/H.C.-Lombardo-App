#!/usr/bin/env python3
"""
HuggingFace Text Classification with BERT
Clean example following the expected steps
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def classify_text():
    print("Text Classification with HuggingFace BERT")
    print("=" * 45)
    
    # Load model and tokenizer
    print("Step 1: Loading model and tokenizer...")
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print(f"✓ Loaded: {model_name}")
    
    # Sample sentence
    sentence = "I love this new smartphone! It's amazing and works perfectly."
    print(f"\nSentence to classify: '{sentence}'")
    
    # Tokenize input
    print("\nStep 2: Tokenize input...")
    tokens = tokenizer.tokenize(sentence)
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    print(f"✓ Tokens: {tokens[:8]}...")  # Show first 8 tokens
    print(f"✓ Input shape: {inputs['input_ids'].shape}")
    
    # Pass through model
    print("\nStep 3: Pass through model...")
    model.eval()  # Set to evaluation mode
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
    
    print(f"✓ Model output shape: {logits.shape}")
    print(f"✓ Logits: {[f'{x:.2f}' for x in logits[0].tolist()]}")
    
    # Print result
    print("\nStep 4: Print result...")
    
    # Get prediction
    predicted_id = torch.argmax(logits, dim=-1).item()
    confidence = probs[0][predicted_id].item()
    
    # Label mapping for 5-star rating system
    star_labels = {
        0: "1 star (very negative)",
        1: "2 stars (negative)", 
        2: "3 stars (neutral)",
        3: "4 stars (positive)",
        4: "5 stars (very positive)"
    }
    
    print(f"✓ Predicted class: {predicted_id}")
    print(f"✓ Prediction: {star_labels[predicted_id]}")
    print(f"✓ Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
    
    print(f"\nFull probability distribution:")
    for i, prob in enumerate(probs[0]):
        print(f"  {star_labels[i]}: {prob.item():.3f} ({prob.item()*100:.1f}%)")

# Run the classification
if __name__ == "__main__":
    classify_text()