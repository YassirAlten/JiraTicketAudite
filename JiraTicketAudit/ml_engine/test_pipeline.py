import pandas as pd
import numpy as np
import re

def preprocess_data_model1 (df):
    #data needed is a textual summary of ticket with an estimation of it's quality score (from 0 to 2)
    df_filtered= df[['summary']]
    df_filtered['clean_summary']=df_filtered['summary'].fillna('EMPTY').str.strip()
    df_filtered['has_prefixe']= df_filtered['clean_summary'].str.contains(r"^\[.*\]|^[^:]+:" , regex=True).astype(int)
    df_filtered['clean_summary2']=df_filtered['clean_summary'].apply(lambda x: re.sub(r'^\[.*?\]\s*' ,'', str(x)))
    df_filtered['summary_lenght']=df_filtered['clean_summary2'].str.len()
    df_filtered['is_lenght_good']= df_filtered['summary_lenght'].between(10,50).astype(int)
    df_filtered=df_filtered[['clean_summary', 'has_prefixe',"summary_lenght",'is_lenght_good']]

    return df_filtered

def preprocess_data_model2(df):
    #data needed is a textual description of tickets and an estimation of the quality score (from 0 to 8)
    df_filtered= df[['description']]
    df_filtered['description']=df_filtered['description'].replace(r'^\s*$' ,np.nan , regex=True)
    df_filtered['clean_description']=df_filtered['description'].fillna('EMPTY').str.strip()
    df_filtered['description_lenght']=df_filtered['clean_description'].str.len()
    df_filtered['is_lenght_good']=df_filtered['description_lenght'].gt(50).astype(int)

    df_filtered['has_scenario_criteria']= df_filtered['clean_description'].str.lower().str.contains(r'(as a | en tant que).*(i want |je veux ).*(so that | afin de)' , regex=True).astype(int)
    df_filtered['has_finishing_crieteria']=df_filtered['clean_description'].str.lower().str.contains(r'(given |étant donné).*(when |quand ).*(then |alors )' , regex=True).astype(int)
    df_filtered=df_filtered[['description', 'description_lenght','is_lenght_good','has_scenario_criteria','has_finishing_crieteria']]

    return df_filtered

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
        "summary":"[auth] fixing authentication endpoint",
        "description":"as a user i want to be able to use jira authentication so that i can access my dashboard . given a mock data when i run a script then it should work",
    },
    {
         "ticket_key":"SCRUM-201",
        "summary":"fixing",
        "description":"fixe db as discusted ",
    }
    ]

if __name__=="__main__":
    df_raw =pd.DataFrame(mock_data)
    df1=preprocess_data_model2(df_raw)
    df2=preprocess_data_model1(df_raw)

    print(df1.to_string(index=False))
    print(df2.to_string(index=False))
