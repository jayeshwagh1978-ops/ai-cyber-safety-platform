import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List, Tuple, Any
import pickle
import json
import joblib
from datetime import datetime
import re
from collections import Counter

class AIModelManager:
    """Manages all ML models for cyber safety prediction"""
    
    _instance = None
    
    def __init__(self):
        self.threat_model = None
        self.cyberbullying_model = None
        self.anomaly_model = None
        self.escalation_model = None
        self.scaler = StandardScaler()
        self.language_models = {}
        
    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load_models()
        return cls._instance
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Load threat detection model
            with open('ml_models/models/threat_detection_model.pkl', 'rb') as f:
                self.threat_model = pickle.load(f)
            
            # Load cyberbullying model
            with open('ml_models/models/cyberbullying_model.pkl', 'rb') as f:
                self.cyberbullying_model = pickle.load(f)
            
            # Load anomaly detection model
            self.anomaly_model = IsolationForest(contamination=0.1, random_state=42)
            
            # Load escalation prediction model
            self.escalation_model = self._build_escalation_model()
            
            # Load language models for 12 Indian languages
            self._load_language_models()
            
        except FileNotFoundError:
            print("Models not found, training new models...")
            self.train_models()
    
    def _build_escalation_model(self):
        """Build LSTM model for escalation prediction"""
        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True, input_shape=(10, 20)),
            keras.layers.Dropout(0.3),
            keras.layers.LSTM(64),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        return model
    
    def analyze_text(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Analyze text for threats and cyberbullying"""
        
        # Feature extraction
        features = self._extract_text_features(text, language)
        
        # Predict threat level
        threat_prob = self.threat_model.predict_proba([features])[0][1] if self.threat_model else 0.5
        
        # Predict cyberbullying
        bullying_prob = self.cyberbullying_model.predict_proba([features])[0][1] if self.cyberbullying_model else 0.5
        
        # Detect anomalies
        anomaly_score = self.anomaly_model.decision_function([features])[0] if self.anomaly_model else 0
        
        # Calculate risk score (0-100)
        risk_score = (threat_prob * 0.4 + bullying_prob * 0.4 + (1 - anomaly_score) * 0.2) * 100
        
        # Predict escalation
        escalation_pred = self.predict_escalation(features)
        
        return {
            'risk_score': round(risk_score, 2),
            'threat_probability': round(threat_prob, 4),
            'bullying_probability': round(bullying_prob, 4),
            'anomaly_score': round(anomaly_score, 4),
            'escalation_predicted': escalation_pred > 0.7,
            'escalation_probability': round(escalation_pred, 4),
            'key_indicators': self._extract_indicators(text, language),
            'recommended_action': self._get_recommendation(risk_score, escalation_pred)
        }
    
    def _extract_text_features(self, text: str, language: str) -> List[float]:
        """Extract features from text for ML models"""
        
        features = []
        
        # Basic text features
        features.append(len(text))  # Text length
        features.append(len(text.split()))  # Word count
        features.append(len(set(text.split())) / max(len(text.split()), 1))  # Unique word ratio
        
        # Threat indicators
        threat_words = self._get_threat_keywords(language)
        threat_count = sum(1 for word in text.lower().split() if word in threat_words)
        features.append(threat_count)
        features.append(threat_count / max(len(text.split()), 1))
        
        # Sentiment features (simplified)
        positive_words = ['good', 'happy', 'great', 'love', 'like']
        negative_words = ['bad', 'hate', 'kill', 'hurt', 'danger']
        
        pos_count = sum(1 for word in text.lower().split() if word in positive_words)
        neg_count = sum(1 for word in text.lower().split() if word in negative_words)
        
        features.append(pos_count)
        features.append(neg_count)
        features.append(neg_count - pos_count)
        
        # Capitalization ratio (shouting detection)
        caps_count = sum(1 for char in text if char.isupper())
        features.append(caps_count / max(len(text), 1))
        
        # Exclamation/question marks
        features.append(text.count('!'))
        features.append(text.count('?'))
        
        # Repeated characters
        repeated = sum(1 for i in range(len(text)-2) if text[i] == text[i+1] == text[i+2])
        features.append(repeated)
        
        return features
    
    def _get_threat_keywords(self, language: str) -> set:
        """Get threat keywords for different languages"""
        
        keywords = {
            'en': {'kill', 'hurt', 'die', 'threat', 'harm', 'danger', 'attack'},
            'hi': {'मार', 'चोट', 'खतरा', 'हानि', 'धमकी'},  # Hindi
            'ta': {'கொல்', 'காயம்', 'அபாயம்', 'தீங்கு'},  # Tamil
            'te': {'చంపు', 'గాయం', 'ప్రమాదం', 'నష్టం'},  # Telugu
            'ml': {'കൊല്ലുക', 'പരിക്ക്', 'അപകടം', 'നഷ്ടം'},  # Malayalam
            'kn': {'ಕೊಲ್ಲು', 'ಗಾಯ', 'ಅಪಾಯ', 'ನಷ್ಟ'},  # Kannada
            'mr': {'मार', 'इजा', 'धोका', 'नुकसान'},  # Marathi
            'bn': {'হত্যা', 'আঘাত', 'বিপদ', 'ক্ষতি'},  # Bengali
            'gu': {'મારી', 'ઈજા', 'ખતરો', 'નુકસાન'},  # Gujarati
            'pa': {'ਮਾਰ', 'ਚੋਟ', 'ਖਤਰਾ', 'ਨੁਕਸਾਨ'},  # Punjabi
            'or': {'ମାର', 'ଆଘାତ', 'ବିପଦ', 'କ୍ଷତି'},  # Odia
            'ur': {'مار', 'چوٹ', 'خطرہ', 'نقصان'}  # Urdu
        }
        
        return keywords.get(language, keywords['en'])
    
    def predict_escalation(self, features: List[float]) -> float:
        """Predict escalation probability"""
        if self.escalation_model:
            # Reshape features for LSTM
            features_reshaped = np.array(features).reshape(1, -1, 1)
            # Pad if necessary
            if features_reshaped.shape[1] < 10:
                padding = np.zeros((1, 10 - features_reshaped.shape[1], 1))
                features_reshaped = np.concatenate([features_reshaped, padding], axis=1)
            elif features_reshaped.shape[1] > 10:
                features_reshaped = features_reshaped[:, :10, :]
            
            prediction = self.escalation_model.predict(features_reshaped)[0][0]
            return float(prediction)
        return 0.5
    
    def _extract_indicators(self, text: str, language: str) -> List[str]:
        """Extract key threat indicators"""
        indicators = []
        text_lower = text.lower()
        
        # Threat indicators
        if any(word in text_lower for word in ['kill', 'murder', 'harm']):
            indicators.append('Violent language detected')
        
        if any(word in text_lower for word in ['die', 'suicide', 'end life']):
            indicators.append('Self-harm references detected')
        
        if text_lower.count('!') > 3:
            indicators.append('Excessive exclamation marks')
        
        if sum(1 for char in text if char.isupper()) / len(text) > 0.5:
            indicators.append('Excessive capitalization (shouting)')
        
        return indicators
    
    def _get_recommendation(self, risk_score: float, escalation_prob: float) -> str:
        """Get recommendation based on risk"""
        if risk_score > 80 or escalation_prob > 0.8:
            return 'IMMEDIATE_ESCALATION'
        elif risk_score > 60:
            return 'SCHEDULE_POLICE_REVIEW'
        elif risk_score > 40:
            return 'MONITOR_CLOSELY'
        else:
            return 'SAFE_ZONE'
    
    def train_models(self):
        """Train models on synthetic data"""
        # This would be called from training scripts
        pass
