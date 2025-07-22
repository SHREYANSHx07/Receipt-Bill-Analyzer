from django.db import models
from django.utils import timezone
import uuid


class Receipt(models.Model):
    """Model for storing parsed receipt data"""
    
    CATEGORY_CHOICES = [
        ('groceries', 'Groceries'),
        ('restaurant', 'Restaurant'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('utilities', 'Utilities'),
        ('healthcare', 'Healthcare'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    
    # File information
    original_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=10, blank=True)  # jpg, png, pdf, txt
    
    # OCR and parsing information
    extracted_text = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['date']),
            models.Index(fields=['amount']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.vendor} - {self.amount} - {self.date}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol"""
        if self.amount:
            return f"${self.amount:.2f}"
        return "N/A"
    
    @property
    def formatted_date(self):
        """Return formatted date"""
        if self.date:
            return self.date.strftime("%Y-%m-%d")
        return "N/A"
