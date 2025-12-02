# Sprint 9 Plan: Neural Network Game Predictions (ML/AI)

**Sprint Duration:** November 6-13, 2025 (Week 7)  
**Phase:** 3A - Machine Learning & AI Predictions  
**Sprint Goal:** Build neural network to predict NFL game outcomes using 950+ historical games  
**Status:** 🟡 Planning → Ready to Start  
**Academic Focus:** ⭐ Aligns with Dr. Foster's ML curriculum (neurons, neural networks, deep learning)

---

## 🎯 Sprint Objectives

### Primary Goal
Create an AI-powered prediction system using **neural networks** that learns from 950+ historical games (2022-2025) to predict winners, scores, spreads, and confidence levels for upcoming NFL matchups.

### Success Criteria
- ✅ Neural network model with multiple hidden layers
- ✅ Train on 35+ features (EPA, success rate, rest days, weather, betting lines, etc.)
- ✅ Predict: Winner, Final Score, Spread Coverage, Over/Under
- ✅ Model accuracy > 55% on test data (beat Vegas baseline)
- ✅ API endpoint: `POST /api/ml/predict-game`
- ✅ Frontend "ML Predictions" tab in Analytics dashboard
- ✅ Model evaluation metrics (accuracy, precision, recall, F1 score)
- ✅ Save trained model for reuse (.h5 or .pkl file)
- ✅ Training visualizations (loss curves, accuracy over epochs)

---

## 🧠 Machine Learning Architecture

### Neural Network Design

**Model Type:** Deep Neural Network (DNN) for binary classification + regression

**Architecture:**
```
Input Layer (70 features) 
    ↓
Hidden Layer 1 (128 neurons, ReLU activation)
    ↓ Dropout (0.3)
Hidden Layer 2 (64 neurons, ReLU activation)
    ↓ Dropout (0.3)
Hidden Layer 3 (32 neurons, ReLU activation)
    ↓ Dropout (0.2)
Output Layer:
    - Winner (1 neuron, Sigmoid) → Binary: Home Win or Away Win
    - Score Prediction (2 neurons, Linear) → Home Score, Away Score
    - Confidence (1 neuron, Sigmoid) → Win Probability %
```

**Why This Architecture:**
- **3 Hidden Layers:** Captures complex relationships in NFL data
- **ReLU Activation:** Prevents vanishing gradient, faster training
- **Dropout Layers:** Prevents overfitting on historical data
- **Multiple Outputs:** Predicts winner AND score simultaneously

### Input Features (70 total)

**Team A Stats (35 features):**
- Offensive: PPG, total yards, pass yards, rush yards, EPA/play, success rate
- Defensive: Points allowed, pass defense, rush defense, sacks, turnovers
- Efficiency: 3rd down %, red zone %, yards per play, completion %
- Situational: Rest days, home/away, division game, weather conditions
- Recent form: L3 game average, L5 game average, win streak
- Betting: Opening spread, closing spread, total line, public betting %
- Contextual: Injuries, season week, time of year

**Team B Stats (35 features):**
- Same 35 features for opponent

**Derived Features:**
- Differential features (Team A stat - Team B stat) for key metrics
- Momentum indicators (trend up/down over last 5 games)

### Training Strategy

**Data Split:**
- Training: 70% (665 games from 2022-2024)
- Validation: 15% (142 games from early 2025)
- Test: 15% (143 games from 2025 Week 8+)

**Loss Functions:**
- Winner prediction: Binary Cross-Entropy
- Score prediction: Mean Squared Error (MSE)
- Combined loss: Weighted sum (0.6 winner + 0.4 score)

**Optimization:**
- Optimizer: Adam (learning rate = 0.001)
- Batch size: 32
- Epochs: 100 (with early stopping)
- Early stopping: Monitor validation loss, patience = 10

**Evaluation Metrics:**
- Accuracy: % of games predicted correctly
- Precision: True positives / (True positives + False positives)
- Recall: True positives / (True positives + False negatives)
- F1 Score: Harmonic mean of precision and recall
- AUC-ROC: Area under receiver operating characteristic curve
- Mean Absolute Error (MAE): Average score prediction error

---

## 📋 Sprint Backlog

### Task 1: Data Preparation & Feature Engineering
**Estimated Time:** 4-5 hours  
**Priority:** CRITICAL  
**Dependencies:** None (uses existing HCL database)

