"""
HeidelFrisch Gym – Weather Data Collector
==========================================
Collects real-time temperature data from Open-Meteo API
No API key required, free forever

Why weather?
- Blueberries spoil faster above 2°C
- Each degree above = one day less shelf life
- Critical for freshness prediction
"""

import requests
import time
from datetime import datetime

class WeatherCollector:
    """
    Collects temperature data for Walsrode–Hamburg route
    
    Open-Meteo API: https://open-meteo.com
    Free, no registration, 10,000 calls/day free
    """
    
    def __init__(self):
        # Walsrode coordinates (approximate)
        self.lat = 52.5
        self.lon = 9.5
        
        # Track API calls for rate limiting
        self.last_call_time = 0
        self.min_interval = 1  # seconds (be nice to free API)
    
    def get_current_temperature(self):
        """
        Fetch current temperature at Walsrode
        
        Returns:
            float: temperature in Celsius
            None: if API fails
        """
        # Rate limiting – don't call too often
        now = time.time()
        time_since_last = now - self.last_call_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        # Build API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "current_weather": True
        }
        
        try:
            # Make the call (timeout=5 so phone doesn't hang)
            response = requests.get(url, params=params, timeout=5)
            self.last_call_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                temp = data['current_weather']['temperature']
                return float(temp)
            else:
                print(f"⚠️ API returned {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Weather API failed: {e}")
            return None
    
    def get_temperature_history(self, date=None):
        """
        Get historical temperature for a specific date
        
        Args:
            date: datetime object (default: today)
        
        Returns:
            float: average temperature for that date
        """
        if date is None:
            date = datetime.now()
        
        # Historical API endpoint
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": date.strftime("%Y-%m-%d"),
            "end_date": date.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_mean"
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data['daily']['temperature_2m_mean'][0]
                return float(temp)
        except:
            pass
        
        # Fallback to current temperature
        return self.get_current_temperature()


# Quick test when run directly
if __name__ == "__main__":
    print("=" * 50)
    print("🌤️ Testing WeatherCollector")
    print("=" * 50)
    
    collector = WeatherCollector()
    
    # Test current temperature
    temp = collector.get_current_temperature()
    print(f"\n📍 Current temperature at Walsrode: {temp}°C")
    
    # Test historical (today)
    hist_temp = collector.get_temperature_history()
    print(f"📅 Historical temperature today: {hist_temp}°C")
