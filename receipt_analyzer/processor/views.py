from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from decimal import Decimal
import json

from .models import Receipt
from .serializers import (
    ReceiptSerializer, 
    ReceiptUploadSerializer, 
    ReceiptSearchSerializer,
    ReceiptStatsSerializer
)
from .utils import extract_text_from_file, parse_receipt_data


class UploadView(APIView):
    """Handle file upload and parsing"""
    
    def post(self, request):
        serializer = ReceiptUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                file_obj = request.FILES['file']
                
                # Extract text from file
                try:
                    extracted_text, file_type = extract_text_from_file(file_obj)
                    print(f"DEBUG: Extracted text length: {len(extracted_text) if extracted_text else 0}")
                    print(f"DEBUG: File type detected: {file_type}")
                    
                    if not extracted_text:
                        return Response(
                            {'error': 'Could not extract text from file. Please ensure the file is readable and in a supported format (JPG, PNG, PDF, TXT).'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception as e:
                    print(f"DEBUG: Error during text extraction: {e}")
                    return Response(
                        {'error': f'Error processing file: {str(e)}. Please try a different file format.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Parse receipt data
                parsed_data = parse_receipt_data(extracted_text)
                
                # Check for manual label override
                manual_label = serializer.validated_data.get('manual_label')
                if manual_label:
                    parsed_data['category'] = manual_label
                    parsed_data['confidence_score'] = 1.0  # High confidence for manual labels
                
                # Create receipt object
                receipt = Receipt.objects.create(
                    vendor=parsed_data.get('vendor'),
                    date=parsed_data.get('date'),
                    amount=parsed_data.get('amount'),
                    category=parsed_data.get('category'),
                    original_file=file_obj,
                    file_name=file_obj.name,
                    file_type=file_type,
                    extracted_text=extracted_text,
                    confidence_score=parsed_data.get('confidence_score', 0.0)
                )
                
                # Return parsed data
                response_data = {
                    'id': receipt.id,
                    'vendor': receipt.vendor,
                    'date': receipt.formatted_date,
                    'amount': receipt.formatted_amount,
                    'category': receipt.category,
                    'confidence_score': receipt.confidence_score,
                    'message': 'Receipt uploaded and parsed successfully'
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Error processing file: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecordListView(generics.ListAPIView):
    """List all records with pagination"""
    
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    
    def get_queryset(self):
        queryset = Receipt.objects.all()
        
        # Optional filtering by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific record"""
    
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    lookup_field = 'id'


class SearchView(APIView):
    """Search records with various filters"""
    
    def get(self, request):
        serializer = ReceiptSearchSerializer(data=request.query_params)
        
        if serializer.is_valid():
            queryset = Receipt.objects.all()
            
            # Keyword search
            keyword = serializer.validated_data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(vendor__icontains=keyword) |
                    Q(category__icontains=keyword) |
                    Q(extracted_text__icontains=keyword)
                )
            
            # Amount range filter
            min_amount = serializer.validated_data.get('min_amount')
            max_amount = serializer.validated_data.get('max_amount')
            
            if min_amount is not None:
                queryset = queryset.filter(amount__gte=min_amount)
            if max_amount is not None:
                queryset = queryset.filter(amount__lte=max_amount)
            
            # Date range filter
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            # Category filter
            category = serializer.validated_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Serialize results
            serializer = ReceiptSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatsView(APIView):
    """Get aggregated statistics"""
    
    def get(self, request):
        try:
            # Basic statistics
            total_receipts = Receipt.objects.count()
            receipts_with_amount = Receipt.objects.exclude(amount__isnull=True)
            
            if receipts_with_amount.exists():
                total_amount = receipts_with_amount.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
                avg_amount = receipts_with_amount.aggregate(Avg('amount'))['amount__avg'] or Decimal('0')
                min_amount = receipts_with_amount.aggregate(Min('amount'))['amount__min'] or Decimal('0')
                max_amount = receipts_with_amount.aggregate(Max('amount'))['amount__max'] or Decimal('0')
                
                # Calculate median
                amounts = list(receipts_with_amount.values_list('amount', flat=True))
                amounts.sort()
                n = len(amounts)
                if n % 2 == 0:
                    median_amount = (amounts[n//2 - 1] + amounts[n//2]) / 2
                else:
                    median_amount = amounts[n//2]
            else:
                total_amount = avg_amount = min_amount = max_amount = median_amount = Decimal('0')
            
            # Category breakdown
            category_breakdown = {}
            category_stats = Receipt.objects.values('category').annotate(
                count=Count('id'),
                total=Sum('amount')
            )
            for stat in category_stats:
                category_breakdown[stat['category']] = {
                    'count': stat['count'],
                    'total': float(stat['total'] or 0)
                }
            
            # Vendor breakdown
            vendor_breakdown = {}
            vendor_stats = Receipt.objects.values('vendor').annotate(
                count=Count('id'),
                total=Sum('amount')
            ).order_by('-total')[:10]  # Top 10 vendors
            for stat in vendor_stats:
                if stat['vendor']:  # Skip None vendors
                    vendor_breakdown[stat['vendor']] = {
                        'count': stat['count'],
                        'total': float(stat['total'] or 0)
                    }
            
            # Time series data
            monthly_totals = {}
            yearly_totals = {}
            
            # Get receipts with dates
            dated_receipts = Receipt.objects.exclude(date__isnull=True)
            
            if dated_receipts.exists():
                # Monthly totals
                monthly_data = dated_receipts.extra(
                    select={'year_month': "strftime('%Y-%m', date)"}
                ).values('year_month').annotate(
                    total=Sum('amount')
                ).order_by('year_month')
                
                for item in monthly_data:
                    monthly_totals[item['year_month']] = float(item['total'] or 0)
                
                # Yearly totals
                yearly_data = dated_receipts.extra(
                    select={'year': "strftime('%Y', date)"}
                ).values('year').annotate(
                    total=Sum('amount')
                ).order_by('year')
                
                for item in yearly_data:
                    yearly_totals[item['year']] = float(item['total'] or 0)
            
            # Prepare response with proper decimal formatting
            from decimal import ROUND_HALF_UP
            
            def format_decimal(value):
                if value is None:
                    return None
                return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            stats_data = {
                'total_receipts': total_receipts,
                'total_amount': format_decimal(total_amount),
                'average_amount': format_decimal(avg_amount),
                'median_amount': format_decimal(median_amount),
                'min_amount': format_decimal(min_amount),
                'max_amount': format_decimal(max_amount),
                'category_breakdown': category_breakdown,
                'vendor_breakdown': vendor_breakdown,
                'monthly_totals': monthly_totals,
                'yearly_totals': yearly_totals,
            }
            
            serializer = ReceiptStatsSerializer(data=stats_data)
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Error calculating statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def export_data(request):
    """Export data as CSV or JSON"""
    format_type = request.query_params.get('format', 'json').lower()
    
    if format_type not in ['json', 'csv']:
        return Response(
            {'error': 'Invalid format. Use "json" or "csv"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        receipts = Receipt.objects.all()
        data = ReceiptSerializer(receipts, many=True).data
        
        if format_type == 'json':
            return Response(data)
        else:  # CSV
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="receipts.csv"'
            
            if data:
                writer = csv.DictWriter(response, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return response
            
    except Exception as e:
        return Response(
            {'error': f'Error exporting data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def clear_all_data(request):
    """Clear all receipt data"""
    try:
        count = Receipt.objects.count()
        Receipt.objects.all().delete()
        return Response({
            'message': f'Successfully deleted {count} records',
            'deleted_count': count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Error deleting data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
