"""
HeidelFrisch Gym – Neuron with Early Stopping
================================================
A single neuron that learns with validation and early stopping
to prevent overfitting.

Key concepts:
- Training set: used to update weights
- Validation set: used to check if model generalizes
- Early stopping: stop when validation error stops improving
- Patience: how many epochs to wait before stopping

This is exactly how professional ML models are trained!
"""

import random
import math

# ============================================
# NEURON CLASS (SAME AS BEFORE)
# ============================================

class Neuron:
    """
    A single neuron that learns from normalized data.
    Includes forward and backward passes.
    """
    
    def __init__(self, num_inputs):
        """
        Initialize neuron with small random weights.
        
        Args:
            num_inputs: number of features (after normalization)
        """
        # Small weights prevent saturation at start
        self.weights = [random.uniform(-0.1, 0.1) for _ in range(num_inputs)]
        self.bias = random.uniform(-0.1, 0.1)
        
        print(f"✨ Neuron created with {num_inputs} inputs")
        print(f"   Initial weights: {[round(w, 3) for w in self.weights]}")
        print(f"   Initial bias: {round(self.bias, 3)}")
    
    def sigmoid(self, x):
        """
        Activation function – squashes any number to (0,1)
        """
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    def forward(self, inputs):
        """
        Forward pass – compute output from normalized inputs
        
        Args:
            inputs: list of feature values (normalized to [0,1])
        
        Returns:
            dictionary with raw_sum and activated output
        """
        weighted_sum = 0
        
        for i in range(len(inputs)):
            weighted_sum += inputs[i] * self.weights[i]
        
        weighted_sum += self.bias
        activated = self.sigmoid(weighted_sum)
        
        return {
            'raw_sum': weighted_sum,
            'activated': activated,
            'inputs': inputs
        }
    
    def backward(self, forward_info, target, learning_rate):
        """
        Backward pass – learn from error
        
        Args:
            forward_info: dictionary from forward()
            target: what the output should be (0 or 1)
            learning_rate: how big a step to take (0.1-0.5 recommended)
        """
        predicted = forward_info['activated']
        error = predicted - target
        
        # Derivative of sigmoid
        sigmoid_grad = predicted * (1 - predicted)
        
        # Delta – how much raw_sum contributed to error
        delta = error * sigmoid_grad
        
        print(f"   📉 Error: {error:.4f}, Delta: {delta:.4f}")
        
        # Update each weight
        for i in range(len(self.weights)):
            input_val = forward_info['inputs'][i]
            weight_grad = input_val * delta
            
            old_weight = self.weights[i]
            self.weights[i] -= learning_rate * weight_grad
            
            print(f"      Weight[{i}]: {old_weight:.4f} → {self.weights[i]:.4f} "
                  f"(grad: {weight_grad:.4f})")
        
        # Update bias
        old_bias = self.bias
        bias_grad = delta
        self.bias -= learning_rate * bias_grad
        
        print(f"      Bias: {old_bias:.4f} → {self.bias:.4f} "
              f"(grad: {bias_grad:.4f})")
        
        return abs(error)


# ============================================
# EARLY STOPPING TRAINER
# ============================================

class EarlyStoppingTrainer:
    """
    Trains a neuron with validation set and early stopping.
    
    Why early stopping?
    - Training error always decreases (good for training set)
    - Validation error eventually increases (bad for new data)
    - We stop at the point where validation error is lowest
    """
    
    def __init__(self, neuron, learning_rate=0.5, patience=5):
        """
        Initialize trainer.
        
        Args:
            neuron: the Neuron object to train
            learning_rate: step size for weight updates
            patience: how many epochs to wait after validation error stops improving
        """
        self.neuron = neuron
        self.learning_rate = learning_rate
        self.patience = patience
        
        # Track best model
        self.best_weights = None
        self.best_bias = None
        self.best_val_error = float('inf')
        self.best_epoch = 0
        
        # Track patience counter
        self.wait = 0
        
    def create_data_split(self, all_data, train_ratio=0.75):
        """
        Split data into training and validation sets.
        
        Args:
            all_data: list of (inputs, target) pairs
            train_ratio: proportion for training (rest for validation)
        
        Returns:
            train_data, val_data
        """
        split_idx = int(len(all_data) * train_ratio)
        train_data = all_data[:split_idx]
        val_data = all_data[split_idx:]
        
        print(f"\n📊 Data split:")
        print(f"   Training: {len(train_data)} samples")
        print(f"   Validation: {len(val_data)} samples")
        
        return train_data, val_data
    
    def train_epoch(self, train_data):
        """
        Train for one epoch on all training samples.
        
        Returns:
            average training error for this epoch
        """
        total_error = 0
        
        for inputs, target in train_data:
            # Forward pass
            result = self.neuron.forward(inputs)
            
            # Backward pass (learn)
            error = self.neuron.backward(result, target, self.learning_rate)
            total_error += error
        
        return total_error / len(train_data)
    
    def validate(self, val_data):
        """
        Check performance on validation set (no learning!).
        
        Returns:
            average validation error
        """
        total_error = 0
        
        for inputs, target in val_data:
            result = self.neuron.forward(inputs)
            error = abs(result['activated'] - target)
            total_error += error
        
        return total_error / len(val_data)
    
    def train(self, train_data, val_data, max_epochs=100):
        """
        Full training with early stopping.
        
        Args:
            train_data: list of (inputs, target) for training
            val_data: list of (inputs, target) for validation
            max_epochs: maximum number of epochs to run
        
        Returns:
            dictionary with training history
        """
        print("\n" + "=" * 60)
        print("🚀 Starting training with early stopping")
        print("=" * 60)
        print(f"   Learning rate: {self.learning_rate}")
        print(f"   Patience: {self.patience}")
        print(f"   Max epochs: {max_epochs}")
        
        history = {
            'train_errors': [],
            'val_errors': [],
            'best_epoch': 0,
            'best_val_error': float('inf')
        }
        
        for epoch in range(max_epochs):
            print(f"\n--- Epoch {epoch + 1} ---")
            
            # Train
            train_error = self.train_epoch(train_data)
            history['train_errors'].append(train_error)
            
            # Validate
            val_error = self.validate(val_data)
            history['val_errors'].append(val_error)
            
            print(f"   📊 Train error: {train_error:.4f}, Val error: {val_error:.4f}")
            
            # Check if this is the best validation error so far
            if val_error < self.best_val_error:
                print(f"   🏆 New best validation error! (was {self.best_val_error:.4f})")
                self.best_val_error = val_error
                self.best_epoch = epoch
                self.best_weights = self.neuron.weights.copy()
                self.best_bias = self.neuron.bias
                self.wait = 0
            else:
                self.wait += 1
                print(f"   ⏳ No improvement for {self.wait}/{self.patience} epochs")
                
                # Early stopping condition
                if self.wait >= self.patience:
                    print(f"\n✅ Early stopping triggered after {epoch + 1} epochs")
                    print(f"   Best validation error was at epoch {self.best_epoch + 1}: {self.best_val_error:.4f}")
                    
                    # Restore best model
                    self.neuron.weights = self.best_weights
                    self.neuron.bias = self.best_bias
                    
                    history['best_epoch'] = self.best_epoch
                    history['best_val_error'] = self.best_val_error
                    break
        
        # If we reached max epochs without early stopping
        if self.wait < self.patience:
            print(f"\n✅ Reached max epochs ({max_epochs})")
            print(f"   Best validation error was at epoch {self.best_epoch + 1}: {self.best_val_error:.4f}")
            
            # Restore best model
            self.neuron.weights = self.best_weights
            self.neuron.bias = self.best_bias
            
            history['best_epoch'] = self.best_epoch
            history['best_val_error'] = self.best_val_error
        
        return history


