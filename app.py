import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from data_processor import HealthDataProcessor
from ai_analysis import AIAnalyzer
from weather_service import WeatherService
from scheduler import DataScheduler
import json
from datetime import datetime as dt
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "health-dashboard-secret-key")

# Debugging: Print environment variables to check if API keys are loaded
# Removed temporary debug print statements as per instruction
CORS(app)

# Initialize services
try:
    data_processor = HealthDataProcessor()
    ai_analyzer = AIAnalyzer(data_processor)
    weather_service = WeatherService()
    scheduler = DataScheduler(data_processor, ai_analyzer, weather_service)
    
    # Start the scheduler
    scheduler.start()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    data_processor = None
    ai_analyzer = None
    weather_service = None

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get main dashboard statistics"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        stats = data_processor.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

@app.route('/api/disease-trends')
def get_disease_trends():
    """Get disease trend data for charts"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        trends = data_processor.get_disease_trends()
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error getting disease trends: {e}")
        return jsonify({"error": "Failed to fetch disease trends"}), 500

@app.route('/api/weather-data')
def get_weather_data():
    """Get current weather data"""
    try:
        if not weather_service:
            return jsonify({"error": "Weather service not available"}), 500
            
        weather = weather_service.get_current_weather()
        return jsonify(weather)
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route('/api/ai-recommendations')
def get_ai_recommendations():
    """Get AI-powered recommendations"""
    try:
        if not ai_analyzer or not data_processor:
            return jsonify({"error": "AI analyzer not available"}), 500
            
        current_data = data_processor.get_current_data()
        recommendations = ai_analyzer.generate_recommendations(current_data)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return jsonify({"error": "Failed to fetch AI recommendations"}), 500

@app.route('/api/scenario-simulation')
def get_scenario_simulation():
    """Get AI scenario simulation"""
    try:
        if not ai_analyzer or not data_processor:
            return jsonify({"error": "AI analyzer not available"}), 500
            
        current_data = data_processor.get_current_data()
        scenarios = ai_analyzer.simulate_scenarios(current_data)
        return jsonify(scenarios)
    except Exception as e:
        logger.error(f"Error getting scenario simulation: {e}")
        return jsonify({"error": "Failed to fetch scenario simulation"}), 500

@app.route('/api/map-data')
def get_map_data():
    """Get data for disease distribution map"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        map_data = data_processor.get_map_data()
        logger.info(f"Returning map data with {len(map_data)} locations")
        return jsonify(map_data)
    except Exception as e:
        logger.error(f"Error getting map data: {e}")
        return jsonify({"error": "Failed to fetch map data"}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get current health alerts"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        alerts = data_processor.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({"error": "Failed to fetch alerts"}), 500

@app.route('/api/high-risk-areas')
def get_high_risk_areas():
    """Get top 5 high-risk areas for health alerts"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        high_risk_areas = data_processor.get_high_risk_areas()
        return jsonify(high_risk_areas)
    except Exception as e:
        logger.error(f"Error getting high-risk areas: {e}")
        return jsonify({"error": "Failed to fetch high-risk areas"}), 500

@app.route('/api/disease-surveillance')
def get_disease_surveillance():
    """Get disease surveillance data"""
    try:
        if not data_processor:
            return jsonify({"error": "Data processor not available"}), 500
            
        surveillance_data = data_processor.get_disease_surveillance()
        return jsonify(surveillance_data)
    except Exception as e:
        logger.error(f"Error getting disease surveillance: {e}")
        return jsonify({"error": "Failed to fetch disease surveillance"}), 500

@app.route('/api/climate-monitoring')
def get_climate_monitoring():
    """Get climate and environmental health monitoring data"""
    try:
        if not weather_service or not data_processor:
            return jsonify({"error": "Services not available"}), 500
            
        climate_data = weather_service.get_climate_health_monitoring()
        return jsonify(climate_data)
    except Exception as e:
        logger.error(f"Error getting climate monitoring: {e}")
        return jsonify({"error": "Failed to fetch climate monitoring"}), 500

@app.route('/api/weather-alerts')
def get_weather_alerts():
    """Get weather alerts for health monitoring"""
    try:
        if not weather_service:
            return jsonify({"error": "Weather service not available"}), 500
            
        alerts = weather_service.get_weather_alerts()
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return jsonify({
            'alerts': [],
            'count': 0,
            'last_updated': dt.now().isoformat()
        }), 500

@app.route('/api/flood/monitoring')
def get_flood_monitoring():
    """Get real-time flood monitoring and health risk assessment"""
    try:
        if not weather_service:
            return jsonify({"error": "Weather service not available"}), 500
            
        flood_data = weather_service.get_flood_monitoring()
        return jsonify(flood_data)
    except Exception as e:
        logger.error(f"Error getting flood monitoring data: {e}")
        return jsonify({"error": "Failed to get flood monitoring data"}), 500

@app.route('/api/outbreak-predictions')
def get_outbreak_predictions():
    """Get outbreak predictions from the AI model"""
    try:
        if not ai_analyzer:
            return jsonify({"error": "AI analyzer not available"}), 500
        
        predictions = ai_analyzer.predict_outbreaks()
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Error getting outbreak predictions: {e}")
        return jsonify({"error": "Failed to fetch outbreak predictions"}), 500

@app.route('/api/comprehensive-forecasts')
def get_comprehensive_forecasts():
    """Get comprehensive 2-3 week disease forecasts with detailed predictions"""
    try:
        if not ai_analyzer:
            return jsonify({"error": "AI analyzer not available"}), 500
        
        forecasts = ai_analyzer.get_comprehensive_forecasts()
        return jsonify(forecasts)
    except Exception as e:
        logger.error(f"Error getting comprehensive forecasts: {e}")
        return jsonify({"error": "Failed to fetch comprehensive forecasts"}), 500

@app.route('/api/model-status')
def get_model_status():
    """Get information about the trained model"""
    try:
        if not ai_analyzer:
            return jsonify({"error": "AI analyzer not available"}), 500
        
        model_info = ai_analyzer.get_model_info()
        return jsonify(model_info)
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return jsonify({"error": "Failed to get model status"}), 500

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Manually refresh all data"""
    try:
        if scheduler:
            scheduler.update_all_data()
            return jsonify({"message": "Data refresh initiated"})
        else:
            return jsonify({"error": "Scheduler not available"}), 500
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({"error": "Failed to refresh data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
