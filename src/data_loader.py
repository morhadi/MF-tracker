import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def scan_excel_files(data_dir: str = "data") -> Dict[str, List[str]]:
    """
    Scan the data directory for Excel files and create a map of fund names to their available months.
    
    Args:
        data_dir (str): Directory containing the Excel files
        
    Returns:
        Dict[str, List[str]]: Map of fund names to sorted list of available months
    """
    fund_month_map = {}
    
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith(('.xlsx', '.xls')):
                try:
                    # Expected format: "ZN250 - Monthly Portfolio September 2024.xlsx"
                    parts = filename.split(' - Monthly Portfolio ')
                    if len(parts) != 2:
                        continue
                        
                    fund_name = parts[0].strip()
                    date_str = parts[1].replace('.xlsx', '').replace('.xls', '').strip()
                    
                    if fund_name not in fund_month_map:
                        fund_month_map[fund_name] = []
                    fund_month_map[fund_name].append(date_str)
                
                except (IndexError, ValueError) as e:
                    print(f"Warning: Could not parse filename {filename}: {str(e)}")
                    continue
        
        # Sort months chronologically for each fund
        for fund in fund_month_map:
            fund_month_map[fund].sort(key=lambda x: datetime.strptime(x, '%B %Y'))
        
    except Exception as e:
        print(f"Error scanning directory {data_dir}: {str(e)}")
    
    return fund_month_map

def load_and_clean_excel_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load and clean data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        Optional[pd.DataFrame]: Cleaned DataFrame or None if loading fails
    """
    try:
        # First read without headers to find the header row
        df_raw = pd.read_excel(file_path, header=None)
        
        # Find the header row by looking for 'ISIN'
        header_row = None
        for idx, row in df_raw.iterrows():
            if 'ISIN' in row.values:
                header_row = idx
                break
        
        if header_row is None:
            print(f"\nCould not find header row in {file_path}")
            return None
            
        # Now read the file again with the correct header row
        df = pd.read_excel(file_path, skiprows=header_row)
        
        # Clean column names (remove extra whitespace and handle unnamed columns)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Rename unnamed columns if they exist
        rename_map = {}
        for col in df.columns:
            if col.startswith('Unnamed:'):
                rename_map[col] = None
        if rename_map:
            df = df.rename(columns=rename_map)
            df = df.drop(columns=[col for col in df.columns if col is None])
        
        print(f"\nFound columns in {file_path}:")
        print(df.columns.tolist())
        
        # Drop rows where ISIN is missing or empty
        df = df.dropna(subset=['ISIN'])
        
        # Drop rows that are section headers or have no data
        df = df[df['ISIN'].str.startswith('INE', na=False)]
        
        # Convert numeric columns
        numeric_cols = ['Quantity', '% to NAV']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Set ISIN as index
        df.set_index('ISIN', inplace=True)
        
        print(f"\nSuccessfully loaded data from {file_path}")
        print(f"Found {len(df)} valid entries")
        print("\nSample of loaded data:")
        # print(df.head())
        
        return df
        
    except Exception as e:
        print(f"\nError loading file {file_path}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def load_data_for_fund_months(fund_name: str, months: List[str], data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """
    Load data for specified fund and months.
    
    Args:
        fund_name (str): Name of the fund
        months (List[str]): List of months to load
        data_dir (str): Directory containing the data files
        
    Returns:
        Dict[str, pd.DataFrame]: Map of months to their corresponding DataFrames
    """
    monthly_data = {}
    
    for month in months:
        # Updated file pattern to match actual format
        file_pattern = f"{fund_name} - Monthly Portfolio {month}.xlsx"
        file_path = os.path.join(data_dir, file_pattern)
        
        print(f"Looking for file: {file_path}")
        if os.path.exists(file_path):
            print(f"Found file: {file_path}")
            df = load_and_clean_excel_data(file_path)
            if df is not None:
                monthly_data[month] = df
        else:
            print(f"File not found: {file_path}")
    
    return monthly_data 

# df = load_and_clean_excel_data("data/ZN250 - Monthly Portfolio September 2024.xlsx") 

# print(df)