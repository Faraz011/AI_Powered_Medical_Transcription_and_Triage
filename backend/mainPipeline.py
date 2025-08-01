import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import sys
import json
import logging
import torch
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import traceback

# Import your existing modules
from transcrib import MedicalTranscriber
from ner import AdvancedMedicalNER
from triageSystem import HybridTriageSystem

class MedicalPipelineIntegrator:
    """
    Complete AI-Powered Medical Transcription and Triage Pipeline
    
    Integrates audio transcription, medical NER, and triage assessment
    into a unified system for processing medical conversations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the complete medical pipeline"""
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_configuration(config_path)
        
        # Initialize components
        self.logger.info("Initializing medical pipeline components...")
        try:
            # Initialize transcription component
            self.transcriber = MedicalTranscriber()
            self.logger.info("Medical transcriber initialized")
            
            # Initialize NER component
            self.ner_system = AdvancedMedicalNER()
            self.logger.info("Medical NER system initialized")
            
            # Initialize triage component
            self.triage_system = HybridTriageSystem()
            self.logger.info("Hybrid triage system initialized")
            
            # Create output directories
            self.setup_output_directories()
            
            self.logger.info("Medical pipeline successfully initialized!")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pipeline: {str(e)}")
            raise
    
    def setup_logging(self):
        """Configure comprehensive logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"medical_pipeline_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized: {log_file}")
    
    def load_configuration(self, config_path: Optional[str] = None) -> Dict:
        """Load pipeline configuration"""
        default_config = {
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
                "enable_rule_based": True,
                "enable_transformer": True
            },
            "triage_settings": {
                "use_hybrid_approach": True,
                "confidence_threshold": 0.7,
                "enable_ml_fallback": True
            },
            "output_settings": {
                "save_intermediate_results": True,
                "export_formats": ["json", "csv", "html"],
                "include_confidence_scores": True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            # Merge configurations
            default_config.update(user_config)
        
        return default_config
    
    def setup_output_directories(self):
        """Create necessary output directories"""
        self.output_dirs = {
            'transcripts': Path('output/transcripts'),
            'entities': Path('output/entities'),
            'triage': Path('output/triage'),
            'reports': Path('output/reports'),
            'logs': Path('logs')
        }
        
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate_audio_file(self, audio_path: Union[str, Path]) -> bool:
        """Validate audio file before processing"""
        audio_path = Path(audio_path)
        
        # Check if file exists
        if not audio_path.exists():
            self.logger.error(f"Audio file not found: {audio_path}")
            return False
        
        # Check file extension
        if audio_path.suffix.lower() not in self.config["audio_settings"]["supported_formats"]:
            self.logger.error(f"Unsupported audio format: {audio_path.suffix}")
            return False
        
        # Check file size
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        max_size = self.config["audio_settings"]["max_file_size_mb"]
        if file_size_mb > max_size:
            self.logger.error(f"File too large: {file_size_mb:.1f}MB > {max_size}MB")
            return False
        
        self.logger.info(f"✓ Audio file validation passed: {audio_path}")
        return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file to verify uniqueness"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:8]
    
    def clear_model_caches(self):
        """Safely clear all model caches to prevent result persistence"""
        try:
            # Clear NER pipeline cache safely
            if hasattr(self.ner_system, 'medical_ner_pipeline'):
                if hasattr(self.ner_system.medical_ner_pipeline, 'model'):
                    if hasattr(self.ner_system.medical_ner_pipeline.model, '_past'):
                        self.ner_system.medical_ner_pipeline.model._past = {}
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            self.logger.debug("Model caches cleared successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to clear model caches: {e}")
    
    def process_single_audio(self, audio_path: Union[str, Path], 
                           patient_id: Optional[str] = None) -> Dict:
        """Process a single audio file through the complete pipeline"""
        audio_path = Path(audio_path)
        
        # Generate UNIQUE session ID for each call
        unique_id = uuid.uuid4().hex[:8]
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
        
        if patient_id:
            session_id = f"{patient_id}_{session_id}"
        
        # Debug: Log file info
        file_size = audio_path.stat().st_size if audio_path.exists() else 0
        file_hash = self.calculate_file_hash(audio_path) if audio_path.exists() else "NO_FILE"
        
        self.logger.info(f"🎵 NEW PIPELINE SESSION: {session_id}")
        self.logger.info(f"📁 File: {audio_path.name}")
        self.logger.info(f"📊 Size: {file_size} bytes")
        self.logger.info(f"🔍 Hash: {file_hash}")
        
        try:
            # Step 1: Validate audio file
            if not self.validate_audio_file(audio_path):
                raise ValueError(f"Audio validation failed for {audio_path}")
            
            # Step 2: Transcription
            self.logger.info(f"📝 Step 1: Starting transcription for {audio_path.name}")
            transcript_result = self.transcriber.transcribe_audio(str(audio_path))
            
            if not transcript_result or not transcript_result.get('text'):
                raise ValueError("Transcription failed or returned empty text")
            
            transcript_text = transcript_result['text']
            transcript_hash = hashlib.md5(transcript_text.encode()).hexdigest()[:8]
            
            self.logger.info(f"✓ Transcription completed:")
            self.logger.info(f"  📄 Length: {len(transcript_text)} characters")
            self.logger.info(f"  🔍 Hash: {transcript_hash}")
            self.logger.info(f"  📝 Preview: {transcript_text[:100]}...")
            
            # Step 3: Named Entity Recognition
            self.logger.info(f"🏥 Step 2: Starting NER extraction...")
            entities = self.ner_system.extract_entities(transcript_text)
            
            entity_count = sum(len(ent_list) for ent_list in entities.values())
            entities_hash = hashlib.md5(str(entities).encode()).hexdigest()[:8]
            
            self.logger.info(f"✓ NER completed:")
            self.logger.info(f"  🔢 Total entities: {entity_count}")
            self.logger.info(f"  🔍 Hash: {entities_hash}")
            self.logger.info(f"  📊 Breakdown: {dict((k, len(v)) for k, v in entities.items())}")
            
            # Step 4: Triage Assessment
            self.logger.info(f"🚑 Step 3: Starting triage assessment...")
            triage_result = self.triage_system.comprehensive_triage(entities, transcript_text)
            
            triage_level = triage_result.get('triage_level', 'Unknown')
            triage_hash = hashlib.md5(str(triage_result).encode()).hexdigest()[:8]
            
            self.logger.info(f"✓ Triage completed:")
            self.logger.info(f"  🚨 Level: {triage_level}")
            self.logger.info(f"  🔍 Hash: {triage_hash}")
            
            # Step 5: Clear model caches SAFELY
            self.clear_model_caches()
            
            # Step 6: Compile comprehensive results
            complete_result = self.compile_results(
                session_id=session_id,
                audio_path=audio_path,
                transcript=transcript_result,
                entities=entities,
                triage=triage_result,
                patient_id=patient_id
            )
            
            # Add debug info to result
            complete_result['debug_info'] = {
                'file_hash': file_hash,
                'transcript_hash': transcript_hash,
                'entities_hash': entities_hash,
                'triage_hash': triage_hash,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Step 7: Save results
            if self.config["output_settings"]["save_intermediate_results"]:
                self.save_session_results(session_id, complete_result)
            
            self.logger.info(f"🎉 Pipeline completed successfully for session: {session_id}")
            return complete_result
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed for {audio_path}: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            return {
                'session_id': session_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'audio_file': str(audio_path)
            }
    
    def compile_results(self, session_id: str, audio_path: Path, 
                       transcript: Dict, entities: Dict, triage: Dict,
                       patient_id: Optional[str] = None) -> Dict:
        """Compile comprehensive results from all pipeline components"""
        
        # Calculate summary statistics
        entity_summary = {
            category: len(entity_list) 
            for category, entity_list in entities.items()
        }
        
        # Generate clinical summary
        clinical_summary = self.generate_clinical_summary(transcript, entities, triage)
        
        # Compile complete result
        result = {
            # Session metadata
            'session_info': {
                'session_id': session_id,
                'patient_id': patient_id,
                'audio_file': str(audio_path),
                'processing_timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            
            # Transcription results
            'transcription': {
                'text': transcript.get('text', ''),
                'language': transcript.get('language', 'en'),
                'confidence': transcript.get('confidence', 0.0),
                'duration': transcript.get('duration', 0.0),
                'word_count': len(transcript.get('text', '').split())
            },
            
            # NER results
            'entities': {
                'extracted_entities': entities,
                'entity_summary': entity_summary,
                'total_entities': sum(entity_summary.values())
            },
            
            # Triage results
            'triage': triage,
            
            # Clinical summary
            'clinical_summary': clinical_summary,
            
            # Processing status
            'status': 'completed',
            'processing_time': self.calculate_processing_time()
        }
        
        return result
    
    def generate_clinical_summary(self, transcript: Dict, entities: Dict, triage: Dict) -> Dict:
        """Generate structured clinical summary"""
        
        # Extract key clinical information
        symptoms = [e.get('text', '') for e in entities.get('SYMPTOM', [])]
        medications = [e.get('text', '') for e in entities.get('MEDICATION', [])]
        diagnoses = [e.get('text', '') for e in entities.get('DISEASE', [])]
        procedures = [e.get('text', '') for e in entities.get('PROCEDURE', [])]
        
        # Generate summary text
        summary_parts = []
        
        if symptoms:
            summary_parts.append(f"Presenting symptoms: {', '.join(symptoms[:5])}")
        
        if medications:
            summary_parts.append(f"Current medications: {', '.join(medications[:5])}")
        
        if diagnoses:
            summary_parts.append(f"Conditions mentioned: {', '.join(diagnoses[:3])}")
        
        if procedures:
            summary_parts.append(f"Procedures discussed: {', '.join(procedures[:3])}")
        
        summary_text = ". ".join(summary_parts) if summary_parts else "No specific clinical entities identified."
        
        return {
            'text_summary': summary_text,
            'key_symptoms': symptoms[:10],
            'current_medications': medications[:10],
            'mentioned_conditions': diagnoses[:5],
            'discussed_procedures': procedures[:5],
            'triage_priority': triage.get('priority', 'Unknown'),
            'recommended_action': triage.get('recommendation', 'Standard evaluation'),
            'urgency_level': triage.get('triage_level', 'Unknown')
        }
    
    def calculate_processing_time(self) -> float:
        """Calculate processing time (placeholder - implement actual timing)"""
        return 0.0  # You can implement actual timing logic here
    
    def save_session_results(self, session_id: str, results: Dict):
        """Save session results in multiple formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Save JSON format
            json_file = self.output_dirs['reports'] / f"{session_id}_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Save CSV format for entities
            if results.get('entities', {}).get('extracted_entities'):
                self.save_entities_csv(session_id, results['entities']['extracted_entities'])
            
            # Save HTML report
            if 'html' in self.config["output_settings"]["export_formats"]:
                self.generate_html_report(session_id, results)
            
            self.logger.info(f"📁 Results saved for session: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session results: {e}")

    def save_entities_csv(self, session_id: str, entities: Dict):
        """Save extracted entities in CSV format"""
        
        try:
            entity_rows = []
            for category, entity_list in entities.items():
                for entity in entity_list:
                    entity_rows.append({
                        'session_id': session_id,
                        'category': category,
                        'text': entity.get('text', ''),
                        'confidence': entity.get('confidence', 0.0),
                        'start': entity.get('start', 0),
                        'end': entity.get('end', 0),
                        'source': entity.get('source', 'unknown')
                    })
            
            if entity_rows:
                df = datetime.now(entity_rows)
                csv_file = self.output_dirs['entities'] / f"{session_id}_entities.csv"
                df.to_csv(csv_file, index=False)
                self.logger.info(f"📊 Entities CSV saved: {csv_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save entities CSV: {e}")

    def generate_html_report(self, session_id: str, results: Dict):
        """Generate HTML report for session results"""
        
        try:
            triage_level = results.get('triage', {}).get('triage_level', 5)
            triage_class = 'urgent' if triage_level <= 2 else 'normal'
            
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Medical AI Report - {session_id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                    .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #fafafa; }}
                    .urgent {{ background-color: #ffe6e6; border-color: #ff9999; }}
                    .normal {{ background-color: #e6ffe6; border-color: #99ff99; }}
                    .entity {{ display: inline-block; margin: 5px; padding: 5px 10px; background-color: #e9ecef; border-radius: 15px; border: 1px solid #ced4da; }}
                    .entity.symptom {{ background-color: #fff3cd; border-color: #ffeaa7; }}
                    .entity.medication {{ background-color: #d1ecf1; border-color: #bee5eb; }}
                    .entity.disease {{ background-color: #f8d7da; border-color: #f5c6cb; }}
                    .entity.procedure {{ background-color: #d4edda; border-color: #c3e6cb; }}
                    .confidence {{ font-size: 0.8em; color: #666; }}
                    .transcript {{ background-color: white; padding: 15px; border-left: 4px solid #007bff; font-style: italic; }}
                    .triage-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 0; }}
                    .level-1 {{ background-color: #dc3545; color: white; }}
                    .level-2 {{ background-color: #fd7e14; color: white; }}
                    .level-3 {{ background-color: #ffc107; color: black; }}
                    .level-4 {{ background-color: #28a745; color: white; }}
                    .level-5 {{ background-color: #6c757d; color: white; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 Medical AI Analysis Report</h1>
                        <p><strong>Session ID:</strong> {session_id}</p>
                        <p><strong>Processing Time:</strong> {results.get('session_info', {}).get('processing_timestamp', 'Unknown')}</p>
                        <p><strong>Audio File:</strong> {results.get('session_info', {}).get('audio_file', 'Unknown')}</p>
                    </div>
                    
                    <div class="section">
                        <h2>📝 Transcript</h2>
                        <div class="transcript">
                            <p>{results.get('transcription', {}).get('text', 'No transcript available')}</p>
                        </div>
                        <p><strong>Confidence:</strong> {results.get('transcription', {}).get('confidence', 0):.2f}</p>
                        <p><strong>Word Count:</strong> {results.get('transcription', {}).get('word_count', 0)}</p>
                        <p><strong>Duration:</strong> {results.get('transcription', {}).get('duration', 0):.1f} seconds</p>
                    </div>
                    
                    <div class="section">
                        <h2>🏥 Medical Entities</h2>
                        <p><strong>Total Entities:</strong> {results.get('entities', {}).get('total_entities', 0)}</p>
                        {self._generate_entity_html(results.get('entities', {}).get('extracted_entities', {}))}
                    </div>
                    
                    <div class="section {triage_class}">
                        <h2>🚑 Triage Assessment</h2>
                        <div class="triage-badge level-{triage_level}">
                            Level {triage_level} - {results.get('triage', {}).get('priority', 'Unknown')}
                        </div>
                        <p><strong>Color Code:</strong> {results.get('triage', {}).get('color_code', 'Unknown')}</p>
                        <p><strong>Recommended Action:</strong> {results.get('triage', {}).get('recommendation', 'Standard care')}</p>
                        <p><strong>Wait Time:</strong> {results.get('triage', {}).get('wait_time', 'Unknown')}</p>
                        <p><strong>Confidence:</strong> {results.get('triage', {}).get('confidence', 'N/A')}</p>
                    </div>
                    
                    <div class="section">
                        <h2>📋 Clinical Summary</h2>
                        <p><strong>Summary:</strong> {results.get('clinical_summary', {}).get('text_summary', 'No summary available')}</p>
                        
                        <div style="margin-top: 15px;">
                            <h4>Key Clinical Information:</h4>
                            <p><strong>Symptoms:</strong> {', '.join(results.get('clinical_summary', {}).get('key_symptoms', [])[:5]) or 'None identified'}</p>
                            <p><strong>Medications:</strong> {', '.join(results.get('clinical_summary', {}).get('current_medications', [])[:5]) or 'None mentioned'}</p>
                            <p><strong>Conditions:</strong> {', '.join(results.get('clinical_summary', {}).get('mentioned_conditions', [])[:3]) or 'None mentioned'}</p>
                            <p><strong>Procedures:</strong> {', '.join(results.get('clinical_summary', {}).get('discussed_procedures', [])[:3]) or 'None discussed'}</p>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🔍 Processing Details</h2>
                        <p><strong>Pipeline Version:</strong> {results.get('session_info', {}).get('pipeline_version', 'Unknown')}</p>
                        <p><strong>Processing Status:</strong> {results.get('status', 'Unknown')}</p>
                        <p><strong>Processing Time:</strong> {results.get('processing_time', 0):.2f} seconds</p>
                        
                        {self._generate_debug_info_html(results.get('debug_info', {}))}
                    </div>
                    
                    <div class="header" style="margin-top: 30px; text-align: center; font-size: 0.9em; color: #666;">
                        <p>Generated by Medical AI Pipeline v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_file = self.output_dirs['reports'] / f"{session_id}_report.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            self.logger.info(f"📄 HTML report saved: {html_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")

    def _generate_entity_html(self, entities: Dict) -> str:
        """Generate HTML for entities display"""
        try:
            html_parts = []
            for category, entity_list in entities.items():
                if entity_list:
                    html_parts.append(f"<h4>{category.title()} ({len(entity_list)} entities)</h4>")
                    for entity in entity_list[:10]:  # Limit display to first 10
                        confidence = entity.get('confidence', 0.0)
                        source = entity.get('source', 'unknown')
                        entity_class = category.lower()
                        html_parts.append(
                            f'<span class="entity {entity_class}">'
                            f'{entity.get("text", "")} '
                            f'<span class="confidence">({confidence:.2f} - {source})</span>'
                            f'</span>'
                        )
                    if len(entity_list) > 10:
                        html_parts.append(f'<p><em>... and {len(entity_list) - 10} more entities</em></p>')
                    html_parts.append('<br><br>')
            
            return "".join(html_parts) if html_parts else "<p>No medical entities identified.</p>"
            
        except Exception as e:
            self.logger.error(f"Error generating entity HTML: {e}")
            return "<p>Error displaying entities.</p>"

    def _generate_debug_info_html(self, debug_info: Dict) -> str:
        """Generate HTML for debug information"""
        try:
            if not debug_info:
                return ""
            
            html_parts = [
                "<h4>🔧 Debug Information</h4>",
                f"<p><strong>File Hash:</strong> {debug_info.get('file_hash', 'N/A')}</p>",
                f"<p><strong>Transcript Hash:</strong> {debug_info.get('transcript_hash', 'N/A')}</p>",
                f"<p><strong>Entities Hash:</strong> {debug_info.get('entities_hash', 'N/A')}</p>",
                f"<p><strong>Triage Hash:</strong> {debug_info.get('triage_hash', 'N/A')}</p>",
            ]
            
            return "".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating debug HTML: {e}")
            return ""

    def process_batch_audio(self, audio_directory: Union[str, Path], 
                           patient_mapping: Optional[Dict] = None) -> List[Dict]:
        """
        Process multiple audio files in batch
        
        Args:
            audio_directory: Directory containing audio files
            patient_mapping: Optional mapping of filenames to patient IDs
            
        Returns:
            List of processing results
        """
        audio_dir = Path(audio_directory)
        if not audio_dir.exists():
            raise ValueError(f"Directory not found: {audio_dir}")
        
        # Find all audio files
        audio_files = []
        for ext in self.config["audio_settings"]["supported_formats"]:
            audio_files.extend(audio_dir.glob(f"*{ext}"))
        
        if not audio_files:
            self.logger.warning(f"No audio files found in {audio_dir}")
            return []
        
        self.logger.info(f"🎵 Processing {len(audio_files)} audio files...")
        
        results = []
        for audio_file in audio_files:
            patient_id = None
            if patient_mapping:
                patient_id = patient_mapping.get(audio_file.name)
            
            result = self.process_single_audio(audio_file, patient_id)
            results.append(result)
        
        # Generate batch summary
        self.generate_batch_summary(results)
        
        return results

    def generate_batch_summary(self, results: List[Dict]):
        """Generate summary report for batch processing"""
        
        try:
            successful = [r for r in results if r.get('status') == 'completed']
            failed = [r for r in results if r.get('status') == 'error']
            
            # Triage distribution
            triage_distribution = {}
            for result in successful:
                level = result.get('triage', {}).get('triage_level', 'Unknown')
                triage_distribution[level] = triage_distribution.get(level, 0) + 1
            
            summary = {
                'batch_summary': {
                    'total_files': len(results),
                    'successful': len(successful),
                    'failed': len(failed),
                    'success_rate': len(successful) / len(results) * 100 if results else 0
                },
                'triage_distribution': triage_distribution,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Save batch summary
            summary_file = self.output_dirs['reports'] / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"📊 Batch summary: {len(successful)}/{len(results)} successful")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate batch summary: {e}")
            return {}


def main():
    """Main function to demonstrate pipeline usage"""
    
    # Initialize pipeline
    pipeline = MedicalPipelineIntegrator()
    
    # Example: Process single audio file
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        if Path(audio_path).is_file():
            # Process single file
            result = pipeline.process_single_audio(audio_path)
            print(f"\n🎉 Processing completed!")
            print(f"Session ID: {result.get('session_info', {}).get('session_id', 'Unknown')}")
            print(f"Triage Level: {result.get('triage', {}).get('triage_level', 'Unknown')}")
            
        elif Path(audio_path).is_dir():
            # Process directory
            results = pipeline.process_batch_audio(audio_path)
            print(f"\n🎉 Batch processing completed: {len(results)} files processed")
        
        else:
            print(f"Invalid path: {audio_path}")
    else:
        print("Usage: python main_pipeline.py <audio_file_or_directory>")


if __name__ == "__main__":
    main()
