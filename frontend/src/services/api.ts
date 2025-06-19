import axios from 'axios';
import { LoginFormData } from '@/components/LoginForm';
import { SignUpFormData } from '@/components/SignUpForm';

// This will be the base URL for our backend
// In development, Next.js can proxy requests to avoid CORS issues.
// In production, this would be the actual domain of your backend.
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  // withCredentials will be important for handling cookies if we use them for auth
  withCredentials: true,
});

export const authService = {
  login: async (credentials: LoginFormData) => {
    // FastAPI's OAuth2PasswordRequestForm expects form data, not JSON.
    const form = new URLSearchParams();
    form.append('username', credentials.email);
    form.append('password', credentials.password);

    try {
      const response = await apiClient.post('/auth/token', form, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Login failed');
      }
      throw new Error('An unexpected error occurred during login.');
    }
  },

  register: async (data: SignUpFormData) => {
    try {
      const response = await apiClient.post('/users/', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Registration failed');
      }
      throw new Error('An unexpected error occurred during registration.');
    }
  },

  getCurrentUser: async (token: string) => {
    // Placeholder for fetching user data with a token
    // This will be implemented fully once we have token management
    try {
        const response = await apiClient.get('/users/me', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'Failed to fetch user');
        }
        throw new Error('An unexpected error occurred while fetching user data.');
    }
  },
};

export const paymentService = {
  initiateBulkPayment: async (policyIds: number[]) => {
    try {
      const response = await apiClient.post('/payments/bulk-initiate', { policy_ids: policyIds });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Bulk payment initiation failed');
      }
      throw new Error('An unexpected error occurred during bulk payment initiation.');
    }
  },
};

export default apiClient; 