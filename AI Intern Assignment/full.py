import pandas as pd
import os
import re
from collections import defaultdict
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from datetime import datetime, timedelta

DATA_FOLDER = "."  # Scan current folder

def scan_excel_files(folder_path):
    """
    Scans the current folder for Excel files matching a naming pattern and
    creates a map of fund names to available months, sorted chronologically.

    Args:
        folder_path: Path to the folder (will be current folder ".").

    Returns:
        A dictionary where keys are fund names and values are lists of available
        months (strings like "November 2024"), sorted chronologically.
    """
    fund_month_map = defaultdict(list)  # Changed value to list to maintain order
    excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

    for file_name in excel_files:
        print(f"Processing: {file_name}")
        match = re.match(r"([A-Za-z0-9\s\-\_]+) - Monthly Portfolio ([A-Za-z]+ \d{4})\.(xlsx|xls)", file_name)
        if match:
            fund_code = match.group(1)
            month_year_str = match.group(2).strip()
            fund_name = fund_code

            try:
                month_date = datetime.strptime(month_year_str, '%B %Y') # Parse month string to datetime
                fund_month_map[fund_name].append((month_date, month_year_str)) # Store datetime and string
            except ValueError:
                print(f"Warning: Could not parse month from filename: {file_name}")

    # Sort months chronologically for each fund and keep only month strings
    for fund in fund_month_map:
        fund_month_map[fund].sort(key=lambda item: item[0]) # Sort based on datetime
        fund_month_map[fund] = [month_str for _, month_str in fund_month_map[fund]] # Keep only month strings

    return fund_month_map


