import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def generate_synthetic_cyberbullying_data(n_samples=10000):
    """Generate synthetic cyberbullying data for training"""
    
    np.random.seed(42)
    
    # Features: text length, threat words count, negative words, etc.
    data = []
    
    for i in range(n_samples):
        # Generate random features
        text_length = np.random.randint(10, 500)
        threat_word_count = np.random.poisson(2)
        negative_word_count = np.random.poisson(3)
        caps_ratio = np.random.beta(2, 5)
        exclamation_count = np.random.poisson(1)
        
        # Determine label (cyberbullying or not)
        is_bullying = (
            (threat_word_count > 3) or 
            (negative_word_count > 5) or 
            (caps_ratio > 0.7 and exclamation_count > 2)
        )
        
        # Add some noise
        if np.random.random() < 0.1:
            is_bullying = not is_bullying
        
        data.append([
            text_length,
            threat_word_count,
            negative_word_count,
            caps_ratio,
            exclamation_count,
            int(is_bullying)
        ])
    
    columns = ['text_length', 'threat_words', 'negative_words', 'caps_ratio', 'exclamations', 'is_cyberbullying']
    return pd.DataFrame(data, columns=columns)

def train_cyberbullying_model():
    """Train cyberbullying detection model"""
    print("Generating synthetic data...")
    df = generate_synthetic_cyberbullying_data()
    
    print(f"Dataset shape: {df.shape}")
    print(f"Cyberbullying cases: {df['is_cyberbullying'].sum()}")
    
    # Split features and target
    X = df.drop('is_cyberbullying', axis=1)
    y = df['is_cyberbullying']
    
    # Split train-test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save model
    model_filename = '../models/cyberbullying_model.pkl'
    with open(model_filename, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {model_filename}")
    
    return model, accuracy

def train_threat_detection_model():
    """Train threat detection model"""
    # Similar implementation for threat detection
    pass

if __name__ == "__main__":
    print("=" * 60)
    print("AI Cyber Safety - ML Model Training")
    print("=" * 60)
    
    # Train cyberbullying model
    print("\n1. Training Cyberbullying Detection Model")
    model, accuracy = train_cyberbullying_model()
    
    print("\n2. Training Threat Detection Model")
    # threat_model = train_threat_detection_model()
    
    print("\n3. Saving model metadata...")
    metadata = {
        'training_date': datetime.now().isoformat(),
        'cyberbullying_model_accuracy': float(accuracy),
        'features_used': ['text_length', 'threat_words', 'negative_words', 'caps_ratio', 'exclamations'],
        'model_type': 'RandomForestClassifier',
        'version': '1.0.0'
    }
    
    with open('../models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n✅ Training completed successfully!")
