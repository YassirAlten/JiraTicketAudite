import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold, cross_val_score,GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from preprocessing import preprocess_data_model2, preprocess_data_model3 , preprocess_data_model5
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm


def train_content_quality_model1 (json_path):
    
    df_raw = pd.read_json(json_path)

    df_raw = df_raw.fillna("")
    df_processed= preprocess_data_model5(df_raw)

    df_processed = df_processed.fillna("")

    feature_cols=[
        #  'clean_description',
        'mandatory_keywords',
        'niceToHave_keywords',
        # 'mandatory_available_keywords',
        # 'niceToHave_available_keywords',
        # 'mandatory_present_keywords',
        # 'niceToHave_present_keywords'
    ]

    X=df_processed[feature_cols]
    Y=df_processed['description_quality_score']

    X_train , X_test ,Y_train,Y_test =train_test_split(X,Y,test_size=0.2,random_state=42)

    preprocessor=ColumnTransformer(
        transformers=[
            ('numeric_features', Pipeline([
                ('scaler', StandardScaler()),
                ('passthrough', 'passthrough')
            ]), [
                'mandatory_keywords',
                'niceToHave_keywords',
                # 'mandatory_available_keywords',
                # 'niceToHave_available_keywords',
                # 'mandatory_present_keywords',
                # 'niceToHave_present_keywords'
               
            ])
        ]
    )

    model_pipeline=Pipeline(steps=[
        ('preprocessor',preprocessor),
        ('classifier',RandomForestRegressor(n_estimators=300,
                                            criterion='absolute_error',
                                            max_depth=10,
                                            min_samples_leaf=1,
                                            random_state=42,
                                            n_jobs=-1 
                                            ))
    ])
   
    param_grid={
        'classifier__n_estimators': [200,300,400,500],
        'classifier__max_depth': [5, 10, 15],
        'classifier__min_samples_leaf':[1,2,3]
    }
    grid=GridSearchCV(model_pipeline,param_grid=param_grid,verbose=3)
    grid.fit(X_train,Y_train)
    kf=KFold(n_splits=5,shuffle=True,random_state=42)

    r2_scores = cross_val_score(model_pipeline,X,Y ,cv=kf,scoring='r2')
    mae_scores= -cross_val_score(model_pipeline,X ,Y,cv=kf,scoring='neg_mean_absolute_error')

    
    print(f"Mean Absolute Error (MAE): {mae_scores.mean():.3f}")
    print(f"R² Score: {np.round(r2_scores ,3)}")
    print(f"{r2_scores.mean():.3f}({r2_scores.std():.3f})")

    # feature_names = model_pipeline.named_steps['preprocessor'].get_feature_names_out()

    # importances = model_pipeline.named_steps['classifier'].feature_importances_

    # # Structure data into a clean, queryable DataFrame
    # importance_df = pd.DataFrame({
    #     'Feature': feature_names,
    #     'Importance': importances
    # }).sort_values(by='Importance', ascending=False)

    # # Isolate top 15 indicator terms
    # top_15_features = importance_df.head(15).iloc[::-1]  # Reverse for clean horizontal presentation

    # # --- 5. VISUALIZATION ---
    # plt.figure(figsize=(10, 6))
    # plt.barh(top_15_features['Feature'], top_15_features['Importance'], color='#1f77b4', edgecolor='none')
    # plt.xlabel('Relative Feature Importance Metric', fontsize=11, fontweight='bold')
    # plt.ylabel('Extracted Text Tokens / Bigrams', fontsize=11, fontweight='bold')
    # plt.title('Top 15 Predictive Text Features driving Quality Evaluation Model', fontsize=13, fontweight='bold', pad=15)
    # plt.grid(axis='x', linestyle='--', alpha=0.5)
    # plt.tight_layout()

    # # Render output canvas
    # plt.show()

    joblib.dump(model_pipeline,"ml_engine/saved_models/text_quality_model6.joblib")
    return model_pipeline

def train_content_quality_model2 (json_path):
    
    df_raw = pd.read_json(json_path)

    df_raw = df_raw.fillna("")
    df_processed= preprocess_data_model3(df_raw)

    df_processed = df_processed.fillna("")

    X_text=df_processed['clean_description']
    y=df_processed['is_description_content_good']
    X_train , X_test ,Y_train,Y_test =train_test_split(X_text,y,test_size=0.2,random_state=42)


    vectorisor=TfidfVectorizer(ngram_range=(1,3),analyzer='char_wb',sublinear_tf=True)
    X=vectorisor.fit_transform(X_train)

    joblib.dump(vectorisor,"ml_engine/saved_models/vectorisor_model7.joblib")
    model_pipeline=MLPClassifier(hidden_layer_sizes=(32,16),activation='relu',solver='lbfgs',max_iter=500,random_state=42)
    param_grid={
        'hidden_layer_sizes': [(32,16),(50,25)],
        'max_iter': [250,500,750,1000]
    }
    grid=GridSearchCV(model_pipeline,param_grid=param_grid,verbose=3)
    grid.fit(X,Y_train)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    accuracy_scores = cross_val_score(model_pipeline, X, Y_train, cv=kf, scoring='accuracy')
    f1_scores = cross_val_score(model_pipeline, X, Y_train, cv=kf, scoring='f1')

    print(f"CV Accuracy par pli : {np.round(accuracy_scores, 3)}")
    print(f"Accuracy Moyenne en CV : {accuracy_scores.mean():.3f} (+/- {accuracy_scores.std():.3f})")
    print(f"F1-Score Moyen en CV   : {f1_scores.mean():.3f}")

    joblib.dump(model_pipeline,"ml_engine/saved_models/text_quality_model7.joblib")
    return model_pipeline

if __name__ == "__main__":

    # train_content_quality_model1(r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\test.json')
    train_content_quality_model2(r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\M2_data.json')