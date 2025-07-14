import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_price_column(price_str):
    """Clean price columns by removing $ and commas, converting to float"""
    if pd.isna(price_str) or price_str == '':
        return np.nan
    # Remove $ and commas, then convert to float
    clean_price = re.sub(r'[\$,]', '', str(price_str))
    try:
        return float(clean_price)
    except (ValueError, TypeError):
        return np.nan

def clean_date_column(date_str):
    """Clean date columns and convert to datetime"""
    if pd.isna(date_str) or date_str == '':
        return pd.NaT
    try:
        # Handle various date formats
        return pd.to_datetime(date_str)
    except:
        return pd.NaT

def load_and_preprocess_data(file_path, dataset_name="Unknown"):
    """Load and preprocess the MLS data"""
    
    # Read the tab-delimited file
    df = pd.read_csv(file_path, sep='\t', low_memory=False)
    
    # Add dataset identifier
    df['Dataset'] = dataset_name
    
    # Define the most pertinent columns for analysis
    key_columns = [
        'Listing Number', 'Street Number', 'Street Name', 'City', 'State', 'Zip Code',
        'Bedrooms', 'Bathrooms', 'Finished Sqft', 'Square Footage', 'Lot SqFt',
        'Year Built', 'Listing Price', 'Selling Price', 'Current Price', 'Original Price',
        'Listing Date', 'Selling Date', 'Entry Date', 'Pending Date',
        'DOM', 'CDOM', 'Status', 'Property Sub Type', 'Architecture Desc',
        'Building Condition', 'Subdivision', 'Area', 'Taxes Annual',
        'Parking Type', 'Exterior', 'Foundation', 'Heating Cooling Type',
        'Style Code', 'Fireplaces Total', 'Parking Covered Total'
    ]
    
    # Keep only the key columns that exist in the dataset
    available_columns = [col for col in key_columns if col in df.columns]
    df_clean = df[available_columns].copy()
    
    # Clean price columns
    price_columns = ['Listing Price', 'Selling Price', 'Current Price', 'Original Price', 'Taxes Annual']
    for col in price_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(clean_price_column)
    
    # Clean date columns
    date_columns = ['Listing Date', 'Selling Date', 'Entry Date', 'Pending Date']
    for col in date_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(clean_date_column)
    
    # Clean numeric columns
    numeric_columns = ['Bedrooms', 'Bathrooms', 'Finished Sqft', 'Square Footage', 
                      'Lot SqFt', 'Year Built', 'DOM', 'CDOM', 'Fireplaces Total', 
                      'Parking Covered Total']
    for col in numeric_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Create additional useful columns
    
    # Price per square foot
    if 'Selling Price' in df_clean.columns and 'Finished Sqft' in df_clean.columns:
        df_clean['Price_Per_SqFt'] = df_clean['Selling Price'] / df_clean['Finished Sqft']
    
    # Sale year and month for time series analysis
    if 'Selling Date' in df_clean.columns:
        df_clean['Sale_Year'] = df_clean['Selling Date'].dt.year
        df_clean['Sale_Month'] = df_clean['Selling Date'].dt.month
        df_clean['Sale_Quarter'] = df_clean['Selling Date'].dt.quarter
        df_clean['Sale_Year_Month'] = df_clean['Selling Date'].dt.to_period('M')
    
    # Listing year and month
    if 'Listing Date' in df_clean.columns:
        df_clean['Listing_Year'] = df_clean['Listing Date'].dt.year
        df_clean['Listing_Month'] = df_clean['Listing Date'].dt.month
    
    # Price difference (if both listing and selling prices exist)
    if 'Listing Price' in df_clean.columns and 'Selling Price' in df_clean.columns:
        df_clean['Price_Difference'] = df_clean['Selling Price'] - df_clean['Listing Price']
        df_clean['Price_Change_Percent'] = (df_clean['Price_Difference'] / df_clean['Listing Price']) * 100
    
    # Full address for display
    if 'Street Number' in df_clean.columns and 'Street Name' in df_clean.columns:
        df_clean['Full_Address'] = (df_clean['Street Number'].astype(str) + ' ' + 
                                   df_clean['Street Name'].astype(str)).str.replace('nan', '').str.strip()
    elif 'Street Name' in df_clean.columns:
        df_clean['Full_Address'] = df_clean['Street Name'].astype(str)
    
    # Clean up status column
    if 'Status' in df_clean.columns:
        df_clean['Status'] = df_clean['Status'].str.strip()
    
    # Filter for sold properties for main analysis
    df_sold = df_clean[df_clean['Status'] == 'Sold'].copy() if 'Status' in df_clean.columns else df_clean.copy()
    
    # Remove obvious outliers (properties with extreme values)
    if 'Selling Price' in df_sold.columns:
        # Remove properties with selling price < $50k or > $2M (likely data errors)
        df_sold = df_sold[(df_sold['Selling Price'] >= 50000) & (df_sold['Selling Price'] <= 2000000)]
    
    # Apply strict square footage filter (1100-1900 sq ft for accurate comparisons)
    if 'Finished Sqft' in df_sold.columns:
        initial_count = len(df_sold)
        # STRICT filtering - must be between 1100-1900 sq ft exactly
        df_sold = df_sold[(df_sold['Finished Sqft'] >= 1100) & 
                         (df_sold['Finished Sqft'] <= 1900) & 
                         (df_sold['Finished Sqft'] > 0) & 
                         (df_sold['Finished Sqft'].notna())]
        sqft_filtered_count = len(df_sold)
        
        if initial_count > sqft_filtered_count:
            print(f"📏 Filtered out {initial_count - sqft_filtered_count} properties outside 1100-1900 sq ft range")
        
        # Double-check: log any remaining properties outside range (shouldn't happen)
        outliers = df_sold[(df_sold['Finished Sqft'] < 1100) | (df_sold['Finished Sqft'] > 1900)]
        if len(outliers) > 0:
            print(f"⚠️  WARNING: {len(outliers)} properties still outside range after filtering!")
            for idx, row in outliers.iterrows():
                print(f"   - {row.get('Full_Address', 'Unknown')}: {row['Finished Sqft']} sq ft")
    
    # Filter out newer construction (built after 2020) to avoid skewing analysis with new construction
    if 'Year Built' in df_sold.columns:
        year_initial_count = len(df_sold)
        # Keep homes built in 2020 or earlier, and handle missing year built data
        df_sold = df_sold[(df_sold['Year Built'] <= 2020) | df_sold['Year Built'].isna()]
        year_filtered_count = len(df_sold)
        
        if year_initial_count > year_filtered_count:
            print(f"🏗️  Filtered out {year_initial_count - year_filtered_count} properties built after 2020")
    
    # Specifically eliminate 15807 131st (problematic outlier - 2688 sq ft shouldn't be in 1100-1900 dataset)
    if 'Street Number' in df_sold.columns and 'Street Name' in df_sold.columns:
        pre_elimination = len(df_sold)
        df_sold = df_sold[~((df_sold['Street Number'] == 15807) & 
                           (df_sold['Street Name'].str.contains('131st', case=False, na=False)))]
        post_elimination = len(df_sold)
        
        if pre_elimination > post_elimination:
            print(f"🚫 Specifically eliminated 15807 131st property ({pre_elimination - post_elimination} properties removed)")
    
    # Additional check: Remove any property with Full_Address containing "15807 131st" (backup filter)
    if 'Full_Address' in df_sold.columns:
        pre_backup = len(df_sold)
        df_sold = df_sold[~df_sold['Full_Address'].str.contains('15807 131st', case=False, na=False)]
        post_backup = len(df_sold)
        
        if pre_backup > post_backup:
            print(f"🚫 Backup filter removed {pre_backup - post_backup} additional 15807 131st properties")
    
    # Sort by selling date for time series analysis
    if 'Selling Date' in df_sold.columns:
        df_sold = df_sold.sort_values('Selling Date')
    
    return df_clean, df_sold

