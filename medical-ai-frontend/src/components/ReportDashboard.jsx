import React from 'react';
import { 
  Download, 
  RefreshCw, 
  User, 
  Clock, 
  FileText, 
  Activity,
  AlertTriangle,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const ReportDashboard = ({ data, onNewUpload }) => {
  const getTriageColor = (level) => {
    const colors = {
      1: 'bg-red-500 text-white',
      2: 'bg-orange-500 text-white', 
      3: 'bg-yellow-500 text-gray-800',
      4: 'bg-green-500 text-white',
      5: 'bg-blue-500 text-white'
    };
    return colors[level] || 'bg-gray-500 text-white';
  };

  const getTriageIcon = (level) => {
    if (level <= 2) return <AlertTriangle className="h-5 w-5" />;
    if (level === 3) return <AlertCircle className="h-5 w-5" />;
    return <CheckCircle className="h-5 w-5" />;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Medical Analysis Report</h1>
            <p className="text-gray-600 mt-1">
              Session: {data.session_id} • Generated: {new Date(data.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onNewUpload}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>New Upload</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
              <Download className="h-4 w-4" />
              <span>Download Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Triage Level</p>
              <p className="text-2xl font-bold text-gray-800">{data.triage.level}</p>
            </div>
            <div className={`p-3 rounded-full ${getTriageColor(data.triage.level)}`}>
              {getTriageIcon(data.triage.level)}
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">{data.triage.priority}</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Entities Found</p>
              <p className="text-2xl font-bold text-gray-800">{data.entities.total_count}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Activity className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Medical entities extracted</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Word Count</p>
              <p className="text-2xl font-bold text-gray-800">{data.transcript.word_count}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Transcribed words</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Confidence</p>
              <p className="text-2xl font-bold text-gray-800">
                {Math.round(data.transcript.confidence * 100)}%
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <CheckCircle className="h-5 w-5 text-purple-600" />
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Transcription accuracy</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Transcript */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Transcript</h2>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {data.transcript.text}
            </p>
          </div>
        </div>

        {/* Triage Assessment */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Triage Assessment</h2>
          <div className="space-y-4">
            <div className={`p-4 rounded-lg ${getTriageColor(data.triage.level)}`}>
              <div className="flex items-center space-x-2 mb-2">
                {getTriageIcon(data.triage.level)}
                <span className="font-bold">Level {data.triage.level}</span>
              </div>
              <p className="text-sm opacity-90">{data.triage.priority}</p>
            </div>
            
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-700">Recommendation</h4>
                <p className="text-sm text-gray-600 mt-1">{data.triage.recommendation}</p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700">Confidence</h4>
                <p className="text-sm text-gray-600 mt-1">{data.triage.confidence}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Medical Entities */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Extracted Medical Entities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Object.entries(data.entities.summary).map(([category, count]) => (
            <div key={category} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-800 mb-2">{category}</h3>
              <p className="text-2xl font-bold text-blue-600 mb-2">{count}</p>
              <div className="space-y-1">
                {data.entities.details[category]?.slice(0, 3).map((entity, index) => (
                  <div key={index} className="text-sm text-gray-600 flex items-center justify-between">
                    <span className="truncate">{entity.text}</span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded ml-2">
                      {Math.round(entity.confidence * 100)}%
                    </span>
                  </div>
                ))}
                {data.entities.details[category]?.length > 3 && (
                  <p className="text-xs text-gray-500">
                    +{data.entities.details[category].length - 3} more
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Clinical Summary */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Clinical Summary</h2>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-gray-700 leading-relaxed">
            {data.clinical_summary.text_summary}
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Key Symptoms</h4>
            <div className="space-y-1">
              {data.clinical_summary.key_symptoms?.slice(0, 5).map((symptom, index) => (
                <span key={index} className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                  {symptom}
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Current Medications</h4>
            <div className="space-y-1">
              {data.clinical_summary.current_medications?.slice(0, 5).map((medication, index) => (
                <span key={index} className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                  {medication}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportDashboard;
