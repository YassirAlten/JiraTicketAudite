import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import re
import json
import difflib



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

def preprocess_data_model1 (df):
    #data needed is a textual summary of ticket with an estimation of it's quality score
    df_filtered= df[['summary','summary_quality_score','ticket_type','configuration_json']]
    df_filtered['clean_summary']=df_filtered['summary'].fillna('EMPTY').str.strip()
    df_filtered['summary_lenght']=df_filtered['clean_summary'].str.len()
    df_filtered['is_lenght_good']= df_filtered['summary_lenght'].between(10,50).astype(int)

    def nettoyer_et_charger_json(val):
        
        try:
            return json.loads(str(val))
        except (json.JSONDecodeError, TypeError):
            return """{"summary":{"tache":{"mandatory_fields": "", "niceToHave_fields": ""},
            {"bug":{"mandatory_fields": "", "niceToHave_fields": ""},
            {"story":{"mandatory_fields": "", "niceToHave_fields": ""},
            {"epic":{"mandatory_fields": "", "niceToHave_fields": ""} }}"""

    df_filtered['parsed_config'] = df_filtered['configuration_json'].apply(nettoyer_et_charger_json)

    m_available_list = []
    m_present_list = []
    n_available_list = []
    n_present_list = []

    for index, row in df_filtered.iterrows():
        row_text = str(row['summary']).lower()
        # print(row_text)
        
        config_dict = row['parsed_config']  
        # print(config_dict)
        summary_block = config_dict.get('summary', {}) 
        print(summary_block)

        ticket_type=summary_block.get(row['ticket_type'],{})
        print(ticket_type)
       
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
        'summary', 'summary_lenght', 'is_lenght_good',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords'
    ]
    return df_filtered[final_cols]

def preprocess_data_model2(df1):

    

    # 1. Sélection et copie pour éviter le SettingWithCopyWarning
    df_filtered = df1[['description','ticket_type', 'configuration_json']]

    # 2. Nettoyage de la description du ticket
    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
    df_filtered= df_filtered.fillna('')
    

    # 3. Fonction de nettoyage de la chaîne de texte JSON (LIGNE PAR LIGNE)
    def nettoyer_et_charger_json(val):
        
        try:
            return json.loads(str(val))
        except (json.JSONDecodeError, TypeError):
            return {"description": {"mandatory_fields": "", "niceToHave_fields": ""}}

    # 4. Application du nettoyage ligne par ligne sur la colonne
    df_filtered['parsed_config'] = df_filtered['configuration_json'].apply(nettoyer_et_charger_json)

    m_available_list = []
    m_present_list = []
    n_available_list = []
    n_present_list = []

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
                    
                    if find_keyword_with_typos(row_text,keyword):
                        m_keyword_count += 1

        m_available_list.append(m_available_keywords_count)
        m_present_list.append(m_keyword_count)

        # --- Traitement des Mots-clés Optionnels ---
        n_keyword_count = 0
        n_available_keywords_count = 0
        if isinstance(niceToHave_fields, dict):
            for k, v in niceToHave_fields.items():
                keywords = [kw.strip().lower() for kw in str(v).split(',') if kw.strip()]
                n_available_keywords_count += len(keywords)
                for keyword in keywords:
                    if find_keyword_with_typos(row_text,keyword):
                        n_keyword_count += 1
                
        n_available_list.append(n_available_keywords_count)
        n_present_list.append(n_keyword_count)

    # 7. Assignation des listes de même longueur aux colonnes
    df_filtered['mandatory_available_keywords'] = m_available_list
    df_filtered['mandatory_present_keywords'] = m_present_list
    df_filtered['niceToHave_available_keywords'] = n_available_list
    df_filtered['niceToHave_present_keywords'] = n_present_list

            
    # 8. Retour des colonnes finales requises
    final_cols = [
        'description',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords','description_quality_score'
    ]
    return df_filtered[final_cols]

def preprocess_data_model3(df1):
    df_filtered = df1[['description','is_description_content_good']]

    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    # df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    # df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
      
    final_cols = [
        'clean_description',
        'is_description_content_good'
    ]
    return df_filtered[final_cols]

def preprocess_data_model4(df):
    #data needed is a number of days estimated to complete a ticket and story points and a rating of the logical relation between them
    df_filtered=df[['estimated_time','start_date','story_point','storyPoint_estimatedTime_logical_relation_score']]
    df_filtered['estimated_time']=pd.to_datetime(df_filtered['estimated_time'])
    df_filtered['start_date']=pd.to_datetime(df_filtered['start_date'])
    df_filtered['duration_estimate']=df_filtered['estimated_time']-df_filtered['start_date']
    df_filtered['duration_estimate']=df_filtered['duration_estimate'].dt.total_seconds() / 3600

    return df_filtered

def preprocess_data_model5(df1):
    # 1. Sélection et copie pour éviter le SettingWithCopyWarning
    df_filtered = df1[['description','ticket_type','description_quality_score', 'configuration_json']]

    # 2. Nettoyage de la description du ticket
    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('')
    df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)
   

    # 3. Fonction de nettoyage de la chaîne de texte JSON (LIGNE PAR LIGNE)
    def nettoyer_et_charger_json(val):
        
        try:
            return json.loads(str(val))
        except (json.JSONDecodeError, TypeError):
            return {"description": {"mandatory_fields": "", "niceToHave_fields": ""}}

    # 4. Application du nettoyage ligne par ligne sur la colonne
    df_filtered['parsed_config'] = df_filtered['configuration_json'].apply(nettoyer_et_charger_json)

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
                    
                    if find_keyword_with_typos(row_text,keyword):
                        m_keyword_count += 1

        if m_available_keywords_count != 0 :
            m_list.append(m_keyword_count/m_available_keywords_count)
        else:
            m_list.append(0)
        

        # --- Traitement des Mots-clés Optionnels ---
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
  

    # 7. Assignation des listes de même longueur aux colonnes
    df_filtered['mandatory_keywords'] = m_list
    df_filtered['niceToHave_keywords'] = n_list
    
            
    # 8. Retour des colonnes finales requises
    final_cols = [
        'clean_description',
        # 'description_lenght', 'is_lenght_good',
        'mandatory_keywords', 'niceToHave_keywords',
        'description_quality_score'
    ]
    return df_filtered[final_cols]