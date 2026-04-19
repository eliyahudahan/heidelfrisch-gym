"""
Sensitivity Analysis for Spoilage Model
Tests how output changes with input variations
"""

import sys
sys.path.append('/data/data/com.termux/files/home/heidelfrisch_gym')

from models.spoilage_model import real_spoilage_rate_germany

def run_sensitivity_analysis():
    """Test spoilage across temperature and delay ranges"""
    print("\n" + "=" * 60)
    print("📊 Sensitivity Analysis")
    print("=" * 60)
    
    temperatures = [0, 5, 10, 15, 20, 25, 30, 35]
    delays = [1, 6, 12, 24, 48]  # hours
    
    print("\nSpoilage % (temp°C → hours delay ↓):")
    print("Temp\\Delay", end="")
    for h in delays:
        print(f" | {h:2}h", end="")
    print("\n" + "-" * 50)
    
    for temp in temperatures:
        print(f"  {temp:2}°C", end="")
        for hours in delays:
            spoilage = real_spoilage_rate_germany(temp, hours)
            print(f" | {spoilage:4.1f}", end="")
        print()
    
    # Find critical thresholds
    print("\n🔍 Critical thresholds (spoilage > 8% = REJECT):")
    for temp in temperatures:
        for hours in delays:
            spoilage = real_spoilage_rate_germany(temp, hours)
            if spoilage > 8:
                print(f"   REJECT at {temp}°C, {hours}h → {spoilage:.1f}%")

if __name__ == "__main__":
    run_sensitivity_analysis()
