#!/usr/bin/env python3
"""
Test script to verify dengue patient data integration with AI analysis system.
This script tests the enhanced model training with both NIH and dengue patient data.
"""

import sys
import os
sys.path.append('/Users/ishtiaq/Desktop/pak-ai')

from data_processor import HealthDataProcessor
from ai_analysis import AIAnalyzer
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dengue_integration():
    """Test the integration of dengue patient data with the AI analysis system."""
    try:
        logger.info("Starting dengue patient data integration test...")
        
        # Initialize data processor
        processor = HealthDataProcessor()
        
        # Load NIH and weather data
        logger.info("Loading NIH and weather data...")
        processor.load_nih_data()
        processor.integrate_climate_data()
        
        # Check if data is loaded
        if processor.current_data.get('nih_data') is None:
            logger.error("NIH data not loaded")
            return False
            
        if processor.current_data.get('weather_data') is None:
            logger.error("Weather data not loaded")
            return False
            
        logger.info(f"NIH data shape: {processor.current_data['nih_data'].shape}")
        logger.info(f"Weather data shape: {processor.current_data['weather_data'].shape}")
        
        # Initialize AI analyzer
        logger.info("Initializing AI analyzer with dengue integration...")
        ai_analyzer = AIAnalyzer(processor)
        
        # Test dengue data processing separately
        logger.info("Testing dengue patient data processing...")
        dengue_data = ai_analyzer._process_dengue_patient_data()
        
        if not dengue_data.empty:
            logger.info(f"Dengue data processed successfully. Shape: {dengue_data.shape}")
            logger.info(f"Dengue data columns: {dengue_data.columns.tolist()}")
            logger.info(f"Dengue data date range: {dengue_data.index.min()} to {dengue_data.index.max()}")
            logger.info(f"Total dengue cases in dataset: {dengue_data['cases'].sum()}")
            logger.info(f"Average daily dengue cases: {dengue_data['cases'].mean():.2f}")
            
            # Check for geographic features
            if 'lat' in dengue_data.columns and 'lon' in dengue_data.columns:
                logger.info(f"Geographic coverage - Lat: {dengue_data['lat'].min():.4f} to {dengue_data['lat'].max():.4f}")
                logger.info(f"Geographic coverage - Lon: {dengue_data['lon'].min():.4f} to {dengue_data['lon'].max():.4f}")
            
            # Check for demographic features
            if 'avg_age' in dengue_data.columns:
                logger.info(f"Average patient age: {dengue_data['avg_age'].mean():.2f} years")
            if 'male_ratio' in dengue_data.columns:
                logger.info(f"Average male ratio: {dengue_data['male_ratio'].mean():.2f}")
        else:
            logger.warning("No dengue data processed")
        
        # Test enhanced model training
        logger.info("Testing enhanced model training with dengue data...")
        training_result = ai_analyzer.train_outbreak_prediction_model(
            processor.current_data, 
            processor.current_data['weather_data']
        )
        
        if training_result.get('success'):
            logger.info("Enhanced model training successful!")
            model_perf = training_result.get('model_performance', {})
            logger.info(f"Model RMSE: {model_perf.get('rmse', 'N/A')}")
            logger.info(f"Training samples: {model_perf.get('training_samples', 'N/A')}")
            logger.info(f"Test samples: {model_perf.get('test_samples', 'N/A')}")
            logger.info(f"Features used: {model_perf.get('features_used', 'N/A')}")
            return True
        else:
            logger.error(f"Enhanced model training failed: {training_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_dengue_integration()
    if success:
        print("\n✅ Dengue patient data integration test PASSED")
        print("The AI analysis system now successfully integrates:")
        print("- NIH weekly disease surveillance data")
        print("- Dengue patient data from Punjab with GIS coordinates")
        print("- Weather data for enhanced outbreak predictions")
    else:
        print("\n❌ Dengue patient data integration test FAILED")
        sys.exit(1)