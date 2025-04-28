import numpy as np  
import matplotlib.pyplot as plt  

# Hyperparameters ka nirdharan
input_size = 4  # Pratyek input data point me 4 features honge  
hidden_size = 5  # Hidden layer me 5 neurons honge  
output_size = 3  # Output 3 classes me se ek hoga  
initial_learning_rate = 0.1  # Adhyayan ke prarambh me gati ki dar  
decay_rate = 0.01  # Learning rate ko dheere-dheere kam karne ka factor  
momentum = 0.9  # Pehle ke gradients ka kitna prabhav naye updates pe hoga  
batch_size = 2  # Har iteration me kitne samples ka upyog hoga  
epochs = 1000  # Maximum baar poore dataset ka training hone ka sankhya  
patience = 10  # Early stopping ke liye maximum epochs jab tak loss improve na ho  

# Weight aur Bias ka initialisation
np.random.seed(42)  # Har baar ek jaisa result lane ke liye random seed set karna  
weights_input_hidden = np.random.randn(input_size, hidden_size)  # Input layer se hidden layer ke weights  
bias_hidden = np.zeros((1, hidden_size))  # Hidden layer ke biases  
weights_hidden_output = np.random.randn(hidden_size, output_size)  # Hidden layer se output layer ke weights  
bias_output = np.zeros((1, output_size))  # Output layer ke biases  

# Activation aur Loss Functions ka nirdharan
def relu(x):  
    """ReLU activation function jo negative values ko 0 bana deta hai"""  
    return np.maximum(0, x)  

def softmax(x):  
    """Softmax function jo output ko probability distribution me convert karta hai"""  
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))  # Numerical stability ke liye max value subtract karna  
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)  # Probability distribution nikalna  

def cross_entropy_loss(y_true, y_pred):  
    """Cross-entropy loss function jo model ki prediction aur actual output ke beech ka antar measure karta hai"""  
    return -np.mean(np.sum(y_true * np.log(y_pred + 1e-8), axis=1))  # 1e-8 numerical stability ke liye add kiya gaya hai  

# Training Function jo Adaptive Learning Rate, Momentum & Early Stopping ka upyog karega  
def train(X, y):  
    global weights_input_hidden, bias_hidden, weights_hidden_output, bias_output  

    # Momentum ke liye velocity variables ka initialisation
    velocity_w_ih = np.zeros_like(weights_input_hidden)  
    velocity_b_h = np.zeros_like(bias_hidden)  
    velocity_w_ho = np.zeros_like(weights_hidden_output)  
    velocity_b_o = np.zeros_like(bias_output)  

    best_loss = float('inf')  # Sabse kam loss ko track karne ke liye  
    patience_counter = 0  # Agar loss improve nahi ho raha hai to patience badhta jayega  
    loss_history = []  # Har epoch ka loss store karne ke liye  
    learning_rate = initial_learning_rate  # Shuruaati learning rate  

    for epoch in range(epochs):  
        indices = np.arange(X.shape[0])  # Data ke indices generate karna  
        np.random.shuffle(indices)  # Data ko randomly shuffle karna  
        X_shuffled, y_shuffled = X[indices], y[indices]  # Naye shuffled sequence me X aur y set karna  

        for i in range(0, X.shape[0], batch_size):  
            X_batch = X_shuffled[i:i+batch_size]  # Batch size ke hisaab se input data lena  
            y_batch = y_shuffled[i:i+batch_size]  # Us batch ke corresponding output labels lena  

            # Forward pass (aage badhne ki prakriya) 
            hidden_input = np.dot(X_batch, weights_input_hidden) + bias_hidden  # Input layer se hidden layer tak signal  
            hidden_output = relu(hidden_input)  # Hidden layer ka activation  
            output_input = np.dot(hidden_output, weights_hidden_output) + bias_output  # Hidden layer se output layer tak signal  
            y_pred = softmax(output_input)  # Output layer ka activation jo probability deta hai  

            # Loss Calculation (model ki galti ka hisaab)  
            loss = cross_entropy_loss(y_batch, y_pred)  

            # Backward pass (Peeche propagate karke gradients nikalna) 
            output_error = y_pred - y_batch  # Output error nikalna  
            hidden_error = np.dot(output_error, weights_hidden_output.T) * (hidden_input > 0)  # ReLU derivative ka use  

            # Momentum-based Weight Updates  
            velocity_w_ho = momentum * velocity_w_ho - learning_rate * np.dot(hidden_output.T, output_error) / batch_size  
            weights_hidden_output += velocity_w_ho  # Hidden-Output weights update  

            velocity_b_o = momentum * velocity_b_o - learning_rate * np.mean(output_error, axis=0, keepdims=True)  
            bias_output += velocity_b_o  # Output layer ke biases update  

            velocity_w_ih = momentum * velocity_w_ih - learning_rate * np.dot(X_batch.T, hidden_error) / batch_size  
            weights_input_hidden += velocity_w_ih  # Input-Hidden weights update  

            velocity_b_h = momentum * velocity_b_h - learning_rate * np.mean(hidden_error, axis=0, keepdims=True)  
            bias_hidden += velocity_b_h  # Hidden layer ke biases update  

        # Adaptive Learning Rate Update (har epoch ke baad learning rate kam karna)
        learning_rate = initial_learning_rate * np.exp(-decay_rate * epoch)  

        loss_history.append(loss)  # Loss ko history me store karna  

        # Early Stopping Check (agar loss improve nahi ho raha ho to ruk jaana)
        if loss < best_loss:  
            best_loss = loss  
            patience_counter = 0  # Agar loss kam ho raha hai to patience reset karna  
        else:  
            patience_counter += 1  # Agar loss improve nahi ho raha hai to patience count badh jayega  

        if patience_counter >= patience:  
            print(f"Stopping early at epoch {epoch} due to no improvement in loss.")  
            break  

        if epoch % 100 == 0:  
            print(f"Epoch {epoch}, Loss: {loss:.4f}, Learning Rate: {learning_rate:.5f}")  

    return loss_history  

# Data Generation & Training Function Call
X_train = np.random.rand(10, input_size)  # Random training data generate karna  
y_train = np.eye(output_size)[np.random.choice(output_size, 10)]  # Output labels ko one-hot encoding format me banana  
loss_history = train(X_train, y_train)  # Model ko train karna  

# Loss ka Visualization (Training ka graph plot karna)  
plt.plot(loss_history)  
plt.xlabel("Epochs")  
plt.ylabel("Loss")  
plt.title("Training Loss Over Time")  
plt.show()  