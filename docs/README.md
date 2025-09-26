# HuggingFace Text Classification Examples

This repository contains simple examples of using pre-trained text classification models from HuggingFace for sentiment analysis.

## Files

### 1. `text_classification.py`
- Uses the **cardiffnlp/twitter-roberta-base-sentiment-latest** model
- Provides detailed sentiment analysis with 3 categories: positive, neutral, negative
- Shows confidence scores for all categories
- Based on RoBERTa architecture, fine-tuned on Twitter data

### 2. `simple_classification.py`
- Uses the default **DistilBERT** sentiment analysis model
- Simple binary classification: POSITIVE or NEGATIVE
- Faster and more straightforward approach
- Good for basic sentiment analysis tasks

### 3. `step_by_step_classification.py` ⭐ **NEW**
- **Detailed step-by-step implementation** following exact requirements
- Manual tokenization process with token visualization
- Raw logit extraction and probability computation
- Uses DistilBERT model with explicit step documentation
- Perfect for learning how transformers work internally

### 4. `bert_step_by_step.py` ⭐ **NEW**
- **BERT model implementation** with 5-class sentiment analysis
- Shows tokenization, model inference, and output decoding
- Uses nlptown/bert-base-multilingual-uncased-sentiment
- 1-5 star rating system (very negative to very positive)
- More detailed model analysis and parameter counting

### 5. `example_classification.py` ⭐ **FOCUSED EXAMPLE**
- **Clean DistilBERT example** following exact 4-step process
- Load model → Tokenize → Pass through model → Print result
- Perfect example for understanding the basic workflow
- Shows tokens, logits, and probabilities clearly

### 6. `gemma_style_classification.py` ⭐ **BERT VARIANT**
- **BERT implementation** with clear step documentation
- 5-star rating classification system
- Clean output with checkmarks for each step
- Alternative to DistilBERT approach

### 7. `minimal_example.py` ⭐ **ULTRA MINIMAL**
- **Shortest possible implementation** (25 lines)
- Pure 4-step process with minimal code
- Perfect for quick testing and demonstrations
- Concise but complete example

## Requirements

### Core Libraries (Required)
- **transformers**: HuggingFace library for pre-trained models
- **torch**: PyTorch for deep learning computations
- **numpy**: Numerical computing support

### Installation

Install the required packages:
```bash
pip install transformers torch numpy
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

### Versions Used
- transformers: Latest compatible version
- torch: 2.8.0+cpu (CPU version)
- numpy: Latest compatible version

## Usage

Run any of the scripts directly:

```bash
# Simple pipeline approach
python simple_classification.py
python text_classification.py

# Step-by-step manual approach (recommended for learning)
python step_by_step_classification.py
python bert_step_by_step.py
```

## Models Used

1. **cardiffnlp/twitter-roberta-base-sentiment-latest**
   - Based on RoBERTa architecture
   - Fine-tuned on Twitter data
   - 3-class classification (positive, negative, neutral)
   - ~501MB model size

2. **distilbert/distilbert-base-uncased-finetuned-sst-2-english**
   - Based on DistilBERT architecture
   - Fine-tuned on SST-2 dataset
   - 2-class classification (POSITIVE, NEGATIVE)
   - ~268MB model size (lighter and faster)

## Output Examples

### Detailed Analysis (text_classification.py):
```
Sample 1: I love this product! It's amazing and works perfectly.
  positive: 0.9890 (98.9%)
  neutral: 0.0066 (0.7%)
  negative: 0.0043 (0.4%)
  → Prediction: positive (confidence: 98.9%)
```

### Simple Analysis (simple_classification.py):
```
1. Text: I absolutely love this new phone!
   Prediction: POSITIVE
   Confidence: 0.9999 (100.0%)
```

## Notes

- Models are downloaded automatically on first run
- Models are cached locally for subsequent runs
- CPU inference is used by default
- Both scripts include sample texts for testing