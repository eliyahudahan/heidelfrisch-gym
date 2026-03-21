"""
HeidelFrisch Gym – Mixed Data Collector
=========================================
Combines real API data with synthetic extreme scenarios

Why?
- Real data: accurate temperature and delays
- Synthetic: creates edge cases (long delays, heat waves)
- Together: robust model that handles reality AND extremes
"""

import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime
from collectors.weather_api import WeatherCollector
from collectors.traffic_api import TrafficCollector

class MixedCollector:
    """
    Collects 50% real data from APIs, 50% synthetic extreme cases
    """
    
    def __init__(self):
        self.weather = WeatherCollector()
        self.traffic = TrafficCollector()
        np.random.seed(42)
        
        print("✅ MixedCollector initialized")
        print("   • Real data: Open-Meteo + Autobahn")
        print("   • Synthetic: extreme delays, heat waves")
    
    def get_real_sample(self):
        """
        Collect one real sample from APIs
        """
        # Get real temperature
        temp = self.weather.get_current_temperature()
        if temp is None:
            temp = 15.0  # fallback
        
        # Get real delay
        delay = self.traffic.get_current_delay()
        
        # Get current hour
        hour = datetime.now().hour
        
        return {
            'temperature': temp,
            'delay_minutes': delay,
            'hour': hour,
            'source': 'real',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_synthetic_extreme(self):
        """
        Create realistic German transport scenarios:
        - Travel time: 6-12 hours (Heidelberg→Hamburg + delays)
        - Temperatures: 0-30°C (typical range including heat waves)
        """
        # Travel time: base 6h + up to 6h delay
        delay = np.random.uniform(6, 12) * 60  # convert to minutes
        
        # Temperature: realistic for Germany (including heat waves)
        if np.random.random() < 0.1:  # 10% chance of heat wave
            temp = np.random.uniform(25, 35)
        else:
            temp = np.random.uniform(0, 25)
        
        hour = np.random.randint(0, 24)
        
        return {
            'temperature': temp,
            'delay_minutes': delay,
            'hour': hour,
            'source': 'synthetic',
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_dataset(self, n_samples=1000, real_ratio=0.5):
        """
        Collect mixed dataset
        
        Args:
            n_samples: total samples to collect
            real_ratio: percentage of real data (0.0-1.0)
        """
        data = []
        n_real = int(n_samples * real_ratio)
        n_synthetic = n_samples - n_real
        
        print(f"\n📡 Collecting {n_samples} samples...")
        print(f"   • Real data: {n_real} samples (APIs)")
        print(f"   • Synthetic: {n_synthetic} samples (extremes)")
        
        # Collect real samples
        print(f"\n🌍 Collecting real data from APIs...")
        for i in range(n_real):
            sample = self.get_real_sample()
            data.append(sample)
            if (i+1) % 10 == 0:
                print(f"   ✓ {i+1}/{n_real} real samples")
            time.sleep(2)  # Rate limiting
        
        # Generate synthetic extremes
        print(f"\n🔄 Generating synthetic extremes...")
        for i in range(n_synthetic):
            sample = self.get_synthetic_extreme()
            data.append(sample)
            if (i+1) % 50 == 0:
                print(f"   ✓ {i+1}/{n_synthetic} synthetic")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Show statistics
        print(f"\n📊 Dataset statistics:")
        print(f"   Temperature: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
        print(f"   Delay: {df['delay_minutes'].min():.0f} to {df['delay_minutes'].max():.0f} min")
        print(f"   Real data: {(df['source']=='real').sum()} samples")
        print(f"   Synthetic: {(df['source']=='synthetic').sum()} samples")
        
        # Save to file
        filename = f"data/mixed_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n✅ Saved to {filename}")
        
        return df


# Quick test
if __name__ == "__main__":
    collector = MixedCollector()
    df = collector.collect_dataset(n_samples=20, real_ratio=0.5)
    print("\n📋 Sample data:")
    print(df[['temperature', 'delay_minutes', 'source']].head(10))
