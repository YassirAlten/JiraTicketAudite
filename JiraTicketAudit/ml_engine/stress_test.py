import random
import re
import numpy as np
import pandas as pd
import joblib
import difflib
import json

def find_keyword_with_typos(text, keyword, threshold=0.75):
    
    words = text.lower().split()
    keyword = keyword.lower()
    
    kw_len = len(keyword.split())
    if kw_len > 1:
        for i in range(len(words) - kw_len + 1):
            phrase = " ".join(words[i:i+kw_len])
            ratio = difflib.SequenceMatcher(None, phrase, keyword).ratio()
            if ratio >= threshold:
                return True
        return False
    else:
        for word in words:
            word = word.strip(":,.;!?")
            ratio = difflib.SequenceMatcher(None, word, keyword).ratio()
            if ratio >= threshold:
                return True
        return False

def preprocess_data_model5(df1):
    df_filtered = df1[['description','ticket_type', 'configuration_json']]

    # 2. Nettoyage de la description du ticket
    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
   

    def nettoyer_et_charger_json(val):
        
        try:
            return json.loads(str(val))
        except (json.JSONDecodeError, TypeError):
            return {"description": {"mandatory_fields": "", "niceToHave_fields": ""}}

    df_filtered['parsed_config'] = df_filtered['configuration_json'].apply(nettoyer_et_charger_json)

    m_list = []
    n_list = []

    for index, row in df_filtered.iterrows():
        row_text = str(row['clean_description']).lower()
        
        config_dict = row['parsed_config']  
        
        desc_block = config_dict.get('description', {}) 

        ticket_type=desc_block.get(row['ticket_type'],{})

        
       
        mandatory_fields = ticket_type.get('mandatory_fields', {})
        niceToHave_fields = ticket_type.get('niceToHave_fields', {})

        m_keyword_count = 0
        m_available_keywords_count = 0
        if isinstance(mandatory_fields, dict):
            for k, v in mandatory_fields.items():
                keywords = [kw.strip().lower() for kw in str(v).split(',') if kw.strip()]
                
                m_available_keywords_count += len(keywords)
                for keyword in keywords:
                    
                    if find_keyword_with_typos(row_text,keyword):
                        m_keyword_count += 1

        if m_available_keywords_count != 0 :
            m_list.append(m_keyword_count/m_available_keywords_count)
        else:
            m_list.append(0)
        

        n_keyword_count = 0
        n_available_keywords_count = 0
        if isinstance(niceToHave_fields, dict):
            for k, v in niceToHave_fields.items():
                keywords = [kw.strip().lower() for kw in str(v).split(',') if kw.strip()]
                n_available_keywords_count += len(keywords)
                for keyword in keywords:
                    if find_keyword_with_typos(row_text,keyword):
                        n_keyword_count += 1
                
        if n_available_keywords_count != 0 :
            n_list.append(n_keyword_count/n_available_keywords_count)
        else:
            n_list.append(0)
  

    df_filtered['mandatory_keywords'] = m_list
    df_filtered['niceToHave_keywords'] = n_list
    
            
    final_cols = [
        'clean_description',
        # 'description_lenght', 'is_lenght_good',
        'mandatory_keywords', 'niceToHave_keywords',
    ]
    return df_filtered[final_cols]
def preprocess_data_model3(df1):
    df_filtered = df1[['description']]

    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    # df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    # df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
      
    final_cols = [
        'clean_description'
    ]
    return df_filtered[final_cols]

def introduce_typos(text):
    """Randomly duplicates or drops characters to simulate human typos."""
    if not isinstance(text, str) or not text:
        return ""
    words = text.split()
    processed_words = []
    for word in words:
        if len(word) > 4 and random.random() < 0.15:  
            idx = random.randint(1, len(word) - 2)
            if random.random() < 0.5:
                word = word[:idx] + word[idx] * 2 + word[idx+1:]  
            else:
                word = word[:idx] + word[idx+1:]  
        processed_words.append(word)
    return " ".join(processed_words)

def structural_chaos(text):
    """Strips rigid field labels or randomly shuffles block positions."""
    if not isinstance(text, str) or not text:
        return ""
    
    blocks = re.split(r'([A-Za-z\s_-]+:)', text)
    if len(blocks) <= 1:
        return introduce_typos(text)
    
    reconstructed_segments = []
    header = ""
    for segment in blocks:
        if segment.endswith(':'):
            header = segment if random.random() > 0.4 else "" 
        else:
            if segment.strip():
                reconstructed_segments.append(f"{header} {segment.strip()}".strip())
                
    random.shuffle(reconstructed_segments)
    final_text = " ".join(reconstructed_segments)
    
    if random.random() < 0.3:
        final_text = final_text.lower()
        
    return introduce_typos(final_text)

model_path1 = 'ml_engine/saved_models/text_quality_model6.joblib'
model_path2 = 'ml_engine/saved_models/text_quality_model7.joblib'

loaded_pipeline1 = joblib.load(model_path1)
loaded_pipeline2 = joblib.load(model_path2)

# Load test data
json_path = r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\test2.json'
df_raw = pd.read_json(json_path).fillna("")

df_stressed = df_raw.copy()
if 'description' in df_stressed.columns:
    df_stressed['description'] = df_stressed['description'].apply(structural_chaos)


print("Sample of a corrupted text description:")
print(df_stressed['description'])

df_processed1_clean = preprocess_data_model5(df_raw).fillna("")

df_processed1_stressed = preprocess_data_model5(df_stressed).fillna("")
print(df_processed1_stressed)
print(df_processed1_clean)
df_processed2_clean = preprocess_data_model3(df_raw).fillna("")
df_processed2_stressed = preprocess_data_model3(df_stressed).fillna("")


pred1_clean = loaded_pipeline1.predict(df_processed1_clean)
vectorisor= joblib.load('ml_engine/saved_models/vectorisor_model7.joblib')
vectorised_data=vectorisor.transform(df_processed2_clean['clean_description'])
pred2_clean = loaded_pipeline2.predict(vectorised_data)

print(pred1_clean)
print(pred2_clean)

pred1_stressed = loaded_pipeline1.predict(df_processed1_stressed)
vectorised_data2=vectorisor.transform(df_processed2_stressed['clean_description'])
pred2_stressed = loaded_pipeline2.predict(vectorised_data2)

print(pred1_stressed)
print(pred2_stressed)

results_clean = [i * 0.5 + int(j) * 2.5 for i, j in zip(pred1_clean, pred2_clean)]
results_stressed = [i * 0.5 + int(j) * 2.5 for i, j in zip(pred1_stressed, pred2_stressed)]

print(results_clean)
print(results_stressed)

print(f" Total test samples evaluated: {len(df_raw)}")
print(f" Average calculated score on CLEAN data:     {np.mean(results_clean):.3f}")
print(f" Average calculated score on STRESSED data:  {np.mean(results_stressed):.3f}")

drift_count = sum(1 for c, s in zip(results_clean, results_stressed) if abs(c - s) > 0.5)
print(f" Score drift alert: {drift_count} tickets changed final score significantly due to noise.")
