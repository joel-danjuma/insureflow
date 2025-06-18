"""
API client for interacting with the InsureFlow FastAPI backend.
"""
import os
import httpx
import streamlit as st

# Use the BACKEND_URL from environment variables in production,
# otherwise default to the local Docker Compose service name.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://app:8000/api/v1")

class InsureFlowApiClient:
    def __init__(self, base_url=BACKEND_URL):
        self.base_url = base_url
        self.client = httpx.Client()
        self.token = st.session_state.get("token")
        if self.token:
            self.client.headers["Authorization"] = f"Bearer {self.token}"

    def login(self, username, password):
        """
        Authenticates with the API and stores the token.
        """
        response = self.client.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password},
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["token"] = token_data.get("access_token")
            st.session_state["user"] = token_data  # Store the whole user object
            self.token = st.session_state["token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            return True
        return False

    def register(self, email, password, full_name, username, role):
        """
        Registers a new user and authenticates if successful.
        """
        response = self.client.post(
            f"{self.base_url}/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "username": username,
                "role": role,
            },
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["token"] = token_data.get("access_token")
            st.session_state["user"] = token_data # Store the whole user object
            self.token = st.session_state["token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            return True, "Registration successful!"
        else:
            error_detail = "An unknown error occurred."
            try:
                error_detail = response.json().get("detail", error_detail)
            except Exception:
                pass
            return False, error_detail

    def get_dashboard_data(self):
        """
        Retrieves aggregated data for the main dashboard.
        """
        if not self.token:
            return None
        response = self.client.get(f"{self.base_url}/dashboard/")
        if response.status_code == 200:
            return response.json()
        return None

    def get_policies(self):
        """
        Retrieves a list of policies.
        """
        if not self.token:
            return None
        response = self.client.get(f"{self.base_url}/policies/")
        if response.status_code == 200:
            return response.json()
        return None

    def get_premiums_for_policy(self, policy_id):
        """
        Retrieves a list of premiums for a specific policy.
        """
        if not self.token:
            return None
        response = self.client.get(f"{self.base_url}/premiums/by-policy/{policy_id}")
        if response.status_code == 200:
            return response.json()
        return None

    def get_broker_profile(self):
        """
        Retrieves the profile for the currently logged-in broker.
        """
        if not self.token:
            return None
        response = self.client.get(f"{self.base_url}/brokers/me")
        if response.status_code == 200:
            return response.json()
        return None

    def update_broker_profile(self, update_data: dict):
        """
        Updates the profile for the currently logged-in broker.
        """
        if not self.token:
            return False, "Not authenticated"
        
        response = self.client.put(f"{self.base_url}/brokers/me", json=update_data)
        
        if response.status_code == 200:
            return True, "Profile updated successfully."
        else:
            error_detail = "An unknown error occurred."
            try:
                error_detail = response.json().get("detail", error_detail)
            except Exception:
                pass
            return False, error_detail

    def initiate_bulk_payment(self, premium_ids: list[int]):
        """
        Initiates a bulk payment for a list of premium IDs.
        """
        if not self.token:
            return None, "Not authenticated"
        
        response = self.client.post(f"{self.base_url}/payments/bulk-initiate", json={"premium_ids": premium_ids})

        if response.status_code == 200:
            return response.json(), None
        else:
            error_detail = "An unknown error occurred."
            try:
                error_detail = response.json().get("detail", error_detail)
            except Exception:
                pass
            return None, error_detail 