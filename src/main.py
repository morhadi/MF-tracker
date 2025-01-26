import os
from typing import List, Dict, Optional, Tuple
import pandas as pd

from user_interface import choose_fund_name_interactive, choose_date_range_interactive
from data_loader import scan_excel_files, load_data_for_fund_months
from data_processor import (
    create_consolidated_dataframe,
    calculate_allocation_changes,
    get_significant_changes
)
from visualizations import create_all_visualizations

def get_months_in_range(start_month: str, end_month: str, available_months: List[str]) -> List[str]:
    """
    Get list of months between start and end month from available months.
    
    Args:
        start_month (str): Start month in format "Month Year"
        end_month (str): End month in format "Month Year"
        available_months (List[str]): List of available months
        
    Returns:
        List[str]: List of months in range
    """
    try:
        sorted_months = sorted(available_months, 
                             key=lambda x: pd.to_datetime(x, format='%B %Y'))
        start_idx = sorted_months.index(start_month)
        end_idx = sorted_months.index(end_month)
        return sorted_months[start_idx:end_idx + 1]
    
    except ValueError as e:
        print(f"Error processing dates: {e}")
        return []

def display_changes(changes_abs: pd.DataFrame, changes_pct: pd.DataFrame) -> None:
    """
    Display allocation changes in a formatted way.
    
    Args:
        changes_abs (pd.DataFrame): DataFrame with absolute changes
        changes_pct (pd.DataFrame): DataFrame with percentage changes
    """
    try:
        if changes_abs.empty or changes_pct.empty:
            print("No changes to display.")
            return
        
        # Get significant changes
        significant_abs = get_significant_changes(changes_abs, threshold=1000, change_type='absolute')
        significant_pct = get_significant_changes(changes_pct, threshold=5.0, change_type='percentage')
        
        print("\nSignificant Changes in Holdings:")
        print("=" * 80)
        
        # Display absolute changes
        if not significant_abs.empty:
            print("\nAbsolute Changes (>1000 units):")
            print("-" * 40)
            
            for idx, row in significant_abs.iterrows():
                print(f"\nInstrument: {row['Name of the Instrument']}")
                print(f"Industry: {row['Rating / Industry^']}")
                
                for col in row.index:
                    if col.startswith('Change_'):
                        if pd.notna(row[col]) and abs(row[col]) > 1000:
                            period = col.replace('Change_', '').replace('_to_', ' to ')
                            print(f"  {period}: {int(row[col]):,} units")
        
        # Display percentage changes
        if not significant_pct.empty:
            print("\nPercentage Changes (>5%):")
            print("-" * 40)
            
            for idx, row in significant_pct.iterrows():
                print(f"\nInstrument: {row['Name of the Instrument']}")
                print(f"Industry: {row['Rating / Industry^']}")
                
                for col in row.index:
                    if col.startswith('Pct_Change_'):
                        if pd.notna(row[col]) and abs(row[col]) > 5:
                            period = col.replace('Pct_Change_', '').replace('_to_', ' to ')
                            print(f"  {period}: {row[col]:.2f}%")

    except Exception as e:
        print(f"Error displaying changes: {str(e)}")
        import traceback
        print(traceback.format_exc())

def main():
    try:
        print("Mutual Fund Allocation Change Tracker")
        print("=" * 40)
        
        # Scan for available fund data
        fund_month_map = scan_excel_files()
        
        if not fund_month_map:
            print("No fund data found in the data directory.")
            return
        
        # Get fund selection from user
        fund_name = choose_fund_name_interactive(list(fund_month_map.keys()))
        if not fund_name:
            print("Operation cancelled.")
            return
        
        # Get date range from user
        start_month, end_month = choose_date_range_interactive(fund_month_map[fund_name])
        if not start_month or not end_month:
            print("Operation cancelled.")
            return
        
        # Get months in selected range
        months = get_months_in_range(start_month, end_month, fund_month_map[fund_name])
        
        print(f"\nLoading data for {fund_name} from {start_month} to {end_month}...")
        
        # Load and process data
        monthly_data = load_data_for_fund_months(fund_name, months)
        if not monthly_data:
            print("No data could be loaded for the selected period.")
            return
        
        consolidated_df = create_consolidated_dataframe(monthly_data)
        changes_abs, changes_pct = calculate_allocation_changes(consolidated_df)
        
        # Display results
        # display_changes(changes_abs, changes_pct)
        
        # Generate visualizationsn
        create_all_visualizations(consolidated_df, changes_abs, months)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())
        return

if __name__ == "__main__":
    main() 

# scan for excel 
# preprocess
# calc alloc
# calc changes
# vis 