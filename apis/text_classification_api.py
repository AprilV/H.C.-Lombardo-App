#!/usr/bin/env python3
"""
Text Classification REST API
FastAPI-based API for HuggingFace text classification
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="H.C. Lombardo Text Analysis API",
    description="Professional text analysis and sentiment classification by H.C. Lombardo",
    version="1.0.0"
)

# Homepage route
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """
    HTML homepage with navigation menu to all API endpoints
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>H.C. Lombardo - Text Analysis API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                line-height: 1.6;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            h1 {
                text-align: center;
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2rem;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .nav-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .nav-card {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 25px;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(5px);
            }
            .nav-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.25);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                color: #FFD700;
            }
            .nav-card h3 {
                margin-top: 0;
                font-size: 1.3rem;
                color: #FFD700;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .nav-card p {
                margin-bottom: 0;
                opacity: 0.9;
                font-size: 0.95rem;
            }
            .icon {
                font-size: 1.5rem;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                opacity: 0.7;
                font-size: 0.9rem;
            }
            .api-status {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="api-status">🟢 API Active</div>
            <h1>🤖 H.C. Lombardo - Text Analysis API</h1>
            <p class="subtitle">Powered by HuggingFace Transformers for Sentiment Analysis</p>
            
            <div class="nav-grid">
                <a href="/docs" class="nav-card">
                    <h3><span class="icon">📚</span> Swagger UI</h3>
                    <p>Interactive API documentation with request/response examples and testing interface</p>
                </a>
                
                <a href="/redoc" class="nav-card">
                    <h3><span class="icon">📖</span> ReDoc UI</h3>
                    <p>Beautiful API documentation with detailed schemas and comprehensive endpoint descriptions</p>
                </a>
                
                <a href="/docs#/default/classify_text_classify_post" class="nav-card">
                    <h3><span class="icon">🎯</span> Single Classification</h3>
                    <p>Classify individual text for sentiment analysis with confidence scores</p>
                </a>
                
                <a href="/docs#/default/batch_classify_classify_batch_post" class="nav-card">
                    <h3><span class="icon">📝</span> Batch Classification</h3>
                    <p>Process multiple texts simultaneously for efficient bulk sentiment analysis</p>
                </a>
                
                <a href="/models" class="nav-card">
                    <h3><span class="icon">🧠</span> Available Models</h3>
                    <p>View supported HuggingFace transformer models and their capabilities</p>
                </a>
                
                <a href="/health" class="nav-card">
                    <h3><span class="icon">💚</span> Health Check</h3>
                    <p>API status and system health monitoring endpoint</p>
                </a>
            </div>
            
            <div class="footer">
                <p>🚀 Built with FastAPI • Powered by HuggingFace Transformers • Version 1.0.0</p>
                <p>🧠 Advanced NLP sentiment analysis and text classification</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Global model storage
models = {}

# Pydantic models for request/response
class TextRequest(BaseModel):
    text: str
    model_name: Optional[str] = "distilbert"

class ClassificationResult(BaseModel):
    text: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    model_used: str
    timestamp: str

class BatchTextRequest(BaseModel):
    texts: List[str]
    model_name: Optional[str] = "distilbert"

class BatchClassificationResult(BaseModel):
    results: List[ClassificationResult]
    total_processed: int
    model_used: str

# Model configurations
MODEL_CONFIGS = {
    "distilbert": {
        "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
        "labels": {0: "NEGATIVE", 1: "POSITIVE"}
    },
    "bert": {
        "model_name": "nlptown/bert-base-multilingual-uncased-sentiment",
        "labels": {0: "1-star", 1: "2-star", 2: "3-star", 3: "4-star", 4: "5-star"}
    },
    "roberta": {
        "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "labels": {0: "negative", 1: "neutral", 2: "positive"}
    }
}

def load_model(model_key: str):
    """Load and cache a model"""
    if model_key in models:
        return models[model_key]
    
    if model_key not in MODEL_CONFIGS:
        raise ValueError(f"Model {model_key} not supported. Available: {list(MODEL_CONFIGS.keys())}")
    
    config = MODEL_CONFIGS[model_key]
    logger.info(f"Loading model: {config['model_name']}")
    
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    model = AutoModelForSequenceClassification.from_pretrained(config['model_name'])
    
    models[model_key] = {
        "tokenizer": tokenizer,
        "model": model,
        "labels": config['labels'],
        "model_name": config['model_name']
    }
    
    logger.info(f"Model {model_key} loaded successfully")
    return models[model_key]

def classify_text(text: str, model_key: str) -> ClassificationResult:
    """Classify a single text"""
    model_info = load_model(model_key)
    tokenizer = model_info["tokenizer"]
    model = model_info["model"]
    labels = model_info["labels"]
    
    # Tokenize and predict
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
    
    # Get prediction
    predicted_class = torch.argmax(logits, dim=-1).item()
    confidence = probabilities[0][predicted_class].item()
    prediction = labels[predicted_class]
    
    # Create probability dictionary
    prob_dict = {}
    for i, prob in enumerate(probabilities[0]):
        prob_dict[labels[i]] = round(prob.item(), 4)
    
    return ClassificationResult(
        text=text,
        prediction=prediction,
        confidence=round(confidence, 4),
        probabilities=prob_dict,
        model_used=model_key,
        timestamp=datetime.now().isoformat()
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "loaded_models": list(models.keys())
    }

@app.get("/models")
async def get_available_models():
    """Get available models"""
    return {
        "available_models": list(MODEL_CONFIGS.keys()),
        "model_details": MODEL_CONFIGS,
        "loaded_models": list(models.keys())
    }

@app.post("/classify", response_model=ClassificationResult)
async def classify_text_endpoint(request: TextRequest):
    """Classify a single text"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = classify_text(request.text, request.model_name)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/classify-batch", response_model=BatchClassificationResult)
async def classify_batch_endpoint(request: BatchTextRequest):
    """Classify multiple texts"""
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        if len(request.texts) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size too large (max 50)")
        
        results = []
        for text in request.texts:
            if text.strip():  # Skip empty texts
                result = classify_text(text, request.model_name)
                results.append(result)
        
        return BatchClassificationResult(
            results=results,
            total_processed=len(results),
            model_used=request.model_name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/preload-model")
async def preload_model(model_name: str):
    """Preload a specific model"""
    try:
        load_model(model_name)
        return {
            "message": f"Model {model_name} loaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load model")

if __name__ == "__main__":
    # Load default model on startup
    print("Loading default model...")
    load_model("distilbert")
    
    print("Starting Text Classification API...")
    print("API Documentation: http://localhost:8003/docs")
    print("API Interface: http://localhost:8003/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)