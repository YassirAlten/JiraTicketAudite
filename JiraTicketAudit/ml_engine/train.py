import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from preprocessing import preprocess_data_model2
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

def train_content_quality_model1 (json_path):
    df_raw = pd.read_json(json_path)

    df_raw = df_raw.fillna("")
    df_processed= preprocess_data_model2(df_raw)

    df_processed = df_processed.fillna("")

    feature_cols=[
        'clean_description',
        'description_lenght',
        'is_lenght_good',
        'mandatory_available_keywords',
        'mandatory_present_keywords',
        'niceToHave_available_keywords',
        'niceToHave_present_keywords'
    ]

    X=df_processed[feature_cols]
    Y=df_processed['description_quality_score']

    X_train , X_test ,Y_train,Y_test =train_test_split(X,Y,test_size=0.2,random_state=42)

    preprocessor=ColumnTransformer(
        transformers=[
            ('text_tfidf',TfidfVectorizer(max_features=500 , ngram_range=(1,2)) , 'clean_description'),
            ('numeric_features', Pipeline([
                ('scaler', StandardScaler()),
                ('passthrough', 'passthrough')
            ]), [
                'description_lenght',
                'is_lenght_good',
                'mandatory_available_keywords',
                'mandatory_present_keywords',
                'niceToHave_available_keywords',
                'niceToHave_present_keywords'
            ])
        ]
    )

    model_pipeline=Pipeline(steps=[
        ('preprocessor',preprocessor),
        ('classifier',RandomForestRegressor(n_estimators=250,
                                            criterion='absolute_error',
                                            max_depth=None,
                                            min_samples_leaf=1,
                                            random_state=42))
    ])

   

    model_pipeline.fit(X_train,Y_train)
    predictions = model_pipeline.predict(X_test)
    mae = mean_absolute_error(Y_test, predictions)
    r2 = r2_score(Y_test, predictions)
    
    print(f"Mean Absolute Error (MAE): {mae:.3f}")
    print(f"R² Score: {r2:.2f}")

    joblib.dump(model_pipeline,"ml_engine/saved_models/text_quality_model5.joblib")
    return model_pipeline

if __name__ == "__main__":
    train_content_quality_model1(r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\m_data.json')