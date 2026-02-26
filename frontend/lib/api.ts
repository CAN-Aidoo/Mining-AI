/**
 * Mining AI Platform - API Client
 *
 * Axios instance pre-configured with base URL and auth interceptors.
 * Import { apiClient } everywhere you need to call the backend.
 */

import axios, { AxiosError, type AxiosInstance } from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
});

// Attach JWT access token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Handle 401 responses (token refresh implemented in Week 2)
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // TODO Week 2: implement token refresh flow
      console.warn("Unauthorized - token refresh not yet implemented");
    }
    return Promise.reject(error);
  }
);
