import { useState, useCallback } from 'react';
import { medicalAPI } from '../services/medicalAPI';

export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadFile = useCallback(async (file, patientId) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const response = await medicalAPI.uploadAudio(file, patientId);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Upload failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, []);

  return {
    uploadFile,
    isUploading,
    uploadProgress,
    error,
    setError
  };
};
export default useFileUpload;