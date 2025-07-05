import React from 'react';
import { Stethoscope, Brain, FileAudio } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-lg border-b-4 border-medical-primary">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Stethoscope className="h-8 w-8 text-medical-primary" />
              <Brain className="h-6 w-6 text-purple-600" />
              <FileAudio className="h-6 w-6 text-medical-success" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Medical AI Transcription & Triage
              </h1>
              <p className="text-sm text-gray-600">
                Powered by Vite • AI Transcription • NER • Intelligent Triage
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-500">Status</div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-medical-success rounded-full"></div>
                <span className="text-sm font-medium text-medical-success">Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
