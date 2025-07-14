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

def load_and_preprocess_data(file_path):
    """Load and preprocess the MLS data"""
    
    # Read the tab-delimited file
    df = pd.read_csv(file_path, sep='\t', low_memory=False)
    
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
    
    if 'Finished Sqft' in df_sold.columns:
        # Remove properties with < 200 sqft or > 8000 sqft (likely data errors)
        df_sold = df_sold[(df_sold['Finished Sqft'] >= 200) & (df_sold['Finished Sqft'] <= 8000)]
    
    # Sort by selling date for time series analysis
    if 'Selling Date' in df_sold.columns:
        df_sold = df_sold.sort_values('Selling Date')
    
    return df_clean, df_sold

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
    # Test the preprocessing
    file_path = "/Users/nathancoons/RebeccaRidge/Full (38).txt"
    df_all, df_sold = load_and_preprocess_data(file_path)
    
    print(f"Total records: {len(df_all)}")
    print(f"Sold properties: {len(df_sold)}")
    print(f"Date range: {df_sold['Selling Date'].min()} to {df_sold['Selling Date'].max()}")
    
    # Show some basic stats
    recent_data = get_recent_market_data(df_sold, 12)
    stats = calculate_market_stats(recent_data)
    
    print("\nRecent Market Stats (Last 12 months):")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: ${value:,.2f}" if 'price' in key else f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")