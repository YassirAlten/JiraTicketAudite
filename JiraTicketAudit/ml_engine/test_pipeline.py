import pandas as pd
import numpy as np
import re
import json

def preprocess_data_model1 (df):
    #data needed is a textual summary of ticket with an estimation of it's quality score
    df_filtered= df[['summary','ticket_type','configuration_json']]
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
    df_filtered = df1[['description','ticket_type', 'configuration_json']].copy()

    # 2. Nettoyage de la description du ticket
    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('EMPTY').str.strip()
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
                    
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
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
                    if re.search(r'\b' + re.escape(keyword) + r'\b', row_text):
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
        'description', 'description_lenght', 'is_lenght_good',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords'
    ]
    return df_filtered[final_cols]


def preprocess_data_model3(df):
    # data needed is a numerically configured priority of the ticket and a starting date and a rating of the 
    # logical relation between the first two (between 0 and 4)
    df_filtered= df[['priority','start_date','startingDate_priority_logical_relation_score']]
    df_filtered['priority']= df_filtered['priority'].map({'Highest': 5, 'High': 4, 'Medium': 3, 'Low': 2, 'Lowest': 1})
    df_filtered['start_date']= pd.to_datetime(df_filtered['start_date'])

    return df_filtered

def preprocess_data_model4(df):
    #data needed is a number of days estimated to complete a ticket and story points and a rating of the logical relation between them
    df_filtered=df[['estimated_time','start_date','story_point']]
    df_filtered['estimated_time']=pd.to_datetime(df_filtered['estimated_time'])
    df_filtered['start_date']=pd.to_datetime(df_filtered['start_date'])
    df_filtered['duration_estimate']=df_filtered['estimated_time']-df_filtered['start_date']
    df_filtered['duration_estimate']=df_filtered['duration_estimate'].dt.total_seconds() / 3600

    return df_filtered

mock_data=[
    {
        "ticket_key":"SCRUM-200",
        "ticket_type":"bug",
        "summary":"[auth]task fixing authentication os",
        "description":"bug task steps clear_instructions browser logs recordings",
        "configuration_json":"""
            {
            "description": {
                "bug":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                },
                "epic":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                }
                
            },
            "summary": {
                "bug":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                },
                "epic":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                }
                
            }
    }"""

    },
    {
        "ticket_key":"SCRUM-200",
        "ticket_type":"epic",
        "summary":"[auth] fixing authentication endpoint",
        "description":"bug  steps clear_instructions browser  recordings",
        "configuration_json":"""
            {
            "description": {
                "bug":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                },
                "epic":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                }
                
            },
            "summary": {
                "bug":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                },
                "epic":{
                    "mandatory_fields": {
                    "issue_type": "bug, task, story",
                    "steps_to_reproduce": "steps, reproduction, clear_instructions"
                    },
                    "niceToHave_fields": {
                    "environment_details": "browser, os, version",
                    "attachments": "screenshots, logs, recordings"
                    }
                }
                
            }
    }"""

    },
    ]

if __name__=="__main__":
    df_raw =pd.DataFrame(mock_data)
    df1=preprocess_data_model2(df_raw)
    df2=preprocess_data_model1(df_raw)


    print(df1.to_string(index=False))
    print(df2.to_string(index=False))

