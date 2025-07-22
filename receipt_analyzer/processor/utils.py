import pytesseract
from PIL import Image
import re
from datetime import datetime, date
from decimal import Decimal
import io
import fitz  # PyMuPDF for PDF processing
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def extract_text_from_image(image_file) -> str:
    """Extract text from image using OCR"""
    try:
        # Open image with PIL
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Try different OCR configurations for better results
        configs = [
            '--oem 3 --psm 6',  # Default: Assume uniform block of text
            '--oem 3 --psm 3',  # Fully automatic page segmentation
            '--oem 3 --psm 4',  # Assume single column of text
            '--oem 3 --psm 8',  # Single word
            '--oem 1 --psm 6',  # Legacy engine with uniform block
        ]
        
        best_text = ""
        for config in configs:
            try:
                text = pytesseract.image_to_string(image, config=config)
                if text.strip() and len(text.strip()) > len(best_text):
                    best_text = text.strip()
            except Exception as e:
                logger.warning(f"OCR config {config} failed: {e}")
                continue
        
        # If no text found, try with preprocessing
        if not best_text:
            # Convert to grayscale for better OCR
            gray_image = image.convert('L')
            text = pytesseract.image_to_string(gray_image, config='--oem 3 --psm 6')
            best_text = text.strip()
        
        return best_text
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return ""


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file"""
    try:
        # Read PDF content
        pdf_content = pdf_file.read()
        pdf_file.seek(0)  # Reset file pointer
        
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        
        # Extract text from all pages
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_file(file_obj) -> Tuple[str, str]:
    """Extract text from uploaded file based on type"""
    file_type = file_obj.content_type
    file_name = file_obj.name.lower()
    
    # Check for image files
    if file_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'] or \
       any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
        text = extract_text_from_image(file_obj)
        return text, 'image'
    elif file_type == 'application/pdf' or file_name.endswith('.pdf'):
        text = extract_text_from_pdf(file_obj)
        return text, 'pdf'
    elif file_type == 'text/plain' or file_name.endswith('.txt'):
        text = file_obj.read().decode('utf-8')
        return text, 'text'
    else:
        # Try to detect by file extension as fallback
        if any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            text = extract_text_from_image(file_obj)
            return text, 'image'
        elif file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_obj)
            return text, 'pdf'
        elif file_name.endswith('.txt'):
            text = file_obj.read().decode('utf-8')
            return text, 'text'
        else:
            return "", 'unknown'


def parse_amount(text: str) -> Optional[Decimal]:
    """Extract amount from text using regex patterns"""
    # Common patterns for amounts - prioritize TOTAL
    patterns = [
        r'TOTAL\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # TOTAL $123.45
        r'Total:\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Total: $123.45
        r'Amount:\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Amount: $123.45
        r'Balance:\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Balance: $123.45
        r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $123.45 or 123.45
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 123.45 USD
    ]
    
    # First, look for TOTAL specifically
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                try:
                    # Remove commas and convert to Decimal
                    clean_amount = match.replace(',', '')
                    amount = Decimal(clean_amount)
                    
                    # If this is a TOTAL match, return it immediately
                    if 'TOTAL' in pattern or 'Total:' in pattern:
                        return amount
                    
                except (ValueError, TypeError):
                    continue
    
    # If no TOTAL found, look for any amount pattern
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            amounts = []
            for match in matches:
                try:
                    clean_amount = match.replace(',', '')
                    amount = Decimal(clean_amount)
                    amounts.append(amount)
                except (ValueError, TypeError):
                    continue
            
            if amounts:
                # Return the largest amount that's reasonable (not too small)
                valid_amounts = [amt for amt in amounts if amt > Decimal('1.00')]
                if valid_amounts:
                    return max(valid_amounts)
    
    return None


def parse_date(text: str) -> Optional[date]:
    """Extract date from text using regex patterns"""
    # Common date patterns - prioritize simple formats first
    patterns = [
        r'(\d{1,2})/(\d{1,2})',  # MM/DD or DD/MM (simple format like 8/24)
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',  # MM.DD.YYYY
        r'Date:\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # Date: MM/DD/YYYY
        r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})',  # Jan 15, 2024
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                try:
                    if len(match) == 2:
                        # Simple format like 8/24 - assume current year
                        month, day = match
                        current_year = datetime.now().year
                        try:
                            return datetime.strptime(f"{month}/{day}/{current_year}", "%m/%d/%Y").date()
                        except ValueError:
                            continue
                    
                    elif len(match) == 3:
                        month, day, year = match
                        
                        # Handle 2-digit years
                        if len(year) == 2:
                            year = '20' + year
                        
                        # Try different date formats
                        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m.%d.%Y']:
                            try:
                                return datetime.strptime(f"{month}/{day}/{year}", fmt).date()
                            except ValueError:
                                continue
                        
                        # Try month name format
                        try:
                            return datetime.strptime(f"{month} {day}, {year}", "%b %d, %Y").date()
                        except ValueError:
                            continue
                
                except (ValueError, TypeError):
                    continue
    
    return None


def parse_vendor(text: str) -> Optional[str]:
    """Extract vendor/store name from text"""
    # Split text into lines and check each line
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 3:  # Skip very short lines
            continue
        
        # Skip lines that are clearly not vendor names
        skip_words = ['receipt', 'total', 'amount', 'date', 'time', 'description', 'price', 'tax', 'thank you']
        if any(word in line.lower() for word in skip_words):
            continue
        
        # Look for vendor patterns
        patterns = [
            r'^([A-Z][A-Za-z\s&]+(?:STORE|MARKET|SHOP|SUPERMARKET|GROCERY|RESTAURANT|CAFE|MALL))',
            r'([A-Z][A-Za-z\s&]+(?:STORE|MARKET|SHOP|SUPERMARKET|GROCERY|RESTAURANT|CAFE|MALL))',
            r'^([A-Z][A-Za-z\s&]+)',  # Start of line with capital letter
            r'([A-Z][A-Za-z\s&]+)',  # Any capital letter followed by text
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            if matches:
                vendor = matches[0].strip()
                # Clean up vendor name
                vendor = re.sub(r'\s+', ' ', vendor)  # Remove extra spaces
                vendor = vendor.title()  # Title case
                
                # Skip if vendor name is too short
                if len(vendor) < 3:
                    continue
                
                # Additional validation - check if it looks like a real vendor name
                if len(vendor.split()) >= 2:  # At least 2 words
                    return vendor
                elif len(vendor) >= 5:  # Or at least 5 characters
                    return vendor
    
    return None


def categorize_receipt(vendor: str, amount: Decimal, text: str = "") -> str:
    """Categorize receipt based on vendor name, amount, and text content"""
    if not vendor:
        return 'other'
    
    vendor_lower = vendor.lower()
    text_lower = text.lower()
    
    # Groceries - check both vendor name and text content for food items
    grocery_keywords = ['grocery', 'supermarket', 'market', 'food', 'fresh', 'organic', 'whole foods', 'trader joe', 'safeway', 'kroger']
    grocery_items = ['orange juice', 'apples', 'tomato', 'fish', 'beef', 'onion', 'cheese', 'milk', 'bread', 'eggs', 'vegetables', 'fruits']
    
    if any(keyword in vendor_lower for keyword in grocery_keywords):
        return 'groceries'
    
    # Check for grocery items in the text
    if any(item in text_lower for item in grocery_items):
        return 'groceries'
    
    # Restaurants
    restaurant_keywords = ['restaurant', 'cafe', 'diner', 'pizza', 'burger', 'mcdonalds', 'kfc', 'subway', 'starbucks', 'coffee']
    if any(keyword in vendor_lower for keyword in restaurant_keywords):
        return 'restaurant'
    
    # Transport
    transport_keywords = ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'transport', 'parking']
    if any(keyword in vendor_lower for keyword in transport_keywords):
        return 'transport'
    
    # Entertainment
    entertainment_keywords = ['movie', 'theater', 'cinema', 'netflix', 'spotify', 'amazon prime', 'hulu', 'disney', 'game', 'entertainment']
    if any(keyword in vendor_lower for keyword in entertainment_keywords):
        return 'entertainment'
    
    # Shopping
    shopping_keywords = ['walmart', 'target', 'amazon', 'best buy', 'home depot', 'lowes', 'macy', 'nordstrom', 'shopping', 'store']
    if any(keyword in vendor_lower for keyword in shopping_keywords):
        return 'shopping'
    
    # Utilities
    utility_keywords = ['electric', 'gas', 'water', 'internet', 'phone', 'cable', 'utility', 'at&t', 'verizon', 'comcast']
    if any(keyword in vendor_lower for keyword in utility_keywords):
        return 'utilities'
    
    # Healthcare
    healthcare_keywords = ['pharmacy', 'drug', 'cvs', 'walgreens', 'rite aid', 'medical', 'doctor', 'hospital', 'clinic', 'health']
    if any(keyword in vendor_lower for keyword in healthcare_keywords):
        return 'healthcare'
    
    return 'other'


def parse_receipt_data(text: str) -> Dict:
    """Parse receipt data from extracted text"""
    result = {
        'vendor': None,
        'date': None,
        'amount': None,
        'category': 'other',
        'confidence_score': 0.0
    }
    
    # Extract data
    vendor = parse_vendor(text)
    date = parse_date(text)
    amount = parse_amount(text)
    
    # Set results
    if vendor:
        result['vendor'] = vendor
        result['confidence_score'] += 0.3
    
    if date:
        result['date'] = date
        result['confidence_score'] += 0.3
    
    if amount:
        result['amount'] = amount
        result['confidence_score'] += 0.3
    
    # Categorize based on vendor and text content
    if vendor:
        result['category'] = categorize_receipt(vendor, amount, text)
        result['confidence_score'] += 0.1
    
    return result 