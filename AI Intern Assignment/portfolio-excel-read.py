import pandas as pd

# Assumes the Excel file is saved with a name like 'portfolio.xlsx'
df = pd.read_excel('ZN250 - Monthly Portfolio November 2024.xlsx' , 
    # Skip initial rows with header text
    skiprows=2,  
    # Specify column names explicitly
    names=['name', 'isin', 'industry', 'quantity', 'market_value', 'nav_percent', 'ytm_percent']
)

# Clean up data types
df['quantity'] = df['quantity'].str.replace(',', '').astype(int)
df['market_value'] = df['market_value'].astype(float)
df['nav_percent'] = df['nav_percent'].str.rstrip('%').astype(float)
df['ytm_percent'] = df['ytm_percent'].str.rstrip('%').astype(float)

print(df)
print("\n--- DataFrame Info ---")
print(df.info())
