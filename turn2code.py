import numpy as np

def relu(x):
    """ReLU activation function."""
    return np.maximum(0, x)

def relu_derivative(x):
    """ReLU function ka derivative (gradient calculation ke liye)."""
    return (x > 0).astype(float)  # Agar x > 0 hai to 1, warna 0

def softmax(x):
    """Softmax activation function."""
    exp_x = np.exp(x - np.max(x))  # Numerical stability ke liye max(x) minus kiya
    return exp_x / np.sum(exp_x, axis=0)

def cross_entropy_loss(y_pred, y_true):
    """Categorical cross-entropy loss function."""
    m = y_true.shape[1]
    loss = -np.sum(y_true * np.log(y_pred + 1e-8)) / m  # Small value add kiya stability ke liye
    return loss

def forward_pass(X, W1, B1, W2, B2):
    """Neural network ka forward pass perform karta hai."""
    Z1 = np.dot(W1, X) + B1
    H = relu(Z1)
    Z2 = np.dot(W2, H) + B2
    output = softmax(Z2)
    return Z1, H, Z2, output

def backward_pass(X, Y, W1, B1, W2, B2, learning_rate):
    """Neural network ka backpropagation algorithm implement karta hai."""
    
    # Forward pass execute karna
    Z1, H, Z2, output = forward_pass(X, W1, B1, W2, B2)
    
    # Loss compute karna
    loss = cross_entropy_loss(output, Y)
    
    # Output layer error aur gradient calculation
    m = X.shape[1]  
    dZ2 = output - Y  
    dW2 = np.dot(dZ2, H.T) / m  
    dB2 = np.sum(dZ2, axis=1, keepdims=True) / m  
    
    # Hidden layer error aur gradient calculation
    dH = np.dot(W2.T, dZ2)  
    dZ1 = dH * relu_derivative(Z1)  
    dW1 = np.dot(dZ1, X.T) / m  
    dB1 = np.sum(dZ1, axis=1, keepdims=True) / m  
    
    # Weights aur biases update karna
    W1 -= learning_rate * dW1  
    B1 -= learning_rate * dB1  
    W2 -= learning_rate * dW2  
    B2 -= learning_rate * dB2  

    return W1, B1, W2, B2, loss

# Neural Network Configuration
np.random.seed(42)  
input_size = 4
hidden_size = 5
output_size = 3
learning_rate = 0.01
epochs = 1000  

# Initialize Weights and Biases
W1 = np.random.rand(hidden_size, input_size)
B1 = np.random.rand(hidden_size, 1)
W2 = np.random.rand(output_size, hidden_size)
B2 = np.random.rand(output_size, 1)

# Training Data (X -> Inputs, Y -> One-hot Encoded Labels)
X = np.random.rand(input_size, 1)  
Y = np.zeros((output_size, 1))  
Y[np.random.randint(0, output_size)] = 1  

# Training Loop
for epoch in range(epochs):
    W1, B1, W2, B2, loss = backward_pass(X, Y, W1, B1, W2, B2, learning_rate)
    if epoch % 100 == 0:
        print(f"Epoch {epoch}, Loss: {loss:.4f}")

# Final Output after Training
_, _, _, final_output = forward_pass(X, W1, B1, W2, B2)
print("Final Network Output:\n", final_output)