def load_all_datasets():
    """Load both Rebecca Ridge and Sunrise datasets"""
    
    # File paths
    rebecca_ridge_path = "/Users/nathancoons/RebeccaRidge/RebeccaRidge11001900sqft.txt"
    sunrise_path = "/Users/nathancoons/RebeccaRidge/SunriseRebeccaRidge11001900sqft.txt"
    
    datasets = {}
    
    try:
        # Load Rebecca Ridge data
        df_all_rr, df_sold_rr = load_and_preprocess_data(rebecca_ridge_path, "Rebecca Ridge")
        datasets['Rebecca Ridge'] = {
            'all': df_all_rr,
            'sold': df_sold_rr,
            'description': 'Rebecca Ridge Neighborhood (1100-1900 sq ft, built 2000-2020)',
            'total_records': len(df_all_rr),
            'sold_records': len(df_sold_rr)
        }
    except Exception as e:
        print(f"Error loading Rebecca Ridge data: {e}")
        datasets['Rebecca Ridge'] = None
    
    try:
        # Load Sunrise data
        df_all_sunrise, df_sold_sunrise = load_and_preprocess_data(sunrise_path, "Sunrise Area")
        datasets['Sunrise Area'] = {
            'all': df_all_sunrise,
            'sold': df_sold_sunrise,
            'description': 'Broader Sunrise Neighborhood (1100-1900 sq ft, built 1991-2020)',
            'total_records': len(df_all_sunrise),
            'sold_records': len(df_sold_sunrise)
        }
    except Exception as e:
        print(f"Error loading Sunrise data: {e}")
        datasets['Sunrise Area'] = None
    
    return datasets

