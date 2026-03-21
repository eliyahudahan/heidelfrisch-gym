"""
HeidelFrisch Gym – Single Neuron
==================================
Building a neuron from scratch (like DortmundFlow)
But now for freshness prediction

Input features will come from FeatureEngineer:
- temp_above_2c
- heat_exposure
- is_peak
- peak_factor
- weighted_delay
- hour_sin, hour_cos
"""

import random
import math

class Neuron:
    """
    A single neuron that learns from data.
    Same as DortmundFlow, but can handle any number of inputs.
    """
    
    def __init__(self, num_inputs):
        """
        Initialize neuron with random weights and bias.
        
        Args:
            num_inputs: how many features we have (will be 6-7)
        """
        # Each input gets a random weight between -1 and 1
        self.weights = [random.uniform(-0.1, 0.1) for _ in range(num_inputs)]
        
        # Bias – the neuron's baseline tendency
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
        Forward pass – compute output from inputs
        
        Args:
            inputs: list of feature values (e.g., [temp, heat, is_peak, ...])
        
        Returns:
            dictionary with raw_sum and activated output
        """
        # Weighted sum
        weighted_sum = 0
        
        for i in range(len(inputs)):
            weighted_sum += inputs[i] * self.weights[i]
        
        # Add bias
        weighted_sum += self.bias
        
        # Activate
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
            learning_rate: how big a step to take
        """
        # Get predicted value
        predicted = forward_info['activated']
        
        # Calculate error
        error = predicted - target
        
        # Derivative of sigmoid
        sigmoid_grad = predicted * (1 - predicted)
        
        # Delta – how much raw_sum contributed to error
        delta = error * sigmoid_grad
        
        print(f"\n📉 Error: {error:.4f}, Delta: {delta:.4f}")
        
        # Update each weight
        for i in range(len(self.weights)):
            input_val = forward_info['inputs'][i]
            
            # Gradient for this weight
            weight_grad = input_val * delta
            
            # Update weight
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


# Quick test
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Testing Single Neuron")
    print("=" * 50)
    
    # Create neuron (will have 3 inputs for this test)
    neuron = Neuron(3)
    
    # Test data: [temp_above_2c, heat_exposure, is_peak]
    test_inputs = [2.5, 15.0, 1]
    target = 1  # should collect
    
    # Forward pass
    result = neuron.forward(test_inputs)
    print(f"\n🔮 Forward pass:")
    print(f"   Raw sum: {result['raw_sum']:.4f}")
    print(f"   Activated: {result['activated']:.4f}")
    
    # Backward pass
    error = neuron.backward(result, target, learning_rate=0.1)
    print(f"\n📊 Absolute error: {error:.4f}")
