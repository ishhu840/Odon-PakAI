import folium
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from weather_service import WeatherService
from population_data import PopulationDatabase

logger = logging.getLogger(__name__)

class HeatmapService:
    """Service for generating Pakistan weather and disease risk heatmaps"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        try:
            self.population_db = PopulationDatabase()
        except Exception as e:
            logger.warning(f"Could not initialize population database: {e}")
            self.population_db = None
        
        # Pakistan geographical bounds
        self.pakistan_bounds = {
            'north': 37.0841,
            'south': 23.6345,
            'east': 77.8375,
            'west': 60.8742
        }
        
        # Center of Pakistan for map initialization
        self.pakistan_center = [30.3753, 69.3451]
        
        # Risk level color mapping
        self.risk_colors = {
            'low': '#28a745',      # Green
            'medium': '#ffc107',   # Yellow
            'high': '#fd7e14',     # Orange
            'critical': '#dc3545'  # Red
        }
        
        # Disease icons
        self.disease_icons = {
            'dengue': 'bug',
            'malaria': 'tint',
            'respiratory': 'lungs',
            'heat_stroke': 'thermometer-full'
        }
    
    def generate_weather_heatmap(self, include_disease_overlay: bool = True) -> str:
        """Generate comprehensive Pakistan weather heatmap with optional disease risk overlay"""
        try:
            # Get current weather data
            weather_data = self.weather_service.get_current_weather()
            
            # Create base map focused on Pakistan with robust tile handling
            m = folium.Map(
                location=self.pakistan_center,
                zoom_start=6,
                tiles=None,  # Start with no tiles to avoid initial loading errors
                prefer_canvas=True,
                control_scale=True
            )
        
        # Add primary tile layer with minimal external requests
            try:
                # Use a simple, reliable tile source with reduced zoom levels to minimize requests
                folium.TileLayer(
                    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    attr='© OpenStreetMap contributors',
                    name='OpenStreetMap',
                    overlay=False,
                    control=True,
                    max_zoom=10,  # Reduced max zoom to minimize tile requests
                    min_zoom=4,
                    subdomains='abc',
                    detect_retina=False  # Disable retina tiles to reduce requests
                ).add_to(m)
            except Exception as e:
                logger.warning(f"Failed to add OpenStreetMap tiles: {e}")
                # Fallback to basic tiles with no external requests
                try:
                    folium.TileLayer(
                        tiles='OpenStreetMap',
                        name='Basic Map',
                        overlay=False,
                        control=True,
                        max_zoom=8
                    ).add_to(m)
                except Exception as fallback_e:
                    logger.error(f"Failed to add fallback tiles: {fallback_e}")
                    # Create a minimal map without external tiles
                    pass
            
            # Skip additional tile layers to prevent network errors
            # Only use the primary OpenStreetMap layer to minimize external requests
            
            # Set map bounds to focus on Pakistan
            m.fit_bounds([[23.5, 60.5], [37.5, 78.0]])
            
            # Add Pakistan boundary (approximate)
            self._add_pakistan_boundary(m)
            
            # Add weather data points
            self._add_weather_markers(m, weather_data.get('cities', []))
            
            # Add temperature heatmap layer
            self._add_temperature_heatmap(m, weather_data.get('cities', []))
            
            if include_disease_overlay:
                # Add disease risk overlay
                self._add_disease_risk_overlay(m, weather_data.get('cities', []))
            
            # Add legend
            self._add_legend(m, include_disease_overlay)
            
            # Add title
            title_html = '''
                <h3 align="center" style="font-size:20px"><b>Pakistan Weather & Disease Risk Monitoring</b></h3>
                <p align="center" style="font-size:12px">Real-time weather conditions and disease outbreak risk assessment</p>
                <p align="center" style="font-size:10px">Last updated: {}</p>
            '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Convert to HTML string
            return m._repr_html_()
            
        except Exception as e:
            logger.error(f"Error generating weather heatmap: {e}")
            return self._generate_fallback_heatmap()
    
    def _add_pakistan_boundary(self, m: folium.Map) -> None:
        """Add Pakistan country boundary to the map with enhanced visibility"""
        # More accurate Pakistan boundary coordinates
        pakistan_coords = [
            [37.084, 74.872],   # Northern Kashmir
            [36.908, 75.406],   # Northeast
            [35.282, 77.838],   # Eastern border with India
            [32.188, 77.838],   # Punjab eastern border
            [30.158, 76.838],   # Eastern Punjab
            [28.614, 75.838],   # Rajasthan border
            [26.396, 70.358],   # Sindh eastern border
            [25.396, 69.358],   # Lower Sindh
            [24.861, 67.001],   # Karachi area
            [23.635, 66.975],   # Southern coast
            [24.635, 62.975],   # Balochistan coast
            [25.396, 61.874],   # Western Balochistan
            [26.614, 60.874],   # Iran border
            [28.614, 60.874],   # Western border
            [30.180, 61.874],   # Afghanistan border
            [32.188, 60.874],   # Northern Afghanistan border
            [34.282, 69.838],   # KPK western border
            [35.282, 71.838],   # Northern KPK
            [36.282, 73.838],   # Northern areas
            [37.084, 74.872]    # Back to start
        ]
        
        # Add main Pakistan boundary
        folium.Polygon(
            locations=pakistan_coords,
            color='#2E8B57',
            weight=3,
            fill=True,
            fillColor='#90EE90',
            fillOpacity=0.1,
            popup='<b>Pakistan</b><br>Islamic Republic of Pakistan',
            tooltip='Pakistan Boundary'
        ).add_to(m)
        
        # Add province boundaries for better visualization
        self._add_province_boundaries(m)
    
    def _add_province_boundaries(self, m: folium.Map) -> None:
        """Add province boundaries for better regional visualization"""
        # Punjab boundary (simplified)
        punjab_coords = [
            [32.188, 77.838], [30.158, 76.838], [28.614, 75.838],
            [29.614, 72.838], [31.188, 72.838], [32.188, 74.838], [32.188, 77.838]
        ]
        
        # Sindh boundary (simplified)
        sindh_coords = [
            [28.614, 75.838], [26.396, 70.358], [25.396, 69.358],
            [24.861, 67.001], [23.635, 66.975], [24.635, 62.975],
            [26.614, 68.874], [28.614, 70.838], [28.614, 75.838]
        ]
        
        # KPK boundary (simplified)
        kpk_coords = [
            [32.188, 72.838], [34.282, 69.838], [35.282, 71.838],
            [36.282, 73.838], [35.282, 75.838], [32.188, 74.838], [32.188, 72.838]
        ]
        
        # Balochistan boundary (simplified)
        balochistan_coords = [
            [28.614, 70.838], [26.614, 68.874], [24.635, 62.975],
            [25.396, 61.874], [28.614, 60.874], [30.180, 61.874],
            [32.188, 60.874], [32.188, 72.838], [28.614, 70.838]
        ]
        
        provinces = [
            {'coords': punjab_coords, 'name': 'Punjab', 'color': '#FF6B6B'},
            {'coords': sindh_coords, 'name': 'Sindh', 'color': '#4ECDC4'},
            {'coords': kpk_coords, 'name': 'Khyber Pakhtunkhwa', 'color': '#45B7D1'},
            {'coords': balochistan_coords, 'name': 'Balochistan', 'color': '#96CEB4'}
        ]
        
        for province in provinces:
            folium.Polygon(
                locations=province['coords'],
                color=province['color'],
                weight=1,
                fill=True,
                fillColor=province['color'],
                fillOpacity=0.05,
                popup=f"<b>{province['name']}</b>",
                tooltip=province['name']
            ).add_to(m)
    
    def _add_weather_markers(self, m: folium.Map, cities: List[Dict[str, Any]]) -> None:
        """Add weather markers for each city"""
        for city in cities:
            try:
                coords = city.get('coordinates', {})
                if not coords:
                    continue
                
                lat = coords.get('lat')
                lon = coords.get('lon')
                
                if lat is None or lon is None:
                    continue
                
                # Determine marker color based on alert level
                alert_level = city.get('alert_level', 'low')
                color = self.risk_colors.get(alert_level, '#28a745')
                
                # Create popup content
                popup_content = self._create_weather_popup(city)
                
                # Add marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=15,
                    popup=folium.Popup(popup_content, max_width=300),
                    color='white',
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.8
                ).add_to(m)
                
                # Add city label
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 12px; font-weight: bold; color: black; text-shadow: 1px 1px 1px white;">{city.get("city", "Unknown")}</div>',
                        icon_size=(100, 20),
                        icon_anchor=(50, 10)
                    )
                ).add_to(m)
                
            except Exception as e:
                logger.error(f"Error adding weather marker for city: {e}")
    
    def _add_temperature_heatmap(self, m: folium.Map, cities: List[Dict[str, Any]]) -> None:
        """Add enhanced temperature heatmap layer with better visibility and error handling"""
        try:
            from folium.plugins import HeatMap
            
            heat_data = []
            for city in cities:
                coords = city.get('coordinates', {})
                lat = coords.get('lat')
                lon = coords.get('lon')
                temp = city.get('temperature', 25)
                
                # Validate coordinates and temperature
                if lat is not None and lon is not None:
                    if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
                        continue
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        continue
                    if not isinstance(temp, (int, float)) or temp < -50 or temp > 60:
                        temp = 25  # Default temperature
                    
                    # Enhanced temperature normalization for better visibility
                    # Scale: 15°C (cool) to 50°C (extreme heat)
                    intensity = max(0.1, min(1.0, (temp - 15) / 35))
                    
                    # Add multiple points around each city for better heat spread
                    offsets = [
                        [0, 0],           # Center
                        [0.1, 0.1],       # NE
                        [0.1, -0.1],      # NW
                        [-0.1, 0.1],      # SE
                        [-0.1, -0.1],     # SW
                        [0.05, 0],        # E
                        [-0.05, 0],       # W
                        [0, 0.05],        # N
                        [0, -0.05]        # S
                    ]
                    
                    for offset_lat, offset_lon in offsets:
                        new_lat = lat + offset_lat
                        new_lon = lon + offset_lon
                        # Ensure coordinates are still valid after offset
                        if -90 <= new_lat <= 90 and -180 <= new_lon <= 180:
                            heat_data.append([
                                new_lat, 
                                new_lon, 
                                intensity * (0.8 if offset_lat == 0 and offset_lon == 0 else 0.6)
                            ])
            
            if heat_data:
                try:
                    # Create heatmap with enhanced visibility
                    heatmap = HeatMap(
                        heat_data,
                        min_opacity=0.4,
                        max_zoom=18,
                        radius=100,
                        blur=30,
                        gradient={
                            0.0: '#313695',   # Deep blue
                            0.2: '#4575b4',   # Blue
                            0.4: '#74add1',   # Light blue
                            0.6: '#fee090',   # Light yellow
                            0.8: '#f46d43',   # Orange
                            1.0: '#a50026'    # Deep red
                        },
                        name='Temperature Heatmap'
                    )
                    heatmap.add_to(m)
                    logger.info(f"Added temperature heatmap with {len(heat_data)} data points")
                    
                    # Add simplified layer control with error handling
                    try:
                        if len([layer for layer in m._children.values() if hasattr(layer, '_name')]) > 1:
                            folium.LayerControl(
                                position='topright',
                                collapsed=True,  # Start collapsed to reduce initial load
                                autoZIndex=True
                            ).add_to(m)
                    except Exception as e:
                        logger.warning(f"Failed to add layer control: {e}")
                        
                except Exception as e:
                    logger.error(f"Error creating heatmap layer: {e}")
            else:
                logger.warning("No valid temperature data for heatmap")
                
        except ImportError:
            logger.warning("HeatMap plugin not available, skipping temperature heatmap")
        except Exception as e:
            logger.error(f"Error adding temperature heatmap: {e}")
    
    def _add_disease_risk_overlay(self, m: folium.Map, cities: List[Dict[str, Any]]) -> None:
        """Add disease risk overlay markers"""
        for city in cities:
            try:
                coords = city.get('coordinates', {})
                lat = coords.get('lat')
                lon = coords.get('lon')
                
                if lat is None or lon is None:
                    continue
                
                disease_analysis = city.get('disease_analysis', {})
                
                # Add disease risk indicators around the main marker
                offset = 0.05  # Small offset for disease markers
                positions = [
                    [lat + offset, lon + offset],      # Top-right
                    [lat + offset, lon - offset],      # Top-left
                    [lat - offset, lon + offset],      # Bottom-right
                    [lat - offset, lon - offset]       # Bottom-left
                ]
                
                disease_list = ['dengue', 'malaria', 'respiratory', 'heat_stroke']
                
                for i, disease in enumerate(disease_list):
                    if i < len(positions) and disease in disease_analysis:
                        risk_data = disease_analysis[disease]
                        risk_level = risk_data.get('risk_level', 'low')
                        
                        if risk_level in ['high', 'critical']:
                            color = self.risk_colors.get(risk_level, '#28a745')
                            
                            folium.CircleMarker(
                                location=positions[i],
                                radius=8,
                                popup=f"{disease.title()}: {risk_level.title()}",
                                color='white',
                                weight=1,
                                fillColor=color,
                                fillOpacity=0.9
                            ).add_to(m)
                            
            except Exception as e:
                logger.error(f"Error adding disease risk overlay: {e}")
    
    def _create_weather_popup(self, city: Dict[str, Any]) -> str:
        """Create detailed popup content for weather markers"""
        try:
            city_name = city.get('city', 'Unknown')
            temp = city.get('temperature', 'N/A')
            humidity = city.get('humidity', 'N/A')
            pressure = city.get('pressure', 'N/A')
            wind_speed = city.get('wind_speed', 'N/A')
            description = city.get('description', 'N/A')
            alert_level = city.get('alert_level', 'low')
            
            # Get population data if available
            population_info = ""
            if self.population_db:
                pop_data = self.population_db.get_city_population(city_name.lower())
                if pop_data and 'error' not in pop_data:
                    population_info = f"""
                    <tr><td><b>Population:</b></td><td>{pop_data.get('population', 'N/A'):,}</td></tr>
                    <tr><td><b>Healthcare Facilities:</b></td><td>{pop_data.get('healthcare_facilities', 'N/A')}</td></tr>
                    """
            
            # Disease risk summary
            disease_analysis = city.get('disease_analysis', {})
            disease_summary = ""
            for disease, data in disease_analysis.items():
                risk_level = data.get('risk_level', 'low')
                color = self.risk_colors.get(risk_level, '#28a745')
                disease_summary += f'<span style="color: {color}; font-weight: bold;">{disease.title()}: {risk_level.title()}</span><br>'
            
            popup_html = f"""
            <div style="width: 250px;">
                <h4 style="margin: 0; color: #333;">{city_name}</h4>
                <hr style="margin: 5px 0;">
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>Temperature:</b></td><td>{temp}°C</td></tr>
                    <tr><td><b>Humidity:</b></td><td>{humidity}%</td></tr>
                    <tr><td><b>Pressure:</b></td><td>{pressure} hPa</td></tr>
                    <tr><td><b>Wind Speed:</b></td><td>{wind_speed} m/s</td></tr>
                    <tr><td><b>Conditions:</b></td><td>{description}</td></tr>
                    {population_info}
                </table>
                <hr style="margin: 5px 0;">
                <div style="font-size: 11px;">
                    <b>Disease Risk Assessment:</b><br>
                    {disease_summary}
                </div>
                <div style="margin-top: 5px; padding: 3px; background-color: {self.risk_colors.get(alert_level, '#28a745')}; color: white; text-align: center; border-radius: 3px; font-size: 11px; font-weight: bold;">
                    Alert Level: {alert_level.title()}
                </div>
            </div>
            """
            
            return popup_html
            
        except Exception as e:
            logger.error(f"Error creating weather popup: {e}")
            return f"<b>{city.get('city', 'Unknown')}</b><br>Weather data unavailable"
    
    def _add_legend(self, m: folium.Map, include_disease_overlay: bool) -> None:
        """Add legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4 style="margin: 0 0 10px 0;">Legend</h4>
        <p style="margin: 5px 0;"><b>Alert Levels:</b></p>
        <p style="margin: 2px 0;"><i class="fa fa-circle" style="color: #28a745;"></i> Low Risk</p>
        <p style="margin: 2px 0;"><i class="fa fa-circle" style="color: #ffc107;"></i> Medium Risk</p>
        <p style="margin: 2px 0;"><i class="fa fa-circle" style="color: #fd7e14;"></i> High Risk</p>
        <p style="margin: 2px 0;"><i class="fa fa-circle" style="color: #dc3545;"></i> Critical Risk</p>
        '''
        
        if include_disease_overlay:
            legend_html += '''
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0;"><b>Disease Monitoring:</b></p>
            <p style="margin: 2px 0; font-size: 12px;">• Large circles: Weather stations</p>
            <p style="margin: 2px 0; font-size: 12px;">• Small circles: Disease risks</p>
            <p style="margin: 2px 0; font-size: 12px;">• Heat overlay: Temperature</p>
            '''
        
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
    
    def _generate_fallback_heatmap(self) -> str:
        """Generate a fallback heatmap when main generation fails"""
        try:
            m = folium.Map(
                location=self.pakistan_center,
                zoom_start=6,
                tiles='OpenStreetMap'
            )
            
            # Add basic markers for major cities
            major_cities = [
                {"name": "Karachi", "lat": 24.8607, "lon": 67.0011, "temp": 32, "risk": "high"},
                {"name": "Lahore", "lat": 31.5204, "lon": 74.3587, "temp": 30, "risk": "medium"},
                {"name": "Islamabad", "lat": 33.6844, "lon": 73.0479, "temp": 28, "risk": "low"},
                {"name": "Peshawar", "lat": 34.0151, "lon": 71.5249, "temp": 29, "risk": "medium"}
            ]
            
            for city in major_cities:
                color = self.risk_colors.get(city['risk'], '#28a745')
                folium.CircleMarker(
                    location=[city['lat'], city['lon']],
                    radius=12,
                    popup=f"<b>{city['name']}</b><br>Temp: {city['temp']}°C<br>Risk: {city['risk'].title()}",
                    color='white',
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.8
                ).add_to(m)
            
            # Add error message
            error_html = '''
                <h3 align="center" style="font-size:20px; color: red;"><b>Pakistan Weather Heatmap (Limited Data)</b></h3>
                <p align="center" style="font-size:12px;">Some features may be unavailable due to data limitations</p>
            '''
            m.get_root().html.add_child(folium.Element(error_html))
            
            return m._repr_html_()
            
        except Exception as e:
            logger.error(f"Error generating fallback heatmap: {e}")
            return "<div style='text-align: center; padding: 50px;'><h3>Heatmap temporarily unavailable</h3><p>Please try again later.</p></div>"
    
    def generate_disease_specific_heatmap(self, disease: str) -> str:
        """Generate heatmap focused on a specific disease"""
        try:
            weather_data = self.weather_service.get_current_weather()
            
            m = folium.Map(
                location=self.pakistan_center,
                zoom_start=6,
                tiles='OpenStreetMap'
            )
            
            # Add Pakistan boundary
            self._add_pakistan_boundary(m)
            
            # Add disease-specific markers
            for city in weather_data.get('cities', []):
                coords = city.get('coordinates', {})
                lat = coords.get('lat')
                lon = coords.get('lon')
                
                if lat is None or lon is None:
                    continue
                
                disease_analysis = city.get('disease_analysis', {})
                if disease in disease_analysis:
                    risk_data = disease_analysis[disease]
                    risk_level = risk_data.get('risk_level', 'low')
                    factors = risk_data.get('factors', [])
                    
                    color = self.risk_colors.get(risk_level, '#28a745')
                    
                    # Create disease-specific popup
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4 style="margin: 0; color: #333;">{city.get('city', 'Unknown')}</h4>
                        <hr style="margin: 5px 0;">
                        <p><b>{disease.title()} Risk:</b> <span style="color: {color}; font-weight: bold;">{risk_level.title()}</span></p>
                        <p><b>Contributing Factors:</b></p>
                        <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                    """
                    
                    for factor in factors:
                        popup_content += f"<li>{factor}</li>"
                    
                    popup_content += "</ul></div>"
                    
                    # Size marker based on risk level
                    radius = {'low': 8, 'medium': 12, 'high': 16, 'critical': 20}.get(risk_level, 8)
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        popup=folium.Popup(popup_content, max_width=250),
                        color='white',
                        weight=2,
                        fillColor=color,
                        fillOpacity=0.8
                    ).add_to(m)
            
            # Add title
            title_html = f'''
                <h3 align="center" style="font-size:20px"><b>Pakistan {disease.title()} Risk Monitoring</b></h3>
                <p align="center" style="font-size:12px">Real-time {disease} outbreak risk assessment</p>
                <p align="center" style="font-size:10px">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            '''
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Add legend
            self._add_legend(m, False)
            
            return m._repr_html_()
            
        except Exception as e:
            logger.error(f"Error generating {disease} heatmap: {e}")
            return self._generate_fallback_heatmap()
    
    def get_heatmap_data_summary(self) -> Dict[str, Any]:
        """Get summary data for heatmap generation"""
        try:
            weather_data = self.weather_service.get_current_weather()
            
            summary = {
                "total_cities": len(weather_data.get('cities', [])),
                "alert_levels": {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                "temperature_range": {'min': float('inf'), 'max': float('-inf')},
                "humidity_range": {'min': float('inf'), 'max': float('-inf')},
                "disease_risks": {'dengue': 0, 'malaria': 0, 'respiratory': 0, 'heat_stroke': 0},
                "last_updated": datetime.now().isoformat()
            }
            
            for city in weather_data.get('cities', []):
                # Count alert levels
                alert_level = city.get('alert_level', 'low')
                if alert_level in summary['alert_levels']:
                    summary['alert_levels'][alert_level] += 1
                
                # Track temperature range
                temp = city.get('temperature', 0)
                if temp > 0:  # Valid temperature
                    summary['temperature_range']['min'] = min(summary['temperature_range']['min'], temp)
                    summary['temperature_range']['max'] = max(summary['temperature_range']['max'], temp)
                
                # Track humidity range
                humidity = city.get('humidity', 0)
                if humidity > 0:  # Valid humidity
                    summary['humidity_range']['min'] = min(summary['humidity_range']['min'], humidity)
                    summary['humidity_range']['max'] = max(summary['humidity_range']['max'], humidity)
                
                # Count high-risk diseases
                disease_analysis = city.get('disease_analysis', {})
                for disease, data in disease_analysis.items():
                    if data.get('risk_level') in ['high', 'critical']:
                        if disease in summary['disease_risks']:
                            summary['disease_risks'][disease] += 1
            
            # Handle edge cases
            if summary['temperature_range']['min'] == float('inf'):
                summary['temperature_range'] = {'min': 0, 'max': 0}
            if summary['humidity_range']['min'] == float('inf'):
                summary['humidity_range'] = {'min': 0, 'max': 0}
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting heatmap data summary: {e}")
            return {
                "total_cities": 0,
                "alert_levels": {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                "temperature_range": {'min': 0, 'max': 0},
                "humidity_range": {'min': 0, 'max': 0},
                "disease_risks": {'dengue': 0, 'malaria': 0, 'respiratory': 0, 'heat_stroke': 0},
                "last_updated": datetime.now().isoformat(),
                "error": "Data unavailable"
            }