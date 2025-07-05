import React, { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ReportDashboard from './components/ReportDashboard';

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [reportData, setReportData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleUploadSuccess = (data) => {
    setReportData(data);
    setCurrentView('report');
    setIsProcessing(false);
  };

  const handleProcessingStart = () => {
    setIsProcessing(true);
  };

  const handleNewUpload = () => {
    setCurrentView('upload');
    setReportData(null);
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {currentView === 'upload' && (
          <FileUpload 
            onUploadSuccess={handleUploadSuccess}
            onProcessingStart={handleProcessingStart}
            isProcessing={isProcessing}
          />
        )}
        
        {currentView === 'report' && reportData && (
          <ReportDashboard 
            data={reportData}
            onNewUpload={handleNewUpload}
          />
        )}
      </main>
    </div>
  );
}

export default App;
