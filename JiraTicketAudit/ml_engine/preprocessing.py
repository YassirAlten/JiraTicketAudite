import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import re
import json



engine = create_engine('sqlite:///db.sqlite3')
query = """
SELECT * 
FROM jira_JiraTicket a 
JOIN ConfigurationData b 
  ON a.project = b.coefficient.project.id
"""

df1 = pd.read_sql_query(query, con=engine)


def preprocess_data_model1 (df):
    #data needed is a textual summary of ticket with an estimation of it's quality score
    df_filtered= df[['summary','summary_quality_score','ticket_type']]
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
        row_text = str(row['clean_summary']).lower()
        
        config_dict = row['parsed_config']  
        
        desc_block = config_dict.get('summary', {}) 

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
        'description', 'description_lenght', 'is_lenght_good',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords'
    ]
    return df_filtered[final_cols]

def preprocess_data_model2(df1):
    df_filtered = df1[['description','ticket_type','description_quality_score', 'configuration_json']].copy()

    df_filtered['description'] = df_filtered['description'].replace(r'^\s*$', np.nan, regex=True)
    df_filtered['clean_description'] = df_filtered['description'].fillna('EMPTY').str.strip()
    df_filtered['description_lenght'] = df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good'] = df_filtered['description_lenght'].gt(50).astype(int)

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
        'description', 'description_lenght', 'is_lenght_good',
        'mandatory_available_keywords', 'mandatory_present_keywords',
        'niceToHave_available_keywords', 'niceToHave_present_keywords'
    ]
    return df_filtered[final_cols]

def preprocess_data_model3(df):
    # data needed is a numerically configured priority of the ticket and a starting date and a rating of the 
    # logical relation between the first two 
    df_filtered= df[['priority','start_date','startingDate_priority_logical_relation_score']]
    df_filtered['priority']= df_filtered['priority'].map({'Highest': 5, 'High': 4, 'Medium': 3, 'Low': 2, 'Lowest': 1})
    df_filtered['start_date']= pd.to_datetime(df_filtered['start_date'])

    return df_filtered

def preprocess_data_model4(df):
    #data needed is a number of days estimated to complete a ticket and story points and a rating of the logical relation between them
    df_filtered=df[['estimated_time','start_date','story_point','storyPoint_estimatedTime_logical_relation_score']]
    df_filtered['estimated_time']=pd.to_datetime(df_filtered['estimated_time'])
    df_filtered['start_date']=pd.to_datetime(df_filtered['start_date'])
    df_filtered['duration_estimate']=df_filtered['estimated_time']-df_filtered['start_date']
    df_filtered['duration_estimate']=df_filtered['duration_estimate'].dt.total_seconds() / 3600

    return df_filtered