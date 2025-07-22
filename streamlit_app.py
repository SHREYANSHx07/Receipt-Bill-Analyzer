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
from datetime import datetime, timedelta
import os

# Configure page
st.set_page_config(
    page_title="Receipt & Bill Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    font-weight: bold;
}

.sidebar .sidebar-content {
    background-color: #f0f2f6;
}

.metric-container {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e0e0e0;
    margin: 0.5rem 0;
}

.success-banner {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
}

.warning-banner {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://web-production-e532c.up.railway.app/api')

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
    """Upload and parse receipt files"""
    st.header("📤 Upload Receipt")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=['jpg', 'jpeg', 'png', 'pdf', 'txt'],
        help="Supported formats: JPG, PNG, PDF, TXT (max 10MB)"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**File Details:**")
            for key, value in file_details.items():
                st.write(f"• {key}: {value}")
        
        with col2:
            # Show preview for images
            if uploaded_file.type and uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="File Preview", use_column_width=True)
        
        # Manual labeling section
        st.subheader("🏷️ Manual Labeling (Optional)")
        st.info("💡 **Tip**: You can manually label your receipt to override automatic categorization.")
        
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
        
        selected_category = st.selectbox(
            "Choose a category (optional):",
            options=list(category_options.keys()),
            format_func=lambda x: category_options[x],
            help="Leave as 'Auto-detect' to let the system categorize automatically"
        )
        
        if st.button("🚀 Upload & Parse Receipt", type="primary"):
            with st.spinner("Processing receipt..."):
                files = {'file': uploaded_file}
                data = {}
                if selected_category:
                    data['manual_label'] = selected_category
                
                result = make_api_request("upload/", method="POST", files=files, data=data)
                
                if result:
                    st.success("🎉 **File Uploaded Successfully!**")
                    banner_message = "Your receipt has been processed and stored successfully!"
                    if selected_category:
                        banner_message += f" 📝 Manually labeled as: {category_options[selected_category]}"
                    
                    st.markdown(f"""
                    <div class="success-banner">
                        <h4 style="color: #155724; margin: 0;">✅ Upload Complete</h4>
                        <p style="color: #155724; margin: 5px 0;">{banner_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display parsed data
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Vendor", result.get('vendor', 'N/A'))
                    with col2:
                        st.metric("Amount", result.get('amount', 'N/A'))
                    with col3:
                        st.metric("Date", result.get('date', 'N/A'))
                    with col4:
                        st.metric("Category", result.get('category', 'N/A').title())
                    
                    # Confidence score
                    confidence = result.get('confidence_score', 0)
                    st.progress(confidence)
                    st.caption(f"Confidence Score: {confidence:.1%}")
                    
                    # Quick actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 View All Records"):
                            st.switch_page("View Records")
                    with col2:
                        if st.button("📊 View Analytics"):
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
                st.metric("Total Receipts", stats['total_receipts'])
            with col2:
                # Handle float values directly
                total_amount = stats['total_amount'] or 0.0
                st.metric("Total Amount", f"${total_amount:,.2f}")
            with col3:
                # Handle float values directly
                avg_amount = stats['average_amount'] or 0.0
                st.metric("Average Amount", f"${avg_amount:,.2f}")
            with col4:
                # Handle float values directly
                median_amount = stats['median_amount'] or 0.0
                st.metric("Median Amount", f"${median_amount:,.2f}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Category Breakdown")
                if stats['category_breakdown']:
                    category_data = pd.DataFrame([
                        {'Category': k.title(), 'Count': v['count'], 'Total': v['total']}
                        for k, v in stats['category_breakdown'].items()
                    ])
                    
                    fig = px.pie(
                        category_data, 
                        values='Total', 
                        names='Category',
                        title="Spending by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🏪 Top Vendors")
                if stats['vendor_breakdown']:
                    vendor_data = pd.DataFrame([
                        {'Vendor': k, 'Total': v['total']}
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
            
            # Time series analysis
            st.subheader("📅 Spending Trends")
            if stats['monthly_totals']:
                monthly_data = pd.DataFrame([
                    {'Month': k, 'Total': v}
                    for k, v in stats['monthly_totals'].items()
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
            
            # Amount distribution
            st.subheader("💰 Amount Distribution")
            try:
                min_amount = stats['min_amount'] or 0.0
                max_amount = stats['max_amount'] or 0.0
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
                result = make_api_request(f"export/?format={export_format.lower()}")
                
                if result:
                    if export_format == "CSV":
                        st.download_button(
                            label="Download CSV",
                            data=result,
                            file_name="receipts_export.csv",
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
    """Main application"""
    st.markdown('<h1 class="main-header">📊 Receipt & Bill Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload", "View Records", "Search", "Analytics", "Edit Records", "Export", "Clear Data", "Connection Test"]
    )
    
    # Page routing
    if page == "Upload":
        upload_file()
    elif page == "View Records":
        view_records()
    elif page == "Search":
        search_records()
    elif page == "Analytics":
        analytics_dashboard()
    elif page == "Edit Records":
        edit_records()
    elif page == "Export":
        export_data()
    elif page == "Clear Data":
        clear_all_data()
    elif page == "Connection Test":
        connection_test()
    
    # Footer
    st.sidebar.markdown("---")
    
    # Show current record count
    try:
        records_response = make_api_request("records/")
        if records_response and 'results' in records_response:
            current_count = len(records_response['results'])
            st.sidebar.metric("📊 Total Records", current_count)
    except:
        st.sidebar.metric("📊 Total Records", "Unknown")
    
    st.sidebar.markdown("**API Status**")
    
    # Check API connection
    try:
        response = requests.get(f"{API_BASE_URL}/stats/", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ Backend Connected")
            try:
                data = response.json()
                st.sidebar.info(f"📊 Records: {data.get('total_receipts', 0)}")
            except:
                st.sidebar.warning("⚠️ Response not JSON")
        else:
            st.sidebar.error(f"❌ Backend Error: {response.status_code}")
            st.sidebar.error(f"Response: {response.text[:100]}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Backend Unreachable")
        st.sidebar.info(f"URL: {API_BASE_URL}")
    except requests.exceptions.Timeout:
        st.sidebar.error("⏰ Backend Timeout")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {str(e)}")
    
    st.sidebar.markdown("**Data Privacy**")
    st.sidebar.info("All data is processed locally and stored securely in your database.")

if __name__ == "__main__":
    main() 