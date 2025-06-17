"""
InsureFlow Payment Monitoring Dashboard
"""
import streamlit as st
import pandas as pd
from app.api_client import InsureFlowApiClient

# Function to load and inject CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Sovereign Trust Insurance",
    layout="wide"
)

local_css("app/styles.css")

st.title("Sovereign Trust Insurance")

# --- Mock Data ---
recent_policies_data = {
    'Policy Number': ['PL-123450', 'PL-234357', 'PL-349378'],
    'Customer Name': ['Alice Johnson', 'Bok Williams', 'Chinedu Okafor'],
    'Broker': ['IBN', 'SCIB', 'Ark Insurance']
}
recent_policies_df = pd.DataFrame(recent_policies_data)

recent_solicies_data = {
    'Pocter': ['SCIB', 'IBN', 'Ark Insurance'],
    'Broker': ['IBN', 'IBN', '37']
}
recent_solicies_df = pd.DataFrame(recent_solicies_data)

outstanding_premiums_data = {
    'Policy Number': ['PL-607980', 'PL-678901', 'PL-050625'],
    'Due': ['10/05/2025', '20/05/2025', '05/06/2025'],
    'Amount': ['N3,500,00', 'N4,500,00', 'N2,330,00']
}
outstanding_premiums_df = pd.DataFrame(outstanding_premiums_data)


# --- Layout ---

# Top KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="New Policies This Month", value="120")
with col2:
    st.metric(label="Outstanding Premiums", value="N 10,250,000")
with col3:
    st.metric(label="Brokers", value="15")

st.divider()

# Main content area
col4, col5 = st.columns([0.7, 0.3])

with col4:
    st.subheader("Recent Policies")
    st.dataframe(recent_policies_df, use_container_width=True)
    st.button("Generate Report", key="report_recent")
    st.button("View All", key="view_all_recent")

with col5:
    st.subheader("Automated Reconciliation Engine")
    st.info("Automated Reconciliation Engine details go here.")
    st.button("Generate Report", key="report_recon")
    st.button("View All", key="view_all_recon")


st.divider()

# Bottom tables
col6, col7 = st.columns(2)

with col6:
    st.subheader("Recent Solicies")
    st.dataframe(recent_solicies_df, use_container_width=True)

with col7:
    st.subheader("Outstanding Premiums")
    st.dataframe(outstanding_premiums_df, use_container_width=True)

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
        signup_role = st.selectbox("Role", ["customer", "broker", "admin"], key="signup_role")

        if st.button("Sign Up"):
            success, message = api_client.register(
                email=signup_email,
                password=signup_password,
                full_name=signup_fullname,
                username=signup_username,
                role=signup_role,
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

st.write("Main dashboard content will be built here.")

# We will add the KPI cards and tables in the next step.