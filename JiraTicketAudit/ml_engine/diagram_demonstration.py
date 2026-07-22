import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # type: ignore[import]
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer  # or CountVectorizer
from sklearn.ensemble import RandomForestRegressor

# --- 1. CONFIGURATION (Your Winning Hyperparameters) ---
# Vectorizer parameters found in your grid search
VECTORIZER_PARAMS = {
    'max_features': 300,
    'min_df': 2,
    'ngram_range': (1, 2)
}

# Random Forest Regressor parameters found in your grid search
MODEL_PARAMS = {
    'n_estimators': 400,
    'criterion': 'absolute_error',
    'max_depth': 10,
    'min_samples_leaf': 1,
    'random_state': 42,
    'n_jobs': -1
}

# --- 2. PIPELINE INITIALIZATION ---
# Using a single text preprocessor step matching your configuration tracking
vectorizer = TfidfVectorizer(**VECTORIZER_PARAMS)
regressor = RandomForestRegressor(**MODEL_PARAMS)

model_pipeline = Pipeline(steps=[
    ('preprocessor', vectorizer),
    ('classifier', regressor)
])

# --- 3. TRAINING & FEATURE EXTRACTION ---
# Assuming 'X_train' is your pandas Series of ticket text blocks (summary + description)
# and 'y_train' is your numeric quality score target.
#
# model_pipeline.fit(X_train, y_train)

# --- 4. FEATURE IMPORTANCE EXTRACTION ---
# Extract feature names from the vectorizer vocabulary layout
feature_names = model_pipeline.named_steps['preprocessor'].get_feature_names_out()

# Extract calculated gini/absolute error importances from the ensemble
importances = model_pipeline.named_steps['classifier'].feature_importances_

# Structure data into a clean, queryable DataFrame
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Isolate top 15 indicator terms
top_15_features = importance_df.head(15).iloc[::-1]  # Reverse for clean horizontal presentation

# --- 5. VISUALIZATION ---
plt.figure(figsize=(10, 6))
plt.barh(top_15_features['Feature'], top_15_features['Importance'], color='#1f77b4', edgecolor='none')
plt.xlabel('Relative Feature Importance Metric', fontsize=11, fontweight='bold')
plt.ylabel('Extracted Text Tokens / Bigrams', fontsize=11, fontweight='bold')
plt.title('Top 15 Predictive Text Features driving Quality Evaluation Model', fontsize=13, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()

# Render output canvas
plt.show()