def load_and_clean_excel_data(file_path, fund_name, month_str):
    """
    Loads data from a single Excel file, cleans it, and returns a Pandas DataFrame.
    Applies ISIN cleaning and sets ISIN as index.

    Args:
        file_path: Path to the Excel file.
        fund_name: Name of the fund.
        month_str: Month string.

    Returns:
        A cleaned Pandas DataFrame, or None if loading fails.
    """
    try:
        df = pd.read_excel(file_path, header=None)
        header_row_index = None
        for index, row in df.iterrows():
            if "Name of the Instrument" in row.values:
                header_row_index = index
                break

        if header_row_index is None:
            print(f"Warning: Header row not found in {file_path}. Skipping.")
            return None

        df = pd.read_excel(file_path, header=header_row_index)
        df.columns = [str(col).strip() for col in df.columns]

        required_cols = ["Name of the Instrument", "ISIN", "Rating / Industry^", "Quantity"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = None

        df_cleaned = df[required_cols].copy()
        df_cleaned.rename(columns={
            "Name of the Instrument": "Instrument Name",
            "Rating / Industry^": "Rating / Industry"
        }, inplace=True)

        df_cleaned['Fund Name'] = fund_name
        df_cleaned['Month'] = month_str

        df_cleaned.dropna(subset=['Instrument Name'], inplace=True)
        df_cleaned = df_cleaned[df_cleaned['Instrument Name'].str.strip() != '']

        # --- ISIN Cleaning ---
        df_cleaned = df_cleaned[df_cleaned['ISIN'].notna()]
        df_cleaned['ISIN'] = df_cleaned['ISIN'].astype(str)
        df_cleaned = df_cleaned[df_cleaned['ISIN'].str.startswith('INE')]
        df_cleaned = df_cleaned.dropna(axis=1, how='all') # Drop cols with all NaN

        df_cleaned = df_cleaned.set_index('ISIN') # Set ISIN as index

        return df_cleaned

    except Exception as e:
        print(f"Error loading/processing {file_path}: {e}")
        return None


def load_data_for_fund_months(folder_path, fund_name, month_strings):
    """
    Loads data for a specific fund and list of months.
    """
    monthly_data = {}
    for month_str in month_strings:
        file_name = f"{fund_name} - Monthly Portfolio {month_str}.xlsx"
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            monthly_df = load_and_clean_excel_data(file_path, fund_name, month_str)
            if monthly_df is not None:
                monthly_data[month_str] = monthly_df
        else:
            print(f"Warning: File not found for {fund_name}, {month_str}: {file_path}")

    if not monthly_data:
        return None
    return monthly_data


def create_consolidated_dataframe(monthly_data_dict):
    """
    Consolidates monthly data DataFrames into a single DataFrame.
    """
    if not monthly_data_dict:
        return None

    consolidated_df = None
    for month_str, df in monthly_data_dict.items():
        df_month_pivot = df.pivot_table(
            index=['ISIN', 'Instrument Name', 'Rating / Industry', 'Fund Name'],
            values='Quantity',
            aggfunc='first'
        ).rename(columns={'Quantity': f'Quantity {month_str}'}).reset_index()

        if consolidated_df is None:
            consolidated_df = df_month_pivot
        else:
            consolidated_df = pd.merge(consolidated_df, df_month_pivot,
                                       on=['ISIN', 'Instrument Name', 'Rating / Industry', 'Fund Name'],
                                       how='outer')
    return consolidated_df


def choose_fund_name_interactive(fund_names):
    """Interactive fund name selection."""
    fund_completer = FuzzyWordCompleter(fund_names)
    while True:
        try:
            fund_name_input = prompt("Enter Fund Name (type to search): ", completer=fund_completer)
            if fund_name_input.strip():
                matched_funds = [fund for fund in fund_names if fund_name_input.lower() in fund.lower()]
                if matched_funds:
                    if len(matched_funds) == 1:
                        return matched_funds[0]
                    else:
                        print("\nDid you mean one of these? (Choose number or continue typing)")
                        for i, fund in enumerate(matched_funds):
                            print(f"{i+1}. {fund}")
                        choice_str = prompt("Enter number to select, or continue typing: ")
                        if choice_str.isdigit() and 1 <= int(choice_str) <= len(matched_funds):
                            return matched_funds[int(choice_str)-1]
                        else:
                             continue
                else:
                    print("No fund names found matching your input. Please try again.")
            else:
                print("Fund name cannot be empty. Please try again.")
        except KeyboardInterrupt:
            print("\nFund selection cancelled.")
            return None
        except EOFError:
            print("\nFund selection cancelled.")
            return None


def choose_date_range_interactive(available_months):
    """Interactive date range selection."""
    while True:
        print("\nChoose Date Range:")
        print("1. Last X Months")
        print("2. Month Range Selection")
        print("3. All Available Months")
        try:
            choice = input("Enter your choice (1-3): ")
            if choice == '1':
                while True:
                    try:
                        months = int(input("Enter number of months (e.g., 5): "))
                        if months > 0:
                            selected_months = available_months[:months] # Already sorted chronologically
                            return "Last X Months", {"months": months}, selected_months
                        else:
                            print("Number of months must be positive.")
                    except ValueError:
                        print("Invalid input. Please enter a number for months.")
            elif choice == '2':
                print("\nAvailable Months:")
                for i, month in enumerate(available_months):
                    print(f"{i+1}. {month}")

                selected_indices = input("Enter month numbers separated by commas (e.g., 1,3,5) or 'all': ").strip().lower()
                if selected_indices == 'all':
                    selected_months = available_months
                else:
                    try:
                        indices = [int(x.strip()) - 1 for x in selected_indices.split(',')]
                        selected_months = [available_months[i] for i in indices if 0 <= i < len(available_months)]
                        if not selected_months:
                            print("No valid month numbers selected.")
                            continue
                    except ValueError:
                        print("Invalid month number format.")
                        continue
                if selected_months:
                    return "Month Range", {"selected_months_count": len(selected_months)}, selected_months
                else:
                    print("No valid months selected.")

            elif choice == '3':
                selected_months = available_months
                return "All Available Months", {"available_months_count": len(selected_months)}, selected_months
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\nDate range selection cancelled.")
            return None, None, None
        except EOFError:
            print("\nDate range selection cancelled.")
            return None, None, None


def main():
    """Main function."""
    fund_month_map = scan_excel_files(DATA_FOLDER)
    if not fund_month_map:
        print(f"No valid Excel files found in folder: {DATA_FOLDER}")
        return

    fund_names = sorted(fund_month_map.keys())
    print("\nAvailable Funds:")
    for fund_name in fund_names:
        print(f"- {fund_name}")

    selected_fund_name = choose_fund_name_interactive(fund_names)
    if not selected_fund_name:
        print("Exiting.")
        return

    available_months_for_fund = fund_month_map[selected_fund_name]
    if not available_months_for_fund:
        print(f"No monthly data available for fund: {selected_fund_name}")
        return

    print(f"\nAvailable months for {selected_fund_name} (Chronological Order):")
    for month in available_months_for_fund: # Months are already sorted in scan_excel_files
        print(f"- {month}")

    date_range_type, date_range_params, selected_month_strings = choose_date_range_interactive(available_months_for_fund)

    if not date_range_type:
        print("Exiting.")
        return

    print("\n--- Input Summary ---")
    print(f"Selected Fund: {selected_fund_name}")
    print(f"Date Range Type: {date_range_type}")
    if date_range_params:
        print(f"Date Range Parameters: {date_range_params}")
    print(f"Selected Months: {selected_month_strings}")

    monthly_data = load_data_for_fund_months(DATA_FOLDER, selected_fund_name, selected_month_strings)
    if not monthly_data:
        print("No data loaded for selected months. Check data files.")
        return

    consolidated_df = create_consolidated_dataframe(monthly_data)
    if consolidated_df is not None:
        print("\n--- Consolidated DataFrame (First 10 rows) ---")
        print(consolidated_df.head(10).to_string())
        # Optional: Save to CSV
        # output_filepath = f"consolidated_fund_data_{selected_fund_name.replace(' ', '_')}.csv"
        # consolidated_df.to_csv(output_filepath, index=False)
        # print(f"\nConsolidated data saved to: {output_filepath}")
    else:
        print("Error creating consolidated DataFrame.")

    print("\n--- Data Processing Complete ---")


if __name__ == "__main__":
    main()