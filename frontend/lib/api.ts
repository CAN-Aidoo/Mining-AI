/**
 * Mining AI Platform - Typed API Client
 *
 * Axios instance with JWT attach + 401 refresh interceptor.
 * All API calls go through this client.
 */

import axios, { AxiosError, type AxiosInstance } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
});

// Attach access token
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    try {
      const raw = localStorage.getItem("mining-auth");
      if (raw) {
        const state = JSON.parse(raw);
        const token = state?.state?.accessToken;
        if (token) config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {}
  }
  return config;
});

// 401 → attempt token refresh once
apiClient.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as any;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        if (typeof window !== "undefined") {
          const raw = localStorage.getItem("mining-auth");
          if (raw) {
            const state = JSON.parse(raw);
            const refreshToken = state?.state?.refreshToken;
            if (refreshToken) {
              const res = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const { access_token, refresh_token } = res.data;
              // Update persisted store
              const updated = {
                ...state,
                state: {
                  ...state.state,
                  accessToken: access_token,
                  refreshToken: refresh_token,
                  isAuthenticated: true,
                },
              };
              localStorage.setItem("mining-auth", JSON.stringify(updated));
              original.headers.Authorization = `Bearer ${access_token}`;
              return apiClient(original);
            }
          }
        }
      } catch {
        // Refresh failed — clear auth and redirect
        if (typeof window !== "undefined") {
          localStorage.removeItem("mining-auth");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Typed helpers
// ---------------------------------------------------------------------------

export const auth = {
  register: (data: { email: string; password: string; full_name: string }) =>
    apiClient.post("/auth/register", data),
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return apiClient.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => apiClient.get("/auth/me"),
  logout: () => apiClient.post("/auth/logout"),
};

export const projects = {
  list: () => apiClient.get("/projects/"),
  create: (data: { title: string; description?: string; field: string }) =>
    apiClient.post("/projects/", data),
  get: (id: string) => apiClient.get(`/projects/${id}`),
  update: (id: string, data: object) => apiClient.patch(`/projects/${id}`, data),
  remove: (id: string) => apiClient.delete(`/projects/${id}`),
};

export const research = {
  list: (skip = 0, limit = 20) =>
    apiClient.get("/research/papers", { params: { skip, limit } }),
  search: (query: string, limit = 10) =>
    apiClient.post("/research/papers/search", { query, limit }),
  ingest: (payload: { doi?: string; arxiv_id?: string; query?: string; limit?: number }) =>
    apiClient.post("/research/papers/ingest", payload),
  remove: (id: string) => apiClient.delete(`/research/papers/${id}`),
};

export const documents = {
  list: (projectId?: string) =>
    apiClient.get("/documents/", { params: projectId ? { project_id: projectId } : {} }),
  create: (data: { title: string; project_id: string; citation_style?: string }) =>
    apiClient.post("/documents/", data),
  get: (id: string) => apiClient.get(`/documents/${id}`),
  update: (id: string, data: object) => apiClient.patch(`/documents/${id}`, data),
  remove: (id: string) => apiClient.delete(`/documents/${id}`),
  generateAll: (id: string) => apiClient.post(`/documents/${id}/generate`),
  generateSection: (id: string, section: string, extraContext?: string) =>
    apiClient.post(`/documents/${id}/generate/${section}`, { section_name: section, extra_context: extraContext }),
  exportUrl: (id: string) => `${API_BASE_URL}/api/v1/documents/${id}/export`,
};

export const prototypes = {
  list: () => apiClient.get("/prototypes/"),
  create: (data: {
    title: string;
    prototype_type: string;
    description: string;
    input_description: string;
    project_id: string;
  }) => apiClient.post("/prototypes/", data),
  get: (id: string) => apiClient.get(`/prototypes/${id}`),
  update: (id: string, data: object) => apiClient.patch(`/prototypes/${id}`, data),
  remove: (id: string) => apiClient.delete(`/prototypes/${id}`),
  build: (id: string) => apiClient.post(`/prototypes/${id}/build`),
  status: (id: string) => apiClient.get(`/prototypes/${id}/status`),
  downloadUrl: (id: string) => `${API_BASE_URL}/api/v1/prototypes/${id}/download`,
};