# Function to get recent market data (last 12 months)
def get_recent_market_data(df_sold, months_back=12):
    """Get data from the last N months for current market analysis"""
    if 'Selling Date' not in df_sold.columns:
        return df_sold
    
    # Get the most recent date in the dataset
    max_date = df_sold['Selling Date'].max()
    if pd.isna(max_date):
        return df_sold
    
    # Calculate the cutoff date
    cutoff_date = max_date - pd.DateOffset(months=months_back)
    
    # Filter for recent sales
    recent_sales = df_sold[df_sold['Selling Date'] >= cutoff_date]
    
    return recent_sales

# Function to calculate market statistics
def calculate_market_stats(df_sold):
    """Calculate key market statistics"""
    stats = {}
    
    if len(df_sold) == 0:
        return stats
    
    # Price statistics
    if 'Selling Price' in df_sold.columns:
        stats['median_price'] = df_sold['Selling Price'].median()
        stats['mean_price'] = df_sold['Selling Price'].mean()
        stats['price_std'] = df_sold['Selling Price'].std()
        stats['min_price'] = df_sold['Selling Price'].min()
        stats['max_price'] = df_sold['Selling Price'].max()
    
    # Square footage statistics
    if 'Finished Sqft' in df_sold.columns:
        stats['median_sqft'] = df_sold['Finished Sqft'].median()
        stats['mean_sqft'] = df_sold['Finished Sqft'].mean()
    
    # Price per square foot
    if 'Price_Per_SqFt' in df_sold.columns:
        stats['median_price_per_sqft'] = df_sold['Price_Per_SqFt'].median()
        stats['mean_price_per_sqft'] = df_sold['Price_Per_SqFt'].mean()
    
    # Days on market
    if 'DOM' in df_sold.columns:
        stats['median_dom'] = df_sold['DOM'].median()
        stats['mean_dom'] = df_sold['DOM'].mean()
    
    # Property characteristics
    if 'Bedrooms' in df_sold.columns:
        stats['avg_bedrooms'] = df_sold['Bedrooms'].mean()
    
    if 'Bathrooms' in df_sold.columns:
        stats['avg_bathrooms'] = df_sold['Bathrooms'].mean()
    
    # Lot size
    if 'Lot SqFt' in df_sold.columns:
        stats['median_lot_size'] = df_sold['Lot SqFt'].median()
    
    # Total sales count
    stats['total_sales'] = len(df_sold)
    
    return stats

if __name__ == "__main__":
    # Test the preprocessing with new datasets
    datasets = load_all_datasets()
    
    print("=== Dataset Loading Test ===")
    for name, data in datasets.items():
        if data is not None:
            print(f"\n{name}:")
            print(f"  Description: {data['description']}")
            print(f"  Total records: {data['total_records']}")
            print(f"  Sold properties: {data['sold_records']}")
            
            df_sold = data['sold']
            if len(df_sold) > 0 and 'Selling Date' in df_sold.columns:
                print(f"  Date range: {df_sold['Selling Date'].min()} to {df_sold['Selling Date'].max()}")
                
                # Show recent stats
                recent_data = get_recent_market_data(df_sold, 12)
                if len(recent_data) > 0:
                    stats = calculate_market_stats(recent_data)
                    print(f"  Recent median price: ${stats.get('median_price', 0):,.0f}")
                    print(f"  Recent median DOM: {stats.get('median_dom', 0):.0f} days")
        else:
            print(f"\n{name}: FAILED TO LOAD")