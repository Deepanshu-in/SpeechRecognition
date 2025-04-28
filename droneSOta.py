import streamlit as st
import pandas as pd
import os

# Load user data
def load_user_data():
    try:
        return pd.read_excel("User_List.xlsx")
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password", "email"])

# Save user data
def save_user_data(df):
    df.to_excel("User_List.xlsx", index=False)

# Validate user credentials
def validate_user(username, password, user_data):
    user = user_data[(user_data['username'] == username) & (user_data['password'] == password)]
    return not user.empty

# Register a new user
def register_user(username, password, email, user_data):
    if username in user_data['username'].values:
        return False
    new_user = pd.DataFrame([[username, password, email]], columns=["username", "password", "email"])
    user_data = pd.concat([user_data, new_user], ignore_index=True)
    save_user_data(user_data)
    return True

# Main function
def main():
    st.title("Drone Detection App")

    # Load user data
    user_data = load_user_data()

    # Sidebar for navigation
    page = st.sidebar.selectbox("Select Page", ["Login", "Register", "Main"])

    if page == "Login":
        st.header("Login Page")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if validate_user(username, password, user_data):
                st.success("Login successful!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.error("Invalid username or password")
        if st.button("New User?"):
            st.session_state['page'] = "Register"

    elif page == "Register":
        st.header("Registration Page")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_email = st.text_input("Email")
        if st.button("Register"):
            if register_user(new_username, new_password, new_email, user_data):
                st.success("Registration successful! Please login.")
                st.session_state['page'] = "Login"
            else:
                st.error("Username already exists. Please choose another.")

    elif page == "Main":
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.header("Main Page - Drone Detection")
            uploaded_file = st.file_uploader("Upload an image or video", type=["jpg", "jpeg", "png", "mp4"])
            if uploaded_file is not None:
                user_folder = os.path.join("uploads", st.session_state['username'])
                os.makedirs(user_folder, exist_ok=True)
                file_path = os.path.join(user_folder, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.image(file_path, caption="Uploaded File", use_column_width=True)
                st.button("Detect", on_click=lambda: st.write("Detection handler to be implemented"))
        else:
            st.error("Please login to access this page.")

if __name__ == "__main__":
    main()