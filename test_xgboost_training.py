#!/usr/bin/env python3
"""
Test script to verify XGBoost model training with corrected NIH data processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import HealthDataProcessor
from ai_analysis import AIAnalyzer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_xgboost_training():
    """Test the XGBoost model training with corrected data processing."""
    try:
        # Initialize data processor
        processor = HealthDataProcessor()
        
        # Load NIH data
        logger.info("Loading NIH data...")
        processor.load_nih_data()
        
        # Load weather data
        logger.info("Loading weather data...")
        processor.integrate_climate_data()
        
        # Check if data is loaded
        if 'nih_data' not in processor.current_data or processor.current_data['nih_data'].empty:
            logger.error("No NIH data loaded")
            return False
            
        if 'weather_data' not in processor.current_data or processor.current_data['weather_data'].empty:
            logger.error("No weather data loaded")
            return False
        
        logger.info(f"NIH data shape: {processor.current_data['nih_data'].shape}")
        logger.info(f"Weather data shape: {processor.current_data['weather_data'].shape}")
        
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzer(processor)
        
        # Test the training data preparation
        logger.info("Testing training data preparation...")
        training_data = ai_analyzer._prepare_training_data(
            processor.current_data['nih_data'],
            processor.current_data['weather_data']
        )
        
        if training_data.empty:
            logger.error("Training data preparation failed - empty result")
            return False
        
        logger.info(f"Training data shape: {training_data.shape}")
        logger.info(f"Training data columns: {training_data.columns.tolist()}")
        
        # Check if 'cases' column exists
        if 'cases' not in training_data.columns:
            logger.error("'cases' column not found in training data")
            return False
        
        logger.info(f"Cases column statistics:")
        logger.info(f"  Min: {training_data['cases'].min()}")
        logger.info(f"  Max: {training_data['cases'].max()}")
        logger.info(f"  Mean: {training_data['cases'].mean():.2f}")
        logger.info(f"  Total records: {len(training_data)}")
        
        # Test actual model training
        logger.info("Testing XGBoost model training...")
        result = ai_analyzer.train_outbreak_prediction_model(
            processor.current_data,
            processor.current_data['weather_data']
        )
        
        if result and 'model_performance' in result:
            logger.info("XGBoost model training successful!")
            logger.info(f"Model performance: {result['model_performance']}")
            return True
        else:
            logger.error("XGBoost model training failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in test_xgboost_training: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_xgboost_training()
    if success:
        print("\n✅ XGBoost training test PASSED!")
    else:
        print("\n❌ XGBoost training test FAILED!")
    
    sys.exit(0 if success else 1)