from typing import List, Tuple, Optional
from datetime import datetime
from fuzzywuzzy import process
from dateutil.relativedelta import relativedelta

def choose_fund_name_interactive(available_funds: List[str]) -> Optional[str]:
    """
    Interactive fund selection with fuzzy matching.
    
    Args:
        available_funds (List[str]): List of available fund names
        
    Returns:
        Optional[str]: Selected fund name or None if cancelled
    """
    if not available_funds:
        print("No funds available.")
        return None
        
    print("\nAvailable funds:")
    for i, fund in enumerate(available_funds, 1):
        print(f"{i}. {fund}")
    
    while True:
        search = input("\nEnter fund name (or part of it) to search, or 'quit' to quit: ").strip()
        
        if search.lower() == 'quit':
            return None
            
        # Use fuzzy matching to find the best matches
        matches = process.extract(search, available_funds, limit=5)
        
        if not matches:
            print("No matching funds found. Please try again.")
            continue
            
        print("\nBest matches:")
        for i, (fund, score) in enumerate(matches, 1):
            print(f"{i}. {fund} (match score: {score})")
            
        choice = input("\nEnter number to select fund, or any other key to search again: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1][0]

def choose_date_range_interactive(available_months: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Interactive date range selection.
    
    Args:
        available_months (List[str]): List of available months
        
    Returns:
        Tuple[Optional[str], Optional[str]]: Selected start and end months, or (None, None) if cancelled
    """
    if not available_months:
        print("No months available.")
        return None, None
        
    # Sort months chronologically
    sorted_months = sorted(available_months, 
                         key=lambda x: datetime.strptime(x, '%B %Y'))
    
    print("\nDate range selection options:")
    print("1. Last X months")
    print("2. Select specific month range")
    print("3. All available months")
    print("4. Cancel")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            while True:
                try:
                    num_months = int(input("\nEnter number of months to look back: "))
                    if num_months <= 0:
                        print("Please enter a positive number.")
                        continue
                    if num_months > len(sorted_months):
                        print(f"Only {len(sorted_months)} months available.")
                        continue
                    return (sorted_months[-num_months], sorted_months[-1])
                except ValueError:
                    print("Please enter a valid number.")
                    
        elif choice == '2':
            print("\nAvailable months:")
            for i, month in enumerate(sorted_months, 1):
                print(f"{i}. {month}")
                
            while True:
                try:
                    start_idx = int(input("\nEnter number for start month: ")) - 1
                    end_idx = int(input("Enter number for end month: ")) - 1
                    
                    if not (0 <= start_idx < len(sorted_months) and 
                           0 <= end_idx < len(sorted_months)):
                        print("Invalid month numbers.")
                        continue
                        
                    if start_idx > end_idx:
                        print("Start month must be before end month.")
                        continue
                        
                    return (sorted_months[start_idx], sorted_months[end_idx])
                    
                except ValueError:
                    print("Please enter valid numbers.")
                    
        elif choice == '3':
            return (sorted_months[0], sorted_months[-1])
            
        elif choice == '4':
            return None, None
            
        else:
            print("Invalid choice. Please try again.") 