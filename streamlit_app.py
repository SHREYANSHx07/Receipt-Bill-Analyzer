#!/usr/bin/env python3
"""
Receipt & Bill Analyzer - Streamlit App
Deployable version for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import time
import sys
from datetime import datetime, timedelta
import os

# Configure page
st.set_page_config(
    page_title="Receipt & Bill Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/SHREYANSHx07/Receipt-Bill-Analyzer',
        'Report a bug': 'https://github.com/SHREYANSHx07/Receipt-Bill-Analyzer/issues',
        'About': '# Receipt & Bill Analyzer\n\nTransform your receipts into actionable insights with AI-powered analysis.'
    }
)

# Professional Color Palette CSS
st.markdown("""
<style>
/* Professional Color Scheme - Based on Telecom Design */
:root {
    --primary-green: #4CAF50;          /* Vibrant green for CTAs */
    --primary-purple: #4B0082;         /* Deep purple for branding */
    --primary-purple-light: #6A0DAD;   /* Lighter purple for accents */
    --text-dark: #262626;              /* Dark grey for main text */
    --text-secondary: #64748b;         /* Medium grey for secondary text */
    --background-white: #FFFFFF;        /* Pure white background */
    --background-light: #f8fafc;       /* Light grey background */
    --border-color: #e2e8f0;           /* Light border color */
    --success-color: #10b981;          /* Success green */
    --warning-color: #f59e0b;          /* Warning amber */
    --error-color: #ef4444;            /* Error red */
}

/* Global Styles */
.stApp {
    background: var(--background-white);
    min-height: 100vh;
}

.main .block-container {
    background: var(--background-white);
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin: 20px;
    padding: 2rem;
}

/* Header Styling */
.main-header {
    text-align: center;
    color: var(--primary-purple);
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -0.025em;
}

.sub-header {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Sidebar Styling */
.sidebar .sidebar-content {
    background: var(--background-light);
    border-radius: 8px;
    padding: 1rem;
    margin: 10px;
}

/* Card Styling */
.metric-container {
    background: var(--background-white);
    padding: 1.25rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    margin: 0.75rem 0;
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.metric-container:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.1);
}

/* Success Banner */
.success-banner {
    background: #f0f9ff;
    border: 1px solid var(--primary-green);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.75rem 0;
    box-shadow: 0 2px 4px -1px rgba(76, 175, 80, 0.1);
}

/* Warning Banner */
.warning-banner {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 2px solid var(--warning-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.1);
}

/* Error Banner */
.error-banner {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border: 2px solid var(--error-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);
}

/* Button Styling */
.stButton > button {
    background: var(--primary-green);
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px -1px rgba(76, 175, 80, 0.3);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px -2px rgba(76, 175, 80, 0.4);
}

/* File Upload Styling */
.stFileUploader {
    border: 2px dashed var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    background: var(--background-light);
    transition: all 0.2s ease;
}

.stFileUploader:hover {
    border-color: var(--primary-green);
    background: #f0f9ff;
}

