#!/usr/bin/env python3
import pandas as pd
from data_processor import HealthDataProcessor

# Initialize processor
processor = HealthDataProcessor()

print('=== NIH Data Structure Check ===')
if 'nih_data' in processor.current_data:
    nih_data = processor.current_data['nih_data']
    print(f'NIH data shape: {nih_data.shape}')
    print(f'NIH data columns: {nih_data.columns.tolist()}')
    print('\nFirst 2 rows:')
    print(nih_data.head(2))
    
    # Check if 'cases' column exists
    if 'cases' in nih_data.columns:
        print('\n✓ "cases" column found')
    else:
        print('\n✗ "cases" column NOT found')
        print('Available numeric columns:')
        numeric_cols = nih_data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        print(numeric_cols)
else:
    print('No NIH data found')

print('\n=== Weather Data Structure Check ===')
if 'weather_data' in processor.current_data:
    weather_data = processor.current_data['weather_data']
    print(f'Weather data shape: {weather_data.shape}')
    print(f'Weather data columns: {weather_data.columns.tolist()}')
else:
    print('No weather data found')