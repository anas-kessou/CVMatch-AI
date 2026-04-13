import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const serverMessage = error.response?.data?.detail;
    const fallbackMessage = error.message || 'Erreur réseau inconnue';

    return Promise.reject(new Error(serverMessage ?? fallbackMessage));
  },
);
