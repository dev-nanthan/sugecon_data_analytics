"""data_process.py: Module to process the data as required"""

import pandas as pd
from flask import current_app
from datetime import datetime
import os

def load_data():
    """Function to load the CSV data."""
    current_dir = os.getcwd()
    print("current wdir:", current_dir)
    csv_path = os.path.join(current_dir, 'data', 'data_p1.csv') 
    return pd.read_csv(csv_path)

def filter_data(start_date_str, end_date_str):
    
    """
    Function to filter data based on date range in MM/DD/YYYY format.

    Parameters:
    - start_date_str (str): The start date in MM/DD/YYYY format.
    - end_date_str (str): The end date in MM/DD/YYYY format.

    Returns:
    - DataFrame: Filtered DataFrame.
    """
    data_df = load_data()
    
    # Convert string dates to datetime objects for comparison
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Ensure MDate is in datetime format for proper comparison
    data_df['MDate'] = pd.to_datetime(data_df['MDate'], format='%m/%d/%Y')

    # Filter the dataframe based on the date range
    filtered_df = data_df[(data_df['MDate'] >= start_date) & (data_df['MDate'] <= end_date)]
    return filtered_df



