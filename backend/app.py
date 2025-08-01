from flask import Flask, request, jsonify, g, has_request_context
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
import os
import numpy as np
import threading
import uuid
import gc
import torch
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from contextlib import contextmanager
import logging
from functools import wraps


from mainPipeline import MedicalPipelineIntegrator

class RequestContextFilter(logging.Filter):
    """
    Adds a request_id to every log record.
    Falls back to 'system' when no request context is active.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if has_request_context() and getattr(g, "request_id", None):
            record.request_id = g.request_id
        else:                       # during app start-up, CLI, celery, etc.
            record.request_id = "system"
        return True

class NumpyJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles NumPy data types for Flask 3.0+"""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        
        return super().default(obj)

class ThreadSafePipelineManager:
    """Thread-safe manager for medical AI pipeline instances"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._pipeline = None
        self._last_used = None
        self._usage_count = 0
        self._max_usage = 100
        
    def get_pipeline(self):
        """Get pipeline instance with thread safety and memory management"""
        with self._lock:
            current_time = time.time()
            
            if (self._pipeline is None or 
                self._usage_count >= self._max_usage or
                (self._last_used and current_time - self._last_used > 3600)):
                
                if self._pipeline is not None:
                    self._cleanup_pipeline()
                
                logging.info("Initializing fresh medical pipeline instance")
                self._pipeline = MedicalPipelineIntegrator()
                self._usage_count = 0
            
            self._last_used = current_time
            self._usage_count += 1
            return self._pipeline
    
    def _cleanup_pipeline(self):
        """Clean up pipeline resources"""
        logging.info("Cleaning up pipeline resources")
        
        if hasattr(self._pipeline, 'transcriber'):
            if hasattr(self._pipeline.transcriber, 'model'):
                del self._pipeline.transcriber.model
        
        if hasattr(self._pipeline, 'ner_system'):
            if hasattr(self._pipeline.ner_system, 'medical_ner_pipeline'):
                del self._pipeline.ner_system.medical_ner_pipeline
            if hasattr(self._pipeline.ner_system, 'medspacy_nlp'):
                del self._pipeline.ner_system.medspacy_nlp
        
        del self._pipeline
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        self._pipeline = None

# Setup logging FIRST - before creating Flask app
def setup_logging():
    """Setup logging configuration with proper filter"""
    
    # Create the filter
    log_filter = RequestContextFilter()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(request_id)s] %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler('medical_api.log')
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(log_filter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(log_filter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addFilter(log_filter)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure Werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addFilter(log_filter)
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)
    
    return log_filter

# Setup logging before everything else
setup_logging()

# Global thread-safe pipeline manager
pipeline_manager = ThreadSafePipelineManager()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3001"])

# Apply the custom JSON provider
app.json = NumpyJSONProvider(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg'}

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_unique_session_id():
    """Generate a unique session ID for each request"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

@contextmanager
def request_memory_management():
    """Context manager for request-level memory management"""
    start_memory = None
    
    if torch.cuda.is_available():
        start_memory = torch.cuda.memory_allocated()
    
    try:
        yield
    finally:
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            end_memory = torch.cuda.memory_allocated()
            
            if start_memory is not None:
                memory_diff = end_memory - start_memory
                logging.info(f"Memory usage change: {memory_diff / 1024 / 1024:.2f} MB")

def log_request_info(f):
    """Decorator to log request information"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.start_time = time.time()
        g.request_id = uuid.uuid4().hex[:8]
        
        logging.info(f"Request {g.request_id} started: {request.endpoint}")
        
        try:
            result = f(*args, **kwargs)
            duration = time.time() - g.start_time
            logging.info(f"Request {g.request_id} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - g.start_time
            logging.error(f"Request {g.request_id} failed after {duration:.2f}s: {str(e)}")
            raise
    
    return decorated_function

@app.before_request
def before_request():
    """Initialize request-specific data"""
    g.start_time = time.time()
    g.request_id = uuid.uuid4().hex[:8]

@app.after_request
def after_request(response):
    """Clean up after each request"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        logging.info(f"Request {getattr(g, 'request_id', 'unknown')} total duration: {duration:.2f}s")
    
    gc.collect()
    return response

