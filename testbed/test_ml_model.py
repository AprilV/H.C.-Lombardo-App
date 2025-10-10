"""
H.C. Lombardo - ML Component Test
Simple test of HuggingFace pre-trained model
"""
from transformers import pipeline

print("\n" + "="*70)
print("ASSIGNMENT: Testing ML Model from HuggingFace")
print("="*70 + "\n")

print("Loading sentiment analysis model...")
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

print("✅ Model loaded successfully!\n")

# Test with NFL-related text
test_texts = [
    "The Detroit Lions are having an amazing season!",
    "The Patriots are struggling this year.",
    "This game was incredibly exciting with a last-second touchdown!"
]

print("Testing model with NFL text:")
print("-" * 70)

for text in test_texts:
    result = classifier(text)[0]
    print(f"\nText: {text}")
    print(f"Result: {result['label']} (confidence: {result['score']:.2%})")

print("\n" + "="*70)
print("✅ ML Model Working - Assignment Requirement Met!")
print("="*70 + "\n")
