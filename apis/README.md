# API Documentation

This folder contains REST APIs for both projects using FastAPI.

## APIs Available

### 1. Text Classification API (`text_classification_api.py`)
**Port**: 8000  
**Purpose**: Sentiment analysis and text classification using HuggingFace models

#### Endpoints:
- `GET /` - API welcome message
- `GET /health` - Health check
- `GET /models` - Get available models
- `POST /classify` - Classify single text
- `POST /classify-batch` - Classify multiple texts
- `POST /preload-model` - Preload a specific model

#### Supported Models:
- **distilbert**: Binary sentiment (POSITIVE/NEGATIVE)
- **bert**: 5-star rating system (1-5 stars)
- **roberta**: 3-class sentiment (positive/neutral/negative)

### 2. NFL Betting API (`nfl_betting_api.py`)
**Port**: 8001  
**Purpose**: NFL betting predictions and database operations

#### Endpoints:
- `GET /` - API welcome message
- `GET /health` - Health check with database stats
- `GET /teams` - Get all teams
- `POST /teams` - Add new team
- `GET /games` - Get games by season/week
- `POST /games` - Add new game
- `POST /predict` - Predict betting lines
- `GET /betting-lines/{game_id}` - Get betting lines
- `GET /stats/team/{team_id}` - Get team statistics
- `GET /database/stats` - Get database statistics

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn requests pydantic
```

### 2. Start APIs
```bash
# Terminal 1 - Text Classification API
python text_classification_api.py

# Terminal 2 - NFL Betting API  
python nfl_betting_api.py
```

### 3. Access APIs
- **Text Classification**: http://localhost:8000/docs
- **NFL Betting**: http://localhost:8001/docs
- **Interactive Docs**: Available at `/docs` endpoint
- **Alternative Docs**: Available at `/redoc` endpoint

## Usage Examples

### Text Classification API

#### Classify Single Text
```python
import requests

response = requests.post(
    "http://localhost:8000/classify",
    json={"text": "I love this movie!", "model_name": "distilbert"}
)
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

#### Batch Classification
```python
response = requests.post(
    "http://localhost:8000/classify-batch",
    json={
        "texts": ["Great product!", "Terrible experience"],
        "model_name": "distilbert"
    }
)
results = response.json()
for result in results['results']:
    print(f"'{result['text']}' -> {result['prediction']}")
```

### NFL Betting API

#### Get Teams
```python
response = requests.get("http://localhost:8001/teams")
teams = response.json()
for team in teams:
    print(f"{team['name']} ({team['abbreviation']})")
```

#### Predict Game
```python
response = requests.post(
    "http://localhost:8001/predict",
    json={
        "home_team_id": 1,
        "away_team_id": 2,
        "season": 2024
    }
)
prediction = response.json()
print(f"Spread: {prediction['predicted_spread']}")
print(f"Total: {prediction['predicted_total']}")
```

## Client Examples

Run the client examples to see both APIs in action:
```bash
python api_client_examples.py
```

This will demonstrate:
- Health checks
- Text classification (single and batch)
- NFL team data retrieval
- Betting predictions

## API Features

### Text Classification API Features:
- ✅ **Multiple Models** - DistilBERT, BERT, RoBERTa
- ✅ **Batch Processing** - Up to 50 texts at once
- ✅ **Model Caching** - Faster subsequent requests
- ✅ **Detailed Results** - Probabilities for all classes
- ✅ **Error Handling** - Comprehensive error responses

### NFL Betting API Features:
- ✅ **CRUD Operations** - Teams, games, betting lines
- ✅ **Predictions** - Spread and total predictions
- ✅ **Statistics** - Team performance analysis
- ✅ **Database Integration** - Full SQLite database access
- ✅ **Query Parameters** - Flexible data filtering

## Production Considerations

For production use:
1. Add authentication/authorization
2. Implement rate limiting
3. Add request validation
4. Set up proper logging
5. Use environment variables for configuration
6. Add monitoring and metrics
7. Implement caching (Redis)
8. Add database connection pooling

## Dependencies

```
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0
requests>=2.25.0
transformers>=4.21.0
torch>=1.12.0
```