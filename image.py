import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Embedding, Dense, Dropout, TimeDistributed, RepeatVector, Concatenate, Add, Activation, Lambda, Layer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import numpy as np
import pandas as pd
import os
import nltk
from PIL import Image
import json
import cv2
import requests
import zipfile
import io
import time

def download_coco_dataset():
    """
    Download the COCO dataset annotations and images subset.
    Returns the path to the annotations file.
    """
    # Create directories if they don't exist
    os.makedirs('coco/annotations', exist_ok=True)
    os.makedirs('coco/images', exist_ok=True)
    
    annotation_file = 'coco/annotations/captions_train2017.json'
    
    # Check if annotations file already exists
    if os.path.exists(annotation_file):
        print(f"Annotations file already exists at {annotation_file}")
        return annotation_file
    
    print("Downloading COCO 2017 annotations...")
    annotations_url = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
    
    try:
        # Download annotations zip file
        response = requests.get(annotations_url, stream=True)
        response.raise_for_status()
        
        # Extract annotations
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall('coco')
        
        print("Annotations downloaded and extracted successfully.")
        
        # We'll also download a small subset of images for testing
        print("Downloading a small subset of COCO images for testing...")
        
        # Create a directory for images
        os.makedirs('coco/images', exist_ok=True)
        
        # Download some test images (we'll use a small subset)
        # First, let's parse the annotations to get image IDs
        with open(annotation_file, 'r') as f:
            data = json.load(f)
        
        # Get a small subset of image IDs (first 100)
        image_ids = set()
        for i, annotation in enumerate(data['annotations']):
            if i >= 100:  # Limit to 100 images for testing
                break
            image_ids.add(annotation['image_id'])
        
        # Download these images
        for img_id in image_ids:
            img_url = f"http://images.cocodataset.org/train2017/{img_id:012d}.jpg"
            img_path = f"coco/images/{img_id}.jpg"
            
            if not os.path.exists(img_path):
                try:
                    print(f"Downloading image {img_id}...")
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)
                    
                    # Add a small delay to avoid overwhelming the server
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error downloading image {img_id}: {e}")
        
        print(f"Downloaded {len(image_ids)} images for testing.")
        
        return annotation_file
        
    except Exception as e:
        print(f"Error downloading COCO dataset: {e}")
        
        # If download fails, create a minimal dataset for testing
        print("Creating minimal dataset for testing...")
        
        minimal_data = {
            "annotations": [
                {"image_id": 1, "caption": "a cat sitting on a table"},
                {"image_id": 2, "caption": "a dog running in a park"}
            ]
        }
        
        with open(annotation_file, 'w') as f:
            json.dump(minimal_data, f)
            
        print(f"Created minimal dataset at {annotation_file}")
        return annotation_file

