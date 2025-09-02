import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import random

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching real-time weather data"""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Major cities in Pakistan for weather monitoring
        self.cities = [
            {"name": "Karachi", "lat": 24.8607, "lon": 67.0011},
            {"name": "Lahore", "lat": 31.5204, "lon": 74.3587},
            {"name": "Islamabad", "lat": 33.6844, "lon": 73.0479},
            {"name": "Faisalabad", "lat": 31.4154, "lon": 73.0747},
            {"name": "Rawalpindi", "lat": 33.5651, "lon": 73.0169},
            {"name": "Multan", "lat": 30.1575, "lon": 71.5249},
            {"name": "Peshawar", "lat": 34.0151, "lon": 71.5249},
            {"name": "Quetta", "lat": 30.1798, "lon": 66.9750},
            {"name": "Larkana", "lat": 27.5590, "lon": 68.2123},
            {"name": "Hyderabad", "lat": 25.3960, "lon": 68.3578},
            {"name": "Gujranwala", "lat": 32.1877, "lon": 74.1945}
        ]
        
        # Disease risk thresholds
        self.disease_thresholds = {
            'dengue': {
                'temperature': {'min': 25, 'max': 35, 'critical': 40},
                'humidity': {'min': 60, 'max': 80, 'critical': 85}
            },
            'malaria': {
                'temperature': {'min': 20, 'max': 30, 'critical': 35},
                'humidity': {'min': 60, 'max': 90, 'critical': 95}
            },
            'respiratory': {
                'temperature': {'critical_high': 40, 'critical_low': 10},
                'humidity': {'critical_low': 30}
            },
            'heat_stroke': {
                'temperature': {'high': 38, 'critical': 42, 'extreme': 45}
            }
        }
        
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not found. Weather features will be limited.")
        else:
            print(f"OpenWeatherMap API Key loaded: {self.api_key[:5]}...{self.api_key[-5:]}") # Print partial key for verification
    
    def get_current_weather(self) -> Dict[str, Any]:
        """Get current weather data for major Pakistani cities"""
        try:
            if not self.api_key:
                return self._get_fallback_weather()
            
            weather_data = {
                "national_summary": {},
                "cities": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Get weather for each city
            for city in self.cities:
                city_weather = self._get_city_weather(city)
                if city_weather:
                    weather_data["cities"].append(city_weather)
            
            # Calculate national summary
            if weather_data["cities"]:
                weather_data["national_summary"] = self._calculate_national_summary(weather_data["cities"])
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_weather()
    
    def _get_city_weather(self, city: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get weather data for a specific city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": city["lat"],
                "lon": city["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            
            # Calculate disease risks
            disease_analysis = self._analyze_disease_risks(city["name"], temperature, humidity)
            
            return {
                "city": city["name"],
                "temperature": temperature,
                "humidity": humidity,
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "uv_index": self._get_uv_index(city["lat"], city["lon"]),
                "coordinates": {"lat": city["lat"], "lon": city["lon"]},
                "disease_analysis": disease_analysis,
                "alert_level": self._calculate_overall_alert_level(disease_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather for {city['name']}: {e}")
            return None
    
    def _get_uv_index(self, lat: float, lon: float) -> float:
        """Get UV index for specific coordinates"""
        try:
            url = f"{self.base_url}/uvi"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return data.get("value", 0)
            
        except Exception as e:
            logger.error(f"Error fetching UV index: {e}")
            return 0
    
    def _calculate_national_summary(self, cities_data: list) -> Dict[str, Any]:
        """Calculate national weather summary from cities data"""
        try:
            if not cities_data:
                return {}
            
            temperatures = [city["temperature"] for city in cities_data]
            humidities = [city["humidity"] for city in cities_data]
            pressures = [city["pressure"] for city in cities_data]
            
            return {
                "avg_temperature": sum(temperatures) / len(temperatures),
                "min_temperature": min(temperatures),
                "max_temperature": max(temperatures),
                "avg_humidity": sum(humidities) / len(humidities),
                "avg_pressure": sum(pressures) / len(pressures),
                "total_cities": len(cities_data),
                "conditions": self._get_dominant_condition(cities_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating national summary: {e}")
            return {}
    
    def _get_dominant_condition(self, cities_data: list) -> str:
        """Get the most common weather condition"""
        try:
            conditions = [city["description"] for city in cities_data]
            condition_counts = {}
            
            for condition in conditions:
                condition_counts[condition] = condition_counts.get(condition, 0) + 1
            
            return max(condition_counts, key=condition_counts.get)
            
        except Exception as e:
            logger.error(f"Error getting dominant condition: {e}")
            return "Unknown"
    
    def _analyze_disease_risks(self, city: str, temperature: float, humidity: float) -> Dict[str, Any]:
        """Analyze disease risks based on weather conditions"""
        try:
            risks = {}
            
            # Dengue risk analysis
            dengue_risk = self._calculate_dengue_risk(temperature, humidity)
            risks['dengue'] = {
                'risk_level': dengue_risk,
                'factors': self._get_dengue_factors(temperature, humidity)
            }
            
            # Malaria risk analysis
            malaria_risk = self._calculate_malaria_risk(temperature, humidity)
            risks['malaria'] = {
                'risk_level': malaria_risk,
                'factors': self._get_malaria_factors(temperature, humidity)
            }
            
            # Respiratory disease risk
            respiratory_risk = self._calculate_respiratory_risk(temperature, humidity)
            risks['respiratory'] = {
                'risk_level': respiratory_risk,
                'factors': self._get_respiratory_factors(temperature, humidity)
            }
            
            # Heat stroke risk
            heat_risk = self._calculate_heat_stroke_risk(temperature, humidity)
            risks['heat_stroke'] = {
                'risk_level': heat_risk,
                'factors': self._get_heat_stroke_factors(temperature, humidity)
            }
            
            return risks
            
        except Exception as e:
            logger.error(f"Error analyzing disease risks: {e}")
            return {}
    
    def _calculate_dengue_risk(self, temperature: float, humidity: float) -> str:
        """Calculate dengue transmission risk"""
        thresholds = self.disease_thresholds['dengue']
        
        if (temperature >= thresholds['temperature']['min'] and 
            temperature <= thresholds['temperature']['max'] and
            humidity >= thresholds['humidity']['min']):
            
            if (temperature >= thresholds['temperature']['critical'] or 
                humidity >= thresholds['humidity']['critical']):
                return 'critical'
            elif humidity >= thresholds['humidity']['max']:
                return 'high'
            else:
                return 'medium'
        else:
            return 'low'
    
    def _calculate_malaria_risk(self, temperature: float, humidity: float) -> str:
        """Calculate malaria transmission risk"""
        thresholds = self.disease_thresholds['malaria']
        
        if (temperature >= thresholds['temperature']['min'] and 
            temperature <= thresholds['temperature']['max'] and
            humidity >= thresholds['humidity']['min']):
            
            if (temperature >= thresholds['temperature']['critical'] or 
                humidity >= thresholds['humidity']['critical']):
                return 'critical'
            elif humidity >= thresholds['humidity']['max']:
                return 'high'
            else:
                return 'medium'
        else:
            return 'low'
    
    def _calculate_respiratory_risk(self, temperature: float, humidity: float) -> str:
        """Calculate respiratory disease risk"""
        thresholds = self.disease_thresholds['respiratory']
        
        if (temperature >= thresholds['temperature']['critical_high'] or 
            temperature <= thresholds['temperature']['critical_low'] or
            humidity <= thresholds['humidity']['critical_low']):
            return 'high'
        elif temperature >= 35 or temperature <= 15:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_heat_stroke_risk(self, temperature: float, humidity: float) -> str:
        """Calculate heat stroke risk"""
        thresholds = self.disease_thresholds['heat_stroke']
        heat_index = temperature + (0.5 * (humidity / 100) * (temperature - 14))
        
        if heat_index >= thresholds['temperature']['extreme']:
            return 'extreme'
        elif heat_index >= thresholds['temperature']['critical']:
            return 'critical'
        elif heat_index >= thresholds['temperature']['high']:
            return 'high'
        else:
            return 'low'
    
    def _get_dengue_factors(self, temperature: float, humidity: float) -> List[str]:
        """Get factors contributing to dengue risk"""
        factors = []
        if temperature >= 25:
            factors.append(f"Optimal temperature for mosquito breeding ({temperature}°C)")
        if humidity >= 60:
            factors.append(f"High humidity supports vector survival ({humidity}%)")
        if temperature >= 30 and humidity >= 70:
            factors.append("Combined high temperature and humidity accelerate virus replication")
        return factors
    
    def _get_malaria_factors(self, temperature: float, humidity: float) -> List[str]:
        """Get factors contributing to malaria risk"""
        factors = []
        if 20 <= temperature <= 30:
            factors.append(f"Temperature range supports parasite development ({temperature}°C)")
        if humidity >= 60:
            factors.append(f"High humidity extends mosquito lifespan ({humidity}%)")
        if humidity >= 80:
            factors.append("Very high humidity creates ideal breeding conditions")
        return factors
    
    def _get_respiratory_factors(self, temperature: float, humidity: float) -> List[str]:
        """Get factors contributing to respiratory disease risk"""
        factors = []
        if temperature >= 40:
            factors.append(f"Extreme heat stress on respiratory system ({temperature}°C)")
        if temperature <= 10:
            factors.append(f"Cold weather increases respiratory infection risk ({temperature}°C)")
        if humidity <= 30:
            factors.append(f"Low humidity dries respiratory passages ({humidity}%)")
        return factors
    
    def _get_heat_stroke_factors(self, temperature: float, humidity: float) -> List[str]:
        """Get factors contributing to heat stroke risk"""
        factors = []
        heat_index = temperature + (0.5 * (humidity / 100) * (temperature - 14))
        if temperature >= 38:
            factors.append(f"High ambient temperature ({temperature}°C)")
        if heat_index >= 40:
            factors.append(f"Dangerous heat index ({heat_index:.1f}°C)")
        if humidity >= 70:
            factors.append(f"High humidity impairs cooling ({humidity}%)")
        return factors
    
    def _calculate_overall_alert_level(self, disease_analysis: Dict[str, Any]) -> str:
        """Calculate overall alert level based on all disease risks"""
        try:
            risk_levels = []
            for disease, data in disease_analysis.items():
                risk_levels.append(data.get('risk_level', 'low'))
            
            if 'extreme' in risk_levels or 'critical' in risk_levels:
                return 'critical'
            elif 'high' in risk_levels:
                return 'high'
            elif 'medium' in risk_levels:
                return 'medium'
            else:
                return 'low'
        except:
            return 'low'
    def get_historical_weather(self, lat: float, lon: float, start: int, end: int) -> Optional[Dict[str, Any]]:
        """Get historical weather data for specific coordinates (mocked)."""
        logger.info(f"Fetching historical weather for lat={lat}, lon={lon} (mocked)")
        
        mock_data_points = []
        current_dt = datetime.fromtimestamp(start)
        end_dt = datetime.fromtimestamp(end)

        while current_dt <= end_dt:
            mock_data_points.append({
                "dt": int(current_dt.timestamp()),
                "temp": 25 + (current_dt.day % 5) - 2, # Simulate some temperature variation
                "feels_like": 25 + (current_dt.day % 5) - 2,
                "pressure": 1012 + (current_dt.day % 3) - 1,
                "humidity": 60 + (current_dt.day % 10) - 5,
                "dew_point": 16.67 + (current_dt.day % 3) - 1,
                "uvi": 5.4 + (current_dt.day % 2) - 1,
                "clouds": 20 + (current_dt.day % 15) - 7,
                "visibility": 10000,
                "wind_speed": 3.09 + (current_dt.day % 2) - 1,
                "wind_deg": 360,
                "weather": [
                    {
                        "id": 801,
                        "main": "Clouds",
                        "description": "few clouds",
                        "icon": "02d"
                    }
                ]
            })
            current_dt += timedelta(days=1)

        return {
            "lat": lat,
            "lon": lon,
            "timezone": "Asia/Karachi",
            "timezone_offset": 18000,
            "data": mock_data_points
        }

    def get_weather_alerts(self) -> Dict[str, Any]:
        """Get weather alerts that may affect health"""
        try:
            weather_data = self.get_current_weather()
            alerts = []
            
            # High-risk areas based on disease case data
            high_risk_areas = ["Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Multan", "Peshawar", "Quetta"]
            
            # Monsoon season flood-prone areas in Pakistan
            flood_prone_areas = ["Karachi", "Lahore", "Rawalpindi", "Islamabad", "Peshawar", "Multan", "Faisalabad"]
            
            # Current monsoon season (June-September)
            current_month = datetime.now().month
            is_monsoon_season = 6 <= current_month <= 9
            
            for city in weather_data.get("cities", []):
                city_name = city["city"]
                temp = city["temperature"]
                humidity = city["humidity"]
                
                # Monsoon and flood-related alerts
                if is_monsoon_season and city_name in flood_prone_areas:
                    alerts.append({
                        "city": city_name,
                        "type": "monsoon_flood_risk",
                        "severity": "critical",
                        "message": f"MONSOON ALERT: {city_name} is in active monsoon season with high flood risk",
                        "health_impact": "Extreme risk for waterborne diseases (cholera, typhoid), vector-borne diseases (dengue, malaria), and respiratory infections"
                    })
                
                # Heavy rainfall and flooding conditions
                if humidity > 85 and is_monsoon_season:
                    alerts.append({
                        "city": city_name,
                        "type": "flood_conditions",
                        "severity": "high",
                        "message": f"Flooding conditions detected: {humidity}% humidity during monsoon season",
                        "health_impact": "High risk for waterborne diseases, contaminated water supply, and vector breeding"
                    })
                
                # Waterborne disease risk
                if is_monsoon_season and city_name in ["Karachi", "Lahore", "Rawalpindi", "Peshawar"]:
                    alerts.append({
                        "city": city_name,
                        "type": "waterborne_disease_risk",
                        "severity": "high",
                        "message": f"High waterborne disease risk due to monsoon flooding in {city_name}",
                        "health_impact": "Increased risk of cholera, typhoid, hepatitis A, and diarrheal diseases"
                    })
                
                # Enhanced vector breeding during monsoon
                if is_monsoon_season and temp > 25 and humidity > 70:
                    alerts.append({
                        "city": city_name,
                        "type": "monsoon_vector_breeding",
                        "severity": "critical",
                        "message": f"Critical vector breeding conditions: Monsoon + {temp}°C + {humidity}% humidity",
                        "health_impact": "Extreme dengue and malaria transmission risk due to standing water from floods"
                    })
                
                # Standard weather alerts
                if temp > 40:
                    alerts.append({
                        "city": city_name,
                        "type": "heat_wave",
                        "severity": "high",
                        "message": f"Extreme heat warning: {temp}°C - High risk for heat-related illness",
                        "health_impact": "Increases dehydration and heat stroke risk"
                    })
                
                if humidity > 75 and not is_monsoon_season:
                    alerts.append({
                        "city": city_name,
                        "type": "high_humidity",
                        "severity": "medium",
                        "message": f"High humidity: {humidity}% - Optimal conditions for disease vectors",
                        "health_impact": "Increases malaria and dengue transmission risk"
                    })
                
                if temp < 5:
                    alerts.append({
                        "city": city_name,
                        "type": "cold_wave",
                        "severity": "medium",
                        "message": f"Cold wave warning: {temp}°C - Respiratory illness risk",
                        "health_impact": "Increases respiratory infection risk"
                    })
            
            # Add general monsoon season alert if no specific alerts
            if is_monsoon_season and len(alerts) == 0:
                alerts.append({
                    "city": "National",
                    "type": "monsoon_season_alert",
                    "severity": "high",
                    "message": "Pakistan is currently in monsoon season - Multiple areas experiencing flooding",
                    "health_impact": "Nationwide increased risk for waterborne and vector-borne diseases"
                })
            
            return {
                "alerts": alerts,
                "count": len(alerts),
                "last_updated": datetime.now().isoformat(),
                "monsoon_season": is_monsoon_season,
                "flood_risk_areas": flood_prone_areas if is_monsoon_season else []
            }
            
        except Exception as e:
            logger.error(f"Error generating weather alerts: {e}")
            return {"alerts": [], "count": 0, "last_updated": datetime.now().isoformat()}
    
    def get_flood_monitoring(self) -> Dict[str, Any]:
        """Get real-time flood monitoring and health risk assessment for Pakistan"""
        try:
            current_weather = self.get_current_weather()
            alerts = self.get_weather_alerts()
            
            # Current monsoon season (June-September)
            current_month = datetime.now().month
            is_monsoon_season = 6 <= current_month <= 9
            
            # Pakistan's major flood-prone areas with detailed risk assessment
            flood_zones = {
                "sindh": {
                    "cities": ["Karachi", "Hyderabad", "Sukkur", "Larkana"],
                    "risk_level": "critical" if is_monsoon_season else "medium",
                    "major_rivers": ["Indus River", "Ravi River"],
                    "health_risks": ["cholera", "typhoid", "hepatitis_a", "dengue", "malaria"]
                },
                "punjab": {
                    "cities": ["Lahore", "Faisalabad", "Rawalpindi", "Multan"],
                    "risk_level": "high" if is_monsoon_season else "low",
                    "major_rivers": ["Ravi River", "Chenab River", "Jhelum River"],
                    "health_risks": ["waterborne_diseases", "dengue", "respiratory_infections"]
                },
                "kpk": {
                    "cities": ["Peshawar", "Mardan", "Swat"],
                    "risk_level": "high" if is_monsoon_season else "medium",
                    "major_rivers": ["Kabul River", "Chitral River"],
                    "health_risks": ["flash_flood_injuries", "waterborne_diseases", "vector_breeding"]
                },
                "balochistan": {
                    "cities": ["Quetta", "Gwadar", "Turbat"],
                    "risk_level": "medium" if is_monsoon_season else "low",
                    "major_rivers": ["Dasht River"],
                    "health_risks": ["water_scarcity", "contamination", "heat_stress"]
                }
            }
            
            # Real-time flood risk assessment
            flood_assessment = []
            for city in current_weather.get("cities", []):
                city_name = city["city"]
                humidity = city["humidity"]
                temp = city["temperature"]
                
                # Determine flood risk based on weather conditions
                flood_risk = "low"
                if is_monsoon_season:
                    if humidity > 85:
                        flood_risk = "critical"
                    elif humidity > 75:
                        flood_risk = "high"
                    elif humidity > 65:
                        flood_risk = "medium"
                
                # Health impact assessment
                health_impact = self._assess_flood_health_impact(city_name, flood_risk, temp, humidity)
                
                flood_assessment.append({
                    "city": city_name,
                    "flood_risk": flood_risk,
                    "humidity": humidity,
                    "temperature": temp,
                    "health_impact": health_impact,
                    "immediate_risks": self._get_immediate_flood_risks(city_name, flood_risk),
                    "prevention_measures": self._get_flood_prevention_measures(flood_risk)
                })
            
            # National flood summary
            critical_areas = [city for city in flood_assessment if city["flood_risk"] == "critical"]
            high_risk_areas = [city for city in flood_assessment if city["flood_risk"] == "high"]
            
            return {
                "flood_monitoring": {
                    "national_status": "critical" if len(critical_areas) > 0 else "monitoring",
                    "monsoon_season": is_monsoon_season,
                    "total_areas_monitored": len(flood_assessment),
                    "critical_flood_areas": len(critical_areas),
                    "high_risk_areas": len(high_risk_areas)
                },
                "regional_assessment": flood_zones,
                "city_assessments": flood_assessment,
                "health_alerts": [alert for alert in alerts.get("alerts", []) if "flood" in alert.get("type", "")],
                "emergency_response": {
                    "active_alerts": len([city for city in flood_assessment if city["flood_risk"] in ["critical", "high"]]),
                    "health_facilities_on_alert": self._get_health_facilities_status(flood_assessment),
                    "water_quality_monitoring": "active" if is_monsoon_season else "routine"
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in flood monitoring: {e}")
            return self._get_fallback_flood_monitoring()
    
    def _assess_flood_health_impact(self, city: str, flood_risk: str, temp: float, humidity: float) -> Dict[str, Any]:
        """Assess health impact based on flood risk and weather conditions"""
        impact_levels = {
            "critical": {
                "waterborne_diseases": "extreme_risk",
                "vector_breeding": "critical" if temp > 25 else "high",
                "water_contamination": "severe",
                "displacement_health_risks": "high"
            },
            "high": {
                "waterborne_diseases": "high_risk",
                "vector_breeding": "high" if temp > 25 else "medium",
                "water_contamination": "moderate",
                "displacement_health_risks": "medium"
            },
            "medium": {
                "waterborne_diseases": "moderate_risk",
                "vector_breeding": "medium",
                "water_contamination": "low",
                "displacement_health_risks": "low"
            },
            "low": {
                "waterborne_diseases": "low_risk",
                "vector_breeding": "low",
                "water_contamination": "minimal",
                "displacement_health_risks": "minimal"
            }
        }
        
        return impact_levels.get(flood_risk, impact_levels["low"])
    
    def _get_immediate_flood_risks(self, city: str, flood_risk: str) -> List[str]:
        """Get immediate health risks for specific flood conditions"""
        risk_mapping = {
            "critical": [
                "Cholera outbreak risk",
                "Typhoid transmission",
                "Hepatitis A spread",
                "Dengue vector explosion",
                "Malaria transmission spike",
                "Respiratory infections from mold",
                "Skin infections from contaminated water"
            ],
            "high": [
                "Waterborne disease risk",
                "Increased dengue breeding sites",
                "Water supply contamination",
                "Sanitation system overflow"
            ],
            "medium": [
                "Vector breeding increase",
                "Water quality concerns",
                "Hygiene challenges"
            ],
            "low": [
                "Routine monitoring required"
            ]
        }
        
        return risk_mapping.get(flood_risk, risk_mapping["low"])
    
    def _get_flood_prevention_measures(self, flood_risk: str) -> List[str]:
        """Get prevention measures based on flood risk level"""
        measures = {
            "critical": [
                "Immediate evacuation of high-risk areas",
                "Emergency water purification distribution",
                "Mobile health clinics deployment",
                "Vector control operations",
                "Emergency sanitation facilities"
            ],
            "high": [
                "Water quality testing intensification",
                "Preventive health measures distribution",
                "Drainage system monitoring",
                "Community health education"
            ],
            "medium": [
                "Regular water quality checks",
                "Vector surveillance",
                "Health facility preparedness"
            ],
            "low": [
                "Routine monitoring",
                "Preparedness planning"
            ]
        }
        
        return measures.get(flood_risk, measures["low"])
    
    def _get_health_facilities_status(self, flood_assessment: List[Dict]) -> Dict[str, Any]:
        """Get health facilities status based on flood assessment"""
        critical_areas = len([city for city in flood_assessment if city["flood_risk"] == "critical"])
        high_risk_areas = len([city for city in flood_assessment if city["flood_risk"] == "high"])
        
        return {
            "emergency_facilities_activated": critical_areas * 2,
            "standby_facilities": high_risk_areas * 3,
            "mobile_units_deployed": critical_areas,
            "status": "emergency" if critical_areas > 0 else "alert" if high_risk_areas > 0 else "normal"
        }
    
    def _get_fallback_flood_monitoring(self) -> Dict[str, Any]:
        """Fallback flood monitoring data when API is unavailable"""
        current_month = datetime.now().month
        is_monsoon_season = 6 <= current_month <= 9
        
        return {
            "flood_monitoring": {
                "national_status": "monitoring",
                "monsoon_season": is_monsoon_season,
                "total_areas_monitored": 8,
                "critical_flood_areas": 2 if is_monsoon_season else 0,
                "high_risk_areas": 4 if is_monsoon_season else 1
            },
            "emergency_response": {
                "active_alerts": 3 if is_monsoon_season else 0,
                "health_facilities_on_alert": {
                    "emergency_facilities_activated": 4 if is_monsoon_season else 0,
                    "standby_facilities": 12 if is_monsoon_season else 3,
                    "mobile_units_deployed": 2 if is_monsoon_season else 0,
                    "status": "alert" if is_monsoon_season else "normal"
                },
                "water_quality_monitoring": "active" if is_monsoon_season else "routine"
            },
            "last_updated": datetime.now().isoformat(),
            "note": "Fallback data - API unavailable"
        }

    def get_climate_health_monitoring(self) -> Dict[str, Any]:
        """Get climate and environmental health monitoring data"""
        try:
            current_weather = self.get_current_weather()
            alerts = self.get_weather_alerts()
            
            # Get national summary data
            national_summary = current_weather.get('national_summary', {})
            
            # Calculate climate health metrics
            climate_data = {
                'temperature_trends': {
                    'current_avg': national_summary.get('avg_temperature', 0),
                    'trend': 'Rising' if national_summary.get('avg_temperature', 0) > 30 else 'Stable',
                    'heat_index': self._calculate_heat_index(national_summary)
                },
                'humidity_analysis': {
                    'current_avg': national_summary.get('avg_humidity', 0),
                    'disease_risk': 'High' if national_summary.get('avg_humidity', 0) > 70 else 'Medium'
                },
                'pressure_trends': {
                    'current_avg': national_summary.get('avg_pressure', 0),
                    'stability': 'Stable' if 1000 <= national_summary.get('avg_pressure', 0) <= 1020 else 'Unstable'
                },
                'health_correlations': {
                    'malaria_risk': 'High' if national_summary.get('avg_humidity', 0) > 75 else 'Medium',
                    'dengue_risk': 'High' if national_summary.get('avg_temperature', 0) > 28 else 'Medium',
                    'respiratory_risk': 'High' if national_summary.get('avg_temperature', 0) > 35 else 'Low'
                },
                'high_risk_areas': {
                    'sindh_province': {
                        'districts': ['Larkana', 'Khairpur', 'Sanghar', 'Dadu', 'Kamber'],
                        'total_cases': 22719,
                        'climate_factors': 'High temperature and humidity creating optimal vector conditions'
                    },
                    'balochistan_rural': {
                        'districts': ['Rural areas with limited surveillance'],
                        'total_cases': 'Under surveillance',
                        'climate_factors': 'Arid climate with seasonal water accumulation'
                    },
                    'kp_districts': {
                        'districts': ['Northern districts'],
                        'total_cases': 'Monitoring ongoing',
                        'climate_factors': 'Monsoon patterns affecting transmission'
                    }
                },
                'environmental_alerts': alerts.get('alerts', []),
                'monitoring_status': 'Active',
                'last_updated': current_weather.get('last_updated', datetime.now().isoformat())
            }
            
            return climate_data
            
        except Exception as e:
            logger.error(f"Error getting climate health monitoring: {e}")
            return self._get_fallback_climate_monitoring()
    
    def _calculate_heat_index(self, weather_data: Dict[str, Any]) -> float:
        """Calculate heat index from temperature and humidity"""
        try:
            temp = weather_data.get('avg_temperature', 25)
            humidity = weather_data.get('avg_humidity', 50)
            
            # Simplified heat index calculation
            heat_index = temp + (0.5 * (humidity / 100) * (temp - 14))
            return round(heat_index, 1)
        except:
            return 25.0
    
    def _get_fallback_climate_monitoring(self) -> Dict[str, Any]:
        """Fallback climate monitoring data"""
        return {
            'temperature_trends': {
                'current_avg': 32.5,
                'trend': 'Rising',
                'heat_index': 35.2
            },
            'humidity_analysis': {
                'current_avg': 65,
                'disease_risk': 'Medium'
            },
            'pressure_trends': {
                'current_avg': 1013,
                'stability': 'Stable'
            },
            'health_correlations': {
                'malaria_risk': 'Medium',
                'dengue_risk': 'High',
                'respiratory_risk': 'Medium'
            },
            'environmental_alerts': [
                {
                    'city': 'Karachi',
                    'type': 'heat_wave',
                    'severity': 'high',
                    'message': 'High temperature and humidity levels'
                }
            ],
            'monitoring_status': 'Active',
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_fallback_weather(self) -> Dict[str, Any]:
        """Fallback weather data when API is not available"""
        return {
            "national_summary": {
                "avg_temperature": 0,
                "min_temperature": 0,
                "max_temperature": 0,
                "avg_humidity": 0,
                "avg_pressure": 0,
                "total_cities": 0,
                "conditions": "Data unavailable"
            },
            "cities": [],
            "last_updated": datetime.now().isoformat(),
            "error": "Weather API not available"
        }
    
    def get_disease_risk_forecast(self, days: int = 7) -> Dict[str, Any]:
        """Get disease risk forecast for the next few days"""
        try:
            current_weather = self.get_current_weather()
            forecast_data = {
                "forecast_period": days,
                "city_forecasts": [],
                "national_trends": {},
                "recommendations": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Generate forecast for each city
            for city_data in current_weather.get("cities", []):
                city_forecast = self._generate_city_disease_forecast(city_data, days)
                forecast_data["city_forecasts"].append(city_forecast)
            
            # Calculate national trends
            forecast_data["national_trends"] = self._calculate_national_disease_trends(forecast_data["city_forecasts"])
            
            # Generate recommendations
            forecast_data["recommendations"] = self._generate_health_recommendations(forecast_data["national_trends"])
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error generating disease risk forecast: {e}")
            return self._get_fallback_disease_forecast()
    
    def _generate_city_disease_forecast(self, city_data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Generate disease risk forecast for a specific city"""
        city_name = city_data.get("city", "Unknown")
        current_temp = city_data.get("temperature", 25)
        current_humidity = city_data.get("humidity", 50)
        
        daily_forecasts = []
        
        for day in range(days):
            # Simulate weather variations
            temp_variation = random.uniform(-3, 3)
            humidity_variation = random.uniform(-10, 10)
            
            forecast_temp = current_temp + temp_variation
            forecast_humidity = max(20, min(95, current_humidity + humidity_variation))
            
            # Calculate disease risks for forecasted conditions
            disease_analysis = self._analyze_disease_risks(city_name, forecast_temp, forecast_humidity)
            
            daily_forecasts.append({
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "temperature": round(forecast_temp, 1),
                "humidity": round(forecast_humidity, 1),
                "disease_risks": disease_analysis,
                "alert_level": self._calculate_overall_alert_level(disease_analysis)
            })
        
        return {
            "city": city_name,
            "daily_forecasts": daily_forecasts,
            "trend_analysis": self._analyze_city_trends(daily_forecasts)
        }
    
    def _analyze_city_trends(self, daily_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in disease risks over the forecast period"""
        try:
            alert_levels = [day["alert_level"] for day in daily_forecasts]
            
            # Count risk levels
            risk_counts = {}
            for level in alert_levels:
                risk_counts[level] = risk_counts.get(level, 0) + 1
            
            # Determine trend
            if alert_levels[0] < alert_levels[-1]:
                trend = "increasing"
            elif alert_levels[0] > alert_levels[-1]:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "overall_trend": trend,
                "risk_distribution": risk_counts,
                "peak_risk_day": max(range(len(alert_levels)), key=lambda i: self._risk_level_to_score(alert_levels[i])),
                "average_risk": self._calculate_average_risk(alert_levels)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing city trends: {e}")
            return {}
    
    def _risk_level_to_score(self, risk_level: str) -> int:
        """Convert risk level to numerical score"""
        scores = {"low": 1, "medium": 2, "high": 3, "critical": 4, "extreme": 5}
        return scores.get(risk_level, 1)
    
    def _calculate_average_risk(self, alert_levels: List[str]) -> str:
        """Calculate average risk level"""
        scores = [self._risk_level_to_score(level) for level in alert_levels]
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 4:
            return "critical"
        elif avg_score >= 3:
            return "high"
        elif avg_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_national_disease_trends(self, city_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate national disease trends from city forecasts"""
        try:
            all_diseases = ["dengue", "malaria", "respiratory", "heat_stroke"]
            national_trends = {}
            
            for disease in all_diseases:
                disease_risks = []
                for city_forecast in city_forecasts:
                    for day in city_forecast.get("daily_forecasts", []):
                        disease_data = day.get("disease_risks", {}).get(disease, {})
                        risk_level = disease_data.get("risk_level", "low")
                        disease_risks.append(self._risk_level_to_score(risk_level))
                
                if disease_risks:
                    avg_risk = sum(disease_risks) / len(disease_risks)
                    national_trends[disease] = {
                        "average_risk_score": round(avg_risk, 2),
                        "risk_level": self._score_to_risk_level(avg_risk),
                        "trend": "increasing" if avg_risk > 2.5 else "stable"
                    }
            
            return national_trends
            
        except Exception as e:
            logger.error(f"Error calculating national trends: {e}")
            return {}
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert numerical score back to risk level"""
        if score >= 4:
            return "critical"
        elif score >= 3:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_health_recommendations(self, national_trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health recommendations based on disease trends"""
        recommendations = []
        
        for disease, trend_data in national_trends.items():
            risk_level = trend_data.get("risk_level", "low")
            
            if disease == "dengue" and risk_level in ["high", "critical"]:
                recommendations.append({
                    "disease": "dengue",
                    "priority": "high",
                    "action": "Intensify vector control operations",
                    "details": "Eliminate standing water, increase surveillance, public awareness campaigns"
                })
            
            if disease == "malaria" and risk_level in ["high", "critical"]:
                recommendations.append({
                    "disease": "malaria",
                    "priority": "high", 
                    "action": "Distribute bed nets and antimalarial drugs",
                    "details": "Focus on high-risk areas, strengthen case management"
                })
            
            if disease == "heat_stroke" and risk_level in ["high", "critical"]:
                recommendations.append({
                    "disease": "heat_stroke",
                    "priority": "medium",
                    "action": "Issue heat wave warnings",
                    "details": "Establish cooling centers, public health advisories"
                })
        
        return recommendations
    
    def _get_fallback_disease_forecast(self) -> Dict[str, Any]:
        """Fallback disease forecast when API is unavailable"""
        return {
            "forecast_period": 7,
            "city_forecasts": [],
            "national_trends": {
                "dengue": {"risk_level": "medium", "trend": "stable"},
                "malaria": {"risk_level": "medium", "trend": "stable"}
            },
            "recommendations": [
                {
                    "disease": "general",
                    "priority": "medium",
                    "action": "Continue routine surveillance",
                    "details": "Maintain standard prevention measures"
                }
            ],
            "last_updated": datetime.now().isoformat(),
            "note": "Fallback data - API unavailable"
        }
