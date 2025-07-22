import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, date
import io
import base64

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
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
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None, files=None):
    """Make API request to Django backend"""
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, data=data, files=files)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            # Try to get detailed error message from response
            try:
                error_data = e.response.json()
                if 'file' in error_data:
                    st.error(f"File Upload Error: {error_data['file'][0]}")
                else:
                    st.error(f"Bad Request: {error_data}")
            except:
                st.error("Invalid file format. Please upload JPG, PNG, PDF, or TXT files.")
        else:
            st.error(f"HTTP Error {e.response.status_code}: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def upload_file():
    """File upload section"""
    st.header("📤 Upload Receipt")
    
    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=['jpg', 'jpeg', 'png', 'pdf', 'txt'],
        help="Supported formats: JPG, PNG, PDF, TXT (max 10MB)"
    )
    
    # Show file validation info
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 10:
            st.error("❌ File too large! Maximum size is 10MB.")
            return
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Manual labeling section
        st.subheader("🏷️ Manual Labeling (Optional)")
        st.info("💡 **Tip**: You can manually label your receipt to override automatic categorization.")
        
        # Category selection
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
        
        # Upload button
        if st.button("🚀 Upload & Parse Receipt", type="primary"):
            with st.spinner("Processing receipt..."):
                files = {'file': uploaded_file}
                data = {}
                
                # Add manual label if selected
                if selected_category:
                    data['manual_label'] = selected_category
                
                result = make_api_request("upload/", method="POST", files=files, data=data)
                
                if result:
                    # Enhanced success notification
                    st.success("🎉 **File Uploaded Successfully!**")
                    
                    # Create a success banner
                    banner_message = "Your receipt has been processed and stored successfully!"
                    if selected_category:
                        banner_message += f" 📝 Manually labeled as: {category_options[selected_category]}"
                    
                    st.markdown(f"""
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 10px 0;">
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
                    st.caption(f"Parsing Confidence: {confidence:.1%}")
                    
                    # Additional file info
                    st.subheader("📊 File Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**File Name:** {uploaded_file.name}")
                        st.write(f"**File Size:** {uploaded_file.size / 1024:.1f} KB")
                        st.write(f"**File Type:** {uploaded_file.type}")
                    with col2:
                        st.write(f"**Upload Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Record ID:** {result.get('id', 'N/A')}")
                        st.write(f"**Processing Status:** ✅ Complete")
                    
                    # Show message if provided
                    if 'message' in result:
                        st.info(f"💡 {result['message']}")
                    
                    # Quick actions
                    st.subheader("🚀 Quick Actions")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📊 View Analytics", key="analytics_btn"):
                            st.switch_page("Analytics")
                    with col2:
                        if st.button("📋 View All Records", key="records_btn"):
                            st.switch_page("View Records")
                    with col3:
                        if st.button("🔍 Search Records", key="search_btn"):
                            st.switch_page("Search")
                    
                    # Refresh data
                    st.rerun()
                else:
                    st.error("❌ Failed to upload file. Please check the file format and try again.")
                    st.info("Supported formats: JPG, PNG, PDF, TXT (max 10MB)")

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
                    if st.button("📄 Export as JSON"):
                        json_str = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name="search_results.json",
                            mime="application/json"
                        )
            else:
                st.info("No records found matching your search criteria")

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
            except (ValueError, TypeError):
                st.info("No amount data available for distribution chart")
        except Exception as e:
            st.error(f"Error displaying analytics: {str(e)}")
            st.info("Please ensure the backend is running and try again.")
    else:
        st.error("Failed to load analytics data. Please ensure the backend is running.")

def edit_records():
    """Edit record data"""
    st.header("✏️ Edit Records")
    
    # Get all records
    records = make_api_request("records/")
    
    if records and 'results' in records:
        df = pd.DataFrame(records['results'])
        
        if not df.empty:
            # Select record to edit
            selected_record = st.selectbox(
                "Select a record to edit",
                options=df['id'].tolist(),
                format_func=lambda x: f"{df[df['id']==x]['vendor'].iloc[0]} - {df[df['id']==x]['amount'].iloc[0]}"
            )
            
            if selected_record:
                record = df[df['id'] == selected_record].iloc[0]
                
                # Edit form
                with st.form("edit_form"):
                    st.write("### Edit Record Details")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_vendor = st.text_input("Vendor", value=record['vendor'] or "")
                        new_amount = st.number_input("Amount", value=float(record['amount'].replace('$', '').replace(',', '')) if record['amount'] != 'N/A' else 0.0, step=0.01)
                    
                    with col2:
                        new_date = st.date_input("Date", value=datetime.strptime(record['date'], '%Y-%m-%d').date() if record['date'] != 'N/A' else date.today())
                        new_category = st.selectbox("Category", ["groceries", "restaurant", "transport", "entertainment", "shopping", "utilities", "healthcare", "other"], index=["groceries", "restaurant", "transport", "entertainment", "shopping", "utilities", "healthcare", "other"].index(record['category']))
                    
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
                        result = make_api_request(f"records/{selected_record}/", method="PUT", data=update_data)
                        
                        if result:
                            st.success("✅ Record updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update record")
        else:
            st.info("No records found to edit")
    else:
        st.error("Failed to load records")

def export_data():
    """Export data functionality"""
    st.header("📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export All Data")
        export_format = st.selectbox("Export Format", ["JSON", "CSV"])
        
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
                    import time
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

def main():
    """Main application"""
    st.markdown('<h1 class="main-header">📊 Receipt & Bill Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload", "View Records", "Search", "Analytics", "Edit Records", "Export", "Clear Data"]
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
        else:
            st.sidebar.error("❌ Backend Error")
    except:
        st.sidebar.error("❌ Backend Unavailable")
    
    st.sidebar.markdown("**Data Privacy**")
    st.sidebar.info("All data is processed locally and stored securely in your database.")

if __name__ == "__main__":
    main() 