def capture_image():
    """
    Capture an image from the webcam and save it.
    Returns the path to the saved image or None if image capture failed.
    """
    image_path = '' 
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera. Using default image path.")
            return image_path  # Return the path even if we couldn't capture
            
        print("Press 's' to capture or 'q' to quit...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Using default image path.")
                break
                
            cv2.imshow('Capture Image', frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                cv2.imwrite(image_path, frame)
                print(f"Image saved to {image_path}")
                break
            elif key == ord('q'):
                print("Capture canceled. Using default image path.")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return image_path
        
    except Exception as e:
        print(f"Error in capture_image: {e}")
        return image_path  # Return default path in case of any error

# Step 1: Pre-trained ResNet50 Model ko load karna
base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
image_model = Model(inputs=base_model.input, outputs=base_model.output)

def extract_features(image_path):
    """Extract features from image using ResNet50"""
    try:
        img = Image.open(image_path).convert('RGB').resize((224, 224))
        img = np.array(img) / 255.0
        # Handle images with different number of channels
        if img.shape[-1] != 3:
            img = np.stack([img, img, img], axis=-1)
        img = np.expand_dims(img, axis=0)
        features = image_model.predict(img, verbose=0)
        return features
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        # Return a zero vector as fallback
        return np.zeros((1, 2048))

# Step 2: MS COCO Dataset ko load karna
def load_coco_data(annotation_file):
    """Load captions and image paths from COCO dataset"""
    try:
        with open(annotation_file, 'r') as f:
            data = json.load(f)
        captions = []
        image_paths = []
        
        # Get unique image IDs to avoid duplicate images
        image_ids = set()
        for annotation in data['annotations'][:1000]:  # Limit to 1000 for testing
            image_id = annotation['image_id']
            image_path = f"coco/images/{image_id}.jpg"
            
            # Only add if the image file exists
            if os.path.exists(image_path):
                captions.append(annotation['caption'])
                image_paths.append(image_path)
                image_ids.add(image_id)
                
        print(f"Found {len(image_ids)} unique images with captions")
        return captions, image_paths
        
    except Exception as e:
        print(f"Error loading COCO data: {e}")
        # Return some dummy data for testing
        return ["a cat sitting on a table", "a dog running in a park"], ["dummy1.jpg", "dummy2.jpg"]

# Step 3: Text Captions ko process karna
def preprocess_captions(captions):
    """Process captions and create vocabulary"""
    # Add start and end tokens
    processed_captions = ['<start> ' + caption + ' <end>' for caption in captions]
    
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(processed_captions)
    sequences = tokenizer.texts_to_sequences(processed_captions)
    max_length = max(len(seq) for seq in sequences)
    vocab_size = len(tokenizer.word_index) + 1
    
    return tokenizer, sequences, max_length, vocab_size

# Step 4: Custom Attention Layer
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        
    def build(self, input_shape):
        self.W1 = self.add_weight(name='W1',
                                 shape=(input_shape[-1], 256),
                                 initializer='glorot_uniform',
                                 trainable=True)
        self.W2 = self.add_weight(name='W2',
                                 shape=(256, 1),
                                 initializer='glorot_uniform',
                                 trainable=True)
        super(AttentionLayer, self).build(input_shape)
        
    def call(self, inputs):
        # inputs shape: (batch_size, time_steps, features)
        # Apply tanh to get attention scores
        attention = tf.keras.backend.dot(inputs, self.W1)
        attention = tf.keras.backend.tanh(attention)
        
        # Get attention weights
        attention = tf.keras.backend.dot(attention, self.W2)
        attention = tf.keras.backend.softmax(attention, axis=1)
        
        # Apply attention weights to input
        context = inputs * attention
        
        return context
    
    def compute_output_shape(self, input_shape):
        return input_shape

# Step 5: Image Captioning Model ko banana with Attention
def build_model(vocab_size, max_length):
    """Build the image captioning model"""
    # Image input
    image_input = tf.keras.layers.Input(shape=(2048,))
    img_dense = Dense(256, activation='relu')(image_input)
    img_dense = RepeatVector(max_length)(img_dense)  # Shape: (batch_size, max_length, 256)
    
    # Text input
    text_input = tf.keras.layers.Input(shape=(max_length,))
    text_emb = Embedding(vocab_size, 256, mask_zero=False)(text_input)  # Disable masking to avoid issues
    
    # Merge inputs
    merged = Concatenate(axis=2)([img_dense, text_emb])  # Shape: (batch_size, max_length, 512)
    
    # Apply attention
    attention_out = AttentionLayer()(merged)
    
    # LSTM layer
    lstm_out = LSTM(256)(attention_out)
    
    # Output layer
    output = Dense(vocab_size, activation='softmax')(lstm_out)
    
    # Create and compile model
    model = Model(inputs=[image_input, text_input], outputs=output)
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    
    return model

# Step 6: Caption ko generate karna
def generate_caption(model, tokenizer, image_path, max_length):
    """Generate caption for an image"""
    features = extract_features(image_path)
    
    # Start with start token
    input_text = ['<start>']
    
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([' '.join(input_text)])[0]
        sequence = pad_sequences([sequence], maxlen=max_length)
        
        # Predict next word
        pred = model.predict([features, sequence], verbose=0)
        idx = np.argmax(pred)
        
        # Get the corresponding word
        word = tokenizer.index_word.get(idx, '')
        
        # Stop if we predict the end token or get an empty word
        if word == '<end>' or word == '':
            break
            
        # Add the word to the caption
        input_text.append(word)
    
    # Remove start token and join
    return ' '.join(input_text[1:])

# Example
if __name__ == "__main__":
    try:
        print("Setting up COCO dataset...")
        annotation_file = download_coco_dataset()
        
        # Load and preprocess data
        print("Loading COCO data...")
        captions, image_paths = load_coco_data(annotation_file)
        print(f"Loaded {len(captions)} captions")
        
        print("Preprocessing captions...")
        tokenizer, sequences, max_length, vocab_size = preprocess_captions(captions)
        print(f"Vocabulary size: {vocab_size}, Max sequence length: {max_length}")
        
        print("Building model...")
        model = build_model(vocab_size, max_length)
        print("Model built successfully!")
        
        # For testing purposes, you might want to use an existing image
        print("Do you want to capture an image? (y/n)")
        choice = input().lower()
        
        if choice == 'y':
            captured_image_path = capture_image()
        else:
            # Use a default image or the first image from the dataset
            captured_image_path = 'captured_image.jpg'
            if os.path.exists(captured_image_path):
                print(f"Using existing image: {captured_image_path}")
            elif len(image_paths) > 0:
                captured_image_path = image_paths[0]
                print(f"Using first image from dataset: {captured_image_path}")
            else:
                print("No default image available. Please run again and capture an image.")
                exit()
        
        print("Generating caption...")
        caption = generate_caption(model, tokenizer, captured_image_path, max_length)
        print(f"Generated Caption: {caption}")
        
    except Exception as e:
        import traceback
        print(f"Error in main: {e}")
        traceback.print_exc()