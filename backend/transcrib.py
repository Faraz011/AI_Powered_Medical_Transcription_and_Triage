import re
import warnings
import os
warnings.filterwarnings('ignore', category=UserWarning)

import whisper

class MedicalTranscriber:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)

    def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe audio file and return structured result"""
        try:
            # Verify file exists
            if not os.path.exists(audio_path):
                raise ValueError(f"Audio file not found: {audio_path}")
            
            print(f"Processing audio file: {audio_path}")
            result = self.model.transcribe(audio_path)
            
            # Safe cache reset - only if method exists
            try:
                if hasattr(self.model, 'decoder') and hasattr(self.model.decoder, 'reset'):
                    self.model.decoder.reset()
            except AttributeError:
                pass  # Skip if reset method doesn't exist
            
            transcribed_text = result['text']
            print(f"Transcription completed: {len(transcribed_text)} characters")
            
            return {
                'text': transcribed_text,
                'language': result.get('language', 'en'),
                'confidence': 1.0,  # Whisper doesn't provide confidence scores
                'duration': result.get('duration', 0.0)
            }
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise ValueError(f"Transcription failed: {str(e)}")

       
