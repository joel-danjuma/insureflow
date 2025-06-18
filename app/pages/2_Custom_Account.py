import streamlit as st
from app.api_client import InsureFlowApiClient

st.set_page_config(layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/styles.css")

st.title("My Account")

api_client = InsureFlowApiClient()

if "token" not in st.session_state:
    st.warning("Please log in to manage your account.")
    st.stop()

# Fetch broker profile
broker_profile = api_client.get_broker_profile()

if not broker_profile:
    st.error("Could not load your broker profile. Please contact support.")
    st.stop()

st.subheader("Update Your Profile")

with st.form(key="update_broker_form"):
    name = st.text_input("Full Name", value=broker_profile.get("name"))
    agency_name = st.text_input("Agency Name", value=broker_profile.get("agency_name"))
    contact_email = st.text_input("Contact Email", value=broker_profile.get("contact_email"))
    contact_phone = st.text_input("Contact Phone", value=broker_profile.get("contact_phone"))
    office_address = st.text_area("Office Address", value=broker_profile.get("office_address"))
    
    submit_button = st.form_submit_button(label="Update Profile")

    if submit_button:
        update_data = {
            "name": name,
            "agency_name": agency_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "office_address": office_address,
        }
        success, message = api_client.update_broker_profile(update_data)
        if success:
            st.success("Profile updated successfully!")
            st.rerun()
        else:
            st.error(f"Failed to update profile: {message}") 