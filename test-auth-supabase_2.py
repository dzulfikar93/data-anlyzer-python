import streamlit as st
from supabase import create_client, Client
import hashlib
import time
from datetime import datetime, timedelta
import json
import os

# Supabase client initialization
url = "https://zrdnqtdqfjueogbznbne.supabase.co"  # Replace with your Supabase URL
key = os.getenv("SUPABASE_KEY") # Replace with your Supabase API key
supabase: Client = create_client(url, key)

# Function to hash the password securely
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Function to create login form
def create_login_form():
    st.title("Login to ITENASIS 🤖 ")
    email = st.text_input("Email", "")
    password = st.text_input("Password", "", type="password")
    
    if st.button("Login"):
        if email and password:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user:
                st.session_state['user'] = user
                st.session_state['logged_in'] = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        else:
            st.warning("Please enter both email and password")

# Function to show main content after successful login
def show_main_content():
    st.title("Main App Content")
    st.write("Welcome to the main application!")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# Streamlit app main logic
def main():
    # Check for existing session or cookies
    # user_session = st.experimental_get_cookie('user_session')
    
    # if user_session:
    #     st.session_state['user'] = json.loads(user_session)
    #     st.session_state['logged_in'] = True

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        create_login_form()
    else:
        show_main_content()

if __name__ == "__main__":
    main()
