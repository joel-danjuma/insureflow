"""
InsureFlow Payment Monitoring Dashboard
"""
import streamlit as st
import pandas as pd
from app.api_client import InsureFlowApiClient

st.set_page_config(page_title="InsureFlow Payments", layout="wide")

# Add an informational message about ports
st.info(
    "ℹ️ **How Ports Work on Render:** This dashboard runs on port `8501` inside its container. "
    "However, Render exposes it to the web on a standard HTTPS port (443), so you don't need to add a port number to the URL."
)

st.title("InsureFlow Payment Monitoring Dashboard")

api_client = InsureFlowApiClient()

if "token" not in st.session_state:
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        st.header("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if api_client.login(login_email, login_password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with signup_tab:
        st.header("Create a New Account")
        signup_email = st.text_input("Email", key="signup_email")
        signup_username = st.text_input("Username", key="signup_username")
        signup_fullname = st.text_input("Full Name", key="signup_fullname")
        signup_password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            success, message = api_client.register(
                email=signup_email,
                password=signup_password,
                full_name=signup_fullname,
                username=signup_username,
            )
            if success:
                st.success("Registration successful! You are now logged in.")
                st.rerun()
            else:
                st.error(f"Registration failed: {message}")
else:
    st.sidebar.success("You are logged in.")
    if st.sidebar.button("Logout"):
        del st.session_state["token"]
        st.rerun()
        
    st.header("Policies and Premiums")
    
    policies = api_client.get_policies()
    
    if policies:
        policy_df = pd.DataFrame(policies)
        st.dataframe(policy_df)
        
        selected_policy_id = st.selectbox("Select a policy to view premiums", options=policy_df['id'])
        
        if selected_policy_id:
            premiums = api_client.get_premiums_for_policy(selected_policy_id)
            if premiums:
                premium_df = pd.DataFrame(premiums)
                st.dataframe(premium_df)
            else:
                st.write("No premiums found for this policy.")
    else:
        st.write("No policies found.")