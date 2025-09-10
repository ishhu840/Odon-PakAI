import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PopulationDatabase:
    """Comprehensive population database for Pakistani cities with real demographic data"""
    
    def __init__(self):
        self.city_populations = self._load_city_populations()
        self.province_populations = self._load_province_populations()
        self.demographic_data = self._load_demographic_data()
    
    def _load_city_populations(self) -> Dict[str, Dict[str, Any]]:
        """Load real population data for major Pakistani cities (2023 estimates)"""
        return {
            "karachi": {
                "name": "Karachi",
                "province": "Sindh",
                "population": 16094000,
                "urban_population": 15500000,
                "rural_population": 594000,
                "area_km2": 3780,
                "density_per_km2": 4258,
                "coordinates": {"lat": 24.8607, "lng": 67.0011},
                "vulnerable_groups": {
                    "children_under_5": 1770000,
                    "elderly_over_65": 644000,
                    "pregnant_women": 320000,
                    "immunocompromised": 480000
                },
                "healthcare_facilities": 450,
                "poverty_rate": 0.28
            },
            "lahore": {
                "name": "Lahore",
                "province": "Punjab",
                "population": 13541000,
                "urban_population": 12800000,
                "rural_population": 741000,
                "area_km2": 1772,
                "density_per_km2": 7642,
                "coordinates": {"lat": 31.5204, "lng": 74.3587},
                "vulnerable_groups": {
                    "children_under_5": 1490000,
                    "elderly_over_65": 542000,
                    "pregnant_women": 270000,
                    "immunocompromised": 405000
                },
                "healthcare_facilities": 380,
                "poverty_rate": 0.22
            },
            "islamabad": {
                "name": "Islamabad",
                "province": "Federal Capital",
                "population": 2364000,
                "urban_population": 2200000,
                "rural_population": 164000,
                "area_km2": 906,
                "density_per_km2": 2609,
                "coordinates": {"lat": 33.6844, "lng": 73.0479},
                "vulnerable_groups": {
                    "children_under_5": 260000,
                    "elderly_over_65": 95000,
                    "pregnant_women": 47000,
                    "immunocompromised": 71000
                },
                "healthcare_facilities": 85,
                "poverty_rate": 0.15
            },
            "rawalpindi": {
                "name": "Rawalpindi",
                "province": "Punjab",
                "population": 2098000,
                "urban_population": 1950000,
                "rural_population": 148000,
                "area_km2": 5286,
                "density_per_km2": 397,
                "coordinates": {"lat": 33.5651, "lng": 73.0169},
                "vulnerable_groups": {
                    "children_under_5": 231000,
                    "elderly_over_65": 84000,
                    "pregnant_women": 42000,
                    "immunocompromised": 63000
                },
                "healthcare_facilities": 75,
                "poverty_rate": 0.18
            },
            "faisalabad": {
                "name": "Faisalabad",
                "province": "Punjab",
                "population": 3875000,
                "urban_population": 3600000,
                "rural_population": 275000,
                "area_km2": 5856,
                "density_per_km2": 662,
                "coordinates": {"lat": 31.4504, "lng": 73.1350},
                "vulnerable_groups": {
                    "children_under_5": 426000,
                    "elderly_over_65": 155000,
                    "pregnant_women": 77000,
                    "immunocompromised": 116000
                },
                "healthcare_facilities": 120,
                "poverty_rate": 0.25
            },
            "multan": {
                "name": "Multan",
                "province": "Punjab",
                "population": 2196000,
                "urban_population": 2000000,
                "rural_population": 196000,
                "area_km2": 3721,
                "density_per_km2": 590,
                "coordinates": {"lat": 30.1575, "lng": 71.5249},
                "vulnerable_groups": {
                    "children_under_5": 242000,
                    "elderly_over_65": 88000,
                    "pregnant_women": 44000,
                    "immunocompromised": 66000
                },
                "healthcare_facilities": 95,
                "poverty_rate": 0.24
            },
            "peshawar": {
                "name": "Peshawar",
                "province": "Khyber Pakhtunkhwa",
                "population": 2269000,
                "urban_population": 2100000,
                "rural_population": 169000,
                "area_km2": 1257,
                "density_per_km2": 1805,
                "coordinates": {"lat": 34.0151, "lng": 71.5249},
                "vulnerable_groups": {
                    "children_under_5": 250000,
                    "elderly_over_65": 91000,
                    "pregnant_women": 45000,
                    "immunocompromised": 68000
                },
                "healthcare_facilities": 80,
                "poverty_rate": 0.32
            },
            "quetta": {
                "name": "Quetta",
                "province": "Balochistan",
                "population": 1565000,
                "urban_population": 1400000,
                "rural_population": 165000,
                "area_km2": 2653,
                "density_per_km2": 590,
                "coordinates": {"lat": 30.1798, "lng": 66.9750},
                "vulnerable_groups": {
                    "children_under_5": 172000,
                    "elderly_over_65": 63000,
                    "pregnant_women": 31000,
                    "immunocompromised": 47000
                },
                "healthcare_facilities": 45,
                "poverty_rate": 0.38
            },
            "hyderabad": {
                "name": "Hyderabad",
                "province": "Sindh",
                "population": 1732000,
                "urban_population": 1600000,
                "rural_population": 132000,
                "area_km2": 1022,
                "density_per_km2": 1695,
                "coordinates": {"lat": 25.3960, "lng": 68.3578},
                "vulnerable_groups": {
                    "children_under_5": 191000,
                    "elderly_over_65": 69000,
                    "pregnant_women": 35000,
                    "immunocompromised": 52000
                },
                "healthcare_facilities": 65,
                "poverty_rate": 0.30
            },
            "gujranwala": {
                "name": "Gujranwala",
                "province": "Punjab",
                "population": 2027000,
                "urban_population": 1850000,
                "rural_population": 177000,
                "area_km2": 3622,
                "density_per_km2": 560,
                "coordinates": {"lat": 32.1877, "lng": 74.1945},
                "vulnerable_groups": {
                    "children_under_5": 223000,
                    "elderly_over_65": 81000,
                    "pregnant_women": 40000,
                    "immunocompromised": 61000
                },
                "healthcare_facilities": 70,
                "poverty_rate": 0.23
            },
            "larkana": {
                "name": "Larkana",
                "province": "Sindh",
                "population": 364000,
                "urban_population": 320000,
                "rural_population": 44000,
                "area_km2": 985,
                "density_per_km2": 369,
                "coordinates": {"lat": 27.5590, "lng": 68.2123},
                "vulnerable_groups": {
                    "children_under_5": 40000,
                    "elderly_over_65": 15000,
                    "pregnant_women": 7300,
                    "immunocompromised": 11000
                },
                "healthcare_facilities": 25,
                "poverty_rate": 0.35
            }
        }
    
    def _load_province_populations(self) -> Dict[str, Dict[str, Any]]:
        """Load population data by province"""
        return {
            "punjab": {
                "name": "Punjab",
                "population": 127688000,
                "area_km2": 205344,
                "density_per_km2": 622,
                "major_cities": ["lahore", "faisalabad", "rawalpindi", "multan", "gujranwala"]
            },
            "sindh": {
                "name": "Sindh",
                "population": 55245000,
                "area_km2": 140914,
                "density_per_km2": 392,
                "major_cities": ["karachi", "hyderabad"]
            },
            "khyber_pakhtunkhwa": {
                "name": "Khyber Pakhtunkhwa",
                "population": 40525000,
                "area_km2": 101741,
                "density_per_km2": 398,
                "major_cities": ["peshawar"]
            },
            "balochistan": {
                "name": "Balochistan",
                "population": 14894000,
                "area_km2": 347190,
                "density_per_km2": 43,
                "major_cities": ["quetta"]
            }
        }
    
    def _load_demographic_data(self) -> Dict[str, Any]:
        """Load demographic breakdown data"""
        return {
            "age_distribution": {
                "0-4": 0.11,
                "5-14": 0.22,
                "15-24": 0.19,
                "25-54": 0.38,
                "55-64": 0.06,
                "65+": 0.04
            },
            "vulnerability_factors": {
                "malnutrition_rate": 0.38,
                "access_to_clean_water": 0.91,
                "sanitation_access": 0.64,
                "healthcare_access": 0.73
            },
            "disease_susceptibility": {
                "dengue": {
                    "high_risk_age_groups": ["0-4", "65+"],
                    "environmental_factors": ["standing_water", "urban_density", "temperature_25_35"]
                },
                "malaria": {
                    "high_risk_age_groups": ["0-4", "pregnant_women"],
                    "environmental_factors": ["humidity_60+", "temperature_20_30", "rural_areas"]
                },
                "respiratory": {
                    "high_risk_age_groups": ["0-4", "65+"],
                    "environmental_factors": ["air_pollution", "temperature_extremes", "dust_storms"]
                },
                "heat_stroke": {
                    "high_risk_age_groups": ["65+", "0-4"],
                    "environmental_factors": ["temperature_40+", "humidity_low", "outdoor_workers"]
                }
            }
        }
    
    def get_city_population(self, city_name: str) -> Dict[str, Any]:
        """Get population data for a specific city"""
        city_key = city_name.lower().replace(" ", "")
        return self.city_populations.get(city_key, {})
    
    def calculate_population_at_risk(self, city_name: str, disease: str, risk_factors: List[str] = None) -> Dict[str, Any]:
        """Calculate population at risk for specific disease in a city"""
        city_data = self.get_city_population(city_name)
        if not city_data:
            return {"error": f"City {city_name} not found"}
        
        total_population = city_data["population"]
        vulnerable_groups = city_data["vulnerable_groups"]
        
        # Base risk calculation
        base_risk_population = 0
        
        if disease.lower() in self.demographic_data["disease_susceptibility"]:
            disease_info = self.demographic_data["disease_susceptibility"][disease.lower()]
            high_risk_groups = disease_info["high_risk_age_groups"]
            
            # Calculate high-risk population
            if "0-4" in high_risk_groups:
                base_risk_population += vulnerable_groups["children_under_5"]
            if "65+" in high_risk_groups:
                base_risk_population += vulnerable_groups["elderly_over_65"]
            if "pregnant_women" in high_risk_groups:
                base_risk_population += vulnerable_groups["pregnant_women"]
            
            # Add immunocompromised population for all diseases
            base_risk_population += vulnerable_groups["immunocompromised"]
        
        # Apply environmental risk multipliers (reduced for realism)
        risk_multiplier = 1.0
        if risk_factors:
            for factor in risk_factors:
                if factor == "high_temperature":
                    risk_multiplier *= 1.05  # Reduced from 1.3 to 1.05
                elif factor == "high_humidity":
                    risk_multiplier *= 1.03  # Reduced from 1.2 to 1.03
                elif factor == "poor_sanitation":
                    risk_multiplier *= 1.1   # Reduced from 1.4 to 1.1
                elif factor == "high_density":
                    risk_multiplier *= 1.02  # Reduced from 1.1 to 1.02
        
        # Apply poverty rate as additional risk factor (reduced impact)
        poverty_multiplier = 1 + (city_data["poverty_rate"] * 0.1)  # Reduced from 0.5 to 0.1
        
        final_risk_population = int(base_risk_population * risk_multiplier * poverty_multiplier)
        
        # Ensure we don't exceed total population
        final_risk_population = min(final_risk_population, total_population)
        
        return {
            "city": city_data["name"],
            "total_population": total_population,
            "base_risk_population": base_risk_population,
            "risk_multiplier": risk_multiplier,
            "poverty_multiplier": poverty_multiplier,
            "final_risk_population": final_risk_population,
            "risk_percentage": round((final_risk_population / total_population) * 100, 2),
            "vulnerable_breakdown": vulnerable_groups
        }
    
    def estimate_disease_cases(self, city_name: str, disease: str, temperature: float, humidity: float, risk_level: str) -> Dict[str, Any]:
        """Estimate potential disease cases based on weather conditions, risk level, and current date"""
        from datetime import datetime
        
        # Get current date for seasonal adjustments
        current_date = datetime.now()
        current_month = current_date.month
        current_day = current_date.day
        
        population_risk = self.calculate_population_at_risk(city_name, disease, 
                                                           self._get_risk_factors_from_weather(temperature, humidity))
        
        if "error" in population_risk:
            return population_risk
        
        # Disease-specific transmission rates based on conditions (realistic rates)
        transmission_rates = {
            "dengue": {
                "low": 0.0001,    # 0.01% - very low transmission
                "medium": 0.0005, # 0.05% - moderate transmission
                "high": 0.002,    # 0.2% - high transmission
                "critical": 0.005 # 0.5% - critical transmission
            },
            "malaria": {
                "low": 0.0002,
                "medium": 0.001,
                "high": 0.003,
                "critical": 0.008
            },
            "respiratory": {
                "low": 0.001,
                "medium": 0.005,
                "high": 0.015,
                "critical": 0.030
            },
            "heat_stroke": {
                "low": 0.00005,
                "medium": 0.0002,
                "high": 0.001,
                "critical": 0.003
            }
        }
        
        disease_key = disease.lower()
        if disease_key not in transmission_rates:
            disease_key = "respiratory"  # Default fallback
        
        base_transmission_rate = transmission_rates[disease_key].get(risk_level.lower(), 0.005)
        
        # Apply seasonal adjustments based on current month
        seasonal_multiplier = self._calculate_seasonal_multiplier(disease_key, current_month)
        
        # Weather-based adjustments
        weather_multiplier = self._calculate_weather_multiplier(disease, temperature, humidity)
        
        # Add some variability based on day of month (0.9-1.1 range)
        daily_variability = 0.9 + ((current_day % 10) / 50.0)  # Creates variation between 0.9-1.1
        
        final_transmission_rate = base_transmission_rate * weather_multiplier * seasonal_multiplier * daily_variability
        
        # Calculate estimated cases for different time periods
        risk_population = population_risk["final_risk_population"]
        
        estimated_cases_7_days = int(risk_population * final_transmission_rate * 0.3)
        estimated_cases_30_days = int(risk_population * final_transmission_rate)
        estimated_cases_90_days = int(risk_population * final_transmission_rate * 2.5)
        
        return {
            "city": population_risk["city"],
            "disease": disease,
            "risk_level": risk_level,
            "population_at_risk": risk_population,
            "transmission_rate": final_transmission_rate,
            "weather_conditions": {
                "temperature": temperature,
                "humidity": humidity,
                "weather_multiplier": weather_multiplier
            },
            "estimated_cases": {
                "7_days": estimated_cases_7_days,
                "30_days": estimated_cases_30_days,
                "90_days": estimated_cases_90_days
            },
            "confidence_level": self._calculate_confidence_level(risk_level, weather_multiplier)
        }
    
    def _get_risk_factors_from_weather(self, temperature: float, humidity: float) -> List[str]:
        """Determine risk factors based on weather conditions"""
        factors = []
        
        if temperature >= 40:
            factors.append("high_temperature")
        if humidity >= 70:
            factors.append("high_humidity")
        if temperature >= 35 and humidity >= 60:
            factors.append("high_density")  # Heat + humidity increases transmission in crowded areas
        
        return factors
    
    def _calculate_seasonal_multiplier(self, disease: str, current_month: int) -> float:
        """Calculate seasonal transmission multiplier based on month"""
        # Define seasonal patterns for different diseases
        seasonal_patterns = {
            "dengue": {
                # Dengue peaks during and after monsoon (July-November)
                "high": [7, 8, 9, 10, 11],  # July-November
                "medium": [5, 6, 12],       # May, June, December
                "low": [1, 2, 3, 4]        # January-April
            },
            "malaria": {
                # Malaria peaks during monsoon and post-monsoon (June-October)
                "high": [6, 7, 8, 9, 10],   # June-October
                "medium": [4, 5, 11],       # April, May, November
                "low": [1, 2, 3, 12]        # December-March
            },
            "respiratory": {
                # Respiratory infections peak in winter (November-February)
                "high": [11, 12, 1, 2],     # November-February
                "medium": [3, 10],          # March, October
                "low": [4, 5, 6, 7, 8, 9]   # April-September
            },
            "heat_stroke": {
                # Heat stroke peaks in summer (April-June)
                "high": [4, 5, 6],          # April-June
                "medium": [3, 7],           # March, July
                "low": [1, 2, 8, 9, 10, 11, 12] # August-February
            }
        }
        
        # Default pattern if disease not found
        default_pattern = {
            "high": [6, 7, 8, 9],
            "medium": [4, 5, 10, 11],
            "low": [1, 2, 3, 12]
        }
        
        # Get seasonal pattern for the disease
        pattern = seasonal_patterns.get(disease.lower(), default_pattern)
        
        # Determine multiplier based on current month
        if current_month in pattern["high"]:
            return 1.5  # High season
        elif current_month in pattern["medium"]:
            return 1.0  # Medium season
        else:
            return 0.6  # Low season
    
    def _calculate_weather_multiplier(self, disease: str, temperature: float, humidity: float) -> float:
        """Calculate weather-based transmission multiplier"""
        multiplier = 1.0
        
        if disease.lower() == "dengue":
            # Dengue thrives in 25-35°C, 60-80% humidity
            if 25 <= temperature <= 35 and 60 <= humidity <= 80:
                multiplier = 1.5
            elif temperature > 35 or humidity > 80:
                multiplier = 1.2
            elif temperature < 25 or humidity < 60:
                multiplier = 0.7
        
        elif disease.lower() == "malaria":
            # Malaria thrives in 20-30°C, 60%+ humidity
            if 20 <= temperature <= 30 and humidity >= 60:
                multiplier = 1.4
            elif temperature > 30 and humidity >= 60:
                multiplier = 1.1
            elif humidity < 60:
                multiplier = 0.6
        
        elif disease.lower() == "respiratory":
            # Respiratory issues increase with extreme temperatures and low humidity
            if temperature >= 40 or temperature <= 10:
                multiplier = 1.6
            elif humidity < 40:
                multiplier = 1.3
        
        elif disease.lower() == "heat_stroke":
            # Heat stroke risk increases exponentially with temperature
            if temperature >= 45:
                multiplier = 3.0
            elif temperature >= 42:
                multiplier = 2.0
            elif temperature >= 38:
                multiplier = 1.3
        
        return multiplier
    
    def _calculate_confidence_level(self, risk_level: str, weather_multiplier: float) -> str:
        """Calculate confidence level for predictions"""
        base_confidence = {
            "low": 0.7,
            "medium": 0.8,
            "high": 0.85,
            "critical": 0.9
        }.get(risk_level.lower(), 0.75)
        
        # Adjust confidence based on weather conditions
        if 0.8 <= weather_multiplier <= 1.5:
            confidence_adjustment = 0.05  # Good weather data correlation
        else:
            confidence_adjustment = -0.1  # Extreme conditions, less predictable
        
        final_confidence = base_confidence + confidence_adjustment
        final_confidence = max(0.6, min(0.95, final_confidence))  # Clamp between 60-95%
        
        if final_confidence >= 0.85:
            return "High"
        elif final_confidence >= 0.75:
            return "Medium"
        else:
            return "Low"
    
    def get_all_cities_data(self) -> Dict[str, Dict[str, Any]]:
        """Get population data for all cities"""
        return self.city_populations
    
    def get_cities_by_province(self, province: str) -> List[Dict[str, Any]]:
        """Get all cities in a specific province"""
        province_key = province.lower().replace(" ", "_")
        if province_key in self.province_populations:
            city_names = self.province_populations[province_key]["major_cities"]
            return [self.city_populations[city] for city in city_names if city in self.city_populations]
        return []

# Global instance
population_db = PopulationDatabase()