import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5 minutes for large file processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Medical API functions
export const medicalAPI = {
  // Upload and process audio file
  uploadAudio: async (file, patientId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (patientId) {
      formData.append('patientId', patientId);
    }

    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        // You can emit progress events here
        console.log(`Upload progress: ${progress}%`);
      },
    });
  },

  // Get report by session ID
  getReport: async (sessionId) => {
    return api.get(`/reports/${sessionId}`);
  },

  // Health check
  healthCheck: async () => {
    return api.get('/health');
  },
};

export default api;
