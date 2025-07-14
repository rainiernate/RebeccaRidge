import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from data_preprocessing import load_and_preprocess_data, get_recent_market_data, calculate_market_stats

# Configure Streamlit page
st.set_page_config(
    page_title="Neighborhood Real Estate Analysis",
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
    """Load and cache the processed data"""
    file_path = "/Users/nathancoons/RebeccaRidge/Full (38).txt"
    df_all, df_sold = load_and_preprocess_data(file_path)
    return df_all, df_sold

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
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Home Prices Over Time', 'Sales Volume'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # Price trends
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Median_Price'],
                  mode='lines+markers', name='Median Price',
                  line=dict(color='#1f77b4', width=3)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Mean_Price'],
                  mode='lines+markers', name='Mean Price',
                  line=dict(color='#ff7f0e', width=2, dash='dash')),
        row=1, col=1
    )
    
    # Price per sqft on secondary axis
    fig.add_trace(
        go.Scatter(x=monthly_stats['Date'], y=monthly_stats['Median_PriceSqFt'],
                  mode='lines', name='Median $/SqFt',
                  line=dict(color='#2ca02c', width=2),
                  yaxis='y2'),
        row=1, col=1
    )
    
    # Sales volume
    fig.add_trace(
        go.Bar(x=monthly_stats['Date'], y=monthly_stats['Sales_Count'],
               name='Sales Count', marker_color='#d62728'),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Neighborhood Real Estate Market Trends",
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Price per SqFt ($)", secondary_y=True, row=1, col=1)
    fig.update_yaxes(title_text="Number of Sales", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
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
            if price_change > 5:
                insights.append(f"📈 **Prices Up {price_change:.1f}%**: From ${price_2024:,.0f} to ${price_2025:,.0f}")
            elif price_change < -5:
                insights.append(f"📉 **Prices Down {abs(price_change):.1f}%**: From ${price_2024:,.0f} to ${price_2025:,.0f}")
            else:
                insights.append(f"📊 **Stable Pricing**: ${price_2025:,.0f} (similar to 2024)")
    
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
        df_all, df_sold = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters & Options")
    
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
    
    # Key metrics overview - simplified for client presentation
    st.header("📊 Current Market Snapshot")
    
    recent_data = get_recent_market_data(df_sold, 12)
    recent_stats = calculate_market_stats(recent_data)
    
    # More prominent display of key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; text-align: center; color: white;">
            <h2 style="margin: 0; color: white;">Median Price</h2>
            <h1 style="margin: 0.5rem 0; color: white;">${recent_stats.get('median_price', 0):,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 1rem; text-align: center; color: white;">
            <h2 style="margin: 0; color: white;">Price per SqFt</h2>
            <h1 style="margin: 0.5rem 0; color: white;">${recent_stats.get('median_price_per_sqft', 0):.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 2rem; border-radius: 1rem; text-align: center; color: white;">
            <h2 style="margin: 0; color: white;">Days on Market</h2>
            <h1 style="margin: 0.5rem 0; color: white;">{recent_stats.get('median_dom', 0):.0f} days</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SECTION 1: HISTORICAL MARKET PERFORMANCE ===
    st.markdown("---")
    st.header("📈 Historical Market Performance")
    st.markdown("""
    **Understanding Long-Term Trends:** This chart shows how home prices have evolved over time in your neighborhood. 
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
        - **Green line** tracks price per square foot
        - **Bar chart** below shows sales volume
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
    st.markdown("*The highest-selling homes set the value ceiling for the neighborhood*")
    
    top_sales_df = get_top_sales(df_sold, 5)
    
    if not top_sales_df.empty:
        # Create horizontal tiles layout
        cols = st.columns(len(top_sales_df))
        
        for idx, (_, row) in enumerate(top_sales_df.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 0.5rem 0;">
                    <h3 style="margin: 0; color: white; font-size: 1.4em;">${row['Selling Price']:,.0f}</h3>
                    <hr style="border-color: rgba(255,255,255,0.3); margin: 1rem 0;">
                    <p style="margin: 0.5rem 0; color: white; font-weight: bold;">{row.get('Full_Address', 'N/A')}</p>
                    <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9em;">
                        {row.get('Finished Sqft', 'N/A'):.0f} sq ft<br>
                        {row.get('Bedrooms', 'N/A'):.0f}bed/{row.get('Bathrooms', 'N/A'):.1f}bath<br>
                        {row.get('Selling Date', 'N/A').strftime('%b %Y') if pd.notna(row.get('Selling Date')) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("**💡 Strategic Value:** These sales represent the peak performance potential for properties in your neighborhood.")
    else:
        st.info("No sales data available.")
    
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
                st.markdown(f"- {insight}")
        
        st.markdown("""
        **💡 How to Read This:** 
        - **Orange bars = 2024** performance (full year)
        - **Blue bars = 2025** performance (current year to date)
        - Compare the heights to see if 2025 is trending higher or lower
        """)
        
        # Show the data table for clarity
        if comparison_data is not None and not comparison_data.empty:
            st.markdown("### 📋 Exact Numbers")
            
            # Format the data nicely
            display_data = comparison_data.copy()
            display_data['Median Price'] = display_data['Median Price'].apply(lambda x: f"${x:,.0f}")
            display_data['Avg Days on Market'] = display_data['Avg Days on Market'].apply(lambda x: f"{x:.0f} days")
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
        
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
        recent_12m = get_recent_market_data(df_sold, 12)
        
        st.markdown("### 📈 Sales Activity")
        
        # Create a simple metrics display
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0;">
            <h4 style="margin: 0; color: #1565c0;">Recent Sales Volume</h4>
            <p style="margin: 0.5rem 0; font-size: 1.1em;"><strong>Last 3 months:</strong> {len(recent_3m)} sales</p>
            <p style="margin: 0.5rem 0; font-size: 1.1em;"><strong>Last 12 months:</strong> {len(recent_12m)} sales</p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(recent_3m) > 0:
            avg_price_3m = recent_3m['Selling Price'].median()
            st.markdown(f"**Current pricing:** ${avg_price_3m:,.0f} median")
    
    with col2:
        if 'DOM' in df_sold.columns:
            recent_dom = recent_12m['DOM'].median() if len(recent_12m) > 0 else 0
            st.markdown("### ⏱️ Market Speed")
            
            if recent_dom <= 30:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #4caf50;">
                    <h4 style="margin: 0; color: #2e7d32;">🚀 Fast-Moving Market</h4>
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
    
    # === SECTION 5: STRATEGIC INSIGHTS ===
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
        st.warning("Not enough recent sales data for strategic analysis.")
        return
    
    # Create organized insight sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Recent Market Indicators")
        st.markdown("*Based on last 12-24 months only*")
        
        insights = []
        
        # Recent price trend (last 2 years vs last 12 months)
        if len(recent_24m) > len(recent_12m) and len(recent_12m) > 0:
            older_recent = recent_24m[~recent_24m.index.isin(recent_12m.index)]
            
            if len(older_recent) > 0:
                recent_median = recent_12m['Selling Price'].median()
                older_median = older_recent['Selling Price'].median()
                price_change = ((recent_median - older_median) / older_median) * 100
                
                if price_change > 10:
                    insights.append(f"📈 **Recent Price Growth**: {price_change:.1f}% increase in last 12 months")
                elif price_change < -5:
                    insights.append(f"📉 **Recent Price Decline**: {abs(price_change):.1f}% decrease in last 12 months")
                else:
                    insights.append(f"📊 **Price Stability**: {price_change:.1f}% change in last 12 months")
        
        # Current DOM based on recent sales only
        if 'DOM' in recent_12m.columns and len(recent_12m) > 0:
            recent_dom = recent_12m['DOM'].median()
            insights.append(f"⏱️ **Current Market Speed**: {recent_dom:.0f} days median time to sell")
        
        # Sales velocity
        sales_12m = len(recent_12m)
        insights.append(f"📊 **Current Activity**: {sales_12m} sales in last 12 months")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    
    with col2:
        st.markdown("### 📊 Current Market Profile")
        st.markdown("*Based on recent sales only*")
        
        profile_insights = []
        
        # Recent price per sqft
        if 'Price_Per_SqFt' in recent_12m.columns and len(recent_12m) > 0:
            recent_psf = recent_12m['Price_Per_SqFt'].median()
            profile_insights.append(f"💰 **Current Value**: ${recent_psf:.0f} per sq ft")
        
        # Recent price range
        if 'Selling Price' in recent_12m.columns and len(recent_12m) > 0:
            recent_min = recent_12m['Selling Price'].min()
            recent_max = recent_12m['Selling Price'].max()
            recent_median = recent_12m['Selling Price'].median()
            profile_insights.append(f"💵 **Recent Price Range**: ${recent_min:,.0f} - ${recent_max:,.0f}")
            profile_insights.append(f"🎯 **Recent Median**: ${recent_median:,.0f}")
        
        # Property characteristics from recent sales
        if 'Finished Sqft' in recent_12m.columns and len(recent_12m) > 0:
            recent_size = recent_12m['Finished Sqft'].median()
            profile_insights.append(f"🏠 **Recently Sold Sizes**: ~{recent_size:.0f} sq ft median")
        
        for insight in profile_insights:
            st.markdown(f"- {insight}")
    
    # Strategic recommendations based on RECENT data only
    st.markdown("### 🎯 Strategic Recommendations")
    st.markdown("*Based on current market conditions*")
    
    recommendations = []
    
    if len(recent_12m) > 0 and 'DOM' in recent_12m.columns:
        recent_dom = recent_12m['DOM'].median()
        
        if recent_dom <= 30:
            recommendations.append("**For Sellers:** Current market favors sellers - homes selling quickly")
            recommendations.append("**For Buyers:** Act decisively on preferred properties")
        elif recent_dom <= 60:
            recommendations.append("**For Sellers:** Balanced market - price competitively")
            recommendations.append("**For Buyers:** Normal market timing - evaluate carefully but don't delay")
        else:
            recommendations.append("**For Sellers:** Extended marketing time - price conservatively")
            recommendations.append("**For Buyers:** More time to negotiate and evaluate options")
    
    # Add context about data recency
    if len(recent_12m) < 5:
        recommendations.append(f"**Note:** Limited recent data ({len(recent_12m)} sales) - trends may not be fully representative")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # Disclaimer
    st.markdown("""
    ---
    **📝 Analysis Note:** These insights focus on recent market activity only. The historical data (2003-present) 
    provides context but strategic recommendations are based on current conditions.
    """)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        display_columns = [col for col in ['Full_Address', 'Selling Price', 'Selling Date', 'Finished Sqft', 
                                         'Bedrooms', 'Bathrooms', 'DOM', 'Price_Per_SqFt'] 
                          if col in df_sold.columns]
        
        if display_columns:
            st.dataframe(
                df_sold[display_columns].sort_values('Selling Date', ascending=False),
                use_container_width=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown("*Data updated through the latest available MLS records. Analysis includes sold properties only.*")

if __name__ == "__main__":
    main()