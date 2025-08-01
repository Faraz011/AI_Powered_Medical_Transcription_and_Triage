from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import medspacy
from medspacy.ner import TargetRule
import warnings
warnings.filterwarnings('ignore')

class AdvancedMedicalNER:
    """
    Hybrid Medical NER combining BioBERT transformer model with rule-based fallback
    """
    
    def __init__(self):
        # Use BioBERT that you're already loading
        self.biobert_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
        self.biobert_model = AutoModelForTokenClassification.from_pretrained("dmis-lab/biobert-v1.1")
        
        # Create pipeline from loaded components
        self.medical_ner_pipeline = pipeline(
            "ner",
            model=self.biobert_model,
            tokenizer=self.biobert_tokenizer,
            aggregation_strategy="simple"
        )
        
        # Keep rule-based system as fallback
        self.medspacy_nlp = medspacy.load()
        self.setup_fallback_rules()
        
        # Entity mapping for standardization
        self.entity_mapping = {
            'CHEMICAL': 'MEDICATION',
            'DISEASE': 'DISEASE', 
            'SYMPTOM': 'SYMPTOM',
            'ANATOMY': 'ANATOMY',
            'PROCEDURE': 'PROCEDURE',
            'DRUG': 'MEDICATION',
            'CONDITION': 'DISEASE',
            'PER': 'OTHER',  # BioBERT might return these
            'LOC': 'OTHER',
            'ORG': 'OTHER'
        }
    
    def setup_fallback_rules(self):
        """Setup rule-based fallback for entities not caught by ML model"""
        rules = [
            # Common medications
            TargetRule("metformin", "MEDICATION"),
            TargetRule("insulin", "MEDICATION"),
            TargetRule("lisinopril", "MEDICATION"),
            TargetRule("aspirin", "MEDICATION"),
            TargetRule("ibuprofen", "MEDICATION"),
            TargetRule("amlodipine", "MEDICATION"),
            TargetRule("atorvastatin", "MEDICATION"),
            
            # Common symptoms
            TargetRule("chest pain", "SYMPTOM"),
            TargetRule("shortness of breath", "SYMPTOM"),
            TargetRule("fatigue", "SYMPTOM"),
            TargetRule("nausea", "SYMPTOM"),
            TargetRule("headache", "SYMPTOM"),
            TargetRule("fever", "SYMPTOM"),
            TargetRule("cough", "SYMPTOM"),
            TargetRule("dizziness", "SYMPTOM"),
            TargetRule("sweating", "SYMPTOM"),
            TargetRule("weakness", "SYMPTOM"),
            
            # Common diseases
            TargetRule("diabetes", "DISEASE"),
            TargetRule("hypertension", "DISEASE"),
            TargetRule("pneumonia", "DISEASE"),
            TargetRule("asthma", "DISEASE"),
            TargetRule("depression", "DISEASE"),
            TargetRule("anxiety", "DISEASE"),
            TargetRule("malaria", "DISEASE"),
            
            # Procedures
            TargetRule("CT scan", "PROCEDURE"),
            TargetRule("MRI", "PROCEDURE"),
            TargetRule("X-ray", "PROCEDURE"),
            TargetRule("blood test", "PROCEDURE"),
            TargetRule("EKG", "PROCEDURE"),
            TargetRule("echocardiogram", "PROCEDURE"),
        ]
        
        target_matcher = self.medspacy_nlp.get_pipe("medspacy_target_matcher")
        target_matcher.add(rules)
    
    def extract_entities_ml(self, text):
        """Extract entities using transformer model"""
        try:
            # Clear any cached states first
            if hasattr(self.medical_ner_pipeline.model, '_past'):
                self.medical_ner_pipeline.model._past = {}
            
            # Use the medical NER model
            ml_entities = self.medical_ner_pipeline(text)
            
            # Format entities
            formatted_entities = []
            for entity in ml_entities:
                # Clean up entity text
                entity_text = entity['word'].replace('##', '').strip()
                if len(entity_text) < 2:  # Skip very short entities
                    continue
                    
                formatted_entities.append({
                    'text': entity_text,
                    'label': self.entity_mapping.get(entity['entity_group'], 'OTHER'),
                    'confidence': float(entity['score']),  # Ensure it's a Python float
                    'start': int(entity['start']),
                    'end': int(entity['end']),
                    'source': 'transformer'
                })
            
            return formatted_entities
            
        except Exception as e:
            print(f"ML extraction failed: {e}")
            # Safe cache clearing
            try:
                if hasattr(self, 'medical_ner_pipeline') and hasattr(self.medical_ner_pipeline.model, '_past'):
                    self.medical_ner_pipeline.model._past = {}
            except:
                pass
            return []
    
    def extract_entities_rules(self, text):
        """Extract entities using rule-based system"""
        try:
            doc = self.medspacy_nlp(text)
            rule_entities = []
            
            for ent in doc.ents:
                rule_entities.append({
                    'text': ent.text.strip(),
                    'label': ent.label_,
                    'confidence': 1.0,  # Rule-based has perfect confidence
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'source': 'rule-based'
                })
            
            return rule_entities
            
        except Exception as e:
            print(f"Rule-based extraction failed: {e}")
            return []
    
    def merge_entities(self, ml_entities, rule_entities):
        """Merge entities from both sources, prioritizing ML with high confidence"""
        entities = {
            'SYMPTOM': [],
            'MEDICATION': [],
            'DISEASE': [],
            'PROCEDURE': [],
            'ANATOMY': []
        }
        
        # Add high-confidence ML entities first
        for entity in ml_entities:
            if entity['confidence'] > 0.7:  # High confidence threshold
                label = entity['label']
                if label in entities:
                    entities[label].append(entity)
        
        # Add rule-based entities that don't overlap
        for rule_entity in rule_entities:
            # Check for overlap with existing ML entities
            overlaps = False
            for label in entities:
                for ml_entity in entities[label]:
                    if self.entities_overlap(rule_entity, ml_entity):
                        overlaps = True
                        break
                if overlaps:
                    break
            
            # Add if no overlap
            if not overlaps:
                label = rule_entity['label']
                if label in entities:
                    entities[label].append(rule_entity)
        
        # Add lower confidence ML entities that don't overlap
        for entity in ml_entities:
            if entity['confidence'] <= 0.7:  # Lower confidence
                label = entity['label']
                if label in entities:
                    # Check for overlap
                    overlaps = False
                    for existing in entities[label]:
                        if self.entities_overlap(entity, existing):
                            overlaps = True
                            break
                    
                    if not overlaps:
                        entities[label].append(entity)
        
        return entities
    
    def entities_overlap(self, entity1, entity2):
        """Check if two entities overlap in text position"""
        return not (entity1['end'] <= entity2['start'] or entity2['end'] <= entity1['start'])
    
    def extract_entities(self, text):
        """Main method: Extract entities using hybrid approach"""
        if not text or not text.strip():
            print("Empty text provided to NER")
            return {
                'SYMPTOM': [],
                'MEDICATION': [],
                'DISEASE': [],
                'PROCEDURE': [],
                'ANATOMY': []
            }
        
        # Extract using both methods
        ml_entities = self.extract_entities_ml(text)
        rule_entities = self.extract_entities_rules(text)
        
        # Merge and return
        merged_entities = self.merge_entities(ml_entities, rule_entities)
        
        # Add statistics
        total_ml = len(ml_entities)
        total_rules = len(rule_entities)
        total_merged = sum(len(ent_list) for ent_list in merged_entities.values())
        
        print(f"Extraction Summary for text: {text[:50]}...")
        print(f"  ML entities: {total_ml}")
        print(f"  Rule-based entities: {total_rules}")
        print(f"  Final merged entities: {total_merged}")
        
        return merged_entities
