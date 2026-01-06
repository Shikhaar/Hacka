import pandas as pd
import numpy as np
import glob
import os
import streamlit as st
from dotenv import load_dotenv

class AadhaarDataLoader:
    """
    Object-Oriented Data Loader for Aadhaar Analytics.
    Encapsulates path management, data ingestion, standardization, and metric calculation.
    """
    def __init__(self):
        load_dotenv()
        # Default to 'Dataset' folder in current directory if env var is not set
        self.dataset_path = os.getenv("DATASET_PATH", "Dataset")
        
        # Check if path exists
        if not os.path.exists(self.dataset_path):
             # Try absolute path fallback or warn
             # For Streamlit Cloud, it will be in root
             pass

    @staticmethod
    def _read_folder(folder_path):
        """Helper to read all CSVs in a folder."""
        if not folder_path or not os.path.exists(folder_path):
            return pd.DataFrame()
        
        all_files = glob.glob(os.path.join(folder_path, "*.csv"))
        if not all_files:
            return pd.DataFrame()
        
        df_list = []
        for filename in all_files:
            try:
                df = pd.read_csv(filename)
                df_list.append(df)
            except Exception as e:
                st.warning(f"Error reading {filename}: {e}")
                
        return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

    @staticmethod
    def _standardize_states(df, state_col='state'):
        """Standardizes state names to a common format."""
        if df.empty:
            return df
        
        state_map = {
            'Orissa': 'Odisha',
            'Pondicherry': 'Puducherry',
            'Delhi': 'NCT of Delhi',
            'Andaman and Nicobar Islands': 'Andaman & Nicobar Islands',
            'Jammu and Kashmir': 'Jammu & Kashmir',
            'Dadra and Nagar Haveli': 'Dadra & Nagar Haveli and Daman & Diu',
            'Daman and Diu': 'Dadra & Nagar Haveli and Daman & Diu',
            'Telengana': 'Telangana'
        }
        
        df[state_col] = df[state_col].astype(str).str.strip()
        df[state_col] = df[state_col].replace(state_map)
        return df

    @st.cache_data
    def get_data(_self):
        """
        Main public method to get the processed dataframe.
        Using `_self` convention to tell Streamlit to ignore the instance for hashing 
        (since it only contains configuration that doesn't change).
        """
        base_path = _self.dataset_path
        bio_path = os.path.join(base_path, "api_data_aadhar_biometric")
        demo_path = os.path.join(base_path, "api_data_aadhar_demographic")
        enrol_path = os.path.join(base_path, "api_data_aadhar_enrolment")
        
        # Load
        df_bio = _self._read_folder(bio_path)
        df_demo = _self._read_folder(demo_path)
        df_enrol = _self._read_folder(enrol_path)
        
        if df_bio.empty or df_enrol.empty:
            st.error("Could not load data. Please check DATASET_PATH.")
            return pd.DataFrame()

        # Standardize
        df_bio = _self._standardize_states(df_bio)
        df_demo = _self._standardize_states(df_demo)
        df_enrol = _self._standardize_states(df_enrol)
        
        # Aggregate
        bio_cols = [c for c in df_bio.columns if c.startswith('bio_age')]
        demo_cols = [c for c in df_demo.columns if c.startswith('demo_age')]
        enrol_cols = [c for c in df_enrol.columns if c.startswith('age_')]
        
        state_bio = df_bio.groupby('state')[bio_cols].sum().reset_index()
        state_demo = df_demo.groupby('state')[demo_cols].sum().reset_index()
        state_enrol = df_enrol.groupby('state')[enrol_cols].sum().reset_index()
        
        # Totals
        state_bio['Total_Biometric'] = state_bio[bio_cols].sum(axis=1)
        state_demo['Total_Demographic'] = state_demo[demo_cols].sum(axis=1)
        state_enrol['Total_Enrolment'] = state_enrol[enrol_cols].sum(axis=1)
        
        # Merge
        df_master = pd.merge(state_enrol[['state', 'Total_Enrolment']], 
                             state_bio[['state', 'Total_Biometric']], on='state', how='outer')
        df_master = pd.merge(df_master, 
                             state_demo[['state', 'Total_Demographic']], on='state', how='outer')
        
        df_master = df_master.fillna(0)
        
        # Derived Metrics
        df_master['Total_Authentications'] = df_master['Total_Biometric'] + df_master['Total_Demographic']
        df_master['Inactivity_Index'] = 1 - (df_master['Total_Authentications'] / df_master['Total_Enrolment'])
        df_master['Inactivity_Index'] = df_master['Inactivity_Index'].replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Z-Scores
        mean_inactivity = df_master['Inactivity_Index'].mean()
        std_inactivity = df_master['Inactivity_Index'].std()
        
        df_master['Z_Score'] = ((df_master['Inactivity_Index'] - mean_inactivity) / std_inactivity).fillna(0)
        df_master['Abs_Z_Score'] = df_master['Z_Score'].abs()
        
        # Clean
        df_master = df_master[~df_master['state'].str.isnumeric()]
        
        return df_master
