"""
HeidelFrisch Gym – Traffic Delay Collector
===========================================
Collects real-time traffic data from Autobahn API
Official German government API, no registration

Why traffic?
- Walsrode→Hamburg uses Autobahn A7
- Delays mean longer exposure to heat
- Critical for freshness prediction
"""

import requests
import time

class TrafficCollector:
    """
    Collects traffic delay data for A7 between Walsrode and Hamburg
    
    Autobahn API: https://autobahn.api.bund.de
    Official German government API, free forever
    """
    
    def __init__(self):
        # A7 is the main autobahn from Walsrode to Hamburg
        self.autobahn_id = "A7"
        
        # Track API calls
        self.last_call_time = 0
        self.min_interval = 2  # seconds (be nice)
        
        # Base travel time without traffic (minutes)
        self.base_travel_time = 90  # Walsrode→Hamburg ~90 min
    
    def get_current_delay(self):
        """
        Fetch current traffic warnings on A7
        
        Returns:
            int: estimated delay in minutes
                 0 if no warnings
        """
        # Rate limiting
        now = time.time()
        time_since_last = now - self.last_call_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        # API endpoint for warnings
        url = f"https://verkehr.autobahn.de/o/autobahn/{self.autobahn_id}/services/warnings"
        
        try:
            response = requests.get(url, timeout=5)
            self.last_call_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                warnings = data.get('warning', [])
                
                # Each warning adds ~5 minutes delay
                # (simplified – real would parse location/duration)
                delay = len(warnings) * 5
                
                # Cap at 60 minutes (anything more = take train!)
                return min(delay, 60)
            else:
                print(f"⚠️ Traffic API returned {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"⚠️ Traffic API failed: {e}")
            return 0
    
    def get_travel_time(self):
        """
        Calculate total travel time including delays
        
        Returns:
            int: estimated travel time in minutes
        """
        delay = self.get_current_delay()
        total_time = self.base_travel_time + delay
        return total_time, delay


# Quick test
if __name__ == "__main__":
    print("=" * 50)
    print("🚗 Testing TrafficCollector")
    print("=" * 50)
    
    collector = TrafficCollector()
    
    # Test current delay
    delay = collector.get_current_delay()
    print(f"\n📍 Current delay on A7: {delay} minutes")
    
    # Test total travel time
    total, d = collector.get_travel_time()
    print(f"🚛 Total travel time: {total} minutes (base 90 + {d} delay)")
