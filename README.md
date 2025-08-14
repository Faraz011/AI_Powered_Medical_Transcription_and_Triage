AI-Powered Medical Transcription and Triage System
🏥 Overview
A comprehensive AI-powered healthcare solution that automatically transcribes medical audio recordings, extracts medical entities using Named Entity Recognition (NER), and performs Emergency Severity Index (ESI) based triage assessment. The system provides real-time medical insights to assist healthcare professionals in making informed decisions.

✨ Key Features
🎵 Audio Transcription: Advanced speech-to-text using OpenAI Whisper
🏥 Medical NER: Hybrid approach combining BioBERT and rule-based entity extraction
🚑 ESI Triage Assessment: Official Emergency Severity Index v4.0 guidelines implementation
📊 Real-time Dashboard: React-based interactive dashboard with visual reports
📁 Multi-format Reports: JSON, CSV, and HTML report generation
🔄 Batch Processing: Support for processing multiple audio files
⚡ Real-time Processing: Live audio analysis with immediate results

🛠️ Tech Stack

Backend:

Python 3.8+
Flask 3.0+ - Web framework
OpenAI Whisper - Audio transcription
Transformers (Hugging Face) - BioBERT for medical NER
MedSpaCy - Medical rule-based NER
PyTorch - Deep learning framework
Pandas - Data processing
NumPy - Numerical computations

Frontend:

React 18+ - User interface framework
JavaScript/TypeScript - Programming language
Tailwind CSS - Styling framework
Axios - HTTP client for API requests

AI/ML Models:

OpenAI Whisper (base model) - Speech recognition
dmis-lab/biobert-v1.1 - Medical entity recognition
MedSpaCy - Medical named entity recognition
Custom ESI Triage Rules - Emergency Severity Index implementation
Storage & Files
JSON - Primary data format
CSV - Tabular data export
HTML - Rich report generation
Audio formats: WAV, MP3, M4A, FLAC, OGG

📋 Prerequisites:

Python 3.8 or higher
Node.js 16+ and npm
Git
4GB+ RAM (8GB recommended for better performance)
GPU support (optional, for faster processing)

 Installation Guide
1. Clone the Repository
bash
git clone https://github.com/Faraz011/AI_Powered_Medical_Transcription_and_Triage.git

2. Backend Setup
Create Virtual Environment
bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
Install Python Dependencies
bash
pip install --upgrade pip
pip install -r requirements.txt
Create requirements.txt
text
Flask==3.0.0
flask-cors==4.0.0
openai-whisper==20231117
torch>=2.0.0
transformers>=4.30.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
medspacy>=1.0.0
werkzeug>=3.0.0
pathlib
hashlib3
uuid
traceback2
Install Additional Requirements
bash
# For CUDA support (optional)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For audio processing
pip install librosa soundfile

# For medical NER
pip install spacy
python -m spacy download en_core_web_sm
3. Frontend Setup
bash
cd ../frontend
npm install
Create package.json dependencies
json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0",
    "tailwindcss": "^3.3.0"
  }
}
4. Directory Structure Setup
text
medical-transcription-triage/
├── backend/
│   ├── app.py                 # Flask application
│   ├── mainPipeline.py        # Main processing pipeline
│   ├── transcrib.py           # Whisper transcription
│   ├── ner.py                 # Medical NER system
│   ├── triageSystem.py        # ESI triage implementation
│   ├── enhanced_ner.py        # Advanced NER (optional)
│   ├── requirements.txt
│   ├── temp_uploads/          # Temporary file storage
│   ├── output/               # Generated reports
│   │   ├── reports/
│   │   ├── entities/
│   │   └── transcripts/
│   └── logs/                 # Application logs
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── public/
│   └── package.json
└── README.md
🔧 Configuration
1. Backend Configuration
Create config.json in the backend directory:

json
{
  "audio_settings": {
    "supported_formats": [".wav", ".mp3", ".m4a", ".flac"],
    "max_file_size_mb": 100,
    "sample_rate": 16000
  },
  "transcription_settings": {
    "model_size": "base",
    "language": "en",
    "task": "transcribe"
  },
  "ner_settings": {
    "confidence_threshold": 0.5,
    "enable_rule_based": true,
    "enable_transformer": true
  },
  "triage_settings": {
    "use_esi_guidelines": true,
    "confidence_threshold": 0.7
  },
  "output_settings": {
    "save_intermediate_results": true,
    "export_formats": ["json", "csv", "html"],
    "include_confidence_scores": true
  }
}
2. Environment Variables
Create .env file in backend directory:

text
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=temp_uploads
🏃‍♂️ Running the Application
1. Start Backend Server
bash
cd backend
python app.py
The backend will start on http://localhost:5000

2. Start Frontend Development Server
bash
cd frontend
npm start
The frontend will start on http://localhost:3000

3. Access the Application
Open your browser and navigate to http://localhost:3000

📖 Usage Guide
1. Upload Audio File
Click on the upload area or drag and drop an audio file

Enter a Patient ID (optional but recommended)

Click "Process Audio"

2. View Results
The dashboard will display:

Transcription: Full text transcript with confidence score

Medical Entities: Extracted symptoms, medications, diseases, procedures

ESI Triage Assessment: Emergency Severity Index level (1-5)

Clinical Summary: Structured medical information

Recommendations: Clinical action recommendations

3. Download Reports
JSON: Raw data export

CSV: Entity data for analysis

HTML: Formatted medical report

🏥 ESI Triage Levels
Level	Priority	Color	Wait Time	Description
1	IMMEDIATE	RED	0 minutes	Life-threatening, requires immediate intervention
2	EMERGENT	ORANGE	≤10-15 minutes	High-risk, should not wait
3	URGENT	YELLOW	≤30 minutes	Stable but needs multiple resources
4	LESS URGENT	GREEN	≤60 minutes	One resource needed
5	NON-URGENT	BLUE	≤120 minutes	No resources needed
🔍 API Documentation
Upload and Process Audio
text
POST /api/upload
Content-Type: multipart/form-data

Body:
- file: Audio file (WAV, MP3, M4A, FLAC, OGG)
- patientId: Patient identifier (optional)
Health Check
text
GET /api/health
Memory Cleanup
text
POST /api/memory/cleanup
Get Report
text
GET /api/reports/{session_id}
🧪 Testing
1. Unit Tests
bash
cd backend
python -m pytest tests/
2. Integration Tests
bash
# Test with sample audio file
python mainPipeline.py sample_audio.mp3
3. API Tests
bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test file upload
curl -X POST -F "file=@test_audio.mp3" -F "patientId=TEST001" http://localhost:5000/api/upload
📊 Performance Optimization
1. GPU Acceleration
For faster processing, ensure CUDA is available:

bash
python -c "import torch; print(torch.cuda.is_available())"
2. Model Caching
The system automatically caches models to improve performance:

Whisper models are cached after first load

BioBERT models are cached in transformers cache

Regular cache clearing prevents memory leaks

3. Batch Processing
For processing multiple files:

python
from mainPipeline import MedicalPipelineIntegrator

pipeline = MedicalPipelineIntegrator()
results = pipeline.process_batch_audio("path/to/audio/directory")

Disclaimer: This system is for educational and research purposes. Always consult qualified healthcare professionals for medical decisions. Not intended for primary clinical diagnosis or treatment.
🛡️ 