#!/usr/bin/env python3
"""
Walmart Sales Analysis Web Application
A comprehensive web-based dashboard for sales data analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from pathlib import Path
import io
import base64
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Walmart Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert > div {
        padding-top: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .sql-query {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

class SalesAnalysisApp:
    def __init__(self):
        self.db_path = Path("data/walmart_sales.db")
        self.data_loaded = False
        
    def connect_db(self):
        """Connect to SQLite database"""
        try:
            if self.db_path.exists():
                self.conn = sqlite3.connect(str(self.db_path))
                self.data_loaded = True
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return False
    
    def load_sample_data(self):
        """Create sample data if real data is not available"""
        np.random.seed(42)
        
        # Generate sample data
        stores = pd.DataFrame({
            'Store': range(1, 46),
            'Type': np.random.choice(['A', 'B', 'C'], 45, p=[0.3, 0.4, 0.3]),
            'Size': np.random.randint(50000, 200000, 45)
        })
        
        # Generate sample sales data
        dates = pd.date_range('2010-02-01', '2012-11-30', freq='W')
        sample_data = []
        
        for store in range(1, 11):  # Limited sample
            for dept in range(1, 21):  # Limited departments
                for date in dates[:52]:  # One year of data
                    base_sales = np.random.normal(15000, 5000)
                    seasonal_factor = 1.2 if date.month in [11, 12] else 1.0
                    weekly_sales = max(0, base_sales * seasonal_factor + np.random.normal(0, 2000))
                    
                    sample_data.append({
                        'Store': store,
                        'Dept': dept,
                        'Date': date,
                        'Weekly_Sales': weekly_sales,
                        'IsHoliday': np.random.choice([True, False], p=[0.1, 0.9])
                    })
        
        train = pd.DataFrame(sample_data)
        
        # Generate features data
        features_data = []
        for store in range(1, 11):
            for date in dates[:52]:
                features_data.append({
                    'Store': store,
                    'Date': date,
                    'Temperature': np.random.normal(70, 20),
                    'Fuel_Price': np.random.normal(3.5, 0.5),
                    'CPI': np.random.normal(200, 20),
                    'Unemployment': np.random.normal(8, 2)
                })
        
        features = pd.DataFrame(features_data)
        
        return train, stores, features
    
    def load_data(self):
        """Load data from database or create sample data"""
        if self.connect_db():
            try:
                train = pd.read_sql_query("SELECT * FROM train LIMIT 10000", self.conn)
                stores = pd.read_sql_query("SELECT * FROM stores", self.conn)
                features = pd.read_sql_query("SELECT * FROM features LIMIT 5000", self.conn)
                
                # Convert date columns
                train['Date'] = pd.to_datetime(train['Date'])
                features['Date'] = pd.to_datetime(features['Date'])
                
                return train, stores, features, True
            except Exception as e:
                st.warning(f"Could not load from database: {e}. Using sample data.")
                train, stores, features = self.load_sample_data()
                return train, stores, features, False
        else:
            st.info("Using sample data for demonstration. Upload your CSV files to use real data.")
            train, stores, features = self.load_sample_data()
            return train, stores, features, False
    
    def run_sql_query(self, query, description="SQL Query"):
        """Execute SQL query and display results"""
        if self.data_loaded:
            try:
                result = pd.read_sql_query(query, self.conn)
                st.subheader(description)
                st.dataframe(result)
                
                # Show query
                with st.expander("View SQL Query"):
                    st.markdown(f'<div class="sql-query">{query}</div>', unsafe_allow_html=True)
                
                return result
            except Exception as e:
                st.error(f"Query error: {e}")
                return None
        else:
            st.warning("Database not available. Please load data first.")
            return None

def main():
    """Main application function"""
    st.title("🛒 Walmart Sales Analysis Dashboard")
    st.markdown("---")
    
    # Initialize app
    app = SalesAnalysisApp()
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        [
            "🏠 Home & Overview",
            "📈 Sales Trends",
            "🏪 Store Performance", 
            "🏷️ Department Analysis",
            "📅 Seasonality Analysis",
            "🔍 Advanced Analytics",
            "📊 SQL Query Interface",
            "📋 Data Upload"
        ]
    )
    
    # Load data
    train, stores, features, is_real_data = app.load_data()
    
    # Data info sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Data Info")
    st.sidebar.metric("Records", len(train))
    st.sidebar.metric("Stores", train['Store'].nunique())
    st.sidebar.metric("Departments", train['Dept'].nunique())
    
    if not is_real_data:
        st.sidebar.warning("⚠️ Using sample data")
    else:
        st.sidebar.success("✅ Using real data")
    
    # Main content based on selected page
    if page == "🏠 Home & Overview":
        show_home_page(train, stores, features)
    
    elif page == "📈 Sales Trends":
        show_sales_trends(train)
    
    elif page == "🏪 Store Performance":
        show_store_performance(train, stores)
    
    elif page == "🏷️ Department Analysis":
        show_department_analysis(train)
    
    elif page == "📅 Seasonality Analysis":
        show_seasonality_analysis(train)
    
    elif page == "🔍 Advanced Analytics":
        show_advanced_analytics(train, features)
    
    elif page == "📊 SQL Query Interface":
        show_sql_interface(app)
    
    elif page == "📋 Data Upload":
        show_data_upload()

def show_home_page(train, stores, features):
    """Display home page with overview metrics"""
    st.header("📊 Sales Analysis Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = train['Weekly_Sales'].sum()
        st.metric("Total Sales", f"${total_sales:,.0f}")
    
    with col2:
        avg_sales = train['Weekly_Sales'].mean()
        st.metric("Average Weekly Sales", f"${avg_sales:,.0f}")
    
    with col3:
        date_range = (train['Date'].max() - train['Date'].min()).days
        st.metric("Analysis Period (Days)", f"{date_range:,}")
    
    with col4:
        total_records = len(train)
        st.metric("Total Records", f"{total_records:,}")
    
    st.markdown("---")
    
    # Overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Over Time")
        monthly_sales = train.groupby(train['Date'].dt.to_period('M'))['Weekly_Sales'].sum().reset_index()
        monthly_sales['Date'] = monthly_sales['Date'].astype(str)
        
        fig = px.line(monthly_sales, x='Date', y='Weekly_Sales',
                     title="Monthly Sales Trend")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏪 Store Type Distribution")
        store_dist = stores['Type'].value_counts()
        
        fig = px.pie(values=store_dist.values, names=store_dist.index,
                    title="Store Types")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data preview
    st.subheader("📋 Data Preview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Sales Data Sample**")
        st.dataframe(train.head())
    
    with col2:
        st.write("**Store Information**")
        st.dataframe(stores.head())
    
    with col3:
        st.write("**Features Data Sample**")
        st.dataframe(features.head())

def show_sales_trends(train):
    """Display sales trends analysis"""
    st.header("📈 Sales Trends Analysis")
    
    # Time period selector
    col1, col2 = st.columns(2)
    with col1:
        aggregation = st.selectbox("Aggregation Period", 
                                  ["Weekly", "Monthly", "Quarterly", "Yearly"])
    
    with col2:
        chart_type = st.selectbox("Chart Type", 
                                 ["Line Chart", "Bar Chart", "Area Chart"])
    
    # Aggregate data based on selection
    if aggregation == "Weekly":
        grouped_data = train.groupby('Date')['Weekly_Sales'].sum().reset_index()
    elif aggregation == "Monthly":
        grouped_data = train.groupby(train['Date'].dt.to_period('M'))['Weekly_Sales'].sum().reset_index()
        grouped_data['Date'] = grouped_data['Date'].astype(str)
    elif aggregation == "Quarterly":
        grouped_data = train.groupby(train['Date'].dt.to_period('Q'))['Weekly_Sales'].sum().reset_index()
        grouped_data['Date'] = grouped_data['Date'].astype(str)
    else:  # Yearly
        grouped_data = train.groupby(train['Date'].dt.year)['Weekly_Sales'].sum().reset_index()
        grouped_data.columns = ['Date', 'Weekly_Sales']
    
    # Create chart based on selection
    if chart_type == "Line Chart":
        fig = px.line(grouped_data, x='Date', y='Weekly_Sales',
                     title=f"{aggregation} Sales Trend")
    elif chart_type == "Bar Chart":
        fig = px.bar(grouped_data, x='Date', y='Weekly_Sales',
                    title=f"{aggregation} Sales")
    else:  # Area Chart
        fig = px.area(grouped_data, x='Date', y='Weekly_Sales',
                     title=f"{aggregation} Sales Trend")
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth analysis
    st.subheader("📊 Growth Analysis")
    if len(grouped_data) > 1:
        growth_rate = ((grouped_data['Weekly_Sales'].iloc[-1] - grouped_data['Weekly_Sales'].iloc[0]) / 
                      grouped_data['Weekly_Sales'].iloc[0] * 100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Growth Rate", f"{growth_rate:.1f}%")
        with col2:
            st.metric("Peak Sales", f"${grouped_data['Weekly_Sales'].max():,.0f}")
        with col3:
            st.metric("Lowest Sales", f"${grouped_data['Weekly_Sales'].min():,.0f}")

def show_store_performance(train, stores):
    """Display store performance analysis"""
    st.header("🏪 Store Performance Analysis")
    
    # Merge train with stores data
    train_stores = train.merge(stores, on='Store')
    
    # Store performance metrics
    store_performance = train_stores.groupby(['Store', 'Type', 'Size']).agg({
        'Weekly_Sales': ['sum', 'mean', 'count']
    }).round(2)
    
    store_performance.columns = ['Total_Sales', 'Avg_Sales', 'Record_Count']
    store_performance = store_performance.reset_index().sort_values('Total_Sales', ascending=False)
    
    # Top performers
    st.subheader("🏆 Top Performing Stores")
    col1, col2 = st.columns(2)
    
    with col1:
        top_stores = store_performance.head(10)
        fig = px.bar(top_stores, x='Store', y='Total_Sales',
                    title="Top 10 Stores by Total Sales")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Store type performance
        type_performance = train_stores.groupby('Type')['Weekly_Sales'].agg(['sum', 'mean', 'count']).reset_index()
        fig = px.bar(type_performance, x='Type', y='sum',
                    title="Sales by Store Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Store Performance Details")
    st.dataframe(store_performance)
    
    # Store size analysis
    st.subheader("📏 Store Size vs Performance")
    fig = px.scatter(store_performance, x='Size', y='Total_Sales', 
                    color='Type', size='Avg_Sales',
                    title="Store Size vs Sales Performance")
    st.plotly_chart(fig, use_container_width=True)

def show_department_analysis(train):
    """Display department analysis"""
    st.header("🏷️ Department Performance Analysis")
    
    # Department performance
    dept_performance = train.groupby('Dept').agg({
        'Weekly_Sales': ['sum', 'mean', 'std', 'count'],
        'Store': 'nunique'
    }).round(2)
    
    dept_performance.columns = ['Total_Sales', 'Avg_Sales', 'Sales_Std', 'Record_Count', 'Store_Count']
    dept_performance['CV'] = (dept_performance['Sales_Std'] / dept_performance['Avg_Sales'] * 100).round(2)
    dept_performance = dept_performance.reset_index().sort_values('Total_Sales', ascending=False)
    
    # Top departments
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔝 Top Revenue Departments")
        top_depts = dept_performance.head(15)
        fig = px.bar(top_depts, x='Dept', y='Total_Sales',
                    title="Top 15 Departments by Revenue")
        fig.update_layout(xaxis={'type': 'category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sales Distribution")
        fig = px.histogram(dept_performance, x='Total_Sales', nbins=20,
                          title="Department Sales Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Consistency analysis
    st.subheader("⚡ Department Consistency")
    col1, col2 = st.columns(2)
    
    with col1:
        # Most consistent (lowest CV)
        consistent_depts = dept_performance[dept_performance['Record_Count'] >= 50].sort_values('CV').head(10)
        fig = px.bar(consistent_depts, x='Dept', y='CV',
                    title="Most Consistent Departments (Low Variability)")
        fig.update_layout(xaxis={'type': 'category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average vs volatility
        filtered_depts = dept_performance[dept_performance['Record_Count'] >= 50]
        fig = px.scatter(filtered_depts, x='Avg_Sales', y='CV',
                        size='Total_Sales', hover_data=['Dept'],
                        title="Average Sales vs Variability")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Department Performance Details")
    st.dataframe(dept_performance)

def show_seasonality_analysis(train):
    """Display seasonality analysis"""
    st.header("📅 Seasonality Analysis")
    
    # Add time components
    train_copy = train.copy()
    train_copy['Month'] = train_copy['Date'].dt.month
    train_copy['DayOfWeek'] = train_copy['Date'].dt.day_name()
    train_copy['Quarter'] = train_copy['Date'].dt.quarter
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📆 Monthly Patterns")
        monthly_pattern = train_copy.groupby('Month')['Weekly_Sales'].mean().reset_index()
        monthly_pattern['Month_Name'] = monthly_pattern['Month'].map({
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        })
        
        fig = px.line(monthly_pattern, x='Month_Name', y='Weekly_Sales',
                     title="Average Sales by Month")
        fig.update_layout(xaxis_title="Month", yaxis_title="Average Sales")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Day of Week Patterns")
        dow_pattern = train_copy.groupby('DayOfWeek')['Weekly_Sales'].mean().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_pattern['DayOfWeek'] = pd.Categorical(dow_pattern['DayOfWeek'], categories=day_order, ordered=True)
        dow_pattern = dow_pattern.sort_values('DayOfWeek')
        
        fig = px.bar(dow_pattern, x='DayOfWeek', y='Weekly_Sales',
                    title="Average Sales by Day of Week")
        st.plotly_chart(fig, use_container_width=True)
    
    # Holiday analysis
    st.subheader("🎉 Holiday Impact Analysis")
    if 'IsHoliday' in train.columns:
        holiday_impact = train.groupby('IsHoliday')['Weekly_Sales'].agg(['mean', 'count']).reset_index()
        holiday_impact.columns = ['IsHoliday', 'Avg_Sales', 'Count']
        holiday_impact['IsHoliday'] = holiday_impact['IsHoliday'].map({True: 'Holiday', False: 'Non-Holiday'})
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(holiday_impact, x='IsHoliday', y='Avg_Sales',
                        title="Average Sales: Holiday vs Non-Holiday")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate impact percentage
            holiday_avg = holiday_impact[holiday_impact['IsHoliday'] == 'Holiday']['Avg_Sales'].iloc[0]
            non_holiday_avg = holiday_impact[holiday_impact['IsHoliday'] == 'Non-Holiday']['Avg_Sales'].iloc[0]
            impact = ((holiday_avg - non_holiday_avg) / non_holiday_avg * 100)
            
            st.metric("Holiday Impact", f"{impact:+.1f}%")
            st.write("Holiday sales impact compared to non-holiday periods")
    
    # Quarterly trends
    st.subheader("📊 Quarterly Trends")
    quarterly_trend = train_copy.groupby(['Date', 'Quarter'])['Weekly_Sales'].sum().reset_index()
    quarterly_avg = quarterly_trend.groupby('Quarter')['Weekly_Sales'].mean().reset_index()
    
    fig = px.bar(quarterly_avg, x='Quarter', y='Weekly_Sales',
                title="Average Sales by Quarter")
    st.plotly_chart(fig, use_container_width=True)

def show_advanced_analytics(train, features):
    """Display advanced analytics"""
    st.header("🔍 Advanced Analytics")
    
    # Moving averages
    st.subheader("📈 Moving Averages")
    
    window_size = st.slider("Moving Average Window (weeks)", 2, 12, 4)
    
    # Calculate moving averages
    weekly_sales = train.groupby('Date')['Weekly_Sales'].sum().reset_index().sort_values('Date')
    weekly_sales[f'MA_{window_size}'] = weekly_sales['Weekly_Sales'].rolling(window=window_size).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekly_sales['Date'], y=weekly_sales['Weekly_Sales'],
                           mode='lines', name='Weekly Sales', opacity=0.6))
    fig.add_trace(go.Scatter(x=weekly_sales['Date'], y=weekly_sales[f'MA_{window_size}'],
                           mode='lines', name=f'{window_size}-Week Moving Average',
                           line=dict(width=3)))
    
    fig.update_layout(title="Sales Trend with Moving Average", height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    if len(features) > 0:
        st.subheader("🔗 Correlation Analysis")
        
        # Merge sales with features
        train_features = train.merge(features, on=['Store', 'Date'], how='inner')
        
        if len(train_features) > 0:
            # Calculate correlations
            numeric_cols = ['Weekly_Sales', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment']
            available_cols = [col for col in numeric_cols if col in train_features.columns]
            
            if len(available_cols) > 1:
                corr_matrix = train_features[available_cols].corr()
                
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                               title="Correlation Matrix: Sales vs External Factors")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show correlations with sales
                sales_corr = corr_matrix['Weekly_Sales'].drop('Weekly_Sales').sort_values(key=abs, ascending=False)
                
                st.write("**Correlation with Weekly Sales:**")
                for factor, corr in sales_corr.items():
                    st.write(f"- {factor}: {corr:.3f}")
    
    # Store consistency ranking
    st.subheader("🏆 Store Consistency Ranking")
    
    store_stats = train.groupby('Store')['Weekly_Sales'].agg(['mean', 'std', 'count']).reset_index()
    store_stats['CV'] = store_stats['std'] / store_stats['mean'] * 100
    store_stats = store_stats[store_stats['count'] >= 10].sort_values('CV')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Most consistent stores
        top_consistent = store_stats.head(10)
        fig = px.bar(top_consistent, x='Store', y='CV',
                    title="Most Consistent Stores (Lowest Variability)")
        fig.update_layout(xaxis={'type': 'category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average vs consistency scatter
        fig = px.scatter(store_stats, x='mean', y='CV', hover_data=['Store'],
                        title="Average Sales vs Consistency")
        fig.update_layout(xaxis_title="Average Sales", yaxis_title="Coefficient of Variation (%)")
        st.plotly_chart(fig, use_container_width=True)

def show_sql_interface(app):
    """Display SQL query interface"""
    st.header("📊 SQL Query Interface")
    
    if not app.data_loaded:
        st.warning("⚠️ Database not available. Please load your data first.")
        return
    
    # Predefined queries
    st.subheader("🔍 Quick Queries")
    
    query_options = {
        "Basic Overview": """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT Store) as unique_stores,
            COUNT(DISTINCT Dept) as unique_departments,
            MIN(Date) as earliest_date,
            MAX(Date) as latest_date,
            ROUND(SUM(Weekly_Sales), 2) as total_sales,
            ROUND(AVG(Weekly_Sales), 2) as avg_weekly_sales
        FROM train;
        """,
        
        "Top 10 Stores": """
        SELECT 
            Store,
            COUNT(*) as records,
            ROUND(SUM(Weekly_Sales), 2) as total_sales,
            ROUND(AVG(Weekly_Sales), 2) as avg_sales
        FROM train 
        GROUP BY Store 
        ORDER BY total_sales DESC 
        LIMIT 10;
        """,
        
        "Department Performance": """
        SELECT 
            Dept,
            COUNT(*) as records,
            COUNT(DISTINCT Store) as stores,
            ROUND(SUM(Weekly_Sales), 2) as total_sales,
            ROUND(AVG(Weekly_Sales), 2) as avg_sales
        FROM train 
        GROUP BY Dept 
        ORDER BY total_sales DESC 
        LIMIT 15;
        """,
        
        "Monthly Sales Trend": """
        SELECT 
            strftime('%Y-%m', Date) as month_year,
            ROUND(SUM(Weekly_Sales), 2) as monthly_sales,
            ROUND(AVG(Weekly_Sales), 2) as avg_weekly_sales,
            COUNT(DISTINCT Store) as active_stores
        FROM train 
        GROUP BY strftime('%Y-%m', Date) 
        ORDER BY month_year;
        """,
        
        "Holiday Impact": """
        SELECT 
            IsHoliday,
            COUNT(*) as record_count,
            ROUND(AVG(Weekly_Sales), 2) as avg_sales,
            ROUND(SUM(Weekly_Sales), 2) as total_sales
        FROM train 
        GROUP BY IsHoliday;
        """
    }
    
    # Quick query selector
    selected_query = st.selectbox("Select a predefined query:", list(query_options.keys()))
    
    if st.button("Run Selected Query"):
        query = query_options[selected_query]
        app.run_sql_query(query, f"Results: {selected_query}")
    
    st.markdown("---")
    
    # Custom query interface
    st.subheader("✏️ Custom SQL Query")
    
    custom_query = st.text_area(
        "Enter your SQL query:",
        height=200,
        placeholder="SELECT * FROM train LIMIT 10;"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Execute Query"):
            if custom_query.strip():
                app.run_sql_query(custom_query, "Custom Query Results")
            else:
                st.error("Please enter a SQL query.")
    
    with col2:
        if st.button("Show Table Schema"):
            schema_query = "SELECT name, sql FROM sqlite_master WHERE type='table';"
            app.run_sql_query(schema_query, "Database Schema")

def show_data_upload():
    """Display data upload interface"""
    st.header("📋 Data Upload & Management")
    
    st.markdown("""
    ### Upload Your Walmart Sales Data
    
    You can upload your CSV files here to use real data instead of the sample data.
    """)
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload Files")
        
        train_file = st.file_uploader("Upload train.csv", type="csv", key="train")
        stores_file = st.file_uploader("Upload stores.csv", type="csv", key="stores")
        features_file = st.file_uploader("Upload features.csv", type="csv", key="features")
    
    with col2:
        st.subheader("ℹ️ File Requirements")
        st.markdown("""
        **train.csv** should contain:
        - Store, Dept, Date, Weekly_Sales, IsHoliday
        
        **stores.csv** should contain:
        - Store, Type, Size
        
        **features.csv** should contain:
        - Store, Date, Temperature, Fuel_Price, CPI, Unemployment
        """)
    
    # Process uploaded files
    if train_file and stores_file:
        if st.button("Process Uploaded Files"):
            try:
                # Read uploaded files
                train_df = pd.read_csv(train_file)
                stores_df = pd.read_csv(stores_file)
                
                # Create database
                db_path = Path("data/walmart_sales.db")
                db_path.parent.mkdir(exist_ok=True)
                
                conn = sqlite3.connect(str(db_path))
                
                # Save to database
                train_df.to_sql('train', conn, if_exists='replace', index=False)
                stores_df.to_sql('stores', conn, if_exists='replace', index=False)
                
                if features_file:
                    features_df = pd.read_csv(features_file)
                    features_df.to_sql('features', conn, if_exists='replace', index=False)
                
                conn.close()
                
                st.success("✅ Files uploaded and database created successfully!")
                st.info("🔄 Please refresh the page to use the new data.")
                
            except Exception as e:
                st.error(f"Error processing files: {e}")
    
    # Download sample data template
    st.markdown("---")
    st.subheader("📥 Download Sample Data")
    st.markdown("If you don't have the data, you can download it from:")
    st.markdown("[Walmart Sales Dataset on Kaggle](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/data)")

if __name__ == "__main__":
    main()
