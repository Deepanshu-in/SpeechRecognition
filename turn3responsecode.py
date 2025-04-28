import numpy as np  

# Hyperparameters (Model ke configurations)
input_size = 4      # Input layer mein neurons ki sankhya (features ki sankhya)
hidden_size = 5     # Hidden layer mein neurons ki sankhya  
output_size = 3     # Output layer mein neurons ki sankhya (classes ki sankhya)  
learning_rate = 0.01  # Gradient descent ke liye learning rate  
batch_size = 2      # Har batch mein kitne samples honge  
epochs = 1000       # Kitne baar poora dataset train kiya jayega  

# Random weight ke initialization
np.random.seed(42)  # Reproducibility ke liye random seed set karna  
weights_input_hidden = np.random.randn(input_size, hidden_size)  # Input se hidden layer ke weights  
bias_hidden = np.zeros((1, hidden_size))  # Hidden layer ka bias  
weights_hidden_output = np.random.randn(hidden_size, output_size)  # Hidden se output layer ke weights  
bias_output = np.zeros((1, output_size))  # Output layer ka bias  

# Activation Functions  
def relu(x):  
    """ReLU activation function jo negative values ko 0 kar deta hai aur positive values ko as it is rakhta hai"""  
    return np.maximum(0, x)  

def relu_derivative(x):  
    """ReLU function ka derivative, jo sirf positive inputs ke liye 1 deta hai, otherwise 0"""  
    return (x > 0).astype(float)  

def softmax(x):  
    """Softmax function jo probabilities calculate karta hai classification ke liye"""  
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))  # Numerical stability ke liye max value minus karna  
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)  # Normalized probabilities return karta hai  

# Loss Function (Cross-Entropy Loss)
def cross_entropy_loss(y_true, y_pred):  
    """Categorical cross-entropy loss function jo classification problems mein use hoti hai"""  
    return -np.mean(np.sum(y_true * np.log(y_pred + 1e-8), axis=1))  # Small value add karna numerical stability ke liye  

# Mini-batch Gradient Descent ka implementation
def train(X, y):  
    """Neural network ko mini-batch gradient descent ka use karke train karna"""  
    global weights_input_hidden, bias_hidden, weights_hidden_output, bias_output  

    for epoch in range(epochs):  
        # Dataset shuffle karna taaki har epoch mein batches random ho
        indices = np.arange(X.shape[0])  
        np.random.shuffle(indices)  
        X_shuffled, y_shuffled = X[indices], y[indices]  

        for i in range(0, X.shape[0], batch_size):  
            # Mini-batch creation 
            X_batch = X_shuffled[i:i+batch_size]  
            y_batch = y_shuffled[i:i+batch_size]  

            # Forward pass
            hidden_input = np.dot(X_batch, weights_input_hidden) + bias_hidden  # Input layer se hidden layer  
            hidden_output = relu(hidden_input)  # Hidden layer activation  
            output_input = np.dot(hidden_output, weights_hidden_output) + bias_output  # Hidden se output layer  
            y_pred = softmax(output_input)  # Output probabilities  

            #Loss calculation  
            loss = cross_entropy_loss(y_batch, y_pred)  

            # Backward pass (Gradient Calculation)
            output_error = y_pred - y_batch  # Output layer ka error  
            hidden_error = np.dot(output_error, weights_hidden_output.T) * relu_derivative(hidden_output)  # Hidden layer ka error  

            # Weights aur biases update karna using Gradient Descent 
            weights_hidden_output -= learning_rate * np.dot(hidden_output.T, output_error) / batch_size  
            bias_output -= learning_rate * np.mean(output_error, axis=0, keepdims=True)  
            weights_input_hidden -= learning_rate * np.dot(X_batch.T, hidden_error) / batch_size  
            bias_hidden -= learning_rate * np.mean(hidden_error, axis=0, keepdims=True)  

        # Har 100 epochs ke baad loss print karna taaki training ka progress track ho sake 
        if epoch % 100 == 0:  
            print(f"Epoch {epoch}, Loss: {loss:.4f}")  

# Dummy Dataset ka creation 
X_train = np.random.rand(10, input_size)  # Random input features  
y_train = np.eye(output_size)[np.random.choice(output_size, 10)]  # One-hot encoded labels  

# Model Training ka call
train(X_train, y_train)  