# Reverse DCF Web App

A Streamlit web app for reverse Discounted Cash Flow analysis.

## Setup

1. Ensure Python is installed.
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment: `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Running the App

Run the app with: `streamlit run main.py`

The app will open in your browser with input panel on the left and output panel on the right.

## Features

- Input fields for DCF parameters with default values.
- Radio buttons to select which parameter to calculate.
- Hover over labels for info tooltips.
- Press "Go" to generate and display a fake matplotlib plot in the output panel.

Note: The calculation functions currently generate fake plots. Replace the plot generation code in `calculations.py` with actual DCF calculations.