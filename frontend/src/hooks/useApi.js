import { useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || error.response.statusText;
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export const useApi = () => {
  const uploadFile = useCallback(async (file, voiceSettings) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', voiceSettings.language);
    formData.append('voice', voiceSettings.voice);
    formData.append('speed', voiceSettings.speed.toString());

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for upload
    });

    return response.data;
  }, []);

  const getTaskStatus = useCallback(async (taskId) => {
    const response = await api.get(`/status/${taskId}`);
    return response.data;
  }, []);

  const getVoices = useCallback(async () => {
    const response = await api.get('/voices');
    return response.data;
  }, []);

  const getAudioUrl = useCallback((taskId, download = false) => {
    const params = download ? '?download=true' : '';
    return `${API_BASE_URL}/audio/${taskId}${params}`;
  }, []);

  const checkHealth = useCallback(async () => {
    const response = await api.get('/health');
    return response.data;
  }, []);

  return {
    uploadFile,
    getTaskStatus,
    getVoices,
    getAudioUrl,
    checkHealth,
  };
};

export default useApi;