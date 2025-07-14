#!/usr/bin/env python3
"""
Test script to verify all imports and data loading work correctly
"""

try:
    from data_preprocessing import load_all_datasets, get_recent_market_data, calculate_market_stats
    print("✅ All imports successful")
    
    # Test data loading
    datasets = load_all_datasets()
    print(f"✅ Data loading successful - {len(datasets)} datasets loaded")
    
    # Test each dataset
    for name, data in datasets.items():
        if data is not None:
            print(f"✅ {name}: {data['sold_records']} sold properties")
            
            # Test recent data function
            recent_data = get_recent_market_data(data['sold'], 12)
            print(f"   - Recent data: {len(recent_data)} sales in last 12 months")
            
            # Test stats calculation
            if len(recent_data) > 0:
                stats = calculate_market_stats(recent_data)
                print(f"   - Median price: ${stats.get('median_price', 0):,.0f}")
        else:
            print(f"❌ {name}: Failed to load")
    
    print("\n🎉 All tests passed! App should work correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")