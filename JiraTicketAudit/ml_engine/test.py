import pandas as pd
import joblib
import json
import re
import numpy as np

def preprocess_data_model5(df1):
    df_filtered = df1[['description','ticket_type', 'configuration_json']]

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
    print(df_filtered['parsed_config'])

    m_list = []
    n_list = []

    for index, row in df_filtered.iterrows():
        row_text = str(row['clean_description']).lower()
        
        config_dict = row['parsed_config']  
        
        # Extraction sécurisée des blocs JSON
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
                    
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
                        m_keyword_count += 1

        m_list.append(m_keyword_count/m_available_keywords_count)
        

        n_keyword_count = 0
        n_available_keywords_count = 0
        if isinstance(niceToHave_fields, dict):
            for k, v in niceToHave_fields.items():
                keywords = [kw.strip().lower() for kw in str(v).split(',') if kw.strip()]
                n_available_keywords_count += len(keywords)
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
                        n_keyword_count += 1
                
        n_list.append(n_keyword_count/n_available_keywords_count)
  

    df_filtered['mandatory_keywords'] = m_list
    df_filtered['niceToHave_keywords'] = n_list
    
            
    final_cols = [
        'clean_description',
        # 'description_lenght', 'is_lenght_good',
        'mandatory_keywords', 'niceToHave_keywords',
        
    ]
    return df_filtered[final_cols]

def preprocess_data_model2(df1):

    df_filtered = df1[['description','ticket_type', 'configuration_json']]

    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
    df_filtered= df_filtered.fillna('')
    

    def nettoyer_et_charger_json(val):
        
        try:
            return json.loads(str(val))
        except (json.JSONDecodeError, TypeError):
            return {"description": {"mandatory_fields": "", "niceToHave_fields": ""}}

    df_filtered['parsed_config'] = df_filtered['configuration_json'].apply(nettoyer_et_charger_json)

    m_available_list = []
    m_present_list = []
    n_available_list = []
    n_present_list = []

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
                    
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
                        m_keyword_count += 1

        m_available_list.append(m_available_keywords_count)
        m_present_list.append(m_keyword_count)

        n_keyword_count = 0
        n_available_keywords_count = 0
        if isinstance(niceToHave_fields, dict):
            for k, v in niceToHave_fields.items():
                keywords = [kw.strip().lower() for kw in str(v).split(',') if kw.strip()]
                n_available_keywords_count += len(keywords)
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
                        n_keyword_count += 1
                
        n_available_list.append(n_available_keywords_count)
        n_present_list.append(n_keyword_count)

    df_filtered['mandatory_available_keywords'] = m_available_list
    df_filtered['mandatory_present_keywords'] = m_present_list
    df_filtered['niceToHave_available_keywords'] = n_available_list
    df_filtered['niceToHave_present_keywords'] = n_present_list

            
    final_cols = [
        'description',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords'
    ]
    return df_filtered[final_cols]


def preprocess_data_model3(df1):
    df_filtered = df1[['description']]

    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    # df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    # df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
      
    final_cols = [
        'clean_description',
    ]
    return df_filtered[final_cols]

model_path1='ml_engine/saved_models/text_quality_model6.joblib'
loaded_pipeline1= joblib.load(model_path1)
model_path2='ml_engine/saved_models/text_quality_model7.joblib'
loaded_pipeline2=joblib.load(model_path2)



df_raw = pd.read_json(r'C:\Users\yjamal\Desktop\JiraTicketAudit\JiraTicketAudite\JiraTicketAudit\ml_engine\test2.json')

df_raw = df_raw.fillna("")
df_processed1= preprocess_data_model5(df_raw)
df_processed2= preprocess_data_model3(df_raw)
df_processed1 = df_processed1.fillna("")
df_processed2=df_processed2.fillna("")

vectorisor=joblib.load("ml_engine/saved_models/vectorisor_model7.joblib")
df2=vectorisor.transform(df_processed2['clean_description'])
print(df2)

prediction1= loaded_pipeline1.predict(df_processed1)
print(prediction1)
prediction2 = loaded_pipeline2.predict(df2)
print(prediction2)
results=[]
for i ,j in zip(prediction1,prediction2):
    result=i*0.5 + float(j)*2.5
    results.append(result)

print(results)