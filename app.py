import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from data_processor import HealthDataProcessor
from ai_analysis import AIAnalyzer
from weather_service import WeatherService
from scheduler import DataScheduler
from heatmap_service import HeatmapService
import json
from datetime import datetime
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
    heatmap_service = HeatmapService()
    scheduler = DataScheduler(data_processor, ai_analyzer, weather_service)
    
    # Start the scheduler
    scheduler.start()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    data_processor = None
    ai_analyzer = None
    weather_service = None
    heatmap_service = None

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/cities-alert')
def cities_alert_page():
    """Cities on alert page"""
    return render_template('cities_alert.html')

@app.route('/heatmap')
def heatmap_page():
    """Weather and disease risk heatmap page"""
    return render_template('heatmap.html')

@app.route('/disease-heatmap/<disease>')
def disease_heatmap_page(disease):
    """Disease-specific heatmap page"""
    return render_template('disease_heatmap.html', disease=disease)

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

@app.route('/api/critical-outbreak-alerts')
def get_critical_outbreak_alerts():
    """Get critical outbreak alerts for next 24-72 hours"""
    try:
        if not ai_analyzer:
            return jsonify({"error": "AI analyzer not available"}), 500
        
        critical_alerts = ai_analyzer.predict_critical_outbreaks()
        return jsonify(critical_alerts)
    except Exception as e:
        logger.error(f"Error getting critical outbreak alerts: {e}")
        return jsonify({"error": "Failed to fetch critical outbreak alerts"}), 500

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

