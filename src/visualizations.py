import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import os

def create_output_dir():
    """Create output directory for plots if it doesn't exist."""
    if not os.path.exists('output'):
        os.makedirs('output')

def plot_top_holdings_pie(df: pd.DataFrame, month: str, output_dir: str = 'output'):
    """
    Create a pie chart of top 10 holdings by NAV percentage for a given month.
    """
    try:
        create_output_dir()
        
        # Get NAV column for the month
        nav_col = f'NAV_{month}'
        if nav_col not in df.columns:
            print(f"NAV column for {month} not found")
            return
        
        # Sort by NAV percentage and get top 10
        top_10 = df.nlargest(10, nav_col)
        
        # Create pie chart
        plt.figure(figsize=(12, 8))
        wedges, texts, autotexts = plt.pie(
            top_10[nav_col], 
            labels=top_10['Name of the Instrument'], 
            autopct='%1.1f%%',
            pctdistance=0.85
        )
        
        # Enhance the appearance
        plt.title(f'Top 10 Holdings by NAV% - {month}', pad=20)
        
        # Make labels more readable
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)
        
        # Add a legend
        plt.legend(
            wedges, 
            top_10['Name of the Instrument'],
            title="Holdings",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # Save plot
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_holdings_pie_{month}.png', bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error creating pie chart for {month}: {str(e)}")

def plot_sector_allocation(df: pd.DataFrame, month: str, output_dir: str = 'output'):
    """
    Create a bar chart showing sector-wise allocation.
    """
    try:
        create_output_dir()
        
        # Get NAV column for the month
        nav_col = f'NAV_{month}'
        if nav_col not in df.columns:
            print(f"NAV column for {month} not found")
            return
        
        # Group by industry and sum NAV percentages
        sector_allocation = df.groupby('Rating / Industry^')[nav_col].sum().sort_values()
        
        # Create horizontal bar chart
        plt.figure(figsize=(12, max(8, len(sector_allocation) * 0.4)))
        
        # Create bars with colors
        bars = plt.barh(range(len(sector_allocation)), sector_allocation.values)
        
        # Customize the chart
        plt.title(f'Sector-wise Allocation - {month}', pad=20)
        plt.xlabel('NAV %')
        plt.ylabel('Sector')
        
        # Set y-axis ticks
        plt.yticks(range(len(sector_allocation)), sector_allocation.index)
        
        # Add value labels on the bars
        for i, v in enumerate(sector_allocation.values):
            plt.text(v, i, f' {v:.2f}%', va='center')
        
        # Save plot
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sector_allocation_{month}.png')
        plt.close()
        
    except Exception as e:
        print(f"Error creating sector allocation chart for {month}: {str(e)}")

def plot_holdings_changes_heatmap(changes_df: pd.DataFrame, output_dir: str = 'output'):
    """
    Create a heatmap showing changes in top holdings across months.
    """
    create_output_dir()
    plt.figure(figsize=(15, 10))
    
    # Get change columns
    change_cols = [col for col in changes_df.columns if col.startswith('Change_')]
    if not change_cols:
        print("No change columns found for heatmap")
        return
        
    # Calculate total absolute change for each instrument
    changes_df['total_change'] = abs(changes_df[change_cols]).sum(axis=1)
    
    # Get top 20 holdings by absolute change
    top_20 = changes_df.nlargest(20, 'total_change')
    
    # Create heatmap data
    heatmap_data = top_20[change_cols].copy()
    heatmap_data.index = top_20['Name of the Instrument']
    
    # Create heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data, 
                cmap='RdYlBu', 
                center=0, 
                annot=True, 
                fmt='.0f',
                cbar_kws={'label': 'Change in Quantity'})
    
    plt.title('Changes in Top 20 Holdings')
    plt.ylabel('Instrument')
    plt.xlabel('Period')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Save plot
    plt.tight_layout()
    plt.savefig(f'{output_dir}/holdings_changes_heatmap.png')
    plt.close()
    
    # Clean up temporary column
    if 'total_change' in changes_df.columns:
        changes_df.drop('total_change', axis=1, inplace=True)

