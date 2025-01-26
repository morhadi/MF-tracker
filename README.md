In short : Just run src/main.py 

# Mutual Fund Portfolio Tracker

A Python-based tool for analyzing and visualizing changes in mutual fund portfolio allocations over time.

## Features

- 📊 Track changes in fund holdings across multiple months

## Installation

1. Clone the repository:

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Place your mutual fund portfolio Excel files in the `data` directory using the following naming convention:

```
{Fund Name} - Monthly Portfolio {Month} {Year}.xlsx
```
Example: `ZN250 - Monthly Portfolio September 2024.xlsx`

1. Run the main script:

```bash
python src/main.py
```

1. Follow the interactive prompts to:
   - Select a fund
   - Choose the date range for analysis
   - View generated visualizations in the `output` directory

## Data Format

The Excel files should contain the following required columns:
- ISIN (unique identifier for securities)
- Name of the Instrument
- Rating / Industry^
- Quantity
- % to NAV

## Project Structure

```
mf-tracker/
├── data/                  # Input Excel files
├── output/               # Generated visualizations
├── src/
│   ├── main.py          # Entry point
│   ├── data_loader.py   # Data loading and preprocessing
│   ├── data_processor.py # Data analysis
│   ├── visualizations.py # Chart generation
│   └── user_interface.py # Interactive CLI
└── requirements.txt      # Python dependencies
```

## Dependencies

- pandas (≥2.0.0)
- openpyxl (≥3.1.0)
- python-dateutil (≥2.8.2)
- fuzzywuzzy (≥0.18.0)
- python-Levenshtein (≥0.21.0)
- matplotlib (≥3.7.0)
- seaborn (≥0.12.0)

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
