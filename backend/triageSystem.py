import re
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
from typing import Dict, List, Tuple
import re

class MedicalTriageSystem:
    """Rule-based medical triage system using ESI guidelines"""
    
    def __init__(self):
        self._cache = {}  # Initialize cache properly
        self.setup_triage_rules()
    
    def setup_triage_rules(self):
        """Define medical triage rules based on ESI guidelines"""
        
        # Level 1 - Immediate (Life-threatening)
        self.level_1_conditions = {
            'symptoms': [
                'cardiac arrest', 'respiratory arrest', 'unresponsive',
                'severe respiratory distress', 'shock', 'stroke symptoms',
                'major trauma', 'severe chest pain', 'unconscious'
            ],
            'vital_signs': {
                'systolic_bp': {'min': 0, 'max': 70},
                'heart_rate': {'min': 0, 'max': 40, 'max_high': 150},
                'respiratory_rate': {'min': 0, 'max': 8, 'max_high': 35},
                'oxygen_saturation': {'min': 0, 'max': 85}
            }
        }
        
        # Level 2 - Emergent (High-risk)
        self.level_2_conditions = {
            'symptoms': [
                'chest pain', 'difficulty breathing', 'severe abdominal pain',
                'altered mental status', 'severe headache', 'high fever',
                'shortness of breath', 'syncope'
            ],
            'medications': ['insulin', 'warfarin', 'heparin'],
            'vital_signs': {
                'systolic_bp': {'min': 71, 'max': 90, 'max_high': 180},
                'heart_rate': {'min': 41, 'max': 60, 'max_high': 120},
                'temperature': {'min': 38.5, 'max': 100}
            }
        }
        
        # Level 3 - Urgent
        self.level_3_conditions = {
            'symptoms': [
                'moderate pain', 'vomiting', 'diarrhea', 'fever',
                'cough', 'rash', 'joint pain', 'urinary symptoms'
            ],
            'diagnoses': ['pneumonia', 'diabetes', 'hypertension', 'infection']
        }
        
        # Level 4 - Less urgent
        self.level_4_conditions = {
            'symptoms': [
                'mild pain', 'minor injury', 'cold symptoms',
                'skin problems', 'minor headache'
            ]
        }
    
    def clear_cache(self):
        """Safely clear the cache"""
        if hasattr(self, '_cache'):
            self._cache.clear()
        else:
            self._cache = {}
    
    def assess_triage_level(self, entities: Dict, transcript: str) -> Dict:
        """Determine triage level based on extracted entities and transcript"""
        
        # Clear cache safely to prevent result persistence
        self.clear_cache()
        
        # Check for Level 1 conditions (Most urgent)
        if self.check_level_1(entities, transcript):
            return {
                'triage_level': 1,
                'priority': 'IMMEDIATE',
                'color_code': 'RED',
                'recommendation': 'Immediate medical attention required',
                'wait_time': '0 minutes',
                'confidence': 'HIGH'
            }
        
        # Check for Level 2 conditions
        elif self.check_level_2(entities, transcript):
            return {
                'triage_level': 2,
                'priority': 'EMERGENT',
                'color_code': 'ORANGE',
                'recommendation': 'Urgent medical evaluation needed within 15 minutes',
                'wait_time': '15 minutes',
                'confidence': 'HIGH'
            }
        
        # Check for Level 3 conditions
        elif self.check_level_3(entities):
            return {
                'triage_level': 3,
                'priority': 'URGENT',
                'color_code': 'YELLOW',
                'recommendation': 'Medical evaluation needed within 30 minutes',
                'wait_time': '30 minutes',
                'confidence': 'MEDIUM'
            }
        
        # Check for Level 4 conditions
        elif self.check_level_4(entities):
            return {
                'triage_level': 4,
                'priority': 'LESS URGENT',
                'color_code': 'GREEN',
                'recommendation': 'Routine medical evaluation within 1 hour',
                'wait_time': '60 minutes',
                'confidence': 'MEDIUM'
            }
        
        # Default to Level 5
        else:
            return {
                'triage_level': 5,
                'priority': 'NON-URGENT',
                'color_code': 'BLUE',
                'recommendation': 'Non-urgent care',
                'wait_time': '120 minutes',
                'confidence': 'LOW'
            }
    
    def check_level_1(self, entities: Dict, transcript: str) -> bool:
        """Check for Level 1 (immediate) conditions"""
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                if any(condition in symptom_text for condition in self.level_1_conditions['symptoms']):
                    return True
        
        # Also check transcript directly for critical terms
        transcript_lower = transcript.lower()
        if any(condition in transcript_lower for condition in self.level_1_conditions['symptoms']):
            return True
            
        return False
    
    def check_level_2(self, entities: Dict, transcript: str) -> bool:
        """Check for Level 2 (emergent) conditions"""
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                if any(condition in symptom_text for condition in self.level_2_conditions['symptoms']):
                    return True
        
        # Check medications for high-risk drugs
        if 'MEDICATION' in entities:
            for medication in entities['MEDICATION']:
                med_text = medication['text'].lower()
                if any(med in med_text for med in self.level_2_conditions['medications']):
                    return True
        
        return False
    
    def check_level_3(self, entities: Dict) -> bool:
        """Check for Level 3 (urgent) conditions"""
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                if any(condition in symptom_text for condition in self.level_3_conditions['symptoms']):
                    return True
        
        # Check diagnoses
        if 'DISEASE' in entities:
            for disease in entities['DISEASE']:
                disease_text = disease['text'].lower()
                if any(condition in disease_text for condition in self.level_3_conditions['diagnoses']):
                    return True
        
        return False
    
    def check_level_4(self, entities: Dict) -> bool:
        """Check for Level 4 (less urgent) conditions"""
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                if any(condition in symptom_text for condition in self.level_4_conditions['symptoms']):
                    return True
        return False

# ML-based triage system placeholder
class MLTriageSystem:
    def __init__(self):
        self._cache = {}
    
    def predict_triage_level(self, entities: Dict, transcript: str) -> Dict:
        """Placeholder for ML-based triage prediction"""
        # Clear cache to prevent result persistence
        self._cache.clear()
        
        return {
            'triage_level': 3,
            'confidence': 0.75,
            'source': 'ml_prediction'
        }

class HybridTriageSystem:
    def __init__(self):
        self.rule_based = MedicalTriageSystem()
        self.ml_based = MLTriageSystem()
    
    def comprehensive_triage(self, entities: Dict, transcript: str) -> Dict:
        """Combine rule-based and ML predictions"""
        import hashlib
        
        # Debug: Log inputs to verify different data is being processed
        entities_hash = hashlib.md5(str(entities).encode()).hexdigest()[:8]
        transcript_hash = hashlib.md5(transcript.encode()).hexdigest()[:8]
        
        print(f"🔍 TRIAGE DEBUG: Entities hash: {entities_hash}")
        print(f"🔍 TRIAGE DEBUG: Transcript hash: {transcript_hash}")
        
        # Get rule-based assessment
        rule_result = self.rule_based.assess_triage_level(entities, transcript)
        
        # Add unique identifier to prevent caching
        import uuid
        rule_result['assessment_id'] = uuid.uuid4().hex[:8]
        rule_result['timestamp'] = pd.Timestamp.now().isoformat()
        
        print(f"🔍 TRIAGE DEBUG: Assessment ID: {rule_result['assessment_id']}")
        print(f"🔍 TRIAGE DEBUG: Triage level: {rule_result['triage_level']}")
        
        return rule_result
