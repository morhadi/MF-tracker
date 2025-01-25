import os
import re
import pandas as pd

def scan_full_folder():
    """Scans the current folder and maps fund names to sets of months."""
    portfolio_map = {}
    try:
        for filename in os.listdir("."):
            if filename.endswith(('.xlsx', '.xls')):
                match = re.match(r"(.+) - Monthly Portfolio (.+)\.xlsx?", filename)
                if match:
                    fund_name = match.group(1)
                    month_str = match.group(2)
                    if fund_name not in portfolio_map:
                        portfolio_map[fund_name] = set()
                    portfolio_map[fund_name].add(month_str)
    except OSError as e:
        print(f"Error scanning directory: {e}")
        return {}
    return portfolio_map

def load_and_process_data(fund_name, month_str):
    """Loads and processes data from a single portfolio file."""
    filename = f"{fund_name} - Monthly Portfolio {month_str}.xlsx"
    try:
        df = pd.read_excel(filename, skiprows=3)
        df['ISIN'] = df['ISIN'].astype(str)
        df = df[df['ISIN'].str.startswith('INE')]
        df = df.dropna(axis=1, how='all')
        df = df.set_index('ISIN')

        month_prefix = month_str.replace(" ", "")
        df = df.rename(columns={
            'Quantity': f'Quantity {month_prefix}',
            'Market value(Rs. in Lakhs)': f'MarketValue {month_prefix}',
            '% to NAV': f'NAVPercent {month_prefix}'
        })
        return df[['Name of the Instrument','Rating / Industry^', f'Quantity {month_prefix}', f'MarketValue {month_prefix}', f'NAVPercent {month_prefix}']]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except pd.errors.ParserError:
        print(f"Error parsing file '{filename}'. Check the format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {filename}: {e}")
        return None

# Example Usage
portfolio_data = scan_full_folder()
all_data = pd.DataFrame(columns=['Name of the Instrument', 'Rating / Industry']) # Initialize with common columns

if portfolio_data:
    print("Portfolio Data Map:")
    for fund, months in portfolio_data.items():
        print(f"{fund}: {months}")

    for fund, months in portfolio_data.items():
        for month in months:
            df = load_and_process_data(fund, month)
            if df is not None:
                # Merge, keeping existing columns and adding new month columns
                if all_data.empty:
                    all_data=df
                else:
                    all_data = pd.merge(all_data, df, left_index=True, right_index=True, how="outer")
            else:
                print(f"Failed to load data for {fund} - {month}")

    if not all_data.empty:
        print("\nCombined Data:")
        print(all_data)
        print(all_data.info())
    else:
        print("No data loaded.")

else:
    print("No portfolio files found.")

# Output:
# Portfolio Data Map:
# Zerodha Nifty 50 Index Fund: {'January 2021', 'February 2021'}
# Axis Bluechip Fund: {'January 2021', 'February 2021'}

# Combined Data:
#                            Name of the Instrument Rating / Industry  Quantity January2021  MarketValue January2021  NAVPercent January2021  Quantity February2021  MarketValue February2021  NAVPercent February2021
# ISIN
# INE1234567890  Company A                          AAA               100.0                  50.0                     1.0                    200.0                  100.0                     55.0                    1.5

if __name__ == "__main__":
    pass

