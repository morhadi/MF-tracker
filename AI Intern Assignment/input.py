import difflib

def suggest_fund(user_input, fund_names):
    """Suggests fund names based on user input using fuzzy matching.

    Args:
        user_input: The user's input string.
        fund_names: A list of available fund names.

    Returns:
        A list of suggested fund names, sorted by similarity, or an empty list if no good matches are found.
    """

    if not user_input:  # Handle empty input
        return []

    # Use difflib.get_close_matches for efficient fuzzy matching
    suggestions = difflib.get_close_matches(user_input, fund_names, n=5, cutoff=0.6) #n=max suggestions, cutoff=similarity threshold

    if not suggestions: #if no close matches, try contains search
        suggestions = [fund for fund in fund_names if user_input.lower() in fund.lower()]
        suggestions.sort(key=lambda x: x.lower().find(user_input.lower())) #sort by index of match

    return suggestions


def get_fund_input(fund_names):
    """Gets user input for a fund name with auto-completion suggestions."""
    while True:
        user_input = input("Enter Mutual Fund Name: ")
        suggestions = suggest_fund(user_input, fund_names)

        if suggestions:
            print("Did you mean:")
            for i, suggestion in enumerate(suggestions):
                print(f"{i+1}. {suggestion}")

            try:
                choice = int(input("Select a number (or press Enter to re-enter): "))
                if 1 <= choice <= len(suggestions):
                    return suggestions[choice - 1]
            except ValueError:
                if not user_input:
                    print("Please enter something.")
                    continue
                else:
                    print("Invalid input. Please select a number or press Enter to re-enter")
                    continue
        elif not user_input:
            print("Please enter fund name.")
            continue
        else:
            print("No matching funds found. Please re-enter or check the name.")


# Example usage:
fund_names = [
    "Zerodha Nifty 50 Index Fund",
    "Axis Bluechip Fund",
    "Parag Parikh Flexi Cap Fund",
    "Quant Small Cap Fund",
    "SBI Focused Equity Fund",
    "ICICI Prudential Bluechip Fund",
    "ZN250 Index Fund",
    "Zerodha Tax Saver Fund",
    "Mirae Asset Emerging Bluechip Fund",
    "HDFC Top 100 Fund",
    "UTI Nifty Index Fund"
]

selected_fund = get_fund_input(fund_names)

if selected_fund:
    print(f"You selected: {selected_fund}")
else:
    print("No fund selected.")