@app.route('/api/health', methods=['GET'])
@log_request_info
def health_check():
    """Health check endpoint with memory info"""
    memory_info = {}
    
    if torch.cuda.is_available():
        memory_info = {
            'cuda_memory_allocated': f"{torch.cuda.memory_allocated() / 1024 / 1024:.2f} MB",
            'cuda_memory_reserved': f"{torch.cuda.memory_reserved() / 1024 / 1024:.2f} MB",
            'cuda_memory_cached': f"{torch.cuda.memory_cached() / 1024 / 1024:.2f} MB"
        }
    
    return jsonify({
        'status': 'healthy',
        'message': 'Medical AI Pipeline API is running',
        'timestamp': datetime.now().isoformat(),
        'request_id': getattr(g, 'request_id', 'unknown'),
        'memory_info': memory_info,
        'pipeline_usage_count': pipeline_manager._usage_count
    })

@app.route('/api/upload', methods=['POST'])
@log_request_info
def upload_and_process():
    """Upload audio file and process through medical AI pipeline"""
    with request_memory_management():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            patient_id = request.form.get('patientId', None)
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'File type not allowed. Supported formats: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Create unique session and file identifiers
            unique_session_id = create_unique_session_id()
            filename = secure_filename(file.filename)
            unique_filename = f"{unique_session_id}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            file.save(file_path)
            
            logging.info(f"Processing file: {filename} (Session: {unique_session_id})")
            
            # Get thread-safe pipeline instance
            pipeline = pipeline_manager.get_pipeline()
            
            # Create unique patient ID for this session
            session_patient_id = f"{patient_id}_{unique_session_id}" if patient_id else unique_session_id
            
            # Process through pipeline
            result = pipeline.process_single_audio(file_path, patient_id=session_patient_id)
        
            
            # Ensure result has unique session info
            if 'session_info' in result:
                result['session_info']['session_id'] = unique_session_id
            
            # Convert numpy types
            result = convert_numpy_types(result)
            
            # Format response
            response_data = {
                'success': True,
                'session_id': unique_session_id,
                'request_id': g.request_id,
                'processing_time': result.get('processing_time', 0),
                'transcript': {
                    'text': result.get('transcription', {}).get('text', ''),
                    'word_count': result.get('transcription', {}).get('word_count', 0),
                    'confidence': result.get('transcription', {}).get('confidence', 0),
                    'duration': result.get('transcription', {}).get('duration', 0)
                },
                'entities': {
                    'summary': result.get('entities', {}).get('entity_summary', {}),
                    'total_count': result.get('entities', {}).get('total_entities', 0),
                    'details': result.get('entities', {}).get('extracted_entities', {})
                },
                'triage': {
                    'level': result.get('triage', {}).get('triage_level', 5),
                    'priority': result.get('triage', {}).get('priority', 'NON-URGENT'),
                    'color_code': result.get('triage', {}).get('color_code', 'BLUE'),
                    'recommendation': result.get('triage', {}).get('recommendation'),
                    'confidence': result.get('triage', {}).get('confidence', 'N/A')
                },
                'clinical_summary': result.get('clinical_summary', {}),
                'timestamp': datetime.now().isoformat(),
                'file_processed': filename
            }
            
            logging.info(f"Successfully processed {filename} (Session: {unique_session_id})")
            return jsonify(response_data)
            
        except Exception as e:
            app.logger.error(f"Processing error for {file.filename if 'file' in locals() else 'unknown'}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'request_id': getattr(g, 'request_id', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }), 500

def convert_numpy_types(obj):
    """Recursively convert NumPy types to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

@app.route('/api/reports/<session_id>', methods=['GET'])
@log_request_info
def get_report(session_id):
    """Get detailed report for a session"""
    try:
        return jsonify({
            'session_id': session_id,
            'status': 'completed',
            'message': 'Report retrieved successfully',
            'request_id': getattr(g, 'request_id', 'unknown')
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500

@app.route('/api/memory/cleanup', methods=['POST'])
@log_request_info
def force_cleanup():
    """Force cleanup of model caches"""
    try:
        pipeline_manager._cleanup_pipeline()
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        return jsonify({
            'success': True,
            'message': 'Memory cleanup completed',
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500

if __name__ == '__main__':
    # Set multiprocessing sharing strategy
    if torch.cuda.is_available():
        try:
            torch.multiprocessing.set_sharing_strategy('file_system')
        except:
            pass
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
