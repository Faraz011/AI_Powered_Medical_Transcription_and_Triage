import re
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

from datetime import datetime
from typing import Dict
import hashlib
import uuid

class ESITriageSystem:
    """
    Pure ESI (Emergency Severity Index) based medical triage system
    Following official ESI guidelines v4 for emergency department triage
    """
    
    def __init__(self):
        self._cache = {}
        self.setup_esi_criteria()
    
    def setup_esi_criteria(self):
        """Define ESI criteria based on official guidelines"""
        
        # ESI Level 1 - Requires immediate life-saving intervention
        self.level_1_criteria = {
            'immediate_threats': [
                'cardiac arrest', 'respiratory arrest', 'pulseless', 'apneic',
                'unresponsive', 'unconscious', 'comatose', 'not breathing',
                'no pulse', 'ventricular fibrillation', 'ventricular tachycardia',
                'complete heart block', 'severe shock', 'major trauma with unstable vitals'
            ],
            'critical_vitals': {
                'systolic_bp_low': 70,
                'heart_rate_low': 40,
                'heart_rate_high': 180,
                'respiratory_rate_low': 8,
                'respiratory_rate_high': 40,
                'oxygen_saturation_low': 85,
                'temperature_high': 106  # 41.1°C
            }
        }
        
        # ESI Level 2 - High-risk situation, shouldn't wait
        self.level_2_criteria = {
            'high_risk_symptoms': [
                'chest pain', 'shortness of breath', 'difficulty breathing',
                'severe abdominal pain', 'altered mental status', 'confusion',
                'severe headache', 'sudden severe headache', 'stroke symptoms',
                'facial drooping', 'slurred speech', 'weakness on one side',
                'syncope', 'near syncope', 'severe dehydration',
                'active bleeding', 'severe trauma', 'severe burns'
            ],
            'high_risk_conditions': [
                'acute myocardial infarction', 'stroke', 'sepsis', 'pulmonary embolism',
                'aortic dissection', 'ruptured aneurysm', 'severe asthma attack',
                'diabetic ketoacidosis', 'severe allergic reaction'
            ],
            'high_risk_medications': [
                'warfarin', 'coumadin', 'heparin', 'insulin overdose',
                'chemotherapy', 'immunosuppressants'
            ],
            'vulnerable_populations': {
                'age_high_risk': 65,
                'pregnancy_complications': True,
                'immunocompromised': True
            }
        }
        
        # ESI Level 3 - Stable but needs multiple resources
        self.level_3_criteria = {
            'moderate_symptoms': [
                'moderate pain', 'fever', 'vomiting', 'diarrhea',
                'minor head injury', 'laceration requiring sutures',
                'moderate abdominal pain', 'urinary tract infection',
                'simple fracture', 'sprain', 'cellulitis'
            ],
            'chronic_conditions': [
                'diabetes', 'hypertension', 'asthma', 'copd',
                'heart disease', 'kidney disease'
            ],
            'resource_intensive': [
                'multiple lab tests', 'imaging studies', 'specialist consultation',
                'IV medications', 'cardiac monitoring'
            ]
        }
        
        # ESI Level 4 - One resource needed
        self.level_4_criteria = {
            'simple_problems': [
                'mild pain', 'minor injury', 'simple laceration',
                'medication refill', 'routine follow-up', 'cold symptoms',
                'minor rash', 'minor headache', 'constipation'
            ],
            'single_resource': [
                'simple x-ray', 'basic blood test', 'urine test',
                'simple prescription', 'wound cleaning'
            ]
        }
        
        # ESI Level 5 - No resources needed
        self.level_5_criteria = {
            'minimal_care': [
                'medication request', 'work note', 'blood pressure check',
                'simple dressing change', 'chronic stable condition',
                'minor complaint', 'health screening'
            ]
        }
    
    def clear_cache(self):
        """Clear cache to prevent result persistence"""
        if hasattr(self, '_cache'):
            self._cache.clear()
        else:
            self._cache = {}
    
    def assess_esi_level(self, entities: Dict, transcript: str) -> Dict:
        """
        Assess ESI triage level based on official ESI guidelines
        """
        self.clear_cache()
        
        # ESI Algorithm Step 1: Does the patient require immediate life-saving intervention?
        if self.check_esi_level_1(entities, transcript):
            return self.create_esi_response(1, 'IMMEDIATE', 'RED', 
                                          'Immediate life-saving intervention required',
                                          '0 minutes')
        
        # ESI Algorithm Step 2: Is this a high-risk situation?
        elif self.check_esi_level_2(entities, transcript):
            return self.create_esi_response(2, 'EMERGENT', 'ORANGE',
                                          'High-risk situation - should not wait',
                                          '≤10 minutes')
        
        # ESI Algorithm Steps 3-4: How many resources will the patient consume?
        elif self.check_esi_level_3(entities, transcript):
            return self.create_esi_response(3, 'URGENT', 'YELLOW',
                                          'Many resources needed - urgent care',
                                          '≤30 minutes')
        
        elif self.check_esi_level_4(entities, transcript):
            return self.create_esi_response(4, 'LESS URGENT', 'GREEN',
                                          'One resource needed - less urgent',
                                          '≤60 minutes')
        
        else:
            return self.create_esi_response(5, 'NON-URGENT', 'BLUE',
                                          'No resources needed - non-urgent',
                                          '≤120 minutes')
    
    def create_esi_response(self, level: int, priority: str, color: str, 
                           recommendation: str, wait_time: str) -> Dict:

        level_recommendations = {
        1: 'Immediate life-saving intervention required - resuscitation team activation',
        2: 'Immediate evaluation and intervention required; see provider within 10-15 minutes. Do not wait in general queue',
        3: 'Urgent medical evaluation needed; multiple resources required within 30 minutes',
        4: 'Less urgent care; single resource needed within 60 minutes',
        5: 'Non-urgent care; routine evaluation within 2 hours'
    }                   
        """Create standardized ESI response"""
        return {
            'triage_level': level,
            'priority': priority,
            'color_code': color,
            'recommendation': recommendation,
            'wait_time': wait_time,
            'esi_version': '4.0',
            'assessment_id': uuid.uuid4().hex[:8],
            'timestamp': datetime.now().isoformat(),
            'confidence': 'HIGH' if level <= 2 else 'MEDIUM' if level == 3 else 'LOW'
        }
    
    def check_esi_level_1(self, entities: Dict, transcript: str) -> bool:
        """
        ESI Level 1: Immediate life-saving intervention required
        """
        transcript_lower = transcript.lower()
        
        # Check for immediate life threats in transcript
        for threat in self.level_1_criteria['immediate_threats']:
            if threat in transcript_lower:
                return True
        
        # Check symptoms in entities
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                for threat in self.level_1_criteria['immediate_threats']:
                    if threat in symptom_text:
                        return True
        
        # Check for critical vital signs mentioned in transcript
        if self.check_critical_vitals(transcript_lower):
            return True
        
        return False
    
    def check_critical_vitals(self, transcript: str) -> bool:
        """Check for critically abnormal vital signs"""
        # Blood pressure patterns
        bp_pattern = r'blood pressure.*?(\d+)/(\d+)|bp.*?(\d+)/(\d+)|(\d+)/(\d+)'
        bp_matches = re.finditer(bp_pattern, transcript)
        
        for match in bp_matches:
            groups = match.groups()
            systolic = None
            for group in groups[:5:2]:  # Check odd indices for systolic
                if group:
                    try:
                        systolic = int(group)
                        break
                    except:
                        continue
            
            if systolic and systolic < self.level_1_criteria['critical_vitals']['systolic_bp_low']:
                return True
        
        # Heart rate patterns
        hr_pattern = r'heart rate.*?(\d+)|pulse.*?(\d+)|hr.*?(\d+)'
        hr_matches = re.finditer(hr_pattern, transcript)
        
        for match in hr_matches:
            try:
                hr = int(match.group(1))
                if (hr < self.level_1_criteria['critical_vitals']['heart_rate_low'] or 
                    hr > self.level_1_criteria['critical_vitals']['heart_rate_high']):
                    return True
            except:
                continue
        
        # Oxygen saturation patterns
        o2_pattern = r'oxygen saturation.*?(\d+)|o2 sat.*?(\d+)|spo2.*?(\d+)'
        o2_matches = re.finditer(o2_pattern, transcript)
        
        for match in o2_matches:
            try:
                o2_sat = int(match.group(1))
                if o2_sat < self.level_1_criteria['critical_vitals']['oxygen_saturation_low']:
                    return True
            except:
                continue
        
        return False
    
    def check_esi_level_2(self, entities: Dict, transcript: str) -> bool:
        """
        ESI Level 2: High-risk situation that shouldn't wait
        """
        transcript_lower = transcript.lower()
        
        # Check high-risk symptoms in transcript
        for symptom in self.level_2_criteria['high_risk_symptoms']:
            if symptom in transcript_lower:
                return True
        
        # Check high-risk conditions
        for condition in self.level_2_criteria['high_risk_conditions']:
            if condition in transcript_lower:
                return True
        
        # Check entities for high-risk symptoms
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                for high_risk in self.level_2_criteria['high_risk_symptoms']:
                    if high_risk in symptom_text:
                        return True
        
        # Check for high-risk diseases
        if 'DISEASE' in entities:
            for disease in entities['DISEASE']:
                disease_text = disease['text'].lower()
                for high_risk in self.level_2_criteria['high_risk_conditions']:
                    if high_risk in disease_text:
                        return True
        
        # Check for high-risk medications
        if 'MEDICATION' in entities:
            for medication in entities['MEDICATION']:
                med_text = medication['text'].lower()
                for high_risk_med in self.level_2_criteria['high_risk_medications']:
                    if high_risk_med in med_text:
                        return True
        
        # Check for elderly patients (ESI considers age >65 higher risk)
        age_pattern = r'(\d+)\s*(?:year|yr)s?\s*old|age\s*(?:is\s*)?(\d+)'
        age_match = re.search(age_pattern, transcript_lower)
        if age_match:
            try:
                age = int(age_match.group(1) or age_match.group(2))
                if age >= self.level_2_criteria['vulnerable_populations']['age_high_risk']:
                    # Elderly with concerning symptoms
                    concerning_terms = ['chest pain', 'shortness of breath', 'confusion', 'fall']
                    if any(term in transcript_lower for term in concerning_terms):
                        return True
            except:
                pass
        
        return False
    
    def check_esi_level_3(self, entities: Dict, transcript: str) -> bool:
        """
        ESI Level 3: Stable patient requiring multiple resources
        """
        transcript_lower = transcript.lower()
        
        # Check for moderate symptoms
        for symptom in self.level_3_criteria['moderate_symptoms']:
            if symptom in transcript_lower:
                return True
        
        # Check entities for moderate symptoms
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                for moderate in self.level_3_criteria['moderate_symptoms']:
                    if moderate in symptom_text:
                        return True
        
        # Check for chronic conditions that may need resources
        if 'DISEASE' in entities:
            for disease in entities['DISEASE']:
                disease_text = disease['text'].lower()
                for chronic in self.level_3_criteria['chronic_conditions']:
                    if chronic in disease_text:
                        return True
        
        # Check for mentions of procedures that indicate resource needs
        if 'PROCEDURE' in entities:
            procedure_count = len(entities['PROCEDURE'])
            if procedure_count >= 2:  # Multiple procedures = multiple resources
                return True
        
        return False
    
    def check_esi_level_4(self, entities: Dict, transcript: str) -> bool:
        """
        ESI Level 4: One resource needed
        """
        transcript_lower = transcript.lower()
        
        # Check for simple problems
        for problem in self.level_4_criteria['simple_problems']:
            if problem in transcript_lower:
                return True
        
        # Check entities for simple symptoms
        if 'SYMPTOM' in entities:
            for symptom in entities['SYMPTOM']:
                symptom_text = symptom['text'].lower()
                for simple in self.level_4_criteria['simple_problems']:
                    if simple in symptom_text:
                        return True
        
        # Check for single resource indicators
        for resource in self.level_4_criteria['single_resource']:
            if resource in transcript_lower:
                return True
        
        return False

