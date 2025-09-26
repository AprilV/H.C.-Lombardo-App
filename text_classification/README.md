# Text Classification with HuggingFace Transformers

This folder contains various implementations of text classification using HuggingFace Transformers library.

## Files Overview

### Simple Examples
- **`minimal_example.py`** - Ultra-minimal 25-line implementation
- **`ultra_simple.py`** - Simple pipeline + manual approach
- **`simple_huggingface_script.py`** - Clean DistilBERT example

### Step-by-Step Tutorials
- **`step_by_step_classification.py`** - Detailed DistilBERT tutorial
- **`bert_step_by_step.py`** - Comprehensive BERT implementation
- **`example_classification.py`** - Clean 4-step process example
- **`gemma_style_classification.py`** - BERT with clear documentation

### Advanced Examples
- **`text_classification.py`** - RoBERTa with 3-class sentiment
- **`simple_classification.py`** - Default DistilBERT sentiment
- **`bert_simple_script.py`** - BERT with 5-star rating system

## Models Used

1. **DistilBERT** (`distilbert-base-uncased-finetuned-sst-2-english`)
   - 2-class sentiment (POSITIVE/NEGATIVE)
   - ~268MB, faster inference
   - Good for binary classification

2. **BERT** (`nlptown/bert-base-multilingual-uncased-sentiment`)
   - 5-class rating system (1-5 stars)
   - ~669MB, more detailed analysis
   - Multilingual support

3. **RoBERTa** (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
   - 3-class sentiment (positive, neutral, negative)
   - ~501MB, Twitter-trained
   - Good for social media text

## Quick Start

### Minimal Example (25 lines)
```bash
python minimal_example.py
```

### Step-by-Step Learning
```bash
python step_by_step_classification.py
```

### BERT Alternative
```bash
python bert_step_by_step.py
```

## Expected Output

```
1. Loading model and tokenizer...
2. Tokenizing input...
   Sentence: 'This product is incredible! Highly recommended.'
3. Passing through model...
4. Result:
   Prediction: POSITIVE
   Confidence: 1.000 (100.0%)
   Raw logits: [-4.34, 4.70]
```

## Learning Path

1. **Start with**: `minimal_example.py` - See the basics
2. **Learn details**: `step_by_step_classification.py` - Understand each step
3. **Try alternatives**: `bert_step_by_step.py` - Different model
4. **Explore advanced**: `text_classification.py` - Multiple features

## Requirements

All scripts use the same dependencies:
```bash
pip install transformers torch numpy
```

Models are downloaded automatically on first run and cached locally.