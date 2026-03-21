"""
HeidelFrisch Gym – Analysis of Problematic Cases
==================================================
Analyzing shipments that need attention and suggesting actions
to PREVENT spoilage, not just report it.
"""

import pandas as pd
import sys
sys.path.append('/data/data/com.termux/files/home/heidelfrisch_gym')

from models.spoilage_model import real_spoilage_rate_germany, risk_score_and_action

# Load the latest data
import glob
files = glob.glob('data/mixed_dataset_*.csv')
latest = max(files, key=lambda f: f.split('_')[-1].split('.')[0])
df = pd.read_csv(latest)

print("=" * 60)
print("🔍 Analysis of Problematic Shipments")
print("=" * 60)
print(f"\n📁 Analyzing: {latest}")
print(f"📊 Total samples: {len(df)}")

# Calculate spoilage and actions for all samples
def analyze_row(row):
    spoilage = real_spoilage_rate_germany(
        row['temperature'],
        row['delay_minutes'] / 60
    )
    decision = risk_score_and_action(spoilage)
    return pd.Series({
        'spoilage_pct': spoilage,
        'action': decision['action'],
        'risk_score': decision['risk_score']
    })

# Add analysis columns
analysis_cols = df.apply(analyze_row, axis=1)
df = pd.concat([df, analysis_cols], axis=1)

# Filter problematic cases (not COLLECT)
problematic = df[df['action'] != 'COLLECT']

print(f"\n⚠️ Problematic cases: {len(problematic)}/{len(df)} ({len(problematic)/len(df)*100:.1f}%)")
print("\n📋 Breakdown by action:")
print(problematic['action'].value_counts())

if len(problematic) > 0:
    print("\n🌡️ Temperature ranges:")
    print(f"   REJECT:     {problematic[problematic['action']=='REJECT']['temperature'].min():.1f}°C to {problematic[problematic['action']=='REJECT']['temperature'].max():.1f}°C")
    print(f"   COOL URGENT: {problematic[problematic['action']=='COOL URGENT']['temperature'].min():.1f}°C to {problematic[problematic['action']=='COOL URGENT']['temperature'].max():.1f}°C")

    print("\n⏱️ Delay ranges (minutes):")
    print(f"   REJECT:     {problematic[problematic['action']=='REJECT']['delay_minutes'].min():.0f} to {problematic[problematic['action']=='REJECT']['delay_minutes'].max():.0f}")
    print(f"   COOL URGENT: {problematic[problematic['action']=='COOL URGENT']['delay_minutes'].min():.0f} to {problematic[problematic['action']=='COOL URGENT']['delay_minutes'].max():.0f}")

    print("\n📊 Source of problematic cases:")
    print(problematic['source'].value_counts())

    # Show top 5 worst cases
    print("\n🔥 Top 5 worst cases (highest spoilage):")
    worst = problematic.sort_values('spoilage_pct', ascending=False).head(5)
    for i, row in worst.iterrows():
        print(f"\n   Case #{i}: {row['spoilage_pct']:.1f}% spoilage")
        print(f"      Temp: {row['temperature']:.1f}°C, Delay: {row['delay_minutes']:.0f} min")
        print(f"      Action: {row['action']}, Source: {row['source']}")
        
        # === ערך מוסף אמיתי – המלצות למניעה ===
        if row['action'] == 'REJECT':
            print(f"      💡 RECOMMENDATION: Do NOT ship. Return to cold storage immediately.")
        elif row['action'] == 'COOL URGENT':
            hours_left = (8 - row['spoilage_pct']) / 2  # הערכה פשוטה
            print(f"      💡 RECOMMENDATION: COOL NOW! You have approximately {hours_left:.0f} hours before rejection.")

print("\n" + "=" * 60)
print("📈 Key Insights & Business Value:")
print("=" * 60)
print(f"• {len(problematic)} shipments ({len(problematic)/len(df)*100:.1f}%) need attention")
print(f"• {len(problematic[problematic['action']=='REJECT'])} shipments would be completely lost (€€€)")
print(f"• {len(problematic[problematic['action']=='COOL URGENT'])} shipments can be saved with immediate action")

if len(problematic) > 0:
    print("\n💰 Potential savings:")
    print(f"   If we save {len(problematic[problematic['action']=='COOL URGENT'])} urgent shipments")
    print(f"   and prevent {len(problematic[problematic['action']=='REJECT'])} rejections by earlier cooling,")
    print(f"   we can save up to {len(problematic)}/{len(df)} shipments ({len(problematic)/len(df)*100:.1f}% of total)!")