/* Table Styling */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Chart Container */
.chart-container {
    background: var(--background-white);
    border-radius: 8px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

/* Progress Bar */
.stProgress > div > div > div {
    background: var(--primary-green);
}

/* Sidebar Navigation */
.sidebar-nav {
    background: var(--background-white);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

/* Status Indicators */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-online {
    background: var(--success-color);
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.status-offline {
    background: var(--error-color);
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    
    .main .block-container {
        margin: 10px;
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')

def check_backend_health():
    """Check if backend is healthy and accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                return True, data
            except json.JSONDecodeError:
                return False, "Invalid JSON response"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - backend not running"
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except Exception as e:
        return False, str(e)

def make_api_request(endpoint, method="GET", data=None, files=None):
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        
        # Debug information
        st.sidebar.write(f"🔗 Connecting to: {url}")
        
        if method == "GET":
            response = requests.get(url, params=data, timeout=10)
        elif method == "POST":
            response = requests.post(url, data=data, files=files, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return None
        
        # Debug response
        st.sidebar.write(f"📊 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                st.error(f"JSON Parse Error: {str(e)}")
                st.error(f"Response content: {response.text[:200]}")
                return None
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Connection Error: Backend not reachable")
        st.error(f"Check if backend is running at: {API_BASE_URL}")
        return None
    except requests.exceptions.Timeout as e:
        st.error(f"⏰ Timeout: Backend not responding")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def upload_file():
    """Upload and parse receipt files with enhanced visual design"""
    
    # Professional header with clean design
    st.markdown("""
    <div style="background: var(--background-light); 
                padding: 2rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid var(--primary-purple);">
        <h1 style="color: var(--primary-purple); text-align: center; margin: 0; font-size: 2.5rem; font-weight: 700;">📤 Upload Receipt</h1>
        <p style="color: var(--text-secondary); text-align: center; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Upload your receipts and let AI extract the important information
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional file upload section
    st.markdown("""
    <div style="background: var(--background-white); padding: 1.5rem; border-radius: 8px; 
                border: 1px solid var(--border-color); margin: 1rem 0;">
        <h3 style="color: var(--text-dark); text-align: center; margin-bottom: 1rem; font-weight: 600;">📁 Choose Your Receipt</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload with enhanced styling
    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=['jpg', 'jpeg', 'png', 'pdf', 'txt'],
        help="Supported formats: JPG, PNG, PDF, TXT (max 10MB)"
    )
    
    if uploaded_file is not None:
        # Enhanced file info display
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        # Professional file details card
        st.markdown("""
        <div style="background: var(--background-light); 
                    padding: 1.25rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid var(--primary-green);">
            <h3 style="color: var(--text-dark); margin: 0 0 1rem 0; font-weight: 600;">📋 File Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Professional file details display
            for key, value in file_details.items():
                st.markdown(f"""
                <div style="background: var(--background-white); padding: 0.75rem; border-radius: 6px; 
                            margin: 0.5rem 0; border-left: 3px solid var(--primary-green);">
                    <div style="font-weight: 600; color: var(--text-dark);">{key}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Professional image preview
            if uploaded_file.type and uploaded_file.type.startswith('image'):
                st.markdown("""
                <div style="background: var(--background-white); padding: 1rem; border-radius: 8px; 
                            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1); border-left: 3px solid var(--primary-purple);">
                    <h4 style="color: var(--text-dark); margin: 0 0 0.5rem 0; font-weight: 600;">🖼️ File Preview</h4>
                </div>
                """, unsafe_allow_html=True)
                st.image(uploaded_file, caption="File Preview", use_container_width=True)
        
        # Professional manual labeling section
        st.markdown("""
        <div style="background: var(--background-light); 
                    padding: 1.25rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid var(--primary-purple);">
            <h3 style="color: var(--text-dark); margin: 0 0 0.5rem 0; font-weight: 600;">🏷️ Manual Labeling (Optional)</h3>
            <p style="color: var(--text-secondary); margin: 0;">💡 <strong>Tip</strong>: You can manually label your receipt to override automatic categorization.</p>
        </div>
        """, unsafe_allow_html=True)
        
        category_options = {
            "": "Auto-detect (recommended)",
            "groceries": "🛒 Groceries",
            "restaurant": "🍽️ Restaurant",
            "transport": "🚗 Transport",
            "entertainment": "🎬 Entertainment",
            "shopping": "🛍️ Shopping",
            "utilities": "⚡ Utilities",
            "healthcare": "🏥 Healthcare",
            "other": "📄 Other"
        }
        
        # Enhanced category selection
        selected_category = st.selectbox(
            "Choose a category (optional):",
            options=list(category_options.keys()),
            format_func=lambda x: category_options[x],
            help="Leave as 'Auto-detect' to let the system categorize automatically"
        )
        
        # Enhanced upload button
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upload & Parse Receipt", type="primary", use_container_width=True):
            with st.spinner("Processing receipt..."):
                files = {'file': uploaded_file}
                data = {}
                if selected_category:
                    data['manual_label'] = selected_category
                
                result = make_api_request("upload/", method="POST", files=files, data=data)
                
                if result:
                    # Professional success banner
                    banner_message = "Your receipt has been processed and stored successfully!"
                    if selected_category:
                        banner_message += f" 📝 Manually labeled as: {category_options[selected_category]}"
                    
                    st.markdown(f"""
                    <div style="background: #f0f9ff; 
                                border: 1px solid var(--primary-green); border-radius: 8px; 
                                padding: 1.25rem; margin: 1rem 0; text-align: center;">
                        <h3 style="color: var(--primary-green); margin: 0 0 0.5rem 0; font-weight: 700;">🎉 Upload Complete!</h3>
                        <p style="color: var(--text-dark); margin: 0;">{banner_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Professional parsed data display
                    st.markdown("""
                    <div style="background: var(--background-light); 
                                padding: 1.25rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid var(--primary-purple);">
                        <h3 style="color: var(--text-dark); margin: 0 0 1rem 0; font-weight: 600;">📊 Extracted Information</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Professional metrics display
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                                    border-left: 3px solid var(--primary-purple); text-align: center;">
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">Vendor</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-dark);">{result.get('vendor', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                                    border-left: 3px solid var(--primary-green); text-align: center;">
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">Amount</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-dark);">{result.get('amount', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                                    border-left: 3px solid var(--warning-color); text-align: center;">
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">Date</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-dark);">{result.get('date', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""
                        <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                                    border-left: 3px solid var(--primary-purple-light); text-align: center;">
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">Category</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-dark);">{result.get('category', 'N/A').title()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Professional confidence score
                    confidence = result.get('confidence_score', 0)
                    st.markdown("""
                    <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid var(--primary-green);">
                        <div style="font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem;">🎯 Confidence Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(confidence)
                    st.caption(f"AI Confidence: {confidence:.1%}")
                    
                    # Professional quick actions
                    st.markdown("""
                    <div style="background: var(--background-light); 
                                padding: 1.25rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid var(--primary-purple);">
                        <h4 style="color: var(--text-dark); margin: 0 0 1rem 0; font-weight: 600;">🚀 Quick Actions</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 View All Records", use_container_width=True):
                            st.switch_page("View Records")
                    with col2:
                        if st.button("📊 View Analytics", use_container_width=True):
                            st.switch_page("Analytics")
                else:
                    st.error("❌ Failed to upload file. Please try again.")

def view_records():
    """View all records in tabular format"""
    st.header("📋 Receipt Records")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")  # Spacer
    with col2:
        if st.button("🔄 Refresh", key="refresh_records"):
            st.rerun()
    
    # Get records from API
    records = make_api_request("records/")
    
    if records and 'results' in records:
        df = pd.DataFrame(records['results'])
        
        if not df.empty:
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                # Handle amount formatting safely
                try:
                    total_amount = df['amount'].str.replace('$', '').str.replace(',', '').astype(float).sum()
                    st.metric("Total Amount", f"${total_amount:,.2f}")
                except:
                    st.metric("Total Amount", "N/A")
            with col3:
                # Handle amount formatting safely
                try:
                    avg_amount = df['amount'].str.replace('$', '').str.replace(',', '').astype(float).mean()
                    st.metric("Average Amount", f"${avg_amount:,.2f}")
                except:
                    st.metric("Average Amount", "N/A")
            with col4:
                categories = df['category'].value_counts().to_dict()
                st.metric("Categories", len(categories))
            
            # Display data table
            st.dataframe(
                df[['vendor', 'amount', 'date', 'category', 'confidence_score']],
                use_container_width=True,
                hide_index=True
            )
            
            # Pagination info
            if 'count' in records:
                st.caption(f"Showing {len(df)} of {records['count']} records")
        else:
            st.info("No records found. Upload some receipts to get started!")
    else:
        st.error("Failed to load records")

def search_records():
    """Search and filter records"""
    st.header("🔍 Search Records")
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            keyword = st.text_input("Keyword Search", placeholder="Search vendor, category, or text...")
            min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0, step=0.01)
            start_date = st.date_input("Start Date", value=None)
        
        with col2:
            category = st.selectbox("Category", ["All"] + ["groceries", "restaurant", "transport", "entertainment", "shopping", "utilities", "healthcare", "other"])
            max_amount = st.number_input("Maximum Amount", min_value=0.0, value=1000.0, step=0.01)
            end_date = st.date_input("End Date", value=None)
        
        submitted = st.form_submit_button("🔍 Search", type="primary")
    
    if submitted:
        # Prepare search parameters
        search_params = {}
        if keyword:
            search_params['keyword'] = keyword
        if min_amount > 0:
            search_params['min_amount'] = min_amount
        if max_amount < 1000:
            search_params['max_amount'] = max_amount
        if start_date:
            search_params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            search_params['end_date'] = end_date.strftime('%Y-%m-%d')
        if category != "All":
            search_params['category'] = category
        
        # Make search request
        results = make_api_request("search/", data=search_params)
        
        if results:
            df = pd.DataFrame(results)
            
            if not df.empty:
                st.success(f"Found {len(df)} matching records")
                
                # Display results
                st.dataframe(
                    df[['vendor', 'amount', 'date', 'category', 'confidence_score']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Export as CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="search_results.csv",
                            mime="text/csv"
                        )
                with col2:
                    if st.button("📊 Export as JSON"):
                        json_data = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name="search_results.json",
                            mime="application/json"
                        )
            else:
                st.info("No records found matching your criteria.")
        else:
            st.error("Failed to search records")

def analytics_dashboard():
    """Analytics and visualizations"""
    st.header("📊 Analytics Dashboard")
    
    # Get statistics from API
    stats = make_api_request("stats/")
    
    if stats:
        try:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Receipts", stats.get('total_receipts', 0))
            with col2:
                # Handle float values directly
                total_amount = stats.get('total_amount', 0.0) or 0.0
                st.metric("Total Amount", f"${total_amount:,.2f}")
            with col3:
                # Handle float values directly
                avg_amount = stats.get('mean_amount', 0.0) or 0.0
                st.metric("Average Amount", f"${avg_amount:,.2f}")
            with col4:
                # Handle float values directly
                median_amount = stats.get('median_amount', 0.0) or 0.0
                st.metric("Median Amount", f"${median_amount:,.2f}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Category Breakdown")
                if stats.get('category_breakdown'):
                    category_data = pd.DataFrame([
                        {'Category': k.title(), 'Count': v.get('count', 0), 'Total': v.get('total', 0)}
                        for k, v in stats['category_breakdown'].items()
                    ])
                    
                    fig = px.pie(
                        category_data, 
                        values='Total', 
                        names='Category',
                        title="Spending by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No category data available")
            
            with col2:
                st.subheader("🏪 Top Vendors")
                if stats.get('vendor_breakdown'):
                    vendor_data = pd.DataFrame([
                        {'Vendor': k, 'Total': v.get('total', 0)}
                        for k, v in stats['vendor_breakdown'].items()
                    ])
                    
                    fig = px.bar(
                        vendor_data.head(10), 
                        x='Vendor', 
                        y='Total',
                        title="Top 10 Vendors by Spending"
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No vendor data available")
            
            # Time series analysis
            st.subheader("📅 Spending Trends")
            if stats.get('monthly_trends'):
                monthly_data = pd.DataFrame([
                    {'Month': k, 'Total': v}
                    for k, v in stats['monthly_trends'].items()
                ])
                monthly_data['Month'] = pd.to_datetime(monthly_data['Month'] + '-01')
                monthly_data = monthly_data.sort_values('Month')
                
                fig = px.line(
                    monthly_data, 
                    x='Month', 
                    y='Total',
                    title="Monthly Spending Trends"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No monthly trend data available")
            
            # Amount distribution
            st.subheader("💰 Amount Distribution")
            try:
                min_amount = stats.get('min_amount', 0.0) or 0.0
                max_amount = stats.get('max_amount', 0.0) or 0.0
                if min_amount > 0 and max_amount > 0:
                    # Create a histogram-like visualization
                    ranges = [
                        (0, 25), (25, 50), (50, 100), (100, 200), 
                        (200, 500), (500, 1000), (1000, float('inf'))
                    ]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=[f"${r[0]}-${r[1] if r[1] != float('inf') else '∞'}" for r in ranges],
                        y=[0] * len(ranges),  # Placeholder - would need actual data
                        name="Amount Ranges"
                    ))
                    fig.update_layout(
                        title="Receipt Amount Distribution",
                        xaxis_title="Amount Range",
                        yaxis_title="Number of Receipts"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No amount data available for distribution analysis.")
            except Exception as e:
                st.error(f"Error creating amount distribution: {str(e)}")
            
        except Exception as e:
            st.error(f"Error displaying analytics: {str(e)}")
    else:
        st.error("Failed to load analytics data")

def edit_records():
    """Edit existing records"""
    st.header("✏️ Edit Records")
    
    # Get records
    records = make_api_request("records/")
    
    if records and 'results' in records:
        df = pd.DataFrame(records['results'])
        
        if not df.empty:
            # Select record to edit
            selected_record = st.selectbox(
                "Select a record to edit:",
                options=df.index,
                format_func=lambda x: f"{df.iloc[x]['vendor']} - {df.iloc[x]['amount']} ({df.iloc[x]['date']})"
            )
            
            if selected_record is not None:
                record = df.iloc[selected_record]
                record_id = record['id']
                
                st.subheader(f"Editing: {record['vendor']}")
                
                # Edit form
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_vendor = st.text_input("Vendor", value=record['vendor'])
                        new_amount = st.text_input("Amount", value=record['amount'])
                    
                    with col2:
                        new_date = st.date_input("Date", value=pd.to_datetime(record['date']).date())
                        new_category = st.selectbox(
                            "Category",
                            options=["groceries", "restaurant", "transport", "entertainment", "shopping", "utilities", "healthcare", "other"],
                            index=["groceries", "restaurant", "transport", "entertainment", "shopping", "utilities", "healthcare", "other"].index(record['category'])
                        )
                    
                    submitted = st.form_submit_button("💾 Save Changes", type="primary")
                
                if submitted:
                    # Prepare update data
                    update_data = {
                        'vendor': new_vendor,
                        'amount': new_amount,
                        'date': new_date.strftime('%Y-%m-%d'),
                        'category': new_category
                    }
                    
                    # Make update request
                    result = make_api_request(f"records/{record_id}/", method="PUT", data=update_data)
                    
                    if result:
                        st.success("✅ Record updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update record")
        else:
            st.info("No records found to edit.")
    else:
        st.error("Failed to load records")

def export_data():
    """Export data functionality"""
    st.header("📊 Export Data")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Export Format")
        export_format = st.selectbox(
            "Choose export format:",
            ["CSV", "JSON"],
            help="CSV for spreadsheet applications, JSON for data processing"
        )
        
        if st.button(f"📊 Export as {export_format}", type="primary"):
            with st.spinner(f"Exporting data as {export_format}..."):
                # Use path parameters instead of query parameters
                if export_format == "CSV":
                    result = make_api_request("export/csv/")
                else:
                    result = make_api_request("export/json/")
                
                if result:
                    if export_format == "CSV":
                        # Handle new CSV response format
                        if isinstance(result, dict) and 'csv_content' in result:
                            csv_content = result['csv_content']
                            filename = result.get('filename', 'receipts_export.csv')
                        else:
                            # Fallback for old format
                            csv_content = result
                            filename = "receipts_export.csv"
                        
                        st.download_button(
                            label="Download CSV",
                            data=csv_content,
                            file_name=filename,
                            mime="text/csv"
                        )
                    else:
                        st.download_button(
                            label="Download JSON",
                            data=json.dumps(result, indent=2),
                            file_name="receipts_export.json",
                            mime="application/json"
                        )
    
    with col2:
        st.subheader("API Endpoints")
        st.code("""
GET /api/records/ - List all records
GET /api/search/ - Search records
GET /api/stats/ - Get statistics
POST /api/upload/ - Upload file
PUT /api/records/{id}/ - Update record
GET /api/export/ - Export data
DELETE /api/clear/ - Clear all data
        """)

def clear_all_data():
    """Clear all data functionality"""
    st.header("🗑️ Clear All Data")
    
    st.warning("⚠️ **Warning**: This action will permanently delete ALL receipt data and cannot be undone!")
    
    # Confirmation
    col1, col2 = st.columns(2)
    
    with col1:
        # Add a confirmation checkbox first
        confirm_delete = st.checkbox("✅ I understand this will delete all data permanently", key="confirm_delete")
        
        if st.button("🗑️ Clear All Data", type="primary", disabled=not confirm_delete):
            # Make API call to clear data
            with st.spinner("Clearing all data..."):
                response = make_api_request("clear/", method="DELETE")
                
                if response:
                    deleted_count = response.get('deleted_count', 0)
                    st.success(f"✅ Successfully deleted {deleted_count} records!")
                    st.info("All data has been cleared. You can now start fresh.")
                    
                    # Show immediate feedback
                    st.balloons()
                    
                    # Force refresh the page after a short delay
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to clear data. Please try again.")
    
    with col2:
        st.info("""
        **What will be deleted:**
        - All uploaded receipts
        - All extracted data
        - All analytics history
        - All search records
        """)
        
        # Show current record count
        try:
            records_response = make_api_request("records/")
            if records_response and 'results' in records_response:
                current_count = len(records_response['results'])
                st.metric("Current Records", current_count)
        except:
            st.metric("Current Records", "Unknown")

def connection_test():
    """Test backend connection and diagnose issues"""
    st.header("🔧 Connection Test")
    
    st.info("This page helps diagnose connection issues with your backend API.")
    
    # Current configuration
    st.subheader("📋 Current Configuration")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**API Base URL:** {API_BASE_URL}")
    with col2:
        st.write(f"**Environment:** {os.getenv('API_BASE_URL', 'Not set')}")
    
    # Test connection
    st.subheader("🧪 Connection Test")
    if st.button("🔍 Test Connection", type="primary"):
        with st.spinner("Testing connection..."):
            is_healthy, message = check_backend_health()
            
            if is_healthy:
                st.success("✅ Backend is healthy!")
                st.json(message)
            else:
                st.error(f"❌ Backend issue: {message}")
    
    # Manual test
    st.subheader("🔧 Manual Testing")
    test_endpoint = st.text_input("Test endpoint:", value="stats/")
    
    if st.button("📡 Test Endpoint"):
        with st.spinner("Testing..."):
            result = make_api_request(test_endpoint)
            if result:
                st.success("✅ Endpoint working!")
                st.json(result)
            else:
                st.error("❌ Endpoint failed")
    
    # Troubleshooting guide
    st.subheader("🛠️ Troubleshooting Guide")
    
    with st.expander("Common Issues & Solutions"):
        st.markdown("""
        ### 1. Connection Refused
        - **Cause**: Backend not running
        - **Solution**: Deploy your Django backend to Railway/Render/Heroku
        
        ### 2. Wrong API URL
        - **Cause**: Incorrect API_BASE_URL
        - **Solution**: Check environment variables in Streamlit Cloud
        
        ### 3. CORS Issues
        - **Cause**: Backend not allowing cross-origin requests
        - **Solution**: Ensure CORS is configured in Django settings
        
        ### 4. Empty Response
        - **Cause**: Backend returning empty JSON
        - **Solution**: Check Django logs for errors
        
        ### 5. Timeout
        - **Cause**: Backend taking too long to respond
        - **Solution**: Check backend performance and database
        """)
    
    # Environment check
    st.subheader("🌍 Environment Check")
    st.code(f"""
    API_BASE_URL = {API_BASE_URL}
    Python Version = {sys.version}
    Streamlit Version = {st.__version__}
    """)

def main():
    """Main application with enhanced visual design"""
    
    # Enhanced header with gradient and better typography
    st.markdown('<h1 class="main-header">📊 Receipt & Bill Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your receipts into actionable insights with AI-powered analysis</p>', unsafe_allow_html=True)
    
    # Professional sidebar with clean design
    st.sidebar.markdown("""
    <div style="background: var(--primary-purple); 
                padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="color: white; text-align: center; margin: 0; font-weight: 600;">🧭 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced page selection with icons
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📤 Upload", "📋 View Records", "🔍 Search", "📊 Analytics", "✏️ Edit Records", "💾 Export", "🗑️ Clear Data", "🔧 Connection Test"]
    )
    
    # Remove icons from page name for routing
    page_clean = page.split(" ", 1)[1] if " " in page else page
    
    # Page routing with clean page names
    if page_clean == "Upload":
        upload_file()
    elif page_clean == "View Records":
        view_records()
    elif page_clean == "Search":
        search_records()
    elif page_clean == "Analytics":
        analytics_dashboard()
    elif page_clean == "Edit Records":
        edit_records()
    elif page_clean == "Export":
        export_data()
    elif page_clean == "Clear Data":
        clear_all_data()
    elif page_clean == "Connection Test":
        connection_test()
    
    # Enhanced footer with better visual design
    st.sidebar.markdown("---")
    
    # Professional status section
    st.sidebar.markdown("""
    <div style="background: var(--background-light); 
                padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="color: var(--text-dark); margin: 0 0 0.5rem 0; font-weight: 600;">📊 System Status</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current record count with enhanced styling
    try:
        records_response = make_api_request("records/")
        if records_response and 'results' in records_response:
            current_count = len(records_response['results'])
            st.sidebar.markdown(f"""
            <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                        border-left: 3px solid var(--primary-green); margin: 0.5rem 0;">
                <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-green);">{current_count}</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.sidebar.markdown("""
        <div style="background: var(--background-white); padding: 1rem; border-radius: 6px; 
                    border-left: 3px solid var(--warning-color); margin: 0.5rem 0;">
            <div style="font-size: 1.5rem; font-weight: bold; color: var(--warning-color);">Unknown</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">Total Records</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced API status with visual indicators
    st.sidebar.markdown("**🔗 API Status**")
    
    # Check API connection with enhanced visual feedback
    try:
        response = requests.get(f"{API_BASE_URL}/stats/", timeout=5)
        if response.status_code == 200:
            st.sidebar.markdown("""
            <div style="background: #f0f9ff; 
                        padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid var(--primary-green);">
                <div style="display: flex; align-items: center;">
                    <span style="background: var(--primary-green); width: 8px; height: 8px; 
                                 border-radius: 50%; margin-right: 0.5rem;"></span>
                    <span style="color: var(--primary-green); font-weight: 600;">✅ Backend Connected</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            try:
                data = response.json()
                st.sidebar.markdown(f"""
                <div style="background: var(--background-white); padding: 0.75rem; border-radius: 6px; 
                            margin: 0.5rem 0; border-left: 3px solid var(--primary-purple);">
                    <div style="color: var(--text-dark); font-weight: 600;">📊 {data.get('total_receipts', 0)} Records</div>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.sidebar.warning("⚠️ Response not JSON")
        else:
            st.sidebar.markdown(f"""
            <div style="background: #fef2f2; 
                        padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid var(--error-color);">
                <div style="display: flex; align-items: center;">
                    <span style="background: var(--error-color); width: 8px; height: 8px; 
                                 border-radius: 50%; margin-right: 0.5rem;"></span>
                    <span style="color: var(--error-color); font-weight: 600;">❌ Backend Error: {response.status_code}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.sidebar.markdown(f"""
        <div style="background: #fef2f2; 
                    padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid var(--error-color);">
            <div style="display: flex; align-items: center;">
                <span style="background: var(--error-color); width: 8px; height: 8px; 
                             border-radius: 50%; margin-right: 0.5rem;"></span>
                <span style="color: var(--error-color); font-weight: 600;">❌ Backend Unreachable</span>
            </div>
            <div style="color: var(--error-color); font-size: 0.8rem; margin-top: 0.25rem;">URL: {API_BASE_URL}</div>
        </div>
        """, unsafe_allow_html=True)
    except requests.exceptions.Timeout:
        st.sidebar.markdown("""
        <div style="background: #fffbeb; 
                    padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid var(--warning-color);">
            <div style="display: flex; align-items: center;">
                <span style="background: var(--warning-color); width: 8px; height: 8px; 
                             border-radius: 50%; margin-right: 0.5rem;"></span>
                <span style="color: var(--warning-color); font-weight: 600;">⏰ Backend Timeout</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.markdown(f"""
        <div style="background: #fef2f2; 
                    padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid var(--error-color);">
            <div style="display: flex; align-items: center;">
                <span style="background: var(--error-color); width: 8px; height: 8px; 
                             border-radius: 50%; margin-right: 0.5rem;"></span>
                <span style="color: var(--error-color); font-weight: 600;">❌ Error: {str(e)[:30]}...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional privacy notice
    st.sidebar.markdown("""
    <div style="background: var(--background-light); 
                padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid var(--primary-purple);">
        <h4 style="color: var(--text-dark); margin: 0 0 0.5rem 0; font-weight: 600;">🔒 Data Privacy</h4>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
            All data is processed locally and stored securely in your database.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 