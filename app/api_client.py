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
            self.token = response.json()["access_token"]
            st.session_state["token"] = self.token
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            return True
        return False

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