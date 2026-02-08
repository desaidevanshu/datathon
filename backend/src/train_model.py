
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import sys
import os
import joblib

# Add src to path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.data_loader import load_traffic_data
from src.novelty_engine import HybridNoveltyEngine

def train_and_evaluate():
    # Define dataset paths
    base_dir = r"c:/Users/Devanshu/OneDrive/Documents/datathon"
    files = [
        os.path.join(base_dir, "all_features_traffic_dataset.csv"),
        os.path.join(base_dir, "smart_mobility_dataset.csv"),
        os.path.join(base_dir, "urban_traffic_flow_with_target.csv")
    ]
    
    print("Loading and Unifying Datasets...")
    try:
        df = load_traffic_data(files)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Unified Data Shape: {df.shape}")
    print(df.head())
    
    # 1. Feature Engineering (Basic)
    # Convert Timestamp to Hour/Day
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
        df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        df = df.drop(columns=['Timestamp'])
    
    # Define Target
    target_col = 'CongestionLevel'
    if target_col not in df.columns:
        print("Error: Target column 'CongestionLevel' not found.")
        return
        
    # Describe Canonical Features
    canonical_cols = [
        'VehicleCount', 'Speed', 'WeatherCondition', 
        'Hour', 'DayOfWeek', 'IsWeekend', 
        'Latitude', 'Longitude',
        'CongestionLevel' # Target
    ]
    
    # Filter DF to only these columns (if they exist)
    # We want to be strict to ensure model portability
    existing_canonical = [c for c in canonical_cols if c in df.columns]
    print(f"Using Canonical Features: {existing_canonical}")
    df = df[existing_canonical]
    
    # Drop rows with missing target
    df = df.dropna(subset=[target_col])
    
    # Separate Features and Target
    X = df.drop(columns=[target_col], errors='ignore')
    y = df[target_col]
    
    # Identify Column Types
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    print(f"Numerical Features: {numerical_cols}")
    print(f"Categorical Features: {categorical_cols}")
    
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 2. Novelty Detection (Hybrid Engine)
    print("\nTraining Hybrid Novelty Engine...")
    novelty_engine = HybridNoveltyEngine(contamination=0.05)
    
    # Fit on numerical features of training data (imputed)
    # We need a temp imputed version for Isolation Forest
    imputer = SimpleImputer(strategy='mean')
    X_train_num = imputer.fit_transform(X_train[numerical_cols])
    novelty_engine.fit(X_train_num)
    
    # Generate Novelty Scores to use as a Feature
    # (Higher score = more likely to be outlier/mismatch)
    print("Generating Novelty Scores as features...")
    X_train['NoveltyScore'] = novelty_engine.get_novelty_score(X_train_num)
    
    X_test_num = imputer.transform(X_test[numerical_cols])
    X_test['NoveltyScore'] = novelty_engine.get_novelty_score(X_test_num)
    
    # Update numerical columns list
    numerical_cols.append('NoveltyScore')
    
    # 3. Main Model Training
    print("\nTraining Traffic Prediction Model...")
    
    # Preprocessing Pipeline
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )
    
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    clf.fit(X_train, y_train)
    
    # 4. Evaluation
    print("\nEvaluating Model...")
    y_pred = clf.predict(X_test)
    
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Check Novelty on Test Set (How many 'New' samples?)
    novel_mask = X_test['NoveltyScore'] > 0.7 # threshold
    num_novel = novel_mask.sum()
    print(f"\nNovel/Mismatch Samples in Test Set: {num_novel} out of {len(X_test)}")
    if num_novel > 0:
        print(f"Accuracy on Novel Samples: {accuracy_score(y_test[novel_mask], y_pred[novel_mask]):.4f}")
        print(f"Accuracy on Normal Samples: {accuracy_score(y_test[~novel_mask], y_pred[~novel_mask]):.4f}")
        
    # Save Model
    joblib.dump(clf, "traffic_model.pkl")
    joblib.dump(novelty_engine, "novelty_engine.pkl")
    print("\nModels saved to traffic_model.pkl and novelty_engine.pkl")

if __name__ == "__main__":
    train_and_evaluate()