def plot_nav_changes_scatter(df: pd.DataFrame, start_month: str, end_month: str, output_dir: str = 'output'):
    """
    Create a scatter plot comparing NAV percentages between two months.
    """
    try:
        create_output_dir()
        
        start_nav = f'NAV_{start_month}'
        end_nav = f'NAV_{end_month}'
        
        if start_nav not in df.columns or end_nav not in df.columns:
            print(f"NAV columns for comparison not found")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        plt.scatter(df[start_nav], df[end_nav], alpha=0.5)
        
        # Add diagonal line for reference
        max_nav = max(df[start_nav].max(), df[end_nav].max())
        plt.plot([0, max_nav], [0, max_nav], 'r--', alpha=0.5, label='No Change Line')
        
        # Add labels for points with significant changes
        threshold = 1.0  # NAV% change threshold
        for idx, row in df.iterrows():
            if abs(row[end_nav] - row[start_nav]) > threshold:
                plt.annotate(
                    row['Name of the Instrument'], 
                    (row[start_nav], row[end_nav]),
                    xytext=(5, 5), 
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                )
        
        plt.title(f'NAV% Changes: {start_month} vs {end_month}')
        plt.xlabel(f'NAV% in {start_month}')
        plt.ylabel(f'NAV% in {end_month}')
        plt.legend()
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.tight_layout()
        plt.savefig(f'{output_dir}/nav_changes_scatter.png')
        plt.close()
        
    except Exception as e:
        print(f"Error creating NAV changes scatter plot: {str(e)}")

def plot_quantity_changes_waterfall(changes_df: pd.DataFrame, period: str, output_dir: str = 'output'):
    """
    Create a waterfall chart showing top increases and decreases in holdings.
    """
    try:
        create_output_dir()
        
        # Get changes for the specified period
        change_cols = [col for col in changes_df.columns if col.startswith('Change_') and period in col]
        if not change_cols:
            print(f"No change columns found for period {period}")
            return
            
        change_col = change_cols[0]
        
        # Get top 5 increases and decreases
        increases = changes_df[changes_df[change_col] > 0].nlargest(5, change_col)
        decreases = changes_df[changes_df[change_col] < 0].nsmallest(5, change_col)
        
        # Combine data
        changes = pd.concat([increases, decreases])
        
        # Create figure
        plt.figure(figsize=(15, 8))
        
        # Create bars with different colors for increases and decreases
        bars = plt.bar(range(len(changes)), 
                      changes[change_col],
                      color=['g' if x > 0 else 'r' for x in changes[change_col]])
        
        # Customize the chart
        plt.title(f'Top Holdings Changes - {period}')
        plt.ylabel('Change in Quantity')
        
        # Set x-axis labels
        plt.xticks(
            range(len(changes)),
            changes['Name of the Instrument'],
            rotation=45,
            ha='right'
        )
        
        # Add value labels
        for i, v in enumerate(changes[change_col]):
            plt.text(
                i, v,
                f'{int(v):,}',
                ha='center',
                va='bottom' if v > 0 else 'top',
                fontweight='bold'
            )
        
        # Add grid
        plt.grid(True, axis='y', alpha=0.3)
        
        # Save plot
        plt.tight_layout()
        plt.savefig(f'{output_dir}/quantity_changes_waterfall_{period}.png')
        plt.close()
        
    except Exception as e:
        print(f"Error creating quantity changes waterfall chart: {str(e)}")

def create_all_visualizations(consolidated_df: pd.DataFrame, 
                            changes_df: pd.DataFrame,
                            months: list,
                            output_dir: str = 'output'):
    try:
        # Create pie charts and sector allocation charts for each month
        for month in months:
            print(f"Creating charts for {month}...")
            plot_top_holdings_pie(consolidated_df, month)
            plot_sector_allocation(consolidated_df, month)
        
        # Create changes heatmap
        print("Creating holdings changes heatmap...")
        plot_holdings_changes_heatmap(changes_df)
        
        # Create NAV changes scatter plot
        print("Creating NAV changes scatter plot...")
        plot_nav_changes_scatter(consolidated_df, months[0], months[-1])
        
        # Create quantity changes waterfall chart
        print("Creating quantity changes waterfall chart...")
        period = f"{months[0]}_to_{months[-1]}"
        plot_quantity_changes_waterfall(changes_df, period)
        
        print(f"\nVisualizations have been saved to the '{output_dir}' directory:")
        
    except Exception as e:
        print(f"Error in visualization creation: {str(e)}")
        import traceback
        print(traceback.format_exc()) 