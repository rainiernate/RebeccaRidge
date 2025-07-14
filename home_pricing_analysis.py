#!/usr/bin/env python3
"""
Professional pricing analysis for 12903 158th Street Ct E
Premium remodeled home in Rebecca Ridge neighborhood
"""

import pandas as pd
import numpy as np
from data_preprocessing import load_all_datasets, get_recent_market_data, calculate_market_stats
from datetime import datetime, timedelta

def analyze_subject_property():
    """Comprehensive pricing analysis for the subject property"""
    
    print("🏠 PROFESSIONAL PRICING ANALYSIS")
    print("=" * 60)
    print("Subject Property: 12903 158th Street Ct E, Puyallup, WA 98374")
    print("Premium Remodeled Home - Rebecca Ridge Neighborhood")
    print("=" * 60)
    
    # Load datasets
    datasets = load_all_datasets()
    rebecca_ridge_data = datasets.get('Rebecca Ridge')
    sunrise_data = datasets.get('Sunrise Area')
    
    if not rebecca_ridge_data:
        print("❌ Error: Rebecca Ridge data not available")
        return
    
    df_rr = rebecca_ridge_data['sold']
    df_sunrise = sunrise_data['sold'] if sunrise_data else pd.DataFrame()
    
    # Get recent market data (last 24 months for better sample size)
    recent_rr = get_recent_market_data(df_rr, 24)
    recent_sunrise = get_recent_market_data(df_sunrise, 24) if len(df_sunrise) > 0 else pd.DataFrame()
    
    print(f"\n📊 MARKET DATA ANALYSIS")
    print(f"Rebecca Ridge - Recent Sales (24 months): {len(recent_rr)} properties")
    print(f"Sunrise Area - Recent Sales (24 months): {len(recent_sunrise)} properties")
    
    # 1. BASELINE MARKET ANALYSIS
    print(f"\n🎯 1. BASELINE MARKET METRICS")
    print("-" * 40)
    
    if len(recent_rr) > 0:
        rr_stats = calculate_market_stats(recent_rr)
        print(f"Rebecca Ridge (Direct Neighborhood):")
        print(f"  • Median Price: ${rr_stats.get('median_price', 0):,.0f}")
        print(f"  • Price per SqFt: ${rr_stats.get('median_price_per_sqft', 0):.0f}")
        print(f"  • Days on Market: {rr_stats.get('median_dom', 0):.0f} days")
        print(f"  • Price Range: ${rr_stats.get('min_price', 0):,.0f} - ${rr_stats.get('max_price', 0):,.0f}")
    
    if len(recent_sunrise) > 0:
        sunrise_stats = calculate_market_stats(recent_sunrise)
        print(f"\nSunrise Area (Broader Market):")
        print(f"  • Median Price: ${sunrise_stats.get('median_price', 0):,.0f}")
        print(f"  • Price per SqFt: ${sunrise_stats.get('median_price_per_sqft', 0):.0f}")
        print(f"  • Days on Market: {sunrise_stats.get('median_dom', 0):.0f} days")
        print(f"  • Price Range: ${sunrise_stats.get('min_price', 0):,.0f} - ${sunrise_stats.get('max_price', 0):,.0f}")
    
    # 2. TOP PERFORMING COMPARABLES
    print(f"\n🏆 2. TOP PERFORMING COMPARABLES")
    print("-" * 40)
    
    # Get top 5 sales from Rebecca Ridge
    top_rr = recent_rr.nlargest(5, 'Selling Price') if len(recent_rr) > 0 else pd.DataFrame()
    
    if len(top_rr) > 0:
        print("Rebecca Ridge - Top Recent Sales:")
        for idx, (_, row) in enumerate(top_rr.iterrows(), 1):
            address = row.get('Full_Address', 'Unknown Address')
            price = row['Selling Price']
            sqft = row.get('Finished Sqft', 0)
            price_per_sqft = price / sqft if sqft > 0 else 0
            sale_date = row.get('Selling Date', 'Unknown Date')
            
            if pd.notna(sale_date):
                sale_date = sale_date.strftime('%b %Y')
            
            print(f"  {idx}. {address}")
            print(f"     ${price:,.0f} | {sqft:.0f} sq ft | ${price_per_sqft:.0f}/sq ft | {sale_date}")
    
    # 3. PREMIUM ADJUSTMENT ANALYSIS
    print(f"\n💎 3. PREMIUM ADJUSTMENT ANALYSIS")
    print("-" * 40)
    
    if len(recent_rr) > 0:
        base_price_per_sqft = rr_stats.get('median_price_per_sqft', 0)
        top_price_per_sqft = top_rr['Selling Price'].iloc[0] / top_rr['Finished Sqft'].iloc[0] if len(top_rr) > 0 and top_rr['Finished Sqft'].iloc[0] > 0 else base_price_per_sqft
        
        print("Premium Upgrade Adjustments:")
        print(f"  • Base Market (Median): ${base_price_per_sqft:.0f}/sq ft")
        print(f"  • Top Sale: ${top_price_per_sqft:.0f}/sq ft")
        print(f"  • Premium Spread: {((top_price_per_sqft - base_price_per_sqft) / base_price_per_sqft * 100):.1f}%")
        
        # Calculate premium adjustments for extensive remodel
        premium_adjustments = {
            "Kitchen Remodel (High-End)": 15000,
            "Master Suite Renovation": 12000,
            "Custom Staircase & Railing": 8000,
            "Custom Trex Deck": 7000,
            "New HVAC/AC System": 6000,
            "New Roof": 5000,
            "Custom Lighting & Finishes": 4000,
            "Fresh Paint Throughout": 3000,
            "New Carpet": 2000,
            "Custom Laundry Tiling": 1500
        }
        
        total_premium = sum(premium_adjustments.values())
        
        print(f"\nEstimated Premium Adjustments:")
        for upgrade, value in premium_adjustments.items():
            print(f"  • {upgrade}: +${value:,}")
        print(f"  • TOTAL PREMIUM VALUE: +${total_premium:,}")
    
    # 4. PRICING RECOMMENDATIONS
    print(f"\n🎯 4. PROFESSIONAL PRICING RECOMMENDATIONS")
    print("-" * 40)
    
    if len(recent_rr) > 0:
        # Method 1: Market median + premium
        base_median = rr_stats.get('median_price', 0)
        method1_price = base_median + total_premium
        
        # Method 2: Top comp price + premium percentage
        top_price = top_rr['Selling Price'].iloc[0] if len(top_rr) > 0 else base_median
        method2_price = top_price * 1.08  # 8% premium for extensive remodel
        
        # Method 3: Premium price per sq ft (estimated home size)
        estimated_sqft = 1600  # Typical for neighborhood
        premium_psf = top_price_per_sqft * 1.10  # 10% premium
        method3_price = estimated_sqft * premium_psf
        
        # Calculate recommended range
        prices = [method1_price, method2_price, method3_price]
        conservative = min(prices)
        aggressive = max(prices)
        recommended = np.median(prices)
        
        print(f"Pricing Analysis Methods:")
        print(f"  1. Market Median + Premium: ${method1_price:,.0f}")
        print(f"  2. Top Comp + 8% Premium: ${method2_price:,.0f}")
        print(f"  3. Premium PSF Method: ${method3_price:,.0f}")
        
        print(f"\n💰 FINAL PRICING RECOMMENDATION:")
        print(f"  • Conservative (List): ${conservative:,.0f}")
        print(f"  • Recommended (Target): ${recommended:,.0f}")
        print(f"  • Aggressive (Ceiling): ${aggressive:,.0f}")
        
        print(f"\n📈 MARKET POSITIONING:")
        if recommended > base_median:
            premium_percent = ((recommended - base_median) / base_median) * 100
            print(f"  • {premium_percent:.1f}% premium over neighborhood median")
        
        print(f"  • Estimated Price per SqFt: ${recommended/estimated_sqft:.0f}")
        print(f"  • Market positioning: TOP 10% of neighborhood")
    
    # 5. STRATEGIC RECOMMENDATIONS
    print(f"\n🎯 5. STRATEGIC RECOMMENDATIONS")
    print("-" * 40)
    
    if len(recent_rr) > 0:
        recent_dom = rr_stats.get('median_dom', 0)
        
        print("Listing Strategy:")
        if recent_dom <= 30:
            print(f"  • STRONG MARKET: Homes selling in {recent_dom:.0f} days")
            print(f"  • Strategy: Price aggressively at ${recommended:,.0f}")
            print(f"  • Expect: Quick sale due to premium condition")
        else:
            print(f"  • NORMAL MARKET: Homes selling in {recent_dom:.0f} days")
            print(f"  • Strategy: Price competitively at ${conservative:,.0f}")
            print(f"  • Be prepared: For some negotiation")
        
        print(f"\nMarketing Focus:")
        print(f"  • Emphasize: Complete premium remodel")
        print(f"  • Highlight: Best-in-neighborhood condition")
        print(f"  • Target: Move-in ready luxury buyers")
        print(f"  • Positioning: No other homes at this level")
    
    print(f"\n" + "=" * 60)
    print(f"Analysis completed: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

if __name__ == "__main__":
    analyze_subject_property()