**Subtasks:**
1. Create `ml_data_pipeline.py` - Extract features from PostgreSQL
2. Engineer 70 input features from team_game_stats table
3. Create derived features (differentials, momentum, trends)
4. Handle missing data (weather, injuries)
5. Normalize/scale features (StandardScaler or MinMaxScaler)
6. Split data into train/validation/test sets (70/15/15)
7. Save processed datasets as CSV for reproducibility

**Key Features to Engineer:**
```python
# Offensive Power
- avg_ppg_last_5
- avg_epa_last_5
- avg_success_rate_last_5

# Defensive Strength
- avg_points_allowed_last_5
- avg_epa_allowed_last_5

# Situational
- rest_days
- home_field_advantage (binary)
- division_game (binary)
- weather_impact_score

# Form/Momentum
- win_streak
- points_trend (increasing/decreasing)
- epa_trend
```

**Files to Create:**
- `ml/ml_data_pipeline.py` - Feature extraction
- `ml/feature_engineering.py` - Derived features
- `ml/data_preprocessor.py` - Scaling and normalization
- `ml/data/train_data.csv` - Training dataset
- `ml/data/validation_data.csv` - Validation dataset
- `ml/data/test_data.csv` - Test dataset

---

### Task 2: Neural Network Model Implementation
**Estimated Time:** 5-6 hours  
**Priority:** CRITICAL  
**Dependencies:** Task 1

**Subtasks:**
1. Install ML libraries (TensorFlow/Keras or PyTorch)
2. Build neural network architecture (3 hidden layers)
3. Implement multi-output model (winner + score)
4. Add dropout layers for regularization
5. Configure loss functions and optimizer
6. Implement early stopping and checkpoints
7. Create training loop with progress tracking
8. Save best model weights

**Model Code Structure:**
```python
import tensorflow as tf
from tensorflow import keras

def build_nfl_predictor():
    # Input layer
    inputs = keras.Input(shape=(70,))
    
    # Hidden layers
    x = keras.layers.Dense(128, activation='relu')(inputs)
    x = keras.layers.Dropout(0.3)(x)
    x = keras.layers.Dense(64, activation='relu')(x)
    x = keras.layers.Dropout(0.3)(x)
    x = keras.layers.Dense(32, activation='relu')(x)
    x = keras.layers.Dropout(0.2)(x)
    
    # Output layers
    winner = keras.layers.Dense(1, activation='sigmoid', name='winner')(x)
    home_score = keras.layers.Dense(1, activation='linear', name='home_score')(x)
    away_score = keras.layers.Dense(1, activation='linear', name='away_score')(x)
    confidence = keras.layers.Dense(1, activation='sigmoid', name='confidence')(x)
    
    model = keras.Model(inputs=inputs, outputs=[winner, home_score, away_score, confidence])
    
    return model
```

**Files to Create:**
- `ml/nfl_neural_network.py` - Neural network architecture
- `ml/model_trainer.py` - Training loop
- `ml/model_evaluator.py` - Evaluation metrics
- `ml/models/nfl_predictor_v1.h5` - Saved model weights
- `ml/models/scaler.pkl` - Feature scaler (for predictions)

---

### Task 3: Model Training & Evaluation
**Estimated Time:** 3-4 hours  
**Priority:** HIGH  
**Dependencies:** Task 2

**Subtasks:**
1. Train model on training dataset (665 games)
2. Monitor validation loss and accuracy
3. Generate training curves (loss, accuracy over epochs)
4. Evaluate on test set (143 games)
5. Calculate performance metrics (accuracy, precision, recall, F1)
6. Analyze misclassifications (where did model fail?)
7. Compare against Vegas spread baseline
8. Document model performance

**Training Monitoring:**
```python
# Track metrics during training
- Training loss per epoch
- Validation loss per epoch
- Training accuracy per epoch
- Validation accuracy per epoch
- Learning rate adjustments
- Early stopping trigger point
```

**Evaluation Outputs:**
```
Model Performance Report:
========================
Test Accuracy: 57.3%
Precision: 0.58
Recall: 0.56
F1 Score: 0.57
AUC-ROC: 0.62

Score Prediction:
Mean Absolute Error: 8.2 points
Root Mean Squared Error: 10.5 points

Vegas Comparison:
Vegas Spread Accuracy: 52.1%
Our Model Accuracy: 57.3%
Improvement: +5.2%
```

**Files to Create:**
- `ml/train_model.py` - Training script
- `ml/evaluate_model.py` - Evaluation script
- `ml/results/training_curves.png` - Loss/accuracy plots
- `ml/results/confusion_matrix.png` - Classification results
- `ml/results/model_performance_report.txt` - Metrics summary

---

### Task 4: Prediction API Endpoint
**Estimated Time:** 3-4 hours  
**Priority:** HIGH  
**Dependencies:** Task 3

