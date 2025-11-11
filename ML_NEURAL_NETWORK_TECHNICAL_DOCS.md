# NFL Neural Network - Technical Documentation

**Sprint 9: Machine Learning Predictions**  
**Created**: November 6, 2025  
**Purpose**: Technical deep-dive into the neural network architecture, training methodology, and mathematical foundations

---

## Table of Contents
1. [Neural Network Architecture](#architecture)
2. [Nodes (Neurons) and Layers](#nodes-and-layers)
3. [Weights and Biases](#weights-and-biases)
4. [Activation Functions](#activation-functions)
5. [Training Process (Backpropagation)](#training-process)
6. [Sample Weighting Strategy](#sample-weighting)
7. [Model Performance](#performance)
8. [Mathematical Foundations](#mathematics)

---

## 1. Neural Network Architecture {#architecture}

### Overview
Our neural network is a **deep feed-forward artificial neural network** with 3 hidden layers, designed to predict NFL game outcomes based on historical team statistics.

### Layer Structure

```
INPUT LAYER (75 neurons)
    ↓
HIDDEN LAYER 1 (128 neurons) + ReLU activation
    ↓
HIDDEN LAYER 2 (64 neurons) + ReLU activation
    ↓
HIDDEN LAYER 3 (32 neurons) + ReLU activation
    ↓
OUTPUT LAYER (1 neuron) + Sigmoid activation
```

### Network Dimensions
- **Input Features**: 75 dimensions
  - Basic stats: 51 columns (points, yards, turnovers, etc.)
  - EPA metrics: 13 columns (epa_per_play, success_rate, wpa, cpoe, etc.)
  - Context: 11 columns (season, week, is_home, betting lines, etc.)

- **Hidden Layers**: 3 layers with decreasing neuron counts (128 → 64 → 32)
  - Design philosophy: Hierarchical feature learning
  - Layer 1 (128): Learns low-level patterns
  - Layer 2 (64): Combines patterns into mid-level features
  - Layer 3 (32): Creates high-level abstractions for prediction

- **Output**: 1 neuron producing probability (0-1)
  - 0 = Team will lose
  - 1 = Team will win
  - 0.5 = Toss-up game

### Total Parameters
Calculating the total weights and biases:

```
Input → Hidden1:  75 × 128 = 9,600 weights  + 128 biases  = 9,728
Hidden1 → Hidden2: 128 × 64 = 8,192 weights  + 64 biases  = 8,256
Hidden2 → Hidden3: 64 × 32 = 2,048 weights  + 32 biases  = 2,080
Hidden3 → Output:  32 × 1 = 32 weights     + 1 bias     = 33

TOTAL PARAMETERS: 20,097
```

The model learns **20,097 numerical values** during training!

---

## 2. Nodes (Neurons) and Layers {#nodes-and-layers}

### What is a Neuron?
A neuron is a computational unit that:
1. Receives inputs from previous layer (or input data)
2. Multiplies each input by a **weight**
3. Sums all weighted inputs
4. Adds a **bias** term
5. Applies an **activation function**
6. Outputs result to next layer

### Neuron Mathematical Formula

For a single neuron:
```
z = (w₁·x₁ + w₂·x₂ + ... + wₙ·xₙ) + b
output = activation(z)
```

Where:
- `xᵢ` = input values
- `wᵢ` = weights (learned during training)
- `b` = bias (learned during training)
- `z` = weighted sum
- `activation()` = ReLU or Sigmoid function

### Example: Single Neuron Calculation

**Inputs**: `[0.5, -0.2, 0.8]` (normalized team stats)  
**Weights**: `[0.7, -0.3, 0.9]` (learned values)  
**Bias**: `0.1`

**Calculation**:
```
z = (0.5 × 0.7) + (-0.2 × -0.3) + (0.8 × 0.9) + 0.1
z = 0.35 + 0.06 + 0.72 + 0.1
z = 1.23

output = ReLU(1.23) = 1.23  (ReLU returns input if positive)
```

### Layer-by-Layer Processing

**Input Layer** (75 neurons):
- Each neuron holds one normalized feature value
- Example: `neuron[0]` = is_home (0 or 1), `neuron[1]` = season (normalized), etc.
- No computation, just passes data forward

**Hidden Layer 1** (128 neurons):
- Each of 128 neurons receives all 75 inputs
- Each neuron has its own set of 75 weights + 1 bias
- Learns basic patterns: "home teams score more", "good offenses win", etc.
- **Total connections**: 75 → 128 = 9,600 weights

**Hidden Layer 2** (64 neurons):
- Each of 64 neurons receives all 128 outputs from Layer 1
- Combines basic patterns into more complex features
- Learns interactions: "home team + good offense = strong advantage"
- **Total connections**: 128 → 64 = 8,192 weights

**Hidden Layer 3** (32 neurons):
- Each of 32 neurons receives all 64 outputs from Layer 2
- Creates high-level abstractions
- Learns strategic patterns: "dominant EPA + home field + weak opponent = likely win"
- **Total connections**: 64 → 32 = 2,048 weights

**Output Layer** (1 neuron):
- Receives all 32 outputs from Layer 3
- Produces final win probability
- **Total connections**: 32 → 1 = 32 weights

---

## 3. Weights and Biases {#weights-and-biases}

### Weights

**What are weights?**
- Weights are the **learned parameters** that determine how much each input matters
- Each connection between neurons has a weight
- Positive weights = positive correlation
- Negative weights = negative correlation
- Magnitude = strength of relationship

**Example Weights**:
```python
# Hypothetical learned weights for "passing_yards" input
Weight to neuron focused on offense: +0.85 (strong positive)
Weight to neuron focused on defense: -0.12 (weak negative)
Weight to neuron focused on weather: +0.03 (negligible)
```

**Initial Weights**:
- Start: Random values (small, centered around 0)
- Example: Uniform distribution between -0.05 and +0.05
- Prevents symmetry breaking problem

**Trained Weights**:
- After training: Optimized values that minimize prediction error
- Range: Typically -3.0 to +3.0 after training
- Updated via backpropagation and gradient descent

### Biases

**What are biases?**
- Biases are **offset values** added to each neuron's weighted sum
- Allow neurons to activate even when all inputs are zero
- Provide flexibility in decision boundaries

**Bias Example**:
```python
# Without bias:
z = 0.5×w₁ + 0.3×w₂ = always 0 if inputs are 0

# With bias:
z = 0.5×w₁ + 0.3×w₂ + 0.7 = 0.7 even if inputs are 0
```

**Why biases matter**:
- Without bias: Neuron output always passes through origin
- With bias: Neuron can be "pre-activated" or "pre-inhibited"
- Example: Home team advantage = positive bias for home predictions

### Weight Initialization

Our model uses **Xavier/Glorot initialization**:
```python
weight_range = sqrt(6 / (n_inputs + n_outputs))
weights ~ Uniform(-weight_range, +weight_range)
```

Purpose: Prevents vanishing/exploding gradients during training

---

## 4. Activation Functions {#activation-functions}

### ReLU (Rectified Linear Unit)

**Used in**: Hidden Layers 1, 2, 3

**Formula**:
```
ReLU(x) = max(0, x)
```

**Behavior**:
- If input ≥ 0: Output = input
- If input < 0: Output = 0

**Graph**:
```
  output
    |
  3 |         /
  2 |        /
  1 |       /
  0 |______/
    |
 -1 +-------------> input
    -2  -1  0  1  2  3
```

**Why ReLU?**
- **Fast**: Simple computation
- **Non-linear**: Enables complex pattern learning
- **Prevents vanishing gradient**: Gradient = 1 for positive inputs
- **Sparse activation**: About 50% of neurons are zero (efficient)

**Example**:
```python
Hidden Layer 1 outputs: [-0.5, 0.3, 1.2, -0.1, 0.8]
After ReLU:             [0.0,  0.3, 1.2, 0.0,  0.8]
```

### Sigmoid

**Used in**: Output Layer

**Formula**:
```
Sigmoid(x) = 1 / (1 + e^(-x))
```

**Behavior**:
- Maps any input to range (0, 1)
- S-shaped curve
- Center point: Sigmoid(0) = 0.5

**Graph**:
```
  output
  1.0 |         _____
      |        /
  0.5 |       /
      |      /
  0.0 |_____/
      |
      +-------------> input
      -5  0  5
```

**Why Sigmoid for output?**
- **Probability interpretation**: Output is win probability (0-1)
- **Smooth gradients**: Enables gradient-based optimization
- **Decision boundary**: 0.5 = neutral prediction

**Example**:
```python
Final hidden layer output: 1.5

Sigmoid(1.5) = 1 / (1 + e^(-1.5))
             = 1 / (1 + 0.223)
             = 1 / 1.223
             = 0.817

Interpretation: 81.7% probability of winning
```

---

## 5. Training Process (Backpropagation) {#training-process}

### Overview

Training is the process of **adjusting weights and biases** to minimize prediction errors.

### Forward Pass

**What happens**:
1. Input data flows through network
2. Each layer computes outputs
3. Final layer produces prediction

**Example**:
```
Input: [team_stats] → Hidden1 → Hidden2 → Hidden3 → Output: 0.62
Actual result: Team won (label = 1)
Error: 0.62 - 1.00 = -0.38 (underpredicted)
```

### Loss Function

**Binary Cross-Entropy Loss**:
```
Loss = -[y·log(ŷ) + (1-y)·log(1-ŷ)]
```

Where:
- `y` = actual outcome (0 or 1)
- `ŷ` = predicted probability (0-1)

**Example**:
```
Actual: 1 (win)
Predicted: 0.62

Loss = -[1·log(0.62) + 0·log(0.38)]
     = -[-0.478 + 0]
     = 0.478
```

Higher loss = worse prediction  
Goal: Minimize loss across all training examples

### Backward Pass (Backpropagation)

**What happens**:
1. Calculate how much each weight contributed to error
2. Compute gradients (partial derivatives)
3. Update weights in direction that reduces loss

**Gradient Descent Update Rule**:
```
weight_new = weight_old - learning_rate × gradient
```

**Example**:
```
Old weight: 0.5
Gradient: 0.2 (positive = increase loss)
Learning rate: 0.001

New weight = 0.5 - (0.001 × 0.2)
           = 0.5 - 0.0002
           = 0.4998

(Weight decreased slightly to reduce loss)
```

### Training Algorithm (Adam Optimizer)

**Adam** = Adaptive Moment Estimation

**Features**:
- Adaptive learning rates per parameter
- Momentum: Uses moving average of past gradients
- Bias correction: Accounts for initialization bias

**Hyperparameters**:
- Initial learning rate: 0.001
- β₁ (momentum): 0.9
- β₂ (velocity): 0.999
- ε (stability): 1e-8

**Why Adam?**
- Converges faster than standard gradient descent
- Handles sparse gradients well
- Robust to hyperparameter choices

### Training Loop

```python
for epoch in range(100):  # Up to 100 epochs
    for batch in training_data:
        # Forward pass
        predictions = model.forward(batch.X)
        loss = compute_loss(predictions, batch.y)
        
        # Backward pass
        gradients = model.backward(loss)
        
        # Update weights
        optimizer.update(model.weights, gradients)
    
    # Check validation performance
    val_accuracy = evaluate(model, validation_data)
    
    # Early stopping if no improvement
    if val_accuracy < best_accuracy for 10 epochs:
        break
```

### Batch Training

**Batch size**: 32 games

**Why batches?**
- **Memory efficient**: Don't load all 26,944 records at once
- **Faster convergence**: Update weights more frequently
- **Regularization effect**: Noisy gradients help escape local minima

**Example**:
```
Training set: 26,944 games
Batch size: 32
Batches per epoch: 26,944 / 32 = 842 batches
Weight updates per epoch: 842 times
```

---

## 6. Sample Weighting Strategy {#sample-weighting}

### Why Weight Samples?

Not all training data is equally relevant:
- **Recent games** (2020-2023): Most similar to current NFL
- **Mid-range games** (2010-2019): Still relevant but rules have changed
- **Old games** (1999-2009): Useful for volume but different era

### Weighting Formula

```python
if season >= 2020:
    weight = 1.0   # 100% importance
elif season >= 2010:
    weight = 0.6   # 60% importance
else:
    weight = 0.2   # 20% importance
```

### Impact on Training

**Without weighting**:
- All 26,944 games treated equally
- Model might learn outdated patterns
- Example: 1999 offensive strategies (run-heavy) vs 2023 (pass-heavy)

**With weighting**:
- Recent games have more influence on loss function
- Model prioritizes learning current NFL patterns
- Older games provide volume but don't dominate learning

**Loss Calculation**:
```
Weighted Loss = Σ (weight_i × loss_i) / Σ weight_i
```

**Example**:
```
2022 game prediction error: 0.3 → Weighted error: 1.0 × 0.3 = 0.3
2005 game prediction error: 0.3 → Weighted error: 0.6 × 0.3 = 0.18
1999 game prediction error: 0.3 → Weighted error: 0.2 × 0.3 = 0.06

Model focuses on fixing 2022 errors (5x more important than 1999)
```

### Training Data Distribution

```
Era          | Games  | Weight | Effective Influence
-------------|--------|--------|-------------------
2020-2023    | 2,136  | 1.0    | 2,136 (36%)
2010-2019    | 5,340  | 0.6    | 3,204 (54%)
1999-2009    | 5,886  | 0.2    | 1,177 (20%)
-------------|--------|--------|-------------------
Total        | 13,362 |        | 5,898 effective
```

---

## 7. Model Performance {#performance}

### Training Data Split

```
Total records: 14,312 team-game records

Training (1999-2023):   26,944 records (70%)
Validation (2024):       1,140 records (15%)
Test (2025):              540 records (15%)
```

### Performance Metrics

**Accuracy**: Percentage of correct predictions
```
Accuracy = (Correct Predictions) / (Total Predictions)
```

**Target Performance**:
- Baseline (no EPA): 55% accuracy
- With EPA + historical data: 60-65% accuracy

**Confusion Matrix**:
```
                 Predicted
                 Loss  Win
Actual  Loss     TN    FP
        Win      FN    TP

TN = True Negative (correctly predicted loss)
FP = False Positive (predicted win but lost)
FN = False Negative (predicted loss but won)
TP = True Positive (correctly predicted win)
```

### Why 60-65% is Good

**Context**:
- NFL is highly competitive (parity by design)
- Vegas betting lines: ~52-55% accuracy
- Best sports betting models: ~57-60% accuracy
- **Our target**: 60-65% with EPA data

**Challenges**:
- Injuries not reflected in stats
- Weather conditions
- Referee decisions
- "Any Given Sunday" - upsets happen!

---

## 8. Mathematical Foundations {#mathematics}

### Matrix Operations

Neural networks use **matrix multiplication** for efficiency.

**Layer computation**:
```
Output = activation(Input × Weights + Bias)
```

**Example (simplified)**:
```python
# Input: 3 features, Output: 2 neurons
Input = [x₁, x₂, x₃]  # Shape: (1, 3)

Weights = [[w₁₁, w₁₂],  # Shape: (3, 2)
           [w₂₁, w₂₂],
           [w₃₁, w₃₂]]

Bias = [b₁, b₂]  # Shape: (1, 2)

# Matrix multiplication
Z = Input @ Weights + Bias
  = [x₁, x₂, x₃] @ [[w₁₁, w₁₂],
                     [w₂₁, w₂₂],
                     [w₃₁, w₃₂]] + [b₁, b₂]
  
  = [x₁·w₁₁ + x₂·w₂₁ + x₃·w₃₁ + b₁,
     x₁·w₁₂ + x₂·w₂₂ + x₃·w₃₂ + b₂]

Output = ReLU(Z)
```

### Gradient Computation

**Chain rule** for backpropagation:

```
∂Loss/∂weight = ∂Loss/∂output × ∂output/∂activation × ∂activation/∂weighted_sum × ∂weighted_sum/∂weight
```

**Example**:
```
Loss = (predicted - actual)²
Output layer: Sigmoid activation

∂Loss/∂weight = 2·(predicted - actual) × sigmoid'(z) × input

If predicted=0.8, actual=1.0, z=1.5, input=0.7:
∂Loss/∂weight = 2·(0.8-1.0) × (0.2×0.8) × 0.7
               = 2·(-0.2) × 0.16 × 0.7
               = -0.0448

Weight update = weight - 0.001 × (-0.0448)
              = weight + 0.0000448
```

### Normalization (StandardScaler)

**Formula**:
```
x_normalized = (x - mean) / std_deviation
```

**Why normalize?**
- Different features have different scales
  - Season: 1999-2025 (range: 26)
  - Points: 0-60 (range: 60)
  - Success rate: 0-1 (range: 1)
- Normalization makes all features comparable
- Improves training speed and stability

**Example**:
```
Raw passing yards: [250, 300, 280, 320]
Mean: 287.5
Std: 29.9

Normalized: [(250-287.5)/29.9, (300-287.5)/29.9, ...]
          = [-1.25, 0.42, -0.25, 1.09]
```

---

## Summary: Key Technical Facts

### Architecture
- **Type**: Feed-forward deep neural network
- **Layers**: 5 total (1 input, 3 hidden, 1 output)
- **Neurons**: 75 → 128 → 64 → 32 → 1 = 300 total neurons
- **Parameters**: 20,097 learnable weights and biases

### Training
- **Algorithm**: Backpropagation with Adam optimizer
- **Learning rate**: 0.001 (adaptive)
- **Batch size**: 32 games
- **Max epochs**: 100 (with early stopping)
- **Loss function**: Binary cross-entropy

### Data
- **Training samples**: 26,944 team-games (1999-2023)
- **Features**: 75 dimensions (51 basic + 13 EPA + 11 context)
- **Sample weighting**: Recent seasons weighted higher (1.0 → 0.6 → 0.2)

### Performance
- **Target accuracy**: 60-65%
- **Baseline**: 55% (without EPA)
- **Vegas lines**: 52-55% accuracy
- **Best models**: 57-60% accuracy

---

## Academic Alignment (Dr. Foster's Curriculum)

This project demonstrates key concepts from machine learning:

✅ **Neurons**: Individual computational units with weights and biases  
✅ **Neural Networks**: Interconnected layers forming deep architecture  
✅ **Activation Functions**: ReLU for hidden layers, Sigmoid for output  
✅ **Backpropagation**: Gradient-based learning algorithm  
✅ **Training/Validation/Test**: Proper data splitting methodology  
✅ **Regularization**: Sample weighting, early stopping, adaptive learning  
✅ **Real-world application**: Solving actual NFL prediction problem  

---

**For more details, see**:
- `ml/nfl_neural_network.py` - Full implementation
- `SPRINT_9_PLAN.md` - Project planning
- Dr. Foster Dashboard - Visual schematic (coming next!)

