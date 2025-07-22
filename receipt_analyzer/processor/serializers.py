from rest_framework import serializers
from .models import Receipt
from decimal import Decimal
import re


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for Receipt model"""
    
    formatted_amount = serializers.ReadOnlyField()
    formatted_date = serializers.ReadOnlyField()
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'vendor', 'date', 'amount', 'category',
            'file_name', 'file_type', 'extracted_text', 'confidence_score',
            'created_at', 'updated_at', 'formatted_amount', 'formatted_date'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'extracted_text', 'confidence_score']
    
    def validate_amount(self, value):
        """Validate amount field"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_vendor(self, value):
        """Validate vendor field"""
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("Vendor cannot be empty")
        return value.strip() if value else value


class ReceiptUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload and parsing"""
    
    file = serializers.FileField(write_only=True)
    manual_label = serializers.ChoiceField(
        choices=Receipt.CATEGORY_CHOICES, 
        required=False, 
        allow_blank=True,
        help_text="Optional: Manually label this receipt (overrides auto-detection)"
    )
    
    class Meta:
        model = Receipt
        fields = ['file', 'vendor', 'date', 'amount', 'category', 'manual_label']
        read_only_fields = ['vendor', 'date', 'amount', 'category']
    
    def validate_file(self, value):
        """Validate uploaded file"""
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf', 'text/plain', 'text/csv', 'application/octet-stream'
        ]
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Get file extension for validation
        file_name = value.name.lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv']
        
        # Check if file has valid extension
        has_valid_extension = any(file_name.endswith(ext) for ext in allowed_extensions)
        
        # If content type is not in allowed types, check extension
        if value.content_type not in allowed_types:
            if not has_valid_extension:
                raise serializers.ValidationError(
                    f"File type not supported. Detected: {value.content_type}. "
                    "Please upload JPG, PNG, PDF, or TXT files."
                )
        
        # Additional validation for octet-stream files
        if value.content_type == 'application/octet-stream' and not has_valid_extension:
            raise serializers.ValidationError(
                "File type not supported. Please upload JPG, PNG, PDF, or TXT files."
            )
        
        if value.size > max_size:
            raise serializers.ValidationError(
                "File size too large. Maximum size is 10MB."
            )
        
        return value


class ReceiptSearchSerializer(serializers.Serializer):
    """Serializer for search parameters"""
    
    keyword = serializers.CharField(required=False, allow_blank=True)
    min_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    category = serializers.ChoiceField(choices=Receipt.CATEGORY_CHOICES, required=False)
    
    def validate(self, data):
        """Validate search parameters"""
        min_amount = data.get('min_amount')
        max_amount = data.get('max_amount')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if min_amount and max_amount and min_amount > max_amount:
            raise serializers.ValidationError("min_amount cannot be greater than max_amount")
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be after end_date")
        
        return data


class ReceiptStatsSerializer(serializers.Serializer):
    """Serializer for statistics response"""
    
    total_receipts = serializers.IntegerField()
    total_amount = serializers.FloatField(allow_null=True)
    average_amount = serializers.FloatField(allow_null=True)
    median_amount = serializers.FloatField(allow_null=True)
    min_amount = serializers.FloatField(allow_null=True)
    max_amount = serializers.FloatField(allow_null=True)
    
    # Category breakdown
    category_breakdown = serializers.DictField()
    
    # Vendor breakdown
    vendor_breakdown = serializers.DictField()
    
    # Time series data
    monthly_totals = serializers.DictField()
    yearly_totals = serializers.DictField() 