# ============================================
# CREATE TEST DATA (NORMALIZED)
# ============================================

def create_freshness_dataset():
    """
    Create a small dataset for freshness prediction.
    
    Features (normalized to 0-1):
    - temp_above_2c: 0 = cold, 1 = very hot
    - heat_exposure: 0 = no exposure, 1 = max exposure
    - is_peak: 0 = off-peak, 1 = peak hour
    
    Target: 1 = collect (freshness OK), 0 = don't collect (spoilage risk)
    """
    dataset = [
        # [temp, heat, peak] → target
        ([0.2, 0.1, 0], 1),   # Cold, low exposure, off-peak → COLLECT
        ([0.3, 0.2, 0], 1),   # Still OK
        ([0.5, 0.3, 0], 1),   # Moderate, still OK
        ([0.7, 0.4, 0], 1),   # Warm but off-peak → maybe collect
        ([0.8, 0.6, 1], 0),   # Warm, high exposure, peak → DON'T collect
        ([0.9, 0.8, 1], 0),   # Very warm, high exposure, peak → DON'T collect
        ([0.6, 0.7, 1], 0),   # Moderate but peak and high exposure → DON'T collect
        ([0.4, 0.5, 0], 1),   # Low-medium, off-peak → COLLECT
    ]
    
    print("\n📦 Created freshness dataset with 8 samples")
    return dataset


# ============================================
# MAIN TESTING
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Testing Neuron with Early Stopping")
    print("=" * 60)
    
    # === STEP 1: Create dataset ===
    all_data = create_freshness_dataset()
    
    # === STEP 2: Create neuron ===
    print("\n🔧 Initializing neuron...")
    neuron = Neuron(num_inputs=3)  # 3 features
    
    # === STEP 3: Create trainer ===
    trainer = EarlyStoppingTrainer(
        neuron=neuron,
        learning_rate=0.5,
        patience=5  # Stop after 5 epochs without improvement
    )
    
    # === STEP 4: Split data ===
    train_data, val_data = trainer.create_data_split(all_data, train_ratio=0.75)
    
    print("\n📋 Training data:")
    for i, (inputs, target) in enumerate(train_data):
        print(f"   {i+1}: {[round(x,1) for x in inputs]} → {target}")
    
    print("\n🔍 Validation data:")
    for i, (inputs, target) in enumerate(val_data):
        print(f"   {i+1}: {[round(x,1) for x in inputs]} → {target}")
    
    # === STEP 5: Train with early stopping ===
    history = trainer.train(
        train_data=train_data,
        val_data=val_data,
        max_epochs=50
    )
    
    # === STEP 6: Final evaluation ===
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"\n🏆 Best model from epoch {history['best_epoch'] + 1}:")
    print(f"   Validation error: {history['best_val_error']:.4f}")
    print(f"   Final weights: {[round(w, 3) for w in neuron.weights]}")
    print(f"   Final bias: {round(neuron.bias, 3)}")
    
    print("\n🔮 Testing on all data with best model:")
    for inputs, target in all_data:
        result = neuron.forward(inputs)
        decision = "COLLECT" if result['activated'] > 0.5 else "DON'T COLLECT"
        correct = "✅" if (result['activated'] > 0.5) == (target == 1) else "❌"
        print(f"   {correct} Inputs: {[round(x,1) for x in inputs]} → "
              f"Pred: {result['activated']:.3f} ({decision}), Target: {target}")
    
    print("\n✅ Training complete! Model is ready for layer construction.")
