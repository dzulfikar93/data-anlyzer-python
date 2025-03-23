import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Replace these with your Supabase credentials
SUPABASE_URL = "https://zrdnqtdqfjueogbznbne.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit login UI
# def login():
#     st.title("Supabase Authentication Example")
    
#     # Provide login form
#     with st.form(key="login_form"):
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         submit_button = st.form_submit_button("Login")

#     if submit_button:
#         # Try to log the user in
#         try:
#             user = supabase.auth.sign_in_with_password(email=email, password=password)
#             st.success(f"Welcome {user['user']['email']}!")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# # Streamlit registration UI
# def register():
#     st.title("Supabase Authentication Example")
    
#     # Provide registration form
#     with st.form(key="register_form"):
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         submit_button = st.form_submit_button("Register")
    
#     if submit_button:
#         # Register the user
#         try:
#             user = supabase.auth.sign_up(email=email, password=password)
#             st.success(f"Account created for {user['user']['email']}!")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# # Streamlit logout UI
# def logout():
#     if st.button("Logout"):
#         supabase.auth.sign_out()
#         st.success("You have logged out successfully!")



# Main page UI logic
def main():
    st.title("Supabase Authentication Example")

    # Check if user is authenticated
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        st.write(f"Welcome, {st.session_state.user.email}!")
        if st.button("Sign out"):
            sign_out()
    else:
        # Authentication forms
        auth_form()

def auth_form():
    auth_type = st.radio("Choose authentication type", ["Sign up", "Sign in"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if auth_type == "Sign up":
            sign_up(email, password)
        else:
            sign_in(email, password)

def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        if user.user:
            st.session_state.user = user.user
            st.success("Sign up successful!")
        else:
            st.error("Sign up failed.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user.user:
            st.session_state.user = user.user
            st.success("Sign in successful!")
        else:
            st.error("Sign in failed.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.success("Signed out successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

"st.session_state object :", st.session_state

if __name__ == "__main__":
    main()
