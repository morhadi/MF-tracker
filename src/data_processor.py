import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime

def create_consolidated_dataframe(monthly_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Consolidate monthly DataFrames into a single DataFrame.
    
    Args:
        monthly_data (Dict[str, pd.DataFrame]): Map of months to their DataFrames
        
    Returns:
        pd.DataFrame: Consolidated DataFrame with month-specific columns
    """
    if not monthly_data:
        return pd.DataFrame()
        
    # Sort months chronologically
    sorted_months = sorted(monthly_data.keys(), 
                         key=lambda x: datetime.strptime(x, '%B %Y'))
    
    # Start with the first month's data
    consolidated_df = monthly_data[sorted_months[0]].copy()
    base_columns = ['Name of the Instrument', 'Rating / Industry^']
    
    # Rename quantity column to include month
    consolidated_df = consolidated_df.rename(
        columns={
            'Quantity': f'Quantity_{sorted_months[0]}',
            '% to NAV': f'NAV_{sorted_months[0]}'
        }
    )
    
    # Merge with subsequent months
    for month in sorted_months[1:]:
        month_df = monthly_data[month].copy()
        month_df = month_df.rename(
            columns={
                'Quantity': f'Quantity_{month}',
                '% to NAV': f'NAV_{month}'
            }
        )
        
        consolidated_df = pd.merge(
            consolidated_df,
            month_df,
            left_index=True,
            right_index=True,
            how='outer',
            suffixes=('', f'_{month}')
        )
        
        # Combine instrument and industry info if they differ
        for col in base_columns:
            if f'{col}_{month}' in consolidated_df.columns:
                consolidated_df[col].fillna(consolidated_df[f'{col}_{month}'], inplace=True)
                consolidated_df.drop(f'{col}_{month}', axis=1, inplace=True)
    
    return consolidated_df

def calculate_allocation_changes(consolidated_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate month-over-month changes in allocations.
    
    Args:
        consolidated_df (pd.DataFrame): Consolidated DataFrame with month-specific columns
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 
            - DataFrame with absolute changes
            - DataFrame with percentage changes
    """
    # Get quantity columns in chronological order
    quantity_cols = sorted(
        [col for col in consolidated_df.columns if col.startswith('Quantity_')],
        key=lambda x: datetime.strptime(x.split('_', 1)[1], '%B %Y')
    )
    
    if len(quantity_cols) < 2:
        return pd.DataFrame(), pd.DataFrame()
    
    changes_abs = pd.DataFrame(index=consolidated_df.index)
    changes_pct = pd.DataFrame(index=consolidated_df.index)
    
    # Calculate month-over-month changes
    for i in range(len(quantity_cols) - 1):
        current_month = quantity_cols[i].split('_', 1)[1]
        next_month = quantity_cols[i + 1].split('_', 1)[1]
        
        # Absolute change
        change_col = f'Change_{current_month}_to_{next_month}'
        changes_abs[change_col] = (
            consolidated_df[quantity_cols[i + 1]] - consolidated_df[quantity_cols[i]]
        )
        
        # Percentage change
        pct_change_col = f'Pct_Change_{current_month}_to_{next_month}'
        changes_pct[pct_change_col] = (
            (consolidated_df[quantity_cols[i + 1]] - consolidated_df[quantity_cols[i]]) /
            consolidated_df[quantity_cols[i]] * 100
        )
    
    # Add instrument and industry info
    changes_abs['Name of the Instrument'] = consolidated_df['Name of the Instrument']
    changes_abs['Rating / Industry^'] = consolidated_df['Rating / Industry^']
    changes_pct['Name of the Instrument'] = consolidated_df['Name of the Instrument']
    changes_pct['Rating / Industry^'] = consolidated_df['Rating / Industry^']
    
    return changes_abs, changes_pct

def get_significant_changes(changes_df: pd.DataFrame, 
                          threshold: float = 5.0,
                          change_type: str = 'absolute') -> pd.DataFrame:
    """
    Filter for significant changes in allocations.
    
    Args:
        changes_df (pd.DataFrame): DataFrame with changes
        threshold (float): Threshold for significant changes
        change_type (str): Type of change ('absolute' or 'percentage')
        
    Returns:
        pd.DataFrame: DataFrame with only significant changes
    """
    # Get change columns (excluding Name of the Instrument and Rating / Industry^)
    change_cols = [col for col in changes_df.columns 
                  if col.startswith('Change_') or col.startswith('Pct_Change_')]
    
    # Create mask for significant changes
    if change_type == 'absolute':
        mask = changes_df[change_cols].abs().gt(threshold).any(axis=1)
    else:  # percentage
        mask = changes_df[change_cols].abs().gt(threshold).any(axis=1)
    
    return changes_df[mask] 