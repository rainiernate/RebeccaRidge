#!/usr/bin/env python3
"""
Test the premium home pricing analysis
"""

from data_preprocessing import load_all_datasets
from neighborhood_analysis_app import analyze_premium_home_pricing

def test_pricing_analysis():
    print("🏠 Testing Premium Home Pricing Analysis...")
    
    datasets = load_all_datasets()
    rebecca_ridge_data = datasets.get('Rebecca Ridge')
    
    if rebecca_ridge_data:
        df_sold = rebecca_ridge_data['sold']
        
        # Test pricing analysis
        pricing = analyze_premium_home_pricing(df_sold, 1600)
        
        if pricing:
            print(f"\n💰 Pricing Results for 1600 sq ft home:")
            print(f"   Conservative: ${pricing['conservative']:,.0f}")
            print(f"   Recommended: ${pricing['recommended']:,.0f}")
            print(f"   Aggressive: ${pricing['aggressive']:,.0f}")
            print(f"   Market median: ${pricing['market_median']:,.0f}")
            print(f"   Premium PSF: ${pricing['premium_psf']:.0f}")
            print(f"   Days on market: {pricing['days_on_market']:.0f}")
            
            premium_percent = ((pricing['recommended'] - pricing['market_median']) / pricing['market_median']) * 100
            print(f"   Premium over market: {premium_percent:.1f}%")
            
            print(f"\n✅ Pricing analysis working correctly!")
        else:
            print("❌ Pricing analysis failed")
    else:
        print("❌ Rebecca Ridge data not available")

if __name__ == "__main__":
    test_pricing_analysis()