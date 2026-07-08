import numpy as np
import pandas as pd
from sqlalchemy import create_engine


engine = create_engine('sqlite:///db.sqlite3')
df1=pd.read_sql_table('select * from jira_summarytrainingdata', con=engine)
df2=pd.read_sql_table('select * from jira_descriptiontrainingdata', con=engine)
df3=pd.read_sql_table('select * from jira_prioritytrainingdata', con=engine)

def preprocess_data_model1 (df):
    #data needed is a textual summary of ticket with an estimation of it's quality score (from 0 to 2)
    pass

def preprocess_data_model2(df):
    #data needed is a textual description of tickets and an estimation of the quality score (from 0 to 8)
    pass


def preprocess_data_model3(df):
    # data needed is a numerically configured priority of the ticket and a starting date and a rating of the 
    # logical relation between the first two (between 0 and 4)
    df['priority']= df['priority'].map({'Highest': 5, 'High': 4, 'Medium': 3, 'Low': 2, 'Lowest': 1})
    df['start_date']= pd.to_datetime(df['start_date'])