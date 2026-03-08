"""
HeidelFrisch Gym – Collectors Package
======================================
Makes all collectors easily accessible
"""

from .weather_api import WeatherCollector
from .traffic_api import TrafficCollector

__all__ = ['WeatherCollector', 'TrafficCollector']