**Subtasks:**
1. Create Flask API endpoint: `POST /api/ml/predict-game`
2. Load trained model and scaler on server startup
3. Accept matchup details in request (teams, date, week)
4. Fetch recent stats from database for both teams
5. Engineer features for prediction
6. Run prediction through neural network
7. Return prediction with confidence score
8. Add error handling for invalid teams/data

**API Request Format:**
```json
POST /api/ml/predict-game
{
  "home_team": "DAL",
  "away_team": "PHI",
  "week": 10,
  "season": 2025,
  "game_date": "2025-11-09"
}
```

**API Response Format:**
```json
{
  "prediction": {
    "winner": "DAL",
    "home_score": 27,
    "away_score": 23,
    "spread": -4.0,
    "confidence": 0.68,
    "over_under": 50
  },
  "model_info": {
    "version": "v1.0",
    "accuracy": 0.573,
    "trained_on": "950 games (2022-2025)"
  },
  "features_used": {
    "dal_avg_ppg": 28.5,
    "phi_avg_ppg": 25.2,
    "dal_rest_days": 7,
    "home_advantage": true
  }
}
```

**Files to Create/Modify:**
- `api_routes_ml.py` - ML prediction endpoints (NEW)
- `api_server.py` - Register ML blueprint (MODIFY)
- `ml/predictor.py` - Prediction wrapper class
- `testbed/test_ml_api.py` - API tests

---

### Task 5: Frontend ML Predictions Dashboard
**Estimated Time:** 4-5 hours  
**Priority:** MEDIUM  
**Dependencies:** Task 4

**Subtasks:**
1. Create `MLPredictions.jsx` component
2. Add "ML Predictions" tab to Analytics dashboard
3. Build matchup selector (home team vs away team)
4. Add week/season selector
5. Display prediction results with visual indicators
6. Show confidence meter (0-100%)
7. Compare prediction vs Vegas spread (if available)
8. Add "Predict All Week X Games" bulk prediction
9. Style with existing gold/blue theme

**UI Layout:**
```
┌─────────────────────────────────────────────────┐
│  🤖 ML Game Predictions (Neural Network)        │
├─────────────────────────────────────────────────┤
│  Select Matchup:                                │
│  Home: [Dallas Cowboys ▼]                       │
│  Away: [Philadelphia Eagles ▼]                  │
│  Week: [10 ▼]  Season: [2025 ▼]                │
│                                                  │
│  [Generate Prediction]                          │
├─────────────────────────────────────────────────┤
│  🏈 Prediction Results                          │
│  ┌───────────────────────────────────────────┐ │
│  │  Predicted Winner: Dallas Cowboys 🏆      │ │
│  │  Score: DAL 27 - 23 PHI                   │ │
│  │  Spread: DAL -4.0                         │ │
│  │  Total: 50 (Over/Under)                   │ │
│  │                                            │ │
│  │  Confidence: ████████░░ 68%               │ │
│  │                                            │ │
│  │  Vegas Comparison:                         │ │
│  │  Vegas Spread: DAL -3.5                   │ │
│  │  Our Model: DAL -4.0 (0.5 pt difference)  │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  Model Info: v1.0 | 57.3% accuracy | 950 games │
└─────────────────────────────────────────────────┘
```

**Files to Create/Modify:**
- `frontend/src/MLPredictions.js` - ML predictions component (NEW)
- `frontend/src/MLPredictions.css` - Styling (NEW)
- `frontend/src/Analytics.js` - Add ML Predictions tab (MODIFY)
- `frontend/src/App.js` - Add route (if needed) (MODIFY)

---

### Task 6: Model Visualization & Documentation
**Estimated Time:** 2-3 hours  
**Priority:** MEDIUM  
**Dependencies:** Task 3, Task 5

**Subtasks:**
1. Create training loss/accuracy curves
2. Generate confusion matrix visualization
3. Create feature importance chart (which stats matter most)
4. Document neural network architecture diagram
5. Write model card (what it does, limitations, use cases)
6. Update dr.foster.md with ML sprint documentation
7. Add to Dr. Foster dashboard HTML

**Visualizations to Create:**
- Training curves (loss and accuracy over epochs)
- Confusion matrix (true positives, false positives, etc.)
- Feature importance (which stats most predict outcomes)
- Prediction distribution (confidence histogram)
- Accuracy by week (does model get better/worse over season?)

