#!/usr/bin/env python3
"""
Test script to verify specific filtering is working correctly
"""

from data_preprocessing import load_all_datasets

def test_filtering():
    print("🧪 Testing Data Filtering...")
    
    datasets = load_all_datasets()
    
    for name, data in datasets.items():
        if data is not None:
            df_sold = data['sold']
            print(f"\n📊 {name}:")
            print(f"   Total properties: {len(df_sold)}")
            
            # Test square footage range
            if 'Finished Sqft' in df_sold.columns:
                min_sqft = df_sold['Finished Sqft'].min()
                max_sqft = df_sold['Finished Sqft'].max()
                print(f"   Square footage range: {min_sqft:.0f} - {max_sqft:.0f} sq ft")
                
                # Check for outliers
                outliers = df_sold[(df_sold['Finished Sqft'] < 1100) | (df_sold['Finished Sqft'] > 1900)]
                if len(outliers) > 0:
                    print(f"   ❌ ERROR: {len(outliers)} properties outside 1100-1900 range found!")
                    for idx, row in outliers.iterrows():
                        print(f"      - {row.get('Full_Address', 'Unknown')}: {row['Finished Sqft']} sq ft")
                else:
                    print(f"   ✅ All properties within 1100-1900 sq ft range")
            
            # Test for 15807 131st specifically
            if 'Full_Address' in df_sold.columns:
                problematic = df_sold[df_sold['Full_Address'].str.contains('15807 131st', case=False, na=False)]
                if len(problematic) > 0:
                    print(f"   ❌ ERROR: 15807 131st still found in dataset!")
                    for idx, row in problematic.iterrows():
                        print(f"      - {row['Full_Address']}: {row.get('Finished Sqft', 'Unknown')} sq ft")
                else:
                    print(f"   ✅ 15807 131st successfully removed")
            
            # Test year built filter
            if 'Year Built' in df_sold.columns:
                recent_homes = df_sold[df_sold['Year Built'] > 2020]
                if len(recent_homes) > 0:
                    print(f"   ❌ ERROR: {len(recent_homes)} properties built after 2020 found!")
                    for idx, row in recent_homes.iterrows():
                        print(f"      - {row.get('Full_Address', 'Unknown')}: Built {row['Year Built']}")
                else:
                    print(f"   ✅ No properties built after 2020")
                
                # Show year range
                min_year = df_sold['Year Built'].min()
                max_year = df_sold['Year Built'].max()
                print(f"   Year built range: {min_year:.0f} - {max_year:.0f}")

if __name__ == "__main__":
    test_filtering()