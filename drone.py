import streamlit as st
import pandas as pd
import os
import re
import traceback
import numpy as np
from datetime import datetime

# Constants
USER_FILE = "User_List.xlsx"
UPLOAD_FOLDER = "uploads"

# Ensure the Excel file exists
def init_user_file():
    try:
        if os.path.exists(USER_FILE):
            try:
                # Try to read the file to check if it's valid
                pd.read_excel(USER_FILE, engine="openpyxl")
            except Exception:
                # If reading fails, delete the file
                st.warning(f"Found corrupted user file. Recreating database.")
                os.remove(USER_FILE)
        
        # Create a new file if it doesn't exist
        if not os.path.exists(USER_FILE):
            df = pd.DataFrame(columns=["Username", "Password", "Email", "Files_Queried"])
            df.to_excel(USER_FILE, index=False, engine="openpyxl")
            st.success(f"Created new user database: {USER_FILE}")
        return True
    except Exception as e:
        error_msg = f"Error initializing user file: {str(e)}\n{traceback.format_exc()}"
        st.error(error_msg)
        return False

# Validate email format
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

# Validate username format
def is_valid_username(username):
    return re.match(r"^[a-zA-Z0-9_]+$", username)

# Register new user
def register_user(username, password, email):
    try:
        if not username or not password or not email:
            return False, "All fields are required!"
        
        # Initialize user file if needed
        init_user_file()
            
        try:
            df = pd.read_excel(USER_FILE, engine="openpyxl")
        except Exception:
            # If reading fails, recreate the file
            df = pd.DataFrame(columns=["Username", "Password", "Email", "Files_Queried"])
        
        if username in df["Username"].values:
            return False, "Username already exists!"
        if not is_valid_email(email):
            return False, "Invalid email format!"
        if not is_valid_username(username):
            return False, "Username can only contain letters, numbers, and underscores!"
        
        new_user = pd.DataFrame({
            "Username": [username], 
            "Password": [password], 
            "Email": [email],
            "Files_Queried": [""]  # Initialize with empty string
        })
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(USER_FILE, index=False, engine="openpyxl")
        return True, "Registration successful! Please login."
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        return False, error_msg

# Update user's file list
def update_user_file_list(username, filename):
    try:
        df = pd.read_excel(USER_FILE, engine="openpyxl")
        user_idx = df[df["Username"] == username].index[0]
        
        # Get current file list and handle NaN values
        current_files = df.at[user_idx, "Files_Queried"]
        
        # Check if value is NaN or empty
        if pd.isna(current_files) or (isinstance(current_files, float) and np.isnan(current_files)):
            current_files = ""
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_entry = f"{filename} ({timestamp})"
        
        # Update file list
        if current_files and str(current_files).strip():
            df.at[user_idx, "Files_Queried"] = f"{current_files}; {file_entry}"
        else:
            df.at[user_idx, "Files_Queried"] = file_entry
        
        # Save changes
        df.to_excel(USER_FILE, index=False, engine="openpyxl")
        return True
    except Exception as e:
        st.error(f"Error updating file list: {str(e)}")
        return False

# Verify login credentials
def authenticate_user(username, password):
    try:
        init_user_file()  # Ensure file exists
        
        df = pd.read_excel(USER_FILE, engine="openpyxl")
        user = df[(df["Username"] == username) & (df["Password"] == password)]
        return not user.empty
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

# Drone detection function placeholder - to be integrated with YOLOv8 later
def detect_drones(image_path):
    """
    Placeholder function for drone detection using YOLOv8.
    This function will be implemented later to integrate with YOLOv8 model.
    
    Args:
        image_path (str): Path to the image/video file
        
    Returns:
        dict: Detection results with bounding boxes, confidence scores, etc.
    """
    # Placeholder for future implementation
    # YOLOv8 integration will go here
    
    results = {
        "status": "success",
        "message": "Detection placeholder - YOLOv8 not yet integrated",
        "detections": [],
        "processing_time": 0
    }
    
    return results

# Initialize app and file system
def init_app():
    # Create upload directory if it doesn't exist
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        init_user_file()
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")

# Initialize app
init_app()

# Streamlit page navigation
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if not username or not password:
                st.error("Username and password are required")
            elif authenticate_user(username, password):
                st.session_state.username = username
                st.session_state.page = "main"
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with col2:
        if st.button("New User?"):
            st.session_state.page = "register"
            st.rerun()

elif st.session_state.page == "register":
    st.title("User Registration")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    new_email = st.text_input("Enter Your Email")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            success, message = register_user(new_username, new_password, new_email)
            if success:
                st.success(message)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        if st.button("Back to Login"):
            st.session_state.page = "login"
            st.rerun()

elif st.session_state.page == "main":
    st.title("Drone Detection System")
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Create user folder for uploads
    user_folder = os.path.join(UPLOAD_FOLDER, st.session_state.username)
    try:
        os.makedirs(user_folder, exist_ok=True)
        
        uploaded_file = st.file_uploader("Upload Image/Video", type=["jpg", "png", "mp4", "avi"])
        
        if uploaded_file:
            try:
                file_path = os.path.join(user_folder, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Update user's file list in Excel
                if update_user_file_list(st.session_state.username, uploaded_file.name):
                    st.success(f"File '{uploaded_file.name}' uploaded and tracked successfully!")
                
                if uploaded_file.type.startswith("image"):
                    st.image(file_path, caption="Uploaded Image", use_container_width=True)
                else:
                    st.video(file_path)
                
                if st.button("Detect"):
                    with st.spinner("Analyzing for drones..."):
                        # Call the detect_drones function (placeholder for now)
                        results = detect_drones(file_path)
                        
                        # Display placeholder results
                        st.info("YOLOv8 detection will be integrated here in the future.")
                        st.json(results)
                        
                        # This section will eventually display detection results
                        st.subheader("Detection Results")
                        st.write("This is where detected drones and their details will be displayed.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Show user's uploaded files history
        try:
            df = pd.read_excel(USER_FILE, engine="openpyxl")
            if st.session_state.username in df["Username"].values:
                user_files = df.loc[df["Username"] == st.session_state.username, "Files_Queried"].values[0]
                
                # Handle NaN values
                if pd.isna(user_files) or (isinstance(user_files, float) and np.isnan(user_files)):
                    user_files = ""
                
                if user_files and str(user_files).strip():
                    st.subheader("Your Upload History")
                    files_list = str(user_files).split(";")
                    for file in files_list:
                        if file.strip():
                            st.write(f"- {file.strip()}")
                else:
                    st.info("You haven't uploaded any files yet.")
        except Exception as e:
            st.warning(f"Could not retrieve upload history: {str(e)}")
        
        # Logout button
        if st.button("Logout"):
            st.session_state.page = "login"
            st.rerun()
    except Exception as e:
        st.error(f"Error accessing user folder: {str(e)}")