**Documentation Sections:**
```markdown
## Neural Network Architecture
- 3 hidden layers (128, 64, 32 neurons)
- ReLU activation functions
- Dropout for regularization
- Multi-output: Winner + Score + Confidence

## Training Process
- 950 games from 2022-2025
- 70 input features per team
- 100 epochs with early stopping
- Adam optimizer (lr=0.001)

## Performance
- Test accuracy: 57.3%
- Better than Vegas by 5.2%
- MAE on score: 8.2 points

## Use Cases
- Pre-game predictions for betting
- Identify value bets (disagree with Vegas)
- Track model performance over season
```

**Files to Create:**
- `ml/visualizations/training_curves.png`
- `ml/visualizations/confusion_matrix.png`
- `ml/visualizations/feature_importance.png`
- `ml/MODEL_CARD.md` - Model documentation
- `dr.foster.md` - Add Sprint 9 ML section

---

## 🛠️ Technology Stack

### Machine Learning Libraries

**Option 1: TensorFlow + Keras (RECOMMENDED)**
```bash
pip install tensorflow numpy pandas scikit-learn matplotlib seaborn
```
- **Pros:** Industry standard, great documentation, Keras API is beginner-friendly
- **Cons:** Large library size

**Option 2: PyTorch**
```bash
pip install torch numpy pandas scikit-learn matplotlib seaborn
```
- **Pros:** More flexible, better for research
- **Cons:** Steeper learning curve

**Recommendation:** Use TensorFlow/Keras - aligns with most ML courses

### Supporting Libraries
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `scikit-learn` - Preprocessing, metrics, train/test split
- `matplotlib` + `seaborn` - Visualizations
- `psycopg2` - Database connection (already installed)
- `joblib` or `pickle` - Save/load scaler

---

## 📅 Sprint Timeline

### Day 1 (Nov 6) - Data Preparation
- ✅ Sprint planning complete
- [ ] Install ML libraries
- [ ] Create data pipeline
- [ ] Engineer 70 features
- [ ] Split train/validation/test sets
- [ ] Save processed datasets

### Day 2 (Nov 7) - Model Development
- [ ] Build neural network architecture
- [ ] Implement multi-output model
- [ ] Configure loss functions
- [ ] Create training script
- [ ] Test model compiles successfully

### Day 3 (Nov 8) - Model Training
- [ ] Train model on 665 games
- [ ] Monitor validation performance
- [ ] Generate training curves
- [ ] Save best model weights
- [ ] Initial evaluation on test set

### Day 4 (Nov 9) - API Integration
- [ ] Create ML prediction API endpoint
- [ ] Load model on server startup
- [ ] Test predictions via Postman
- [ ] Write API tests
- [ ] Document endpoint

### Day 5 (Nov 10) - Frontend Dashboard
- [ ] Create MLPredictions component
- [ ] Add matchup selector
- [ ] Display prediction results
- [ ] Add confidence meter
- [ ] Integrate with Analytics tab

### Day 6 (Nov 11) - Visualization & Testing
- [ ] Generate all visualizations
- [ ] Create model card documentation
- [ ] Manual testing of predictions
- [ ] Compare against Vegas lines
- [ ] Fix any bugs discovered

### Day 7 (Nov 12-13) - Polish & Documentation
- [ ] Update dr.foster.md with ML sprint
- [ ] Create demo predictions for portfolio
- [ ] Performance optimization
- [ ] Final testing
- [ ] Sprint 9 retrospective
- [ ] Plan Sprint 10 (Custom Query Builder)

---

## 🎓 Academic Alignment (Dr. Foster's ML Curriculum)

### Key ML Concepts Demonstrated

**Neurons:**
- ✅ Each neuron has weights, bias, activation function
- ✅ Visualize neuron computation: `output = activation(Σ(weights × inputs) + bias)`

**Neural Networks:**
- ✅ Multiple layers of interconnected neurons
- ✅ Forward propagation (input → hidden → output)
- ✅ Backpropagation (adjusting weights to minimize loss)

**Deep Learning:**
- ✅ "Deep" = multiple hidden layers (we have 3)
- ✅ Learns hierarchical representations
- ✅ Layer 1: Basic stats, Layer 2: Combinations, Layer 3: Complex patterns

**Activation Functions:**
- ✅ ReLU in hidden layers (non-linearity)
- ✅ Sigmoid for probability outputs (0-1 range)
- ✅ Linear for score predictions (any number)

**Regularization:**
- ✅ Dropout layers prevent overfitting
- ✅ Early stopping prevents overtraining
- ✅ Train/validation/test split

**Optimization:**
- ✅ Adam optimizer (adaptive learning rate)
- ✅ Loss functions (Binary Cross-Entropy, MSE)
- ✅ Gradient descent to find optimal weights

**Model Evaluation:**
- ✅ Accuracy, precision, recall, F1 score
- ✅ Confusion matrix
- ✅ ROC curve and AUC

---

## 🎯 Success Metrics

### Model Performance Targets
- **Baseline (Random):** 50% accuracy
- **Vegas Spread:** ~52% accuracy
- **Our Goal:** >55% accuracy (beat Vegas by 3%+)
- **Stretch Goal:** >60% accuracy (professional-grade)

### Score Prediction Targets
- **Mean Absolute Error:** <10 points per game
- **Root Mean Squared Error:** <12 points per game

### Production Readiness
- ✅ API responds in <2 seconds
- ✅ Model loads on server startup
- ✅ Handles edge cases (missing data, invalid teams)
- ✅ Frontend displays predictions clearly
- ✅ All tests passing (100%)

---

## 🔬 Testbed Strategy

### Development Phases
1. **Testbed ML Training:** Train model in `testbed/ml/` first
2. **Validate Performance:** Ensure >55% accuracy before production
3. **API Prototyping:** Test endpoint in testbed with sample data
4. **Frontend Prototype:** Build UI in testbed first
5. **Production Migration:** Move to production only after full validation

### Test Datasets
- Use 2025 games as test set (model has never seen this data)
- Validate predictions against actual outcomes
- Track accuracy week by week

---

## 🚀 Definition of Done

### Sprint 9 Complete When:
- ✅ Neural network trained with 3 hidden layers
- ✅ Model accuracy >55% on test data
- ✅ API endpoint `/api/ml/predict-game` working
- ✅ Frontend ML Predictions tab functional
- ✅ All visualizations generated (training curves, confusion matrix)
- ✅ Model card documentation complete
- ✅ dr.foster.md updated with Sprint 9 ML section
- ✅ All tests passing (model tests + API tests)
- ✅ Code committed to GitHub
- ✅ Demo predictions generated for portfolio

---

## 📊 Sprint Metrics

**Estimated Effort:** 21-27 hours  
**Team Velocity:** ~20 hours/week  
**Confidence Level:** MEDIUM-HIGH (new ML territory, but strong data foundation)

**Risk Assessment:**
- 🟡 MEDIUM RISK: ML model performance (may need tuning)
- 🟢 LOW RISK: Data availability (950 games ready in database)
- 🟢 LOW RISK: API integration (familiar pattern)
- 🟡 MEDIUM RISK: Frontend visualization (new component)

---

## 🔜 Sprint 10 Preview: Custom Query Builder

**After Sprint 9 ML predictions are complete, Sprint 10 will focus on:**

### Sprint 10 Goals
- Transform Custom Builder tab from "Coming Soon" to functional
- Allow users to select custom stats and filters
- Display results in sortable table
- Export to CSV
- Save/load custom queries

**Estimated Duration:** 4-5 days  
**Estimated Effort:** 14-18 hours

---

## 📚 Learning Resources

### Neural Networks
- TensorFlow Keras Guide: https://www.tensorflow.org/guide/keras
- Neural Networks Explained: https://www.youtube.com/watch?v=aircAruvnKk
- Deep Learning Book (Free): https://www.deeplearningbook.org/

### Sports Prediction Models
- NFL Analytics Papers: https://arxiv.org/search/?query=nfl+prediction
- Kaggle NFL Competitions: https://www.kaggle.com/c/nfl-big-data-bowl-2021

### Python ML Stack
- scikit-learn documentation: https://scikit-learn.org/stable/
- pandas for data manipulation: https://pandas.pydata.org/docs/
- matplotlib for plots: https://matplotlib.org/stable/contents.html

---

## 🎬 Next Steps (Day 1 - Nov 6)

### Immediate Actions:
1. ✅ Sprint 9 plan created
2. [ ] Install TensorFlow: `pip install tensorflow numpy pandas scikit-learn matplotlib seaborn`
3. [ ] Create `ml/` directory structure
4. [ ] Start Task 1: Data pipeline and feature engineering
5. [ ] Extract 950 games from PostgreSQL
6. [ ] Engineer 70 features per matchup

**Let's start with installing libraries and creating the data pipeline!**

---

**Sprint Created:** November 6, 2025  
**Sprint Owner:** April V  
**Course:** IS330 (Weeks 6-8)  
**Academic Focus:** Dr. Foster's Machine Learning Unit  
**Next Sprint:** Sprint 10 - Custom Query Builder (Nov 14-20, 2025)  
**Next Review:** November 13, 2025
