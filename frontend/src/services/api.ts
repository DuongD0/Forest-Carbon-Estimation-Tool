import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// Define the base URL for API calls
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token to headers
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle specific status codes if needed
    if (error.response?.status === 401) {
      // e.g., redirect to login
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service for authentication
export const authService = {
  login: async (credentials: any) => {
    const response = await apiClient.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('accessToken', response.data.access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('accessToken');
  },
  getCurrentUser: async () => {
    // This assumes you have a /users/me endpoint
    const response = await apiClient.get('/users/me');
    return response.data;
  }
};

// API service for projects
export const projectService = {
  getProjects: async () => {
    const response = await apiClient.get('/projects/');
    return response.data;
  },
  getProjectById: async (id: number) => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },
  createProject: async (projectData: any) => {
    const response = await apiClient.post('/projects/', projectData);
    return response.data;
  },
  updateProject: async (id: number, projectData: any) => {
    const response = await apiClient.put(`/projects/${id}`, projectData);
    return response.data;
  },
  deleteProject: async (id: number) => {
    const response = await apiClient.delete(`/projects/${id}`);
    return response.data;
  },
  calculateCarbon: async (id: number) => {
    const response = await apiClient.post(`/projects/${id}/calculate`);
    return response.data;
  }
};

// API service for forests
export const forestService = {
    getForestsByProject: async (projectId: number) => {
        const response = await apiClient.get(`/forests/?project_id=${projectId}`);
        return response.data;
    },
    getForestById: async (id: number) => {
        const response = await apiClient.get(`/forests/${id}`);
        return response.data;
    }
    // Add other forest-related calls here (create, update, delete)
};

// API service for imagery
export const imageryService = {
    getImageryByProject: async (projectId: number) => {
        const response = await apiClient.get(`/imagery/?project_id=${projectId}`);
        return response.data;
    },
    getImageryById: async (id: number) => {
        const response = await apiClient.get(`/imagery/${id}`);
        return response.data;
    },
    uploadImagery: async (formData: FormData) => {
        const response = await apiClient.post('/imagery/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },
    processImagery: async (id: number) => {
        const response = await apiClient.post(`/imagery/${id}/process`);
        return response.data;
    },
    deleteImagery: async (id: number) => {
        const response = await apiClient.delete(`/imagery/${id}`);
        return response.data;
    }
};

export default apiClient;
