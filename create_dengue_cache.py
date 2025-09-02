#!/usr/bin/env python3
"""
Dengue Data Cache Generator
Creates a lightweight summary of the large dengue dataset for faster loading.
"""

import pandas as pd
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dengue_cache():
    """Create a cached summary of dengue data for faster dashboard loading."""
    
    dengue_file_path = 'denguedata/Patieints.xlsx'
    cache_file_path = 'denguedata/dengue_cache.json'
    
    if not os.path.exists(dengue_file_path):
        logger.error(f"Dengue data file not found: {dengue_file_path}")
        return False
    
    try:
        logger.info("Loading dengue data for cache generation...")
        start_time = datetime.now()
        
        # Read the large Excel file
        df = pd.read_excel(dengue_file_path)
        logger.info(f"Loaded {len(df)} dengue records in {datetime.now() - start_time}")
        
        # Create summary statistics
        cache_data = {
            'total_records': len(df),
            'date_range': {
                'start': None,
                'end': None
            },
            'geographic_coverage': {
                'lat_min': None,
                'lat_max': None,
                'lon_min': None,
                'lon_max': None
            },
            'monthly_summary': {},
            'district_summary': {},
            'age_demographics': {},
            'gender_distribution': {},
            'last_updated': datetime.now().isoformat(),
            'cache_version': '1.0'
        }
        
        # Process date columns
        date_columns = ['Date', 'Admission Date', 'Discharge Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                valid_dates = df[col].dropna()
                if not valid_dates.empty:
                    cache_data['date_range']['start'] = valid_dates.min().isoformat()
                    cache_data['date_range']['end'] = valid_dates.max().isoformat()
                    break
        
        # Process geographic data
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
            
            valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
            if not valid_coords.empty:
                cache_data['geographic_coverage'] = {
                    'lat_min': float(valid_coords['Latitude'].min()),
                    'lat_max': float(valid_coords['Latitude'].max()),
                    'lon_min': float(valid_coords['Longitude'].min()),
                    'lon_max': float(valid_coords['Longitude'].max()),
                    'total_locations': len(valid_coords)
                }
        
        # Monthly case distribution (for seasonal analysis)
        if 'Date' in df.columns:
            df['Month'] = df['Date'].dt.month
            monthly_counts = df['Month'].value_counts().sort_index()
            cache_data['monthly_summary'] = monthly_counts.to_dict()
        
        # District/City distribution
        location_columns = ['District', 'City', 'Location', 'Address']
        for col in location_columns:
            if col in df.columns:
                district_counts = df[col].value_counts().head(20)  # Top 20 districts
                cache_data['district_summary'] = district_counts.to_dict()
                break
        
        # Age demographics
        if 'Age' in df.columns:
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            valid_ages = df['Age'].dropna()
            if not valid_ages.empty:
                cache_data['age_demographics'] = {
                    'mean_age': float(valid_ages.mean()),
                    'median_age': float(valid_ages.median()),
                    'age_groups': {
                        '0-18': int(len(valid_ages[valid_ages <= 18])),
                        '19-35': int(len(valid_ages[(valid_ages > 18) & (valid_ages <= 35)])),
                        '36-60': int(len(valid_ages[(valid_ages > 35) & (valid_ages <= 60)])),
                        '60+': int(len(valid_ages[valid_ages > 60]))
                    }
                }
        
        # Gender distribution
        gender_columns = ['Gender', 'Sex']
        for col in gender_columns:
            if col in df.columns:
                gender_counts = df[col].value_counts()
                cache_data['gender_distribution'] = gender_counts.to_dict()
                break
        
        # Save cache file
        with open(cache_file_path, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        
        logger.info(f"Dengue cache created successfully: {cache_file_path}")
        logger.info(f"Cache contains summary of {cache_data['total_records']} records")
        logger.info(f"Total processing time: {datetime.now() - start_time}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating dengue cache: {e}")
        return False

if __name__ == '__main__':
    success = create_dengue_cache()
    if success:
        print("✅ Dengue cache created successfully")
    else:
        print("❌ Failed to create dengue cache")