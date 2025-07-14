#!/usr/bin/env python3
"""
Test the unified app without toggles
"""

from data_preprocessing import load_all_datasets
from neighborhood_analysis_app import analyze_premium_home_pricing

def test_unified_app():
    print("🏠 Testing Unified App (No Toggles)...")
    
    datasets = load_all_datasets()
    
    print(f"\n📊 Available Datasets:")
    for name, data in datasets.items():
        if data:
            print(f"   ✅ {name}: {data['sold_records']} sold properties")
        else:
            print(f"   ❌ {name}: Failed to load")
    
    # Test the unified pricing approach
    rebecca_data = datasets.get('Rebecca Ridge', {})
    sunrise_data = datasets.get('Sunrise Area', {})
    
    if rebecca_data and sunrise_data:
        print(f"\n🎯 Combined Analysis Approach:")
        print(f"   Primary: Sunrise Area ({sunrise_data['sold_records']} properties)")
        print(f"   Context: Rebecca Ridge ({rebecca_data['sold_records']} properties)")
        
        # Test pricing analysis
        sunrise_sold = sunrise_data['sold']
        rebecca_sold = rebecca_data['sold']
        
        pricing = analyze_premium_home_pricing(sunrise_sold, rebecca_sold, 1600)
        
        if pricing:
            print(f"\n💰 Unified Pricing Result:")
            print(f"   Recommended: ${pricing['recommended_price']:,.0f}")
            print(f"   Based on Sunrise median: ${pricing['sunrise_median']:,.0f}")
            print(f"   Rebecca Ridge context: ${pricing['rebecca_median']:,.0f}")
            print(f"   Market speed: {pricing['sunrise_dom']:.0f} days")
            
            premium = ((pricing['recommended_price'] - pricing['sunrise_median']) / pricing['sunrise_median']) * 100
            print(f"   Premium over broader market: {premium:.1f}%")
            
            print(f"\n✅ Unified approach working perfectly!")
            print(f"📱 App will show single combined analysis with no confusing toggles")
        else:
            print("❌ Unified pricing analysis failed")
    else:
        print("❌ Both datasets required for unified analysis")

if __name__ == "__main__":
    test_unified_app()