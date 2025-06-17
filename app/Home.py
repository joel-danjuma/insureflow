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
api_client = InsureFlowApiClient()

def main_dashboard():
    st.title("Sovereign Trust Insurance")

    dashboard_data = api_client.get_dashboard_data()

    if dashboard_data:
        kpis = dashboard_data.get('kpis', {})
        recent_policies = dashboard_data.get('recent_policies', [])

        # Top KPI Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="New Policies This Month", value=kpis.get('new_policies_this_month', 0))
        with col2:
            st.metric(label="Outstanding Premiums", value=f"N {kpis.get('outstanding_premiums_total', 0):,}")
        with col3:
            st.metric(label="Brokers", value=kpis.get('broker_count', 0))

        st.divider()

        # Main content area
        col4, col5 = st.columns([0.7, 0.3])

        with col4:
            st.subheader("Recent Policies")
            if recent_policies:
                st.dataframe(pd.DataFrame(recent_policies), use_container_width=True)
            else:
                st.write("No recent policies found.")
            st.button("Generate Report", key="report_recent")
            st.button("View All", key="view_all_recent")

        with col5:
            st.subheader("Automated Reconciliation Engine")
            st.info("Automated Reconciliation Engine details go here.")
            st.button("Generate Report", key="report_recon")
            st.button("View All", key="view_all_recon")
    else:
        st.warning("Could not load dashboard data.")


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
    main_dashboard()
