import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileAudio, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import { useFileUpload } from '../hooks/useFileUpload';

const FileUpload = ({ onUploadSuccess, onProcessingStart }) => {
  const [patientId, setPatientId] = useState('');
  const { uploadFile, isUploading, error, setError } = useFileUpload();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    onProcessingStart();

    try {
      const result = await uploadFile(file, patientId);
      onUploadSuccess(result);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  }, [uploadFile, patientId, onProcessingStart, onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
    onDropRejected: (fileRejections) => {
      const rejection = fileRejections[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError('File size must be less than 100MB');
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError('Please upload an audio file (WAV, MP3, M4A, FLAC, OGG)');
      } else {
        setError('File upload failed. Please try again.');
      }
    }
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="medical-card p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            Upload Medical Audio Recording
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload your audio file for AI-powered medical transcription, 
            entity extraction, and intelligent triage assessment.
          </p>
        </div>

        {/* Patient ID Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Patient ID (Optional)
          </label>
          <input
            type="text"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            className="medical-input"
            placeholder="Enter patient identifier"
            disabled={isUploading}
          />
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
            transition-all duration-300 ease-in-out
            ${isDragActive
              ? 'border-medical-primary bg-blue-50 scale-105'
              : 'border-gray-300 hover:border-medical-primary hover:bg-gray-50'
            }
            ${isUploading ? 'pointer-events-none opacity-75' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            {isUploading ? (
              <div className="flex flex-col items-center space-y-4">
                <Loader2 className="h-16 w-16 text-medical-primary animate-spin" />
                <p className="text-lg font-medium text-gray-700">
                  Processing with AI Pipeline...
                </p>
              </div>
            ) : (
              <>
                <FileAudio className="h-16 w-16 text-gray-400 mx-auto" />
                <div>
                  <p className="text-xl font-medium text-gray-700">
                    {isDragActive
                      ? 'Drop your audio file here'
                      : 'Drag & drop your audio file here'
                    }
                  </p>
                  <p className="text-gray-500 mt-2">
                    or click to browse files
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-medium text-red-800">Upload Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Features Grid */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <FileAudio className="h-6 w-6 text-medical-primary" />
            </div>
            <h3 className="font-medium text-gray-800">AI Transcription</h3>
            <p className="text-sm text-gray-600 mt-1">
              Powered by Whisper AI for accurate medical transcription
            </p>
          </div>
          
          <div className="text-center p-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle className="h-6 w-6 text-medical-success" />
            </div>
            <h3 className="font-medium text-gray-800">Medical NER</h3>
            <p className="text-sm text-gray-600 mt-1">
              Extract symptoms, medications, and diagnoses automatically
            </p>
          </div>
          
          <div className="text-center p-4">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <AlertCircle className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-medium text-gray-800">Smart Triage</h3>
            <p className="text-sm text-gray-600 mt-1">
              ESI-based priority assessment for optimal care decisions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
