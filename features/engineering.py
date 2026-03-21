"""
HeidelFrisch Gym – Feature Engineering
========================================
EXCLUSIVELY based on Alnatura research (German retailer)

Key research finding (EXACT):
- At 0°C:  14% spoilage per day
- At 20°C: 28% spoilage per day
- Linear interpolation in between

All old assumptions (2°C threshold) have been removed.
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('/data/data/com.termux/files/home/heidelfrisch_gym')

from models.spoilage_model import real_spoilage_rate_germany, risk_score_and_action

# ============================================
# NEW: Load mixed data from APIs + synthetic
# ============================================

def load_mixed_data(n_samples=1000, real_ratio=0.5):
    """
    Load mixed dataset (real APIs + synthetic extremes)
    
    Args:
        n_samples: total samples to collect
        real_ratio: percentage of real data (0.0-1.0)
    
    Returns:
        DataFrame with temperature, delay_minutes, hour
    """
    from collectors.mixed_collector import MixedCollector
    
    print(f"\n📡 Loading mixed dataset ({n_samples} samples, {real_ratio:.0%} real)...")
    collector = MixedCollector()
    df = collector.collect_dataset(n_samples=n_samples, real_ratio=real_ratio)
    return df


class FeatureEngineer:
    """
    Creates features based SOLELY on Alnatura research.
    No legacy features from old models.
    """
    
    def __init__(self):
        self.peak_hours = [7, 8, 9, 16, 17, 18]  # German rush hours
        
        print("✅ FeatureEngineer initialized")
        print(f"   Using Alnatura research ONLY")
        print(f"   Peak hours: {self.peak_hours}")
    
    def add_alnatura_features(self, df):
        """
        Add Alnatura spoilage features using the realistic German model.
        """
        # Calculate spoilage using the new realistic model
        df['spoilage_rate_alnatura'] = df.apply(
          lambda row: real_spoilage_rate_germany(
          row['temperature'],
          row['delay_minutes'] / 60
        ) / 100,  # Convert from percentage (0-100) to rate (0-1)
        axis=1
        )
    
        # Get risk score and action from the new model
        risk_actions = df['spoilage_rate_alnatura'].apply(
         lambda x: risk_score_and_action(x * 100)  # Convert back to percentage
        )
        df['risk_score_alnatura'] = risk_actions.apply(lambda x: x['risk_score'])
        df['action'] = risk_actions.apply(lambda x: x['action'])
    
        # Decision based on risk score
        df['should_collect'] = (df['risk_score_alnatura'] <= 0.5).astype(int)
    
        print(f"✅ Added Alnatura features (using realistic model)")
        print(f"   Spoilage rate: {df['spoilage_rate_alnatura'].mean():.3%} mean, {df['spoilage_rate_alnatura'].max():.3%} max")
        print(f"   Actions: {df['action'].value_counts().to_dict()}")
        return df
    
    def create_features(self, df):
        """
        Create features from raw data.
        
        Raw data columns:
        - temperature: real °C
        - delay_minutes: real minutes
        - hour: 0-23
        - timestamp: datetime
        
        New features (ALL relevant to Alnatura):
        """
        # FEATURE 1: Peak hour indicator
        df['is_peak'] = df['hour'].isin(self.peak_hours).astype(int)
        
        # FEATURE 2: Peak multiplier (Bologna 2025 style)
        df['peak_factor'] = 1.0 + (0.5 * df['is_peak'])
        
        # FEATURE 3: Weighted delay
        df['weighted_delay'] = df['delay_minutes'] * df['peak_factor']
        
        # FEATURE 4-5: Circular time encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        print(f"✅ Created {len(df.columns) - 4} features")
        return df


# ============================================
# TESTING
# ============================================

def create_sample_data(n_samples=1000):
    """
    Create realistic German summer data (fallback if no API).
    """
    np.random.seed(42)
    
    data = {
        'temperature': np.random.normal(15, 5, n_samples),
        'delay_minutes': np.random.exponential(10, n_samples),
        'hour': np.random.randint(0, 24, n_samples),
        'timestamp': [pd.Timestamp.now() for _ in range(n_samples)]
    }
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing FeatureEngineer (Alnatura ONLY)")
    print("=" * 60)
    
    # OPTION 1: Load mixed real+synthetic data
    use_mixed_data = True  # שים True כדי להשתמש ב-API
    
    if use_mixed_data:
        df_raw = load_mixed_data(n_samples=1000, real_ratio=0.3)
    else:
        df_raw = create_sample_data(100)
    
    print(f"\n📊 Raw data:")
    print(f"   Temperature: {df_raw['temperature'].min():.1f}°C to {df_raw['temperature'].max():.1f}°C")
    print(f"   Avg delay: {df_raw['delay_minutes'].mean():.1f} min")
    
    # Initialize engineer
    engineer = FeatureEngineer()
    
    # Create features
    df_features = engineer.create_features(df_raw)
    
    # Add Alnatura features
    df_features = engineer.add_alnatura_features(df_features)
    
    # Show results
    print(f"\n📊 Alnatura Results:")
    print(f"   Mean spoilage rate: {df_features['spoilage_rate_alnatura'].mean():.3%}")
    print(f"   Max spoilage rate: {df_features['spoilage_rate_alnatura'].max():.3%}")
    print(f"   Mean risk score: {df_features['risk_score_alnatura'].mean():.2f}")
    print(f"   Should collect: {df_features['should_collect'].sum()}/{len(df_features)}")

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10,5))
        plt.hist(df_features['spoilage_percent'], bins=20, edgecolor='black')
        plt.axvline(5, color='orange', linestyle='--', label='5% warning')
        plt.axvline(8, color='red', linestyle='--', label='8% reject')
        plt.xlabel('Spoilage %')
        plt.ylabel('Frequency')
        plt.title('Spoilage Distribution – Heidelberg→Hamburg Transport')
        plt.legend()
        plt.savefig('spoilage_distribution.png')
        print("\n📊 Saved histogram to spoilage_distribution.png")
    except:
        pass
