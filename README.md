# Receipt & Bill Analyzer

A full-stack application for analyzing receipts and bills with Django backend and Streamlit frontend.

## Features

- **File Upload**: Support for .jpg, .png, .pdf, .txt files
- **OCR Processing**: Automatic text extraction from images/PDFs
- **Data Parsing**: Extract vendor, date, amount, and category information
- **Search & Filter**: Search by keyword, amount range, date range
- **Analytics**: Statistical analysis with charts and visualizations
- **Manual Correction**: Edit parsed data through the UI
- **Export**: Download data as CSV/JSON

## Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Frontend**: Streamlit 1.28.1
- **Database**: SQLite
- **OCR**: pytesseract
- **Visualization**: Plotly
- **Validation**: Pydantic

## Setup Instructions

### Prerequisites

1. Install Python 3.8+
2. Install Tesseract OCR:
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python start_app.py
   ```

3. **Access the application:**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/api/

### Manual Setup

1. **Setup Django backend:**
   ```bash
   cd receipt_analyzer
   python manage.py migrate
   python manage.py runserver
   ```

2. **Run Streamlit frontend (in a new terminal):**
   ```bash
   streamlit run frontend/app.py
   ```

### Testing

Run the test script to verify everything is working:
```bash
python test_setup.py
```

## API Documentation

### Upload File
- **POST** `/api/upload/`
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file` (required): Receipt file (jpg, png, pdf, txt)
  - `manual_label` (optional): Override automatic categorization
    - Available categories: `groceries`, `restaurant`, `transport`, `entertainment`, `shopping`, `utilities`, `healthcare`, `other`
- **Response**: Parsed receipt data with manual label applied

### Get Records
- **GET** `/api/records/`
- **Parameters**: 
  - `page` (optional): Page number
  - `page_size` (optional): Items per page
- **Response**: List of all parsed records

### Search Records
- **GET** `/api/search/`
- **Parameters**:
  - `keyword` (optional): Search in vendor/category
  - `min_amount` (optional): Minimum amount
  - `max_amount` (optional): Maximum amount
  - `start_date` (optional): Start date (YYYY-MM-DD)
  - `end_date` (optional): End date (YYYY-MM-DD)
- **Response**: Filtered records

### Get Statistics
- **GET** `/api/stats/`
- **Parameters**: None
- **Response**: Aggregated statistics

### Update Record
- **PUT** `/api/records/{id}/`
- **Body**: JSON with updated fields
- **Response**: Updated record

## Usage

1. Open Streamlit app at `http://localhost:8501`
2. Upload receipt files with optional manual labeling
3. View parsed data in tabular format
4. Use search filters to find specific records
5. View analytics and visualizations
6. Edit data manually if needed
7. Export data as needed

### Manual Labeling Feature

When uploading receipts, you can now manually label them to override automatic categorization:

- **Auto-detect**: Let the system automatically categorize based on content
- **Manual Label**: Choose from predefined categories:
  - 🛒 Groceries
  - 🍽️ Restaurant  
  - 🚗 Transport
  - 🎬 Entertainment
  - 🛍️ Shopping
  - ⚡ Utilities
  - 🏥 Healthcare
  - 📄 Other

Manual labels are given 100% confidence and override automatic detection.

## Project Structure

```
8_bite/
├── receipt_analyzer/          # Django backend
│   ├── receipt_analyzer/      # Django settings
│   ├── processor/             # Main app
│   │   ├── models.py         # Database models
│   │   ├── serializers.py    # DRF serializers
│   │   ├── views.py          # API views
│   │   ├── utils.py          # OCR and parsing utilities
│   │   └── urls.py           # URL routing
│   └── manage.py
├── frontend/                  # Streamlit frontend
│   └── app.py                # Main Streamlit app
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Data Privacy

- All uploaded files are processed locally
- No data is sent to external services
- OCR processing happens on your machine
- Data is stored in local SQLite database 