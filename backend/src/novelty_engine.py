
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os
try:
    from scraper import get_event_impact_score
except ImportError:
    # Fallback if scraper not found in path
    def get_event_impact_score(city): return 0.0

class HybridNoveltyEngine:
    def __init__(self, contamination=0.05):
        self.iso_forest = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
        
    def fit(self, X):
        """
        Fits the statistical anomaly detector.
        X: DataFrame or 2D array of numerical features.
        """
        print("Fitting Isolation Forest for Novelty Detection...")
        self.iso_forest.fit(X)
        self.is_fitted = True
        
    def get_novelty_score(self, X, context_data=None):
        """
        Returns a hybrid novelty score (0 to 1).
        Higher score = More Novel / Mismatch likely.
        
        X: Feature samples
        context_data: Optional dict with 'city', 'timestamp' etc.
        """
        if not self.is_fitted:
            raise ValueError("Engine must be fitted before prediction.")
            
        # 1. Statistical Score (Isolation Forest)
        # decision_function returns negative for outliers, positive for inliers.
        # We invert it: Lower (more negative) = Higher Anomaly Score.
        raw_scores = self.iso_forest.decision_function(X)
        
        # Normalize to roughly 0-1 (Sigmoid or MinMax approximation)
        # score < 0 is anomaly. range usually -0.5 to 0.5
        stat_score = 1 / (1 + np.exp(raw_scores * 10)) # Sigmoid-ish
        
        # 2. Contextual Score (External Events)
        context_score = 0.0
        if context_data and 'city' in context_data:
            context_score = get_event_impact_score(context_data['city'])
            
        # 3. Hybrid Combination (Weighted)
        # If stat anomaly is high, it dominates. If event is high, it adds up.
        final_score = 0.7 * stat_score + 0.3 * context_score
        
        return final_score

    def is_novel(self, X, threshold=0.7):
        scores = self.get_novelty_score(X)
        return scores > threshold

    def save(self, path):
        joblib.dump(self.iso_forest, path)
        
    def load(self, path):
        self.iso_forest = joblib.load(path)
        self.is_fitted = True
