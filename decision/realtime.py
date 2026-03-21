"""
HeidelFrisch Gym – Real-time Decision System
==============================================
Live recommendations for truck drivers based on current conditions
Saves all checks to CSV for model improvement
"""

import sys
import time
import csv
import os
from datetime import datetime
sys.path.append('/data/data/com.termux/files/home/heidelfrisch_gym')

from models.spoilage_model import real_spoilage_rate_germany, risk_score_and_action
from collectors.weather_api import WeatherCollector
from collectors.traffic_api import TrafficCollector

class RealTimeChecker:
    """
    Checks current conditions and gives live recommendations
    Saves all data to CSV for model improvement
    """
    
    def __init__(self):
        self.weather = WeatherCollector()
        self.traffic = TrafficCollector()
        self.data_file = 'data/live_readings.csv'
        
        # Create data file with headers if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'temperature', 'delay_minutes', 
                    'spoilage_percent', 'action', 'risk_score'
                ])
            print(f"✅ Created new data file: {self.data_file}")
        
        print("✅ RealTimeChecker initialized")
        print(f"   Heidelberg→Hamburg route | Saving to {self.data_file}")
    
    def check_now(self):
        """Get current conditions and recommendation"""
        print("\n" + "=" * 50)
        print("🚛 Heidelberg→Hamburg Live Check")
        print("=" * 50)
        
        # Get real-time data
        temp = self.weather.get_current_temperature()
        delay = self.traffic.get_current_delay()
        
        if temp is None:
            temp = 11.0  # fallback to current Heidelberg temp
            print("⚠️ Using fallback temperature (11°C)")
        
        print(f"\n🌡️ Current temperature: {temp}°C")
        print(f"🚦 Current delay: {delay} min")
        
        # Calculate spoilage
        spoilage = real_spoilage_rate_germany(temp, delay/60)
        decision = risk_score_and_action(spoilage)
        
        print(f"\n📊 Estimated spoilage: {spoilage:.2f}%")
        print(f"🎯 Recommendation: {decision['action']}")
        
        # Give specific advice
        if decision['action'] == 'COLLECT':
            print("✅ All good! Ship as planned.")
            print("   Keep cooling at 0-5°C")
        
        elif decision['action'] == 'COOL URGENT':
            hours_left = max(1, int((8 - spoilage) / 2))
            print(f"⚠️ ACTION NEEDED: Cool immediately!")
            print(f"   You have approximately {hours_left} hours to act.")
            print("   • Check cooling system")
            print("   • Reduce truck speed to minimize heat")
            print("   • Consider emergency stop at cooling station")
        
        elif decision['action'] == 'REJECT':
            print("❌ CRITICAL: Shipment at risk!")
            print("   • Do NOT ship under current conditions")
            print("   • Return to cold storage")
            print("   • Check if insurance covers this loss")
        
        # Prepare result dictionary
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': temp,
            'delay_minutes': delay,
            'spoilage_percent': round(spoilage, 2),
            'action': decision['action'],
            'risk_score': round(decision['risk_score'], 3)
        }
        
        # Save to CSV
        self._save_to_csv(result)
        
        return result
    
    def _save_to_csv(self, result):
        """Save a single check result to CSV"""
        with open(self.data_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                result['timestamp'],
                result['temperature'],
                result['delay_minutes'],
                result['spoilage_percent'],
                result['action'],
                result['risk_score']
            ])
        print(f"\n💾 Saved to {self.data_file}")
    
    def monitor(self, interval_minutes=5):
        """
        Continuously monitor conditions
        """
        print(f"\n🔄 Monitoring every {interval_minutes} minutes...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                result = self.check_now()
                print(f"\n📝 Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
            self._show_statistics()
    
    def _show_statistics(self):
        """Show summary of collected data"""
        try:
            import pandas as pd
            df = pd.read_csv(self.data_file)
            print("\n" + "=" * 50)
            print("📊 Collected Data Statistics")
            print("=" * 50)
            print(f"Total checks: {len(df)}")
            print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"\nTemperature: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
            print(f"Average: {df['temperature'].mean():.1f}°C")
            print(f"\nDelay: {df['delay_minutes'].min():.0f} to {df['delay_minutes'].max():.0f} min")
            print(f"Average: {df['delay_minutes'].mean():.1f} min")
            print(f"\nActions:")
            print(df['action'].value_counts())
        except:
            print("\n📊 No data yet or pandas not installed")

# Quick test
if __name__ == "__main__":
    checker = RealTimeChecker()
    
    # Single check (saves to CSV)
    checker.check_now()
    
    # Uncomment for continuous monitoring:
    # checker.monitor(interval_minutes=5)
