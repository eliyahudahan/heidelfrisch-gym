"""
HeidelFrisch Gym – Single Neuron (Fixed Version)
==================================================
Now with normalized inputs and proper learning
"""

import random
import math

class Neuron:
    """
    A single neuron that learns from normalized data.
    """
    
    def __init__(self, num_inputs):
        """
        Initialize neuron with random weights and bias.
        
        Args:
            num_inputs: number of features (after normalization)
        """
        # Smaller initialization range to prevent saturation
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(num_inputs)]
        self.bias = random.uniform(-0.5, 0.5)
        
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
        
        print(f"\n📉 Error: {error:.4f}, Delta: {delta:.4f}")
        
        # Update each weight
        for i in range(len(self.weights)):
            input_val = forward_info['inputs'][i]
            weight_grad = input_val * delta
            
            old_weight = self.weights[i]
            self.weights[i] -= learning_rate * weight_grad
            
            print(f"   Weight[{i}]: {old_weight:.4f} → {self.weights[i]:.4f} "
                  f"(grad: {weight_grad:.4f})")
        
        # Update bias
        old_bias = self.bias
        bias_grad = delta
        self.bias -= learning_rate * bias_grad
        
        print(f"   Bias: {old_bias:.4f} → {self.bias:.4f} "
              f"(grad: {bias_grad:.4f})")
        
        return abs(error)


# ============================================
# TESTING WITH NORMALIZED DATA
# ============================================

def create_normalized_test_data():
    """
    Create test data that's already normalized to [0,1]
    """
    # Normalized values:
    # temp_above_2c: 2.5 → assume range 0-5 → 0.5
    # heat_exposure: 15 → assume range 0-30 → 0.5
    # is_peak: 1 → 1.0 (already binary)
    
    test_cases = [
        # [temp_above_2c_norm, heat_exposure_norm, is_peak] → target
        ([0.5, 0.5, 1], 1),   # peak, medium temp+delay → collect
        ([0.1, 0.1, 0], 0),   # off-peak, low temp+delay → don't collect
        ([0.9, 0.8, 1], 1),   # peak, high temp+delay → collect
        ([0.2, 0.9, 0], 0),   # off-peak, high delay but low temp → don't collect
    ]
    
    return test_cases


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Fixed Neuron with Normalized Data")
    print("=" * 60)
    
    # Create neuron (3 inputs)
    neuron = Neuron(3)
    
    # Get normalized test data
    test_data = create_normalized_test_data()
    
    print("\n📊 Training on normalized data...")
    
    # Train for multiple epochs
    for epoch in range(10):
        print(f"\n--- Epoch {epoch + 1} ---")
        total_error = 0
        
        for inputs, target in test_data:
            result = neuron.forward(inputs)
            error = neuron.backward(result, target, learning_rate=0.5)
            total_error += error
            
            print(f"   Inputs: {[round(x, 2) for x in inputs]} → "
                  f"Predicted: {result['activated']:.4f} (target: {target})")
        
        avg_error = total_error / len(test_data)
        print(f"   📊 Average error: {avg_error:.4f}")
    
    print("\n✅ Fixed neuron ready for layer construction!")
