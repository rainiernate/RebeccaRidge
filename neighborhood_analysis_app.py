import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from data_preprocessing import load_all_datasets, get_recent_market_data, calculate_market_stats

# Configure Streamlit page
st.set_page_config(
    page_title="Rebecca Ridge Real Estate Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache all datasets"""
    import os
    
    # Minimal path verification (helps with initialization)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rebecca_file = os.path.join(current_dir, "RebeccaRidge11001900sqft.txt")
    sunrise_file = os.path.join(current_dir, "SunriseRebeccaRidge11001900sqft.txt")
    
    # Quick file check (seems to help with loading)
    if os.path.exists(rebecca_file) and os.path.exists(sunrise_file):
        st.success("✅ Data files loaded successfully")
    else:
        st.error("❌ Data files not found")
    
    return load_all_datasets()

def create_price_trend_chart(df_sold):
    """Create an interactive price trend chart over time"""
    if 'Sale_Year_Month' not in df_sold.columns or 'Selling Price' not in df_sold.columns:
        return None
    
    # Monthly price trends
    monthly_stats = df_sold.groupby('Sale_Year_Month').agg({
        'Selling Price': ['median', 'mean', 'count'],
        'Price_Per_SqFt': ['median', 'mean']
    }).round(2)
    
    monthly_stats.columns = ['Median_Price', 'Mean_Price', 'Sales_Count', 'Median_PriceSqFt', 'Mean_PriceSqFt']
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['Date'] = monthly_stats['Sale_Year_Month'].astype(str)
    
    # Create single chart with secondary y-axis for price per sqft
    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )
    
    # Price trends
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Median_Price'],
                  mode='lines+markers', name='Median Price',
                  line=dict(color='#1f77b4', width=3))
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Mean_Price'],
                  mode='lines+markers', name='Mean Price',
                  line=dict(color='#ff7f0e', width=2, dash='dash'))
    )
    
    # Price per sqft on secondary axis
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Median_PriceSqFt'],
                  mode='lines', name='Median $/SqFt',
                  line=dict(color='#2ca02c', width=2),
                  yaxis='y2')
    )
    
    fig.update_layout(
        title="Neighborhood Real Estate Market Trends",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price ($)")
    fig.update_yaxes(title_text="Price per SqFt ($)", secondary_y=True)
    fig.update_xaxes(title_text="Date")
    
    return fig

def create_simplified_price_chart(df_sold):
    """Create a simplified, clean price vs square footage chart"""
    if len(df_sold) == 0 or 'Finished Sqft' not in df_sold.columns or 'Selling Price' not in df_sold.columns:
        return None
    
    # Clean data
    clean_data = df_sold.dropna(subset=['Finished Sqft', 'Selling Price']).copy()
    
    # Create simple scatter plot
    fig = go.Figure()
    
    # Add scatter points
    fig.add_trace(go.Scatter(
        x=clean_data['Finished Sqft'],
        y=clean_data['Selling Price'],
        mode='markers',
        marker=dict(
            size=8,
            color='#1f77b4',
            opacity=0.7
        ),
        text=[f"{row.get('Full_Address', 'N/A')}<br>${row['Selling Price']:,.0f}<br>{row['Finished Sqft']:.0f} sq ft" 
              for _, row in clean_data.iterrows()],
        hovertemplate='%{text}<extra></extra>',
        name='Sold Homes'
    ))
    
    # Remove trendline - keeping it simple
    
    fig.update_layout(
        title="Home Prices by Size",
        xaxis_title="Square Footage",
        yaxis_title="Sale Price ($)",
        height=400,
        showlegend=False
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig

def get_top_sales(df_sold, top_n=5):
    """Get the top N highest selling homes"""
    if 'Selling Price' not in df_sold.columns or len(df_sold) == 0:
        return pd.DataFrame()
    
    top_sales = df_sold.nlargest(top_n, 'Selling Price').copy()
    
    # Select relevant columns for display
    display_cols = []
    for col in ['Full_Address', 'Selling Price', 'Selling Date', 'Finished Sqft', 
                'Bedrooms', 'Bathrooms', 'DOM', 'Year Built']:
        if col in top_sales.columns:
            display_cols.append(col)
    
    return top_sales[display_cols]

def analyze_premium_home_pricing(sunrise_data, rebecca_data, home_sqft=1600):
    """Analyze pricing for a premium remodeled home using broader market data"""
    
    # Primary analysis: Sunrise area (broader market)
    sunrise_recent = get_recent_market_data(sunrise_data, 18) if len(sunrise_data) > 0 else pd.DataFrame()
    rebecca_recent = get_recent_market_data(rebecca_data, 24) if len(rebecca_data) > 0 else pd.DataFrame()
    
    if len(sunrise_recent) == 0:
        return None
    
    # Calculate market stats from broader Sunrise area
    sunrise_stats = calculate_market_stats(sunrise_recent)
    rebecca_stats = calculate_market_stats(rebecca_recent) if len(rebecca_recent) > 0 else {}
    
    # Get comparables from both areas
    sunrise_top = sunrise_recent.nlargest(5, 'Selling Price')
    rebecca_top = rebecca_recent.nlargest(3, 'Selling Price') if len(rebecca_recent) > 0 else pd.DataFrame()
    
    # Pricing strategy based on broader market
    sunrise_median = sunrise_stats.get('median_price', 0)
    sunrise_psf = sunrise_stats.get('median_price_per_sqft', 0)
    
    # Premium for extensive remodel (conservative approach)
    remodel_premium = 50000  # $50k premium for luxury remodel
    
    # Three pricing approaches
    market_approach = sunrise_median + remodel_premium  # Market + premium
    psf_approach = home_sqft * (sunrise_psf * 1.10)     # 10% premium PSF
    comp_approach = sunrise_top['Selling Price'].iloc[0] * 1.05 if len(sunrise_top) > 0 else market_approach  # 5% over top comp
    
    # Final pricing recommendation
    pricing_options = [market_approach, psf_approach, comp_approach]
    recommended_price = int(np.median(pricing_options))
    
    return {
        'sunrise_median': sunrise_median,
        'sunrise_psf': sunrise_psf,
        'rebecca_median': rebecca_stats.get('median_price', 0),
        'recommended_price': recommended_price,
        'sunrise_dom': sunrise_stats.get('median_dom', 0),
        'sunrise_top': sunrise_top.head(3),
        'rebecca_top': rebecca_top,
        'premium_psf': sunrise_psf * 1.10,
        'recent_sales_count': len(sunrise_recent)
    }

def analyze_2025_market_trend(df_sold):
    """Analyze what's happening in 2025 specifically - simplified and clear"""
    if 'Sale_Year' not in df_sold.columns or len(df_sold) == 0:
        return None, None, None
    
    # Get 2025 data
    df_2025 = df_sold[df_sold['Sale_Year'] == 2025].copy()
    
    # Get 2024 data for comparison
    df_2024 = df_sold[df_sold['Sale_Year'] == 2024].copy()
    
    if len(df_2025) == 0:
        return None, None, "No 2025 sales data available yet."
    
    # Calculate key metrics
    metrics_2025 = calculate_market_stats(df_2025)
    metrics_2024 = calculate_market_stats(df_2024) if len(df_2024) > 0 else {}
    
    # Create simple comparison chart
    comparison_data = []
    
    if metrics_2024:
        comparison_data.append({
            'Year': '2024',
            'Median Price': metrics_2024.get('median_price', 0),
            'Sales Count': len(df_2024),
            'Avg Days on Market': metrics_2024.get('median_dom', 0)
        })
    
    comparison_data.append({
        'Year': '2025',
        'Median Price': metrics_2025.get('median_price', 0),
        'Sales Count': len(df_2025),
        'Avg Days on Market': metrics_2025.get('median_dom', 0)
    })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create clear comparison chart
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Median Home Price', 'Total Sales', 'Days on Market'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # Price comparison
    fig.add_trace(
        go.Bar(
            x=comparison_df['Year'], 
            y=comparison_df['Median Price'],
            name='Median Price',
            marker_color=['#ff7f0e', '#1f77b4'],
            text=[f"${x:,.0f}" for x in comparison_df['Median Price']],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Sales count comparison
    fig.add_trace(
        go.Bar(
            x=comparison_df['Year'], 
            y=comparison_df['Sales Count'],
            name='Sales Count',
            marker_color=['#ff7f0e', '#1f77b4'],
            text=comparison_df['Sales Count'],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # DOM comparison
    fig.add_trace(
        go.Bar(
            x=comparison_df['Year'], 
            y=comparison_df['Avg Days on Market'],
            name='Days on Market',
            marker_color=['#ff7f0e', '#1f77b4'],
            text=[f"{x:.0f} days" for x in comparison_df['Avg Days on Market']],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        title="2024 vs 2025 Market Comparison",
        height=400,
        showlegend=False
    )
    
    # Format y-axes
    fig.update_yaxes(tickformat='$,.0f', row=1, col=1)
    
    # Generate simple insights
    insights = []
    
    # Year-over-year comparison
    if metrics_2024 and 'median_price' in metrics_2024:
        price_2025 = metrics_2025.get('median_price', 0)
        price_2024 = metrics_2024.get('median_price', 0)
        
        if price_2024 > 0:
            price_change = ((price_2025 - price_2024) / price_2024) * 100
            # Pre-format price values to avoid f-string formatting issues
            price_2024_formatted = f"${price_2024:,.0f}"
            price_2025_formatted = f"${price_2025:,.0f}"
            change_percent = f"{price_change:.1f}%"
            
            if price_change > 5:
                insights.append(f"📈 **Prices Up {change_percent}**: From {price_2024_formatted} to {price_2025_formatted}")
            elif price_change < -5:
                abs_change = f"{abs(price_change):.1f}%"
                insights.append(f"📉 **Prices Down {abs_change}**: From {price_2024_formatted} to {price_2025_formatted}")
            else:
                insights.append(f"📊 **Stable Pricing**: {price_2025_formatted} (similar to 2024)")
    
    # Sales volume with clear explanation
    sales_2025 = len(df_2025)
    sales_2024 = len(df_2024)
    
    if sales_2024 > 0:
        # Get current month to project full year
        current_month = datetime.now().month
        projected_2025 = (sales_2025 / current_month) * 12 if current_month > 0 else sales_2025
        
        insights.append(f"📊 **2025 Activity**: {sales_2025} sales so far (on pace for ~{projected_2025:.0f} total vs {sales_2024} in 2024)")
    
    # DOM trends with clear language
    if 'median_dom' in metrics_2025 and 'median_dom' in metrics_2024:
        dom_2025 = metrics_2025['median_dom']
        dom_2024 = metrics_2024['median_dom']
        
        if dom_2025 < dom_2024 * 0.9:
            insights.append(f"⚡ **Selling Faster**: {dom_2025:.0f} days vs {dom_2024:.0f} days in 2024")
        elif dom_2025 > dom_2024 * 1.1:
            insights.append(f"🐌 **Taking Longer**: {dom_2025:.0f} days vs {dom_2024:.0f} days in 2024")
        else:
            insights.append(f"📊 **Similar Speed**: ~{dom_2025:.0f} days (consistent with 2024)")
    
    return fig, comparison_df, insights

def create_current_market_analysis(df_sold):
    """Analyze current market conditions"""
    if len(df_sold) == 0:
        return None
    
    # Get different time periods for comparison
    recent_3m = get_recent_market_data(df_sold, 3)
    recent_6m = get_recent_market_data(df_sold, 6)
    recent_12m = get_recent_market_data(df_sold, 12)
    
    periods = {
        'Last 3 Months': recent_3m,
        'Last 6 Months': recent_6m,
        'Last 12 Months': recent_12m
    }
    
    comparison_data = []
    for period_name, period_data in periods.items():
        if len(period_data) > 0:
            stats = calculate_market_stats(period_data)
            stats['Period'] = period_name
            stats['Sales_Count'] = len(period_data)
            comparison_data.append(stats)
    
    if not comparison_data:
        return None
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create comparison chart
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Median Price Trends', 'Days on Market', 'Price per SqFt', 'Sales Volume'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    metrics = [
        ('median_price', 'Median Price ($)', 1, 1),
        ('median_dom', 'Median DOM', 1, 2),
        ('median_price_per_sqft', 'Median $/SqFt', 2, 1),
        ('Sales_Count', 'Sales Count', 2, 2)
    ]
    
    for metric, title, row, col in metrics:
        if metric in comparison_df.columns:
            fig.add_trace(
                go.Bar(x=comparison_df['Period'], y=comparison_df[metric], 
                      name=title, showlegend=False),
                row=row, col=col
            )
    
    fig.update_layout(height=600, title_text="Market Trends Comparison")
    
    return fig

def main():
    # App header
    st.markdown('<h1 class="main-header">🏠 Neighborhood Real Estate Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading and processing data...'):
        datasets = load_data()
    
    # Check if data loaded successfully
    available_datasets = {k: v for k, v in datasets.items() if v is not None}
    
    if not available_datasets:
        st.error("❌ No datasets could be loaded. Please check file paths and data availability.")
        return
    
    # Get combined dataset for analysis
    rebecca_data = available_datasets.get('Rebecca Ridge', {})
    sunrise_data = available_datasets.get('Sunrise Area', {})
    
    # Use broader Sunrise data as primary, Rebecca Ridge as context
    if sunrise_data and rebecca_data:
        df_all = sunrise_data['all']
        df_sold = sunrise_data['sold']
        primary_description = "Sunrise Area & Rebecca Ridge Combined Analysis"
        
        # Show combined market info in sidebar
        st.sidebar.header("📊 Market Data")
        
        # Get recent data for both areas
        rebecca_recent = get_recent_market_data(rebecca_data['sold'], 12)
        sunrise_recent = get_recent_market_data(sunrise_data['sold'], 12)
        
        rr_median = rebecca_recent['Selling Price'].median() if len(rebecca_recent) > 0 else 0
        sunrise_median = sunrise_recent['Selling Price'].median() if len(sunrise_recent) > 0 else 0
        
        st.sidebar.markdown(f"""
        **Rebecca Ridge:**
        - {rebecca_data['sold_records']} sold properties
        - Median: ${rr_median:,.0f}
        
        **Sunrise Area:**
        - {sunrise_data['sold_records']} sold properties  
        - Median: ${sunrise_median:,.0f}
        """)
        
    elif rebecca_data:
        df_all = rebecca_data['all']
        df_sold = rebecca_data['sold']
        primary_description = rebecca_data['description']
    elif sunrise_data:
        df_all = sunrise_data['all']
        df_sold = sunrise_data['sold']
        primary_description = sunrise_data['description']
    else:
        st.error("No data available")
        return
    
    # Update header
    st.markdown(f"### 📍 Market Analysis: **{primary_description}**")
    
    # Add context about data filtering
    st.markdown("""
    <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #1f77b4;">
        <strong>📏 Data Focus:</strong> Analysis limited to homes between 1,100-1,900 sq ft built through 2020 for accurate comparisons of established market values.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("🔍 Additional Filters")
    
    # Date range filter
    if 'Selling Date' in df_sold.columns and len(df_sold) > 0:
        min_date = df_sold['Selling Date'].min().date()
        max_date = df_sold['Selling Date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_sold = df_sold[
                (df_sold['Selling Date'].dt.date >= start_date) & 
                (df_sold['Selling Date'].dt.date <= end_date)
            ]
    
    # Property type filter
    if 'Property Sub Type' in df_sold.columns:
        property_types = df_sold['Property Sub Type'].dropna().unique()
        if len(property_types) > 1:
            selected_types = st.sidebar.multiselect(
                "Property Types",
                options=property_types,
                default=property_types
            )
            df_sold = df_sold[df_sold['Property Sub Type'].isin(selected_types)]
    
    # Price range filter
    if 'Selling Price' in df_sold.columns and len(df_sold) > 0:
        min_price = int(df_sold['Selling Price'].min())
        max_price = int(df_sold['Selling Price'].max())
        
        price_range = st.sidebar.slider(
            "Price Range ($)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=10000,
            format="$%d"
        )
        
        df_sold = df_sold[
            (df_sold['Selling Price'] >= price_range[0]) & 
            (df_sold['Selling Price'] <= price_range[1])
        ]
    
    # Main content
    if len(df_sold) == 0:
        st.warning("No data available for the selected filters.")
        return
    
    # Create top-level tabs for the entire analysis
    summary_tab, analysis_tab, pricing_tab, proceeds_tab = st.tabs(["📋 Executive Summary", "📈 Market Analysis", "💰 Price Recommendation", "📊 Net Proceeds"])
    
    # === EXECUTIVE SUMMARY TAB ===
    with summary_tab:
        # Header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; border-left: 4px solid #007bff;">
            <h1 style="margin: 0; color: #495057; font-size: 2.2em;">📋 Executive Summary</h1>
            <h3 style="margin: 0.5rem 0 0 0; color: #6c757d;">12903 158th Street Ct E Market Analysis</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-style: italic;">Comprehensive real estate market overview and pricing strategy</p>
            <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 0.9em;">Prepared by Nathan Coons, Managing Broker - Washington Realty Group</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get pricing data for summary
        if len(available_datasets) > 1:
            sunrise_sold = sunrise_data.get('sold', pd.DataFrame())
            rebecca_sold = rebecca_data.get('sold', pd.DataFrame())
            pricing = analyze_premium_home_pricing(sunrise_sold, rebecca_sold, 1576)
            recent_data = get_recent_market_data(df_sold, 12)
            recent_stats = calculate_market_stats(recent_data)
            
            if pricing:
                sunrise_premium = ((pricing['recommended_price'] - pricing['sunrise_median']) / pricing['sunrise_median']) * 100
                
                # Text-based executive summary - pre-format all price values
                recommended_price = f"${pricing['recommended_price']:,.0f}"
                premium_psf = f"${pricing['premium_psf']:.0f}"
                premium_percent = f"{sunrise_premium:.0f}%"
                sunrise_median = f"${recent_stats.get('median_price', 0):,.0f}"
                rebecca_median = f"${pricing['rebecca_median']:,.0f}"
                median_dom = f"{recent_stats.get('median_dom', 0):.0f}"
                
                st.markdown("## Executive Summary")
                
                st.markdown("**Property:** 12903 158th Street Ct E represents a premium luxury home opportunity in an optimal market segment. This extensively remodeled home sits in the optimal size category for current buyer demand and features over $100,000 in premium upgrades throughout.")
                
                st.markdown("**Market Dynamics:** The current real estate market is experiencing mixed trends that strongly favor your property's positioning. The market is experiencing a mix of trends, with larger homes over 2,000 square feet facing longer market times, while homes in the 1,100-1,900 square foot range continue to favor sellers. Your 1,576 square foot home sits in the optimal size category for current buyer demand.")
                
                st.markdown("**Competitive Advantages:** This property benefits from over $100,000 in premium upgrades that justify the premium positioning. Key improvements include a complete roof replacement, new AC system, custom built staircase, and elegant custom deck on the structural side, complemented by a luxury kitchen remodel, custom master suite with spa-like shower, custom built-ins, high tech wiring, shiplap feature walls, and new premium flooring throughout the main floor with abundant natural light. These improvements position the home as move-in ready luxury rather than a fixer-upper.")
                
                
                st.markdown("**Strategic Positioning:** The extensive remodel elevates this property above standard market offerings. The combination of structural improvements (roof, HVAC, custom staircase, deck) and luxury interior upgrades (kitchen, master suite, shower, built-ins, premium flooring, feature walls) creates a compelling value proposition for buyers seeking turnkey luxury.")
                
                st.markdown("**Recommendation:** The extensive improvements and premium positioning justify a premium price point to capture the luxury market while remaining competitive within the established range. This strategy leverages the current seller-favorable conditions in your segment while the extensive improvements justify the premium over standard comparable properties.")
                
                # Market Timing Alert Box - More Visible
                st.markdown("""
                <div style="background-color: #fff3cd; padding: 1.5rem; border-radius: 0.8rem; border-left: 4px solid #ffc107; margin: 2rem 0; border: 1px solid #ffeaa7;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #856404;"><i>⚠️ Market Timing Alert</i></h4>
                    <p style="margin: 0; color: #856404; font-weight: 500;">
                        The real estate market is moving every day and appears to be slipping. While current conditions favor sellers in your size segment, <strong>this window may not stick around</strong>. Acting decisively on pricing and marketing strategy is essential to capitalize on present market conditions before they shift.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Simple bottom line in box
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; border-left: 4px solid #007bff; margin: 2rem 0;">
                    <h3 style="margin: 0; color: #495057;">🎯 Bottom Line</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #495057; font-size: 1.1em;">
                        <strong>Premium luxury positioning</strong> — Optimal market segment with seller-favorable conditions and extensive improvements justify premium pricing.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("⚠️ Unable to generate executive summary - insufficient pricing data")
        else:
            st.warning("⚠️ Executive summary requires both Rebecca Ridge and Sunrise datasets")
    
    # === MARKET ANALYSIS TAB ===
    with analysis_tab:
        # Key metrics overview - simplified for client presentation
        st.header("📊 Current Market Snapshot")
        st.markdown("*Based on Sunrise area data (1,100-1,900 sq ft, 2+ story, built through 2020, last 12 months)*")
        
        recent_data = get_recent_market_data(df_sold, 12)
        recent_stats = calculate_market_stats(recent_data)
        
        # More prominent display of key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                <h3 style="margin: 0; color: #495057;">Median Price</h3>
                <h1 style="margin: 0.5rem 0; color: #007bff;">{sunrise_median}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                <h3 style="margin: 0; color: #495057;">Price per SqFt</h3>
                <h1 style="margin: 0.5rem 0; color: #28a745;">${recent_stats.get('median_price_per_sqft', 0):.0f}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                <h3 style="margin: 0; color: #495057;">Days on Market</h3>
                <h1 style="margin: 0.5rem 0; color: #6c757d;">{recent_stats.get('median_dom', 0):.0f} days</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Add detailed context to explain the market snapshot numbers
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745;">
        <h4 style="color: #155724; margin-top: 0;">📋 Understanding These Numbers</h4>
        <p style="margin-bottom: 1rem; color: #495057;">
        <strong>What you're seeing:</strong> These metrics represent the <em>median values</em> for homes sold in the last 12 months 
        within our specific criteria (1,100-1,900 sq ft, built through 2020). Here's why these numbers provide accurate market insight:
        </p>
        
        <ul style="color: #495057; margin-bottom: 1rem;">
        <li><strong>Median Price:</strong> The middle value of all recent sales - more reliable than averages because it's not skewed by extreme high or low sales</li>
        <li><strong>Size-Filtered Data:</strong> We're comparing similar-sized homes (1,100-1,900 sq ft) to ensure accurate comparisons for your property</li>
        <li><strong>Recent Market Focus:</strong> Last 12 months only - reflects current market conditions, not historical peaks</li>
        <li><strong>Established Homes:</strong> Built through 2020 - excludes new construction premiums that don't apply to existing homes</li>
        </ul>
        
        <p style="color: #495057; margin-bottom: 0;">
        <strong>💡 For Premium Properties:</strong> High-end renovated homes typically command 15-25% premiums above these baseline numbers. 
        The pricing analysis below shows how your specific property's features and improvements position it in the market.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Market Timing Alert in Analysis Tab
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1.5rem; border-radius: 0.8rem; border-left: 4px solid #ffc107; margin: 2rem 0; border: 1px solid #ffeaa7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #856404;"><i>⚠️ Market Timing Alert</i></h4>
            <p style="margin: 0; color: #856404; font-weight: 500;">
                Market conditions are shifting daily. Current seller-favorable trends in your size segment may not persist. <strong>Time-sensitive opportunity</strong> - act quickly while conditions remain favorable.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # === SECTION 1: HISTORICAL MARKET PERFORMANCE ===
        st.markdown("---")
        st.header("📈 Historical Market Performance")
        st.markdown("""
        **Understanding Long-Term Trends:** This chart shows how home prices have evolved over time in the broader Sunrise area. 
        Look for patterns in pricing cycles, seasonal trends, and overall market direction.
        """)
        
        price_chart = create_price_trend_chart(df_sold)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True)
            
            # Add context below the chart
            st.markdown("""
            **💡 How to Read This:** 
            - **Blue line** shows median sale prices by month
            - **Orange dashed line** shows average prices  
            - **Green line** tracks price per square foot (right axis)
            """)
        else:
            st.info("Historical price trend data not available.")
        
        # === SECTION 2: PROPERTY VALUE ANALYSIS ===
        st.markdown("---")
        st.header("🏘️ Property Value Analysis")
        st.markdown("""
        **Size vs. Price Relationship:** Understanding how square footage impacts home values helps determine 
        if a property is priced competitively and identify the best value opportunities.
        """)
        
        # Price by home size chart (full width)
        st.subheader("Price by Home Size")
        price_chart = create_simplified_price_chart(df_sold)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True)
            st.markdown("**💡 What This Shows:** Each dot represents a sold home. Hover over dots to see details about address, price, and size.")
        else:
            st.info("Price vs size data not available.")
        
        # === TOP PERFORMING SALES - SEPARATE SECTION ===
        st.markdown("---")
        st.header("🏆 Top Performing Sales")
        st.markdown("*The highest-selling homes set the value ceiling for comparison*")
        
        # Create three tabs for different categories
        tab1, tab2, tab3 = st.tabs(["📏 Your Square Footage (1500-1600 sq ft)", "🏘️ Rebecca Ridge (All)", "🌅 Sunrise Area (All)"])
        
        with tab1:
            st.markdown("**Top performers in your exact size range (1500-1600 sq ft):**")
            # Filter for 1500-1600 sq ft specifically
            size_filtered = df_sold[(df_sold['Finished Sqft'] >= 1500) & (df_sold['Finished Sqft'] <= 1600)]
            top_size_sales = get_top_sales(size_filtered, 5)
            
            if not top_size_sales.empty:
                # Create horizontal tiles layout
                cols = st.columns(min(len(top_size_sales), 5))
                
                for idx, (_, row) in enumerate(top_size_sales.iterrows()):
                    if idx < 5:  # Limit to 5 columns
                        with cols[idx]:
                            # Use appropriate price field based on status
                            price = row.get('Analysis_Price', row.get('Selling Price', 0))
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 0.5rem 0;">
                                <h3 style="margin: 0; color: white; font-size: 1.4em;">${price:,.0f}</h3>
                                <hr style="border-color: rgba(255,255,255,0.3); margin: 1rem 0;">
                                <p style="margin: 0.5rem 0; color: white; font-weight: bold;">{row.get('Full_Address', 'N/A')}</p>
                                <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                    {row.get('Finished Sqft', 'N/A'):.0f} sq ft<br>
                                    {row.get('Bedrooms', 'N/A'):.0f}bed/{row.get('Bathrooms', 'N/A'):.1f}bath<br>
                                    {row.get('Status', 'N/A')}<br>
                                    {row.get('Selling Date', 'N/A').strftime('%b %Y') if pd.notna(row.get('Selling Date')) else 'Recent'}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("**💡 Direct Comparables:** These homes match your exact square footage range and represent your most direct competition.")
            else:
                st.info("No properties available in the 1500-1600 sq ft range.")
        
        with tab2:
            if rebecca_data and 'sold' in rebecca_data:
                st.markdown("**Top performers within Rebecca Ridge neighborhood (all sizes):**")
                rebecca_top_sales = get_top_sales(rebecca_data['sold'], 5)
                
                if not rebecca_top_sales.empty:
                    # Create horizontal tiles layout
                    cols = st.columns(min(len(rebecca_top_sales), 5))
                    
                    for idx, (_, row) in enumerate(rebecca_top_sales.iterrows()):
                        if idx < 5:  # Limit to 5 columns
                            with cols[idx]:
                                # Use appropriate price field based on status
                                price = row.get('Analysis_Price', row.get('Selling Price', 0))
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 0.5rem 0;">
                                    <h3 style="margin: 0; color: white; font-size: 1.4em;">${price:,.0f}</h3>
                                    <hr style="border-color: rgba(255,255,255,0.3); margin: 1rem 0;">
                                    <p style="margin: 0.5rem 0; color: white; font-weight: bold;">{row.get('Full_Address', 'N/A')}</p>
                                    <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                        {row.get('Finished Sqft', 'N/A'):.0f} sq ft<br>
                                        {row.get('Bedrooms', 'N/A'):.0f}bed/{row.get('Bathrooms', 'N/A'):.1f}bath<br>
                                        {row.get('Status', 'N/A')}<br>
                                        {row.get('Selling Date', 'N/A').strftime('%b %Y') if pd.notna(row.get('Selling Date')) else 'Recent'}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("**💡 Neighborhood Performance:** The highest achievers specifically within Rebecca Ridge, showing local market potential.")
                else:
                    st.info("No sales data available for Rebecca Ridge.")
            else:
                st.info("Rebecca Ridge data not available.")
                
        with tab3:
            st.markdown("**Top performers across the broader Sunrise area (all sizes):**")
            top_sunrise_sales = get_top_sales(df_sold, 5)
            
            if not top_sunrise_sales.empty:
                # Create horizontal tiles layout
                cols = st.columns(min(len(top_sunrise_sales), 5))
                
                for idx, (_, row) in enumerate(top_sunrise_sales.iterrows()):
                    if idx < 5:  # Limit to 5 columns
                        with cols[idx]:
                            # Use appropriate price field based on status
                            price = row.get('Analysis_Price', row.get('Selling Price', 0))
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #ff7f0e 0%, #ff6b6b 100%); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 0.5rem 0;">
                                <h3 style="margin: 0; color: white; font-size: 1.4em;">${price:,.0f}</h3>
                                <hr style="border-color: rgba(255,255,255,0.3); margin: 1rem 0;">
                                <p style="margin: 0.5rem 0; color: white; font-weight: bold;">{row.get('Full_Address', 'N/A')}</p>
                                <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                    {row.get('Finished Sqft', 'N/A'):.0f} sq ft<br>
                                    {row.get('Bedrooms', 'N/A'):.0f}bed/{row.get('Bathrooms', 'N/A'):.1f}bath<br>
                                    {row.get('Status', 'N/A')}<br>
                                    {row.get('Selling Date', 'N/A').strftime('%b %Y') if pd.notna(row.get('Selling Date')) else 'Recent'}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("**💡 Market Ceiling:** The highest achievers across the broader Sunrise market, showing regional premium potential.")
            else:
                st.info("No sales data available for the broader Sunrise area.")
        
        # === SECTION 3: CURRENT MARKET CONDITIONS ===
        st.markdown("---")
        st.header("🎯 2025 vs 2024 Market Comparison")
        st.markdown("""
        **What's Different This Year:** Simple side-by-side comparison of 2025 vs 2024 
        to understand if the market is improving, declining, or staying consistent.
        """)
        
        trend_chart, comparison_data, trend_insights = analyze_2025_market_trend(df_sold)
        
        if trend_chart is not None:
            st.plotly_chart(trend_chart, use_container_width=True)
            
            st.markdown("### 📊 What This Tells Us")
            if trend_insights:
                for insight in trend_insights:
                    st.markdown(f"• {insight}")
            
            st.markdown("""
            **💡 How to Read This:** 
            - **Orange bars = 2024** performance
            - **Blue bars = 2025** performance (current year to date)
            - Compare the heights to see if 2025 is trending higher or lower
            """)
            
            # Data table removed - not helpful for client presentation
            
        elif isinstance(trend_insights, str):
            st.info(trend_insights)
        else:
            st.info("2025 market analysis not available.")
        
        # === SECTION 4: MARKET VELOCITY ===
        st.markdown("---")
        st.header("⚡ Market Velocity & Activity")
        st.markdown("""
        **Market Speed Indicators:** How quickly homes sell and current activity levels 
        help determine the best pricing and timing strategies.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            recent_3m = get_recent_market_data(df_sold, 3)
            recent_dom = recent_3m['DOM'].median() if len(recent_3m) > 0 and 'DOM' in recent_3m.columns else 0
            
            if recent_dom <= 30:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #4caf50 100%); padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #4caf50;">
                    <h4 style="margin: 0; color: #2e7d32;">🔥 Fast Market</h4>
                    <p style="margin: 0.5rem 0; font-size: 1.1em;">Homes sell in <strong>{recent_dom:.0f} days</strong></p>
                    <p style="margin: 0; color: #2e7d32;"><em>Sellers' market conditions</em></p>
                </div>
                """, unsafe_allow_html=True)
            elif recent_dom <= 60:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%); padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #ff9800;">
                    <h4 style="margin: 0; color: #e65100;">📊 Balanced Market</h4>
                    <p style="margin: 0.5rem 0; font-size: 1.1em;">Homes sell in <strong>{recent_dom:.0f} days</strong></p>
                    <p style="margin: 0; color: #e65100;"><em>Normal market conditions</em></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%); padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #e91e63;">
                    <h4 style="margin: 0; color: #ad1457;">🐌 Slower Market</h4>
                    <p style="margin: 0.5rem 0; font-size: 1.1em;">Homes sell in <strong>{recent_dom:.0f} days</strong></p>
                    <p style="margin: 0; color: #ad1457;"><em>Buyers' market conditions</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        # === SECTION 6: STRATEGIC INSIGHTS ===
        st.markdown("---")
        st.header("💡 Strategic Market Insights")
        st.markdown("""
        **Current Market Analysis:** Key takeaways and strategic recommendations based on **recent market activity only** 
        (not the full 20+ year historical data).
        """)
        
        # Focus on recent data only for strategic insights
        recent_24m = get_recent_market_data(df_sold, 24)  # Last 2 years
        recent_12m = get_recent_market_data(df_sold, 12)  # Last 12 months
        
        if len(recent_12m) == 0:
            st.info("Insufficient recent market data for strategic insights.")
        else:
            # Recent market stats
            stats_24m = calculate_market_stats(recent_24m) if len(recent_24m) > 0 else {}
            stats_12m = calculate_market_stats(recent_12m)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Market Positioning")
                
                if stats_24m and stats_12m:
                    median_change = ((stats_12m.get('median_price', 0) - stats_24m.get('median_price', 0)) / stats_24m.get('median_price', 1)) * 100
                    dom_change = stats_12m.get('median_dom', 0) - stats_24m.get('median_dom', 0)
                    
                    if median_change > 5:
                        price_trend = "📈 Appreciating"
                        price_color = "#4caf50"
                    elif median_change < -5:
                        price_trend = "📉 Declining"
                        price_color = "#f44336"
                    else:
                        price_trend = "➡️ Stable"
                        price_color = "#ff9800"
                    
                    if dom_change < -10:
                        speed_trend = "⚡ Accelerating"
                        speed_color = "#4caf50"
                    elif dom_change > 10:
                        speed_trend = "🐌 Slowing"
                        speed_color = "#f44336"
                    else:
                        speed_trend = "➡️ Consistent"
                        speed_color = "#ff9800"
                    
                    st.markdown(f"""
                    **Recent Trends:**
                    - **Price Direction:** <span style="color: {price_color};">{price_trend}</span> ({median_change:+.1f}%)
                    - **Market Speed:** <span style="color: {speed_color};">{speed_trend}</span> ({dom_change:+.0f} days)
                    - **Current Median:** ${stats_12m.get('median_price', 0):,.0f}
                    - **Recent Sales:** {len(recent_12m)} properties
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                **Pricing Strategy:**
                - Price competitively within market range
                - Recent median: ${stats_12m.get('median_price', 0):,.0f}
                - Average DOM: {stats_12m.get('median_dom', 0):.0f} days
                """)
            
            with col2:
                st.markdown("### 📊 Market Activity")
                
                # Recent sales by month
                if 'Sale_Year_Month' in recent_12m.columns:
                    monthly_activity = recent_12m.groupby('Sale_Year_Month').size().tail(6)
                    avg_monthly_sales = monthly_activity.mean()
                    
                    latest_month_sales = monthly_activity.iloc[-1] if len(monthly_activity) > 0 else 0
                    
                    if latest_month_sales > avg_monthly_sales * 1.2:
                        activity_level = "🔥 High Activity"
                        activity_color = "#4caf50"
                    elif latest_month_sales < avg_monthly_sales * 0.8:
                        activity_level = "😴 Low Activity"
                        activity_color = "#f44336"
                    else:
                        activity_level = "📊 Normal Activity"
                        activity_color = "#ff9800"
                    
                    st.markdown(f"""
                    **Recent Activity:**
                    - **Current Level:** <span style="color: {activity_color};">{activity_level}</span>
                    - **This Month:** {latest_month_sales} sales
                    - **6-Month Avg:** {avg_monthly_sales:.1f} sales/month
                    """, unsafe_allow_html=True)
                
                # Price range distribution
                if len(recent_12m) > 0 and 'Selling Price' in recent_12m.columns:
                    price_ranges = {
                        "Under $500k": len(recent_12m[recent_12m['Selling Price'] < 500000]),
                        "$500k-$600k": len(recent_12m[(recent_12m['Selling Price'] >= 500000) & (recent_12m['Selling Price'] < 600000)]),
                        "$600k+": len(recent_12m[recent_12m['Selling Price'] >= 600000])
                    }
                    
                    st.markdown("**Price Range Activity:**")
                    for range_name, count in price_ranges.items():
                        pct = (count / len(recent_12m)) * 100
                        st.markdown(f"- {range_name}: {count} sales ({pct:.0f}%)")
        
        # Footer for analysis tab
        st.markdown("---")
        st.markdown("*Analysis based on Sunrise area data (1,100-1,900 sq ft, 2+ story, built through 2020)*")
    
    # === PRICING TAB ===
    with pricing_tab:
        # Market Timing Alert at top of pricing tab
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1.5rem; border-radius: 0.8rem; border-left: 4px solid #ffc107; margin: 2rem 0; border: 1px solid #ffeaa7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #856404;"><i>⚠️ Market Timing Alert</i></h4>
            <p style="margin: 0; color: #856404; font-weight: 500;">
                Market conditions are shifting daily and appear to be slipping. <strong>This pricing window may not last</strong>. Quick action on pricing strategy is essential to capitalize on current market conditions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if len(available_datasets) > 1:  # Show when both datasets available
            # Header with property details
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; border-left: 4px solid #007bff;">
                <h1 style="margin: 0; color: #495057; font-size: 2.2em;">🏠 Premium Home Pricing Analysis</h1>
                <h3 style="margin: 0.5rem 0 0 0; color: #6c757d;">12903 158th Street Ct E, Puyallup WA</h3>
                <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-style: italic;">Extensively remodeled luxury home • 1,576 sq ft • 3 bed, 2.5 bath • Built 2000</p>
                <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 0.9em;">Prepared by Nathan Coons, Managing Broker - Washington Realty Group</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Get both datasets for analysis
            sunrise_sold = sunrise_data.get('sold', pd.DataFrame())
            rebecca_sold = rebecca_data.get('sold', pd.DataFrame())
            
            # Calculate pricing analysis using broader market (fixed at 1600 sq ft)
            pricing = analyze_premium_home_pricing(sunrise_sold, rebecca_sold, 1576)
            
            if pricing:
                # MAIN PRICING RECOMMENDATION - Full Width
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 3rem; border-radius: 1rem; text-align: center; margin: 2rem 0;">
                    <h2 style="margin: 0; color: white; font-weight: 300; opacity: 0.9;">🎯 Recommended List Price</h2>
                    <h1 style="margin: 1rem 0; color: white; font-size: 3.5em; font-weight: bold;">{recommended_price}</h1>
                    <p style="margin: 0; color: white; opacity: 0.9; font-size: 1.2em;">Premium luxury home pricing strategy</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # THREE COLUMN LAYOUT FOR KEY METRICS
                col1, col2, col3 = st.columns(3)
                
                sunrise_premium = ((pricing['recommended_price'] - pricing['sunrise_median']) / pricing['sunrise_median']) * 100
                
                with col1:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                        <h4 style="margin: 0; color: #495057;">Market Premium</h4>
                        <h2 style="margin: 0.5rem 0; color: #28a745;">+{sunrise_premium:.0f}%</h2>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">Above Sunrise median</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                        <h4 style="margin: 0; color: #495057;">Price per SqFt</h4>
                        <h2 style="margin: 0.5rem 0; color: #007bff;">${pricing['premium_psf']:.0f}</h2>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">Premium positioning</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if pricing['sunrise_dom'] <= 15:
                        market_speed = "🔥 Very Fast"
                        timing_strategy = "List immediately"
                        speed_color = "#28a745"
                    elif pricing['sunrise_dom'] <= 30:
                        market_speed = "🚀 Fast Moving"
                        timing_strategy = "List within 2 weeks"
                        speed_color = "#ffc107"
                    else:
                        market_speed = "📊 Normal Pace"
                        timing_strategy = "Prepare thoroughly"
                        speed_color = "#6c757d"
                    
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.8rem; text-align: center; border: 1px solid #dee2e6;">
                        <h4 style="margin: 0; color: #495057;">Market Speed</h4>
                        <h2 style="margin: 0.5rem 0; color: {speed_color};">{pricing['sunrise_dom']:.0f} days</h2>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">{market_speed}</p>
                        <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.8em; font-style: italic;">Premium luxury homes typically take 30-60 days</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # TWO COLUMN LAYOUT FOR DETAILED INFO
                col1, col2 = st.columns([1.2, 1])
                
                with col1:
                    st.markdown("### 🏆 Premium Features & Upgrades")
                    
                    # Structural & Systems section
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 1.2rem; border-radius: 0.6rem; border-left: 4px solid #007bff; margin-bottom: 1rem;">
                        <h5 style="margin: 0 0 0.8rem 0; color: #495057;">🏠 Structural & Systems</h5>
                        <div style="color: #495057;">
                            • <strong>New roof</strong> - Complete replacement<br>
                            • <strong>New AC system</strong> - Modern HVAC<br>
                            • <strong>Custom built staircase</strong> - Architectural feature<br>
                            • <strong>Custom built deck</strong> - Outdoor living space
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Interior Luxury section
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 1.2rem; border-radius: 0.6rem; border-left: 4px solid #28a745;">
                        <h5 style="margin: 0 0 0.8rem 0; color: #495057;">✨ Interior Luxury</h5>
                        <div style="color: #495057;">
                            • <strong>Luxury kitchen remodel</strong> - High-end finishes<br>
                            • <strong>Custom master suite</strong> - Completely redesigned<br>
                            • <strong>Spa-like custom shower</strong> - Luxury experience<br>
                            • <strong>Custom built-ins</strong> - Integrated storage solutions<br>
                            • <strong>High tech wiring</strong> - Modern electrical systems<br>
                            • <strong>Shiplap feature walls</strong> - Designer accent walls<br>
                            • <strong>New premium flooring</strong> - Throughout main floor<br>
                            • <strong>Natural light</strong> - Abundant throughout
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;">
                        <strong>💡 Investment Summary:</strong> Over $100,000 in premium upgrades justify the {sunrise_premium:.0f}% premium positioning above standard market rates.
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 📊 Market Context")
                    
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
                        <strong>Sunrise Area Median:</strong><br>
                        <span style="color: #007bff; font-size: 1.1em;">{sunrise_median}</span><br>
                        <small style="color: #6c757d;">(broader market baseline)</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
                        <strong>Rebecca Ridge Median:</strong><br>
                        <span style="color: #28a745; font-size: 1.1em;">{rebecca_median}</span><br>
                        <small style="color: #6c757d;">(neighborhood context)</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #6c757d;">
                        <strong>Strategic Timing:</strong><br>
                        <span style="color: #495057;">{timing_strategy}</span><br>
                        <small style="color: #6c757d;">Market conditions favor sellers</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # COMPARABLE SALES SECTION
                st.markdown("---")
                st.markdown("### 📈 Supporting Market Data")
                
                comp_col1, comp_col2 = st.columns(2)
                
                with comp_col1:
                    st.markdown("**🌅 Sunrise Area Recent Sales**")
                    if len(pricing['sunrise_top']) > 0:
                        for idx, (_, row) in enumerate(pricing['sunrise_top'].iterrows()):
                            price = row['Selling Price']
                            sqft = row.get('Finished Sqft', 0)
                            psf = price / sqft if sqft > 0 else 0
                            date = row.get('Selling Date', 'Unknown')
                            if pd.notna(date):
                                date = date.strftime('%b %Y')
                            
                            mls = row.get('Listing Number', 'N/A')
                            address = row.get('Full_Address', 'N/A')
                            
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 0.4rem; margin: 0.5rem 0; border-left: 3px solid #007bff;">
                                <strong>${price:,.0f}</strong> • {sqft:.0f} sq ft • ${psf:.0f}/sq ft<br>
                                <strong>{address}</strong><br>
                                <small style="color: #6c757d;">MLS #{mls} • {date}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No comparable sales data available")
                
                with comp_col2:
                    st.markdown("**🏘️ Rebecca Ridge Recent Sales**")
                    if len(pricing['rebecca_top']) > 0:
                        for idx, (_, row) in enumerate(pricing['rebecca_top'].iterrows()):
                            price = row['Selling Price']
                            sqft = row.get('Finished Sqft', 0)
                            psf = price / sqft if sqft > 0 else 0
                            date = row.get('Selling Date', 'Unknown')
                            if pd.notna(date):
                                date = date.strftime('%b %Y')
                            
                            mls = row.get('Listing Number', 'N/A')
                            address = row.get('Full_Address', 'N/A')
                            
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 0.4rem; margin: 0.5rem 0; border-left: 3px solid #28a745;">
                                <strong>${price:,.0f}</strong> • {sqft:.0f} sq ft • ${psf:.0f}/sq ft<br>
                                <strong>{address}</strong><br>
                                <small style="color: #6c757d;">MLS #{mls} • {date}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No comparable sales data available")
                
                # FINAL STRATEGY SUMMARY
                st.markdown("---")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 1rem; border-left: 4px solid #007bff; margin: 2rem 0;">
                    <h4 style="margin: 0 0 1rem 0; color: #495057;">🎯 Final Recommendation</h4>
                    <p style="margin: 0; color: #495057; font-size: 1.1em; line-height: 1.6;">
                        <strong>List at ${pricing['recommended_price']:,.0f}</strong> to position as a premium luxury option while remaining competitive within the established market range. 
                        The extensive remodel and custom features justify the {sunrise_premium:.0f}% premium over the broader Sunrise market median.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.error("⚠️ Insufficient market data for pricing analysis. Please check data availability.")
        else:
            st.warning("⚠️ Both Rebecca Ridge and Sunrise datasets needed for pricing analysis.")
    
    # === NET PROCEEDS TAB ===
    with proceeds_tab:
        # Market Timing Alert at top of net proceeds tab
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1.5rem; border-radius: 0.8rem; border-left: 4px solid #ffc107; margin: 2rem 0; border: 1px solid #ffeaa7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #856404;"><i>⚠️ Market Timing Alert</i></h4>
            <p style="margin: 0; color: #856404; font-weight: 500;">
                Market conditions are changing rapidly. <strong>Current pricing may not hold</strong> if market continues to slip. Consider these proceeds calculations as time-sensitive projections.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(available_datasets) > 1:
            # Get pricing data
            sunrise_sold = sunrise_data.get('sold', pd.DataFrame())
            rebecca_sold = rebecca_data.get('sold', pd.DataFrame())
            pricing = analyze_premium_home_pricing(sunrise_sold, rebecca_sold, 1576)
            
            if pricing:
                st.header("💰 Net Proceeds Calculator")
                st.markdown("*Calculate your actual take-home amount after all selling costs*")
                
                # Use recommended price as default but allow adjustment
                final_sale_price = st.number_input(
                    "Final Sale Price", 
                    min_value=400000, 
                    max_value=800000, 
                    value=int(pricing['recommended_price']), 
                    step=5000,
                    help="Adjust this to see how different sale prices affect your net proceeds"
                )
                
                # Selling costs inputs
                st.markdown("#### 📋 Selling Costs")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    listing_agent_rate = st.slider("Listing Agent Compensation (%)", 1.0, 4.0, 2.5, 0.25)
                    selling_agent_rate = st.slider("Selling Agent Compensation (%)", 0.0, 4.0, 2.5, 0.25, help="Not mandatory - set to 0 if not offering")
                    commission_rate = listing_agent_rate + selling_agent_rate
                    title_insurance = st.number_input("Title Insurance", value=1300, step=100)
                    escrow_fees = st.number_input("Escrow Fees", value=1400, step=100)
                    mortgage_payoff = st.number_input("Mortgage Payoff", value=285000, step=1000, help="Remaining balance on current mortgage")
                    
                with col2:
                    transfer_tax = st.number_input("Transfer Tax/Recording", value=500, step=50)
                    excise_tax = st.number_input("Excise Tax", value=9000, step=100, help="Washington state real estate excise tax")
                    misc_fees = st.number_input("Misc. Closing Costs", value=300, step=50)
                
                # Seller concessions
                concessions = st.number_input(
                    "Buyer Concessions (if any)", 
                    value=0, 
                    step=1000,
                    help="Amount you agree to pay toward buyer's closing costs"
                )
                
                # Calculate proceeds
                commission = final_sale_price * (commission_rate / 100)
                total_costs = commission + title_insurance + escrow_fees + transfer_tax + excise_tax + misc_fees + concessions
                net_proceeds = final_sale_price - total_costs - mortgage_payoff
                
                # Display results
                st.markdown("---")
                st.markdown("### 📊 Proceeds Breakdown")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    listing_commission = final_sale_price * (listing_agent_rate / 100)
                    selling_commission = final_sale_price * (selling_agent_rate / 100)
                    
                    st.markdown(f"""
                    **Sale Details:**
                    - **Sale Price:** ${final_sale_price:,.0f}
                    - **Listing Agent Compensation ({listing_agent_rate}%):** ${listing_commission:,.0f}
                    - **Selling Agent Compensation ({selling_agent_rate}%):** ${selling_commission:,.0f}
                    - **Title & Escrow:** ${title_insurance + escrow_fees:,.0f}
                    - **Excise Tax:** ${excise_tax:,.0f}
                    - **Other Taxes & Fees:** ${transfer_tax + misc_fees:,.0f}
                    - **Buyer Concessions:** ${concessions:,.0f}
                    - **Mortgage Payoff:** ${mortgage_payoff:,.0f}
                    """)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 2rem; border-radius: 1rem; text-align: center;">
                        <h3 style="margin: 0; color: white;">💰 Net Proceeds</h3>
                        <h1 style="margin: 1rem 0; color: white; font-size: 2.2em;">${net_proceeds:,.0f}</h1>
                        <p style="margin: 0; color: white; opacity: 0.9;">After all selling costs</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Proceeds percentage
                proceeds_percentage = (net_proceeds / final_sale_price) * 100
                total_deductions = total_costs + mortgage_payoff
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; text-align: center;">
                    <strong>You keep {proceeds_percentage:.1f}% of the sale price</strong><br>
                    Selling costs: ${total_costs:,.0f} ({(total_costs/final_sale_price)*100:.1f}%) | 
                    Mortgage payoff: ${mortgage_payoff:,.0f} ({(mortgage_payoff/final_sale_price)*100:.1f}%)<br>
                    <strong>Total deductions: ${total_deductions:,.0f} ({(total_deductions/final_sale_price)*100:.1f}%)</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Pricing data needed for net proceeds calculator.")
        else:
            st.info("Both Rebecca Ridge and Sunrise datasets needed for net proceeds calculator.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Data updated through the latest available MLS records. Analysis includes sold, pending, and active properties.*")
    st.markdown("**Report prepared by Nathan Coons, Managing Broker - Washington Realty Group**")

if __name__ == "__main__":
    main()