class HybridTriageSystem:
    """
    Simple wrapper that uses only ESI-based triage (no ML)
    """
    
    def __init__(self):
        self.esi_system = ESITriageSystem()
    
    def comprehensive_triage(self, entities: Dict, transcript: str) -> Dict:
        """
        Perform triage assessment using pure ESI guidelines
        """
        
        # Debug: Log inputs to verify different data is being processed
        entities_hash = hashlib.md5(str(entities).encode()).hexdigest()[:8]
        transcript_hash = hashlib.md5(transcript.encode()).hexdigest()[:8]
        
        print(f"🔍 ESI TRIAGE DEBUG: Entities hash: {entities_hash}")
        print(f"🔍 ESI TRIAGE DEBUG: Transcript hash: {transcript_hash}")
        
        # Get ESI assessment
        esi_result = self.esi_system.assess_esi_level(entities, transcript)
        
        print(f"🔍 ESI TRIAGE DEBUG: Assessment ID: {esi_result['assessment_id']}")
        print(f"🔍 ESI TRIAGE DEBUG: ESI Level: {esi_result['triage_level']}")
        print(f"🔍 ESI TRIAGE DEBUG: Priority: {esi_result['priority']}")
        
        return esi_result

# For backward compatibility, keep the same class name
class MedicalTriageSystem:
    """
    ESI-based medical triage system (replaces the old rule-based system)
    """
    
    def __init__(self):
        self._cache = {}
        self.esi_system = ESITriageSystem()
    
    def clear_cache(self):
        """Clear cache to prevent result persistence"""
        if hasattr(self, '_cache'):
            self._cache.clear()
        else:
            self._cache = {}
    
    def assess_triage_level(self, entities: Dict, transcript: str) -> Dict:
        """Assess triage level using ESI guidelines"""
        self.clear_cache()
        return self.esi_system.assess_esi_level(entities, transcript)