@app.route('/api/heatwave-data')
def get_heatwave_data():
    """Get comprehensive heatwave and disease risk data for Pakistani cities"""
    try:
        from population_data import population_db
        
        if not ai_analyzer or not weather_service:
            return jsonify({"error": "Services not available"}), 500
        
        weather_data = weather_service.get_current_weather()
        ai_predictions = ai_analyzer.analyze_disease_patterns(weather_data)
        
        heatwave_cities = []
        cities_on_alert = []
        
        for city_data in weather_data.get('cities', []):
            city_name = city_data['city']
            temperature = city_data['temperature']
            humidity = city_data['humidity']
            
            # Get real population data
            population_data = population_db.get_city_population(city_name)
            total_population = population_data.get('population', 0)
            
            # Get disease analysis from weather service
            disease_analysis = city_data.get('disease_analysis', {})
            alert_level = city_data.get('alert_level', 'low')
            
            # Calculate comprehensive disease risk score
            disease_risk_score = calculate_comprehensive_disease_risk(temperature, humidity, disease_analysis)
            
            # Get predicted diseases with risk levels
            predicted_diseases_with_risk = []
            population_at_risk_total = 0
            estimated_cases_total = 0
            
            for disease, risk_data in disease_analysis.items():
                risk_level = risk_data.get('risk_level', 'low')
                if risk_level in ['medium', 'high', 'critical', 'extreme']:
                    # Calculate population at risk and estimated cases
                    risk_factors = {
                        'high_temperature': temperature >= 35,
                        'high_humidity': humidity >= 70,
                        'extreme_heat': temperature >= 40,
                        'vector_breeding_conditions': temperature >= 25 and humidity >= 60
                    }
                    
                    pop_risk_data = population_db.calculate_population_at_risk(
                        city_name, disease, risk_factors
                    )
                    
                    if 'error' not in pop_risk_data:
                        case_estimates = population_db.estimate_disease_cases(
                            city_name, disease, temperature, humidity, risk_level
                        )
                        
                        if 'error' not in case_estimates:
                            predicted_diseases_with_risk.append({
                                'disease': disease.title(),
                                'risk_level': risk_level.title(),
                                'population_at_risk': pop_risk_data['final_risk_population'],
                                'estimated_cases_30_days': case_estimates['estimated_cases']['30_days'],
                                'factors': risk_data.get('factors', [])
                            })
                            
                            population_at_risk_total += pop_risk_data['final_risk_population']
                            estimated_cases_total += case_estimates['estimated_cases']['30_days']
            
            # Determine if city is on alert
            is_on_alert = (alert_level in ['high', 'critical', 'extreme'] or 
                          temperature >= 38 or 
                          any(d['risk_level'] in ['High', 'Critical', 'Extreme'] for d in predicted_diseases_with_risk))
            
            city_info = {
                'city': city_name,
                'temperature': temperature,
                'humidity': humidity,
                'population': total_population,
                'risk_level': alert_level.upper(),
                'disease_risk_score': round(disease_risk_score, 1),
                'population_at_risk': population_at_risk_total,
                'estimated_cases_30_days': estimated_cases_total,
                'predicted_diseases': predicted_diseases_with_risk,
                'coordinates': city_data.get('coordinates', {}),
                'is_on_alert': is_on_alert,
                'alert_reasons': get_alert_reasons(temperature, humidity, predicted_diseases_with_risk)
            }
            
            heatwave_cities.append(city_info)
            
            if is_on_alert:
                cities_on_alert.append(city_info)
        
        # Calculate national statistics
        national_stats = calculate_national_statistics(heatwave_cities)
        
        return jsonify({
            'status': 'success',
            'data': {
                'cities': heatwave_cities,
                'cities_on_alert': cities_on_alert,
                'national_statistics': national_stats,
                'last_updated': datetime.now().isoformat(),
                'ai_analysis': ai_predictions,
                'alert_summary': {
                    'total_cities_monitored': len(heatwave_cities),
                    'cities_on_alert': len(cities_on_alert),
                    'highest_risk_city': max(heatwave_cities, key=lambda x: x['disease_risk_score'])['city'] if heatwave_cities else None,
                    'total_population_at_risk': sum(city['population_at_risk'] for city in heatwave_cities),
                    'total_estimated_cases': sum(city['estimated_cases_30_days'] for city in heatwave_cities)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting heatwave data: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch heatwave data: {str(e)}'
        }), 500

# Helper functions for heatwave data processing
def calculate_comprehensive_disease_risk(temperature, humidity, disease_analysis):
    """Calculate comprehensive disease risk score"""
    base_score = min(100, (temperature - 25) * 2 + (humidity - 30) * 1.5)
    base_score = max(0, base_score)
    
    # Add disease-specific risk factors
    disease_multiplier = 1.0
    for disease, risk_data in disease_analysis.items():
        risk_level = risk_data.get('risk_level', 'low')
        if risk_level == 'extreme':
            disease_multiplier += 0.5
        elif risk_level == 'critical':
            disease_multiplier += 0.3
        elif risk_level == 'high':
            disease_multiplier += 0.2
        elif risk_level == 'medium':
            disease_multiplier += 0.1
    
    return min(100, base_score * disease_multiplier)

def get_risk_factors_from_weather(temperature, humidity):
    """Get risk factors based on weather conditions"""
    factors = []
    if temperature >= 40:
        factors.append('extreme_heat')
    elif temperature >= 35:
        factors.append('high_temperature')
    
    if humidity >= 70:
        factors.append('high_humidity')
    elif humidity <= 30:
        factors.append('low_humidity')
    
    return factors

def get_alert_reasons(temperature, humidity, predicted_diseases):
    """Get reasons for alert status"""
    reasons = []
    
    if temperature >= 42:
        reasons.append(f'Extreme temperature: {temperature}°C')
    elif temperature >= 38:
        reasons.append(f'High temperature: {temperature}°C')
    
    if humidity >= 70:
        reasons.append(f'High humidity: {humidity}%')
    
    high_risk_diseases = [d for d in predicted_diseases if d['risk_level'] in ['High', 'Critical', 'Extreme']]
    if high_risk_diseases:
        disease_names = [d['disease'] for d in high_risk_diseases]
        disease_list = ', '.join(disease_names)
        reasons.append(f'High disease risk: {disease_list}')
    
    return reasons

def calculate_national_statistics(cities_data):
    """Calculate national-level statistics"""
    if not cities_data:
        return {}
    
    total_population = sum(city['population'] for city in cities_data)
    total_at_risk = sum(city['population_at_risk'] for city in cities_data)
    total_estimated_cases = sum(city['estimated_cases_30_days'] for city in cities_data)
    
    avg_temperature = sum(city['temperature'] for city in cities_data) / len(cities_data)
    avg_humidity = sum(city['humidity'] for city in cities_data) / len(cities_data)
    avg_risk_score = sum(city['disease_risk_score'] for city in cities_data) / len(cities_data)
    
    return {
        'total_population': total_population,
        'total_population_at_risk': total_at_risk,
        'total_estimated_cases_30_days': total_estimated_cases,
        'risk_percentage': round((total_at_risk / total_population * 100) if total_population > 0 else 0, 2),
        'average_temperature': round(avg_temperature, 1),
        'average_humidity': round(avg_humidity, 1),
        'average_risk_score': round(avg_risk_score, 1),
        'cities_monitored': len(cities_data)
    }

@app.route('/api/cities-on-alert')
def get_cities_on_alert():
    """Get all cities currently on alert with detailed disease and population information"""
    try:
        from population_data import population_db
        
        weather_data = weather_service.get_current_weather()
        ai_predictions = ai_analyzer.analyze_disease_patterns(weather_data)
        
        cities_on_alert = []
        alert_summary = {
            'total_cities_on_alert': 0,
            'total_population_affected': 0,
            'total_estimated_cases': 0,
            'diseases_by_frequency': {},
            'risk_levels_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0, 'extreme': 0}
        }
        
        for city_data in weather_data.get('cities', []):
            city_name = city_data['city']
            temperature = city_data['temperature']
            humidity = city_data['humidity']
            
            # Get real population data
            population_data = population_db.get_city_population(city_name)
            total_population = population_data.get('population', 0)
            
            # Get disease analysis from weather service
            disease_analysis = city_data.get('disease_analysis', {})
            alert_level = city_data.get('alert_level', 'low')
            
            # Check if city should be on alert
            is_on_alert = False
            alert_diseases = []
            total_population_at_risk = 0
            total_estimated_cases = 0
            
            # Analyze each disease for alert conditions
            for disease, risk_data in disease_analysis.items():
                risk_level = risk_data.get('risk_level', 'low')
                
                # Alert conditions: medium risk or higher, OR specific temperature/humidity thresholds
                if (risk_level in ['medium', 'high', 'critical', 'extreme'] or 
                    temperature >= 38 or 
                    (disease == 'dengue' and temperature >= 25 and humidity >= 60) or
                    (disease == 'malaria' and temperature >= 20 and humidity >= 60) or
                    (disease == 'heat_stroke' and temperature >= 38)):
                    
                    is_on_alert = True
                    
                    # Calculate population at risk and estimated cases
                    pop_risk_data = population_db.calculate_population_at_risk(
                        city_name, disease, 
                        get_risk_factors_from_weather(temperature, humidity)
                    )
                    
                    if 'error' not in pop_risk_data:
                        case_estimates = population_db.estimate_disease_cases(
                            city_name, disease, temperature, humidity, risk_level
                        )
                        
                        if 'error' not in case_estimates:
                            population_at_risk = pop_risk_data['final_risk_population']
                            estimated_cases_30_days = case_estimates['estimated_cases']['30_days']
                            
                            alert_diseases.append({
                                'disease': disease.title(),
                                'risk_level': risk_level.title(),
                                'population_at_risk': population_at_risk,
                                'estimated_cases_30_days': estimated_cases_30_days,
                                'estimated_cases_7_days': case_estimates['estimated_cases']['7_days'],
                                'estimated_cases_90_days': case_estimates['estimated_cases']['90_days'],
                                'transmission_rate': round(case_estimates['transmission_rate'] * 100, 3),
                                'confidence_level': case_estimates['confidence_level'],
                                'contributing_factors': risk_data.get('factors', []),
                                'weather_conditions': {
                                    'temperature_impact': 'High' if temperature >= 35 else 'Medium' if temperature >= 30 else 'Low',
                                    'humidity_impact': 'High' if humidity >= 70 else 'Medium' if humidity >= 50 else 'Low'
                                }
                            })
                            
                            total_population_at_risk += population_at_risk
                            total_estimated_cases += estimated_cases_30_days
                            
                            # Update summary statistics
                            disease_name = disease.title()
                            alert_summary['diseases_by_frequency'][disease_name] = alert_summary['diseases_by_frequency'].get(disease_name, 0) + 1
            
            if is_on_alert:
                # Get vulnerable population breakdown
                vulnerable_groups = population_data.get('vulnerable_groups', {})
                
                city_alert_info = {
                    'city': city_name,
                    'province': population_data.get('province', 'Unknown'),
                    'coordinates': city_data.get('coordinates', {}),
                    'current_conditions': {
                        'temperature': temperature,
                        'humidity': humidity,
                        'weather_description': city_data.get('description', 'Unknown'),
                        'uv_index': city_data.get('uv_index', 0)
                    },
                    'population_data': {
                        'total_population': total_population,
                        'population_density': population_data.get('density_per_km2', 0),
                        'urban_population': population_data.get('urban_population', 0),
                        'rural_population': population_data.get('rural_population', 0),
                        'vulnerable_groups': vulnerable_groups,
                        'poverty_rate': population_data.get('poverty_rate', 0),
                        'healthcare_facilities': population_data.get('healthcare_facilities', 0)
                    },
                    'alert_details': {
                        'overall_risk_level': alert_level.upper(),
                        'total_population_at_risk': total_population_at_risk,
                        'total_estimated_cases_30_days': total_estimated_cases,
                        'risk_percentage': round((total_population_at_risk / total_population * 100) if total_population > 0 else 0, 2)
                    },
                    'diseases_on_alert': alert_diseases,
                    'recommendations': generate_city_recommendations(city_name, alert_diseases, temperature, humidity),
                    'last_updated': datetime.now().isoformat()
                }
                
                cities_on_alert.append(city_alert_info)
                
                # Update summary statistics
                alert_summary['total_cities_on_alert'] += 1
                alert_summary['total_population_affected'] += total_population_at_risk
                alert_summary['total_estimated_cases'] += total_estimated_cases
                alert_summary['risk_levels_distribution'][alert_level] += 1
        
        # Sort cities by risk level and estimated cases
        cities_on_alert.sort(key=lambda x: (x['alert_details']['total_estimated_cases_30_days'], x['alert_details']['total_population_at_risk']), reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'cities_on_alert': cities_on_alert,
                'alert_summary': alert_summary,
                'national_overview': {
                    'total_cities_monitored': len(weather_data.get('cities', [])),
                    'cities_on_alert': len(cities_on_alert),
                    'alert_percentage': round((len(cities_on_alert) / len(weather_data.get('cities', [])) * 100) if weather_data.get('cities') else 0, 1),
                    'most_affected_city': cities_on_alert[0]['city'] if cities_on_alert else None,
                    'dominant_diseases': sorted(alert_summary['diseases_by_frequency'].items(), key=lambda x: x[1], reverse=True)[:3]
                },
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting cities on alert: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch cities on alert: {str(e)}'
        }), 500

def generate_city_recommendations(city_name, alert_diseases, temperature, humidity):
    """Generate specific recommendations for a city based on its alert conditions"""
    recommendations = []
    
    # Temperature-based recommendations
    if temperature >= 42:
        recommendations.append({
            'category': 'Heat Emergency',
            'priority': 'Critical',
            'action': 'Activate heat emergency protocols',
            'details': 'Open cooling centers, issue public warnings, increase medical staff'
        })
    elif temperature >= 38:
        recommendations.append({
            'category': 'Heat Warning',
            'priority': 'High',
            'action': 'Issue heat wave advisory',
            'details': 'Advise public to stay indoors, increase hydration, check on vulnerable populations'
        })
    
    # Disease-specific recommendations
    for disease_info in alert_diseases:
        disease = disease_info['disease'].lower()
        risk_level = disease_info['risk_level'].lower()
        
        if disease == 'dengue' and risk_level in ['high', 'critical', 'extreme']:
            recommendations.append({
                'category': 'Vector Control',
                'priority': 'High',
                'action': 'Intensify dengue prevention measures',
                'details': 'Eliminate standing water, increase surveillance, distribute repellents, public awareness campaigns'
            })
        
        if disease == 'malaria' and risk_level in ['high', 'critical', 'extreme']:
            recommendations.append({
                'category': 'Malaria Prevention',
                'priority': 'High',
                'action': 'Deploy malaria control measures',
                'details': 'Distribute bed nets, antimalarial drugs, increase case detection and treatment'
            })
        
        if disease == 'respiratory' and risk_level in ['high', 'critical']:
            recommendations.append({
                'category': 'Respiratory Health',
                'priority': 'Medium',
                'action': 'Respiratory health advisory',
                'details': 'Advise vulnerable groups to limit outdoor activities, ensure air quality monitoring'
            })
        
        if disease == 'heat_stroke' and risk_level in ['high', 'critical', 'extreme']:
            recommendations.append({
                'category': 'Heat Safety',
                'priority': 'High',
                'action': 'Heat stroke prevention measures',
                'details': 'Establish cooling centers, public hydration stations, emergency medical preparedness'
            })
    
    return recommendations

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

@app.route('/api/heatmap')
def get_heatmap():
    """Generate weather and disease risk heatmap"""
    try:
        if not heatmap_service:
            return jsonify({"error": "Heatmap service not available"}), 500
            
        include_disease_overlay = request.args.get('disease_overlay', 'true').lower() == 'true'
        heatmap_html = heatmap_service.generate_weather_heatmap(include_disease_overlay=include_disease_overlay)
        
        return heatmap_html, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        return jsonify({"error": "Failed to generate heatmap"}), 500

@app.route('/api/disease-heatmap/<disease>')
def get_disease_heatmap(disease):
    """Generate disease-specific heatmap"""
    try:
        if not heatmap_service:
            return jsonify({"error": "Heatmap service not available"}), 500
            
        heatmap_html = heatmap_service.generate_disease_heatmap(disease)
        
        return heatmap_html, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        logger.error(f"Error generating disease heatmap for {disease}: {e}")
        return jsonify({"error": f"Failed to generate heatmap for {disease}"}), 500

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
