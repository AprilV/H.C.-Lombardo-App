#!/usr/bin/env python3
"""
Step-by-Step Text Classification with BERT Model
Alternative implementation with detailed manual processing
"""

# Step 1: Import required libraries
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F

def main():
    print("=" * 60)
    print("STEP-BY-STEP TEXT CLASSIFICATION WITH BERT")
    print("=" * 60)
    
    # Step 2: Load a text model and tokenizer from HuggingFace
    print("\nStep 2: Loading BERT model and tokenizer...")
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    print(f"Model: {model_name}")
    
    # Load tokenizer and model
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name)
    
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    print(f"Model config: {model.config.num_labels} labels")
    
    # Sample text
    sample_text = "This is an amazing product! I love it so much!"
    print(f"\nSample text: '{sample_text}'")
    
    print("\n" + "=" * 60)
    
    # Step 3: Tokenize a sample text input
    print("Step 3: Manual tokenization process...")
    
    # Show tokenization step by step
    print(f"Original text: {sample_text}")
    
    # Add special tokens manually
    tokens = tokenizer.tokenize(sample_text)
    print(f"Tokenized words: {tokens}")
    
    # Convert to IDs
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    print(f"Token IDs: {token_ids}")
    
    # Add special tokens and create proper input
    inputs = tokenizer(
        sample_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )
    
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    
    print(f"Final input IDs: {input_ids[0].tolist()}")
    print(f"Attention mask: {attention_mask[0].tolist()}")
    print(f"Input shape: {input_ids.shape}")
    
    # Step 4: Run the model and get prediction logits
    print(f"\nStep 4: Model inference...")
    
    # Set model to evaluation mode
    model.eval()
    
    with torch.no_grad():
        # Forward pass
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
    
    print(f"Raw logits: {logits[0].tolist()}")
    print(f"Logits tensor shape: {logits.shape}")
    
    # Apply softmax to get probabilities
    probabilities = F.softmax(logits, dim=-1)
    print(f"Probabilities: {probabilities[0].tolist()}")
    
    # Step 5: Print or decode the output
    print(f"\nStep 5: Decoding results...")
    
    # Get prediction
    predicted_class = torch.argmax(logits, dim=-1).item()
    confidence = probabilities[0][predicted_class].item()
    
    # Map class to sentiment (this model uses 1-5 star rating)
    sentiment_labels = {0: "1 star (very negative)", 1: "2 stars (negative)", 
                       2: "3 stars (neutral)", 3: "4 stars (positive)", 
                       4: "5 stars (very positive)"}
    
    print(f"Predicted class index: {predicted_class}")
    print(f"Predicted sentiment: {sentiment_labels.get(predicted_class, f'Class {predicted_class}')}")
    print(f"Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
    
    print(f"\nDetailed probability breakdown:")
    for i, prob in enumerate(probabilities[0]):
        label = sentiment_labels.get(i, f"Class {i}")
        print(f"  {label}: {prob.item():.4f} ({prob.item()*100:.1f}%)")
    
    # Additional analysis
    print(f"\nModel analysis:")
    print(f"- Input sequence length: {input_ids.shape[1]} tokens")
    print(f"- Model parameters: ~{sum(p.numel() for p in model.parameters()):,}")
    print(f"- Inference device: {next(model.parameters()).device}")

if __name__ == "__main__":
    main()