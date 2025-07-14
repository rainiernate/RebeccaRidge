#!/usr/bin/env python3
"""
Test the new streamlined premium home pricing analysis
"""

from data_preprocessing import load_all_datasets
from neighborhood_analysis_app import analyze_premium_home_pricing

def test_new_pricing():
    print("🏠 Testing New Streamlined Pricing Analysis...")
    
    datasets = load_all_datasets()
    
    sunrise_data = datasets.get('Sunrise Area', {}).get('sold', None)
    rebecca_data = datasets.get('Rebecca Ridge', {}).get('sold', None)
    
    if sunrise_data is not None and rebecca_data is not None:
        # Test new pricing analysis
        pricing = analyze_premium_home_pricing(sunrise_data, rebecca_data, 1600)
        
        if pricing:
            print(f"\n💰 New Pricing Analysis (1600 sq ft):")
            print(f"   Recommended Price: ${pricing['recommended_price']:,.0f}")
            print(f"   Sunrise median: ${pricing['sunrise_median']:,.0f}")
            print(f"   Rebecca median: ${pricing['rebecca_median']:,.0f}")
            print(f"   Premium PSF: ${pricing['premium_psf']:.0f}")
            print(f"   Sunrise DOM: {pricing['sunrise_dom']:.0f} days")
            print(f"   Recent sales analyzed: {pricing['recent_sales_count']}")
            
            # Calculate premium
            premium = ((pricing['recommended_price'] - pricing['sunrise_median']) / pricing['sunrise_median']) * 100
            print(f"   Premium over Sunrise: {premium:.1f}%")
            
            print(f"\n✅ New streamlined pricing analysis working!")
            
            # Show sample comparables
            if len(pricing['sunrise_top']) > 0:
                print(f"\nTop Sunrise Comparables:")
                for idx, (_, row) in enumerate(pricing['sunrise_top'].iterrows()):
                    price = row['Selling Price']
                    sqft = row.get('Finished Sqft', 0)
                    print(f"   {idx+1}. ${price:,.0f} | {sqft:.0f} sq ft")
        else:
            print("❌ New pricing analysis failed")
    else:
        print("❌ Required data not available")

if __name__ == "__main__":
    test_new_pricing()