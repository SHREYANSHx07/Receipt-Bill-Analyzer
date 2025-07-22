from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta, date
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
from .computational_utils import ComputationalAnalyzer


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
    """Advanced search with computational algorithms"""
    
    def get(self, request):
        try:
            # Get search parameters
            keyword = request.GET.get('keyword', '').strip()
            pattern = request.GET.get('pattern', '').strip()
            search_type = request.GET.get('search_type', 'linear')  # linear, binary, hash, fuzzy
            search_field = request.GET.get('search_field', 'vendor')
            min_amount = request.GET.get('min_amount')
            max_amount = request.GET.get('max_amount')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            category = request.GET.get('category', '').strip()
            vendor = request.GET.get('vendor', '').strip()
            
            # Get all records
            queryset = Receipt.objects.all()
            records = list(queryset)
            
            # Convert to list of dictionaries for computational analysis
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'vendor': record.vendor,
                    'date': record.date,
                    'amount': record.amount,
                    'category': record.category,
                    'extracted_text': record.extracted_text,
                    'confidence_score': record.confidence_score
                })
            
            # Initialize computational analyzer
            analyzer = ComputationalAnalyzer()
            
            # Apply advanced search algorithms
            results = analyzer.advanced_search(
                records=records_data,
                query=keyword if keyword else None,
                pattern=pattern if pattern else None,
                field=search_field,
                search_type=search_type,
                min_amount=float(min_amount) if min_amount else None,
                max_amount=float(max_amount) if max_amount else None,
                date_from=datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None,
                date_to=datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
            )
            
            # Apply additional Django ORM filters for efficiency
            if category:
                results = [r for r in results if category.lower() in r.get('category', '').lower()]
            
            if vendor:
                results = [r for r in results if vendor.lower() in r.get('vendor', '').lower()]
            
            # Convert back to Django queryset for serialization
            result_ids = [r['id'] for r in results]
            final_queryset = Receipt.objects.filter(id__in=result_ids)
            
            # Serialize results
            serializer = ReceiptSerializer(final_queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Search error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StatsView(APIView):
    """Advanced statistics with computational algorithms"""
    
    def get(self, request):
        try:
            # Get all records for computational analysis
            queryset = Receipt.objects.all()
            records = list(queryset)
            
            # Convert to list of dictionaries for computational analysis
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'vendor': record.vendor,
                    'date': record.date,
                    'amount': record.amount,
                    'category': record.category,
                    'extracted_text': record.extracted_text,
                    'confidence_score': record.confidence_score
                })
            
            # Initialize computational analyzer
            analyzer = ComputationalAnalyzer()
            
            # Calculate comprehensive aggregations using computational algorithms
            aggregations = analyzer.calculate_aggregations(records_data)
            
            # Basic statistics using computational functions
            total_receipts = len(records_data)
            receipts_with_amount = [r for r in records_data if r.get('amount') is not None]
            
            if receipts_with_amount:
                # Use computational aggregation functions
                total_amount = analyzer.aggregation_functions.calculate_sum(records_data, 'amount')
                mean_amount = analyzer.aggregation_functions.calculate_mean(records_data, 'amount')
                median_amount = analyzer.aggregation_functions.calculate_median(records_data, 'amount')
                mode_amount = analyzer.aggregation_functions.calculate_mode(records_data, 'amount')
                
                # Get min/max from statistical summary
                stats_summary = aggregations['statistical_summary']
                min_amount = stats_summary.get('min', Decimal('0'))
                max_amount = stats_summary.get('max', Decimal('0'))
                std_dev = stats_summary.get('std_dev')
                variance = stats_summary.get('variance')
            else:
                total_amount = mean_amount = median_amount = mode_amount = min_amount = max_amount = Decimal('0')
                std_dev = variance = None
            
            # Format response with computational results
            response_data = {
                'total_receipts': total_receipts,
                'total_amount': float(total_amount),
                'mean_amount': float(mean_amount) if mean_amount else 0,
                'median_amount': float(median_amount) if median_amount else 0,
                'mode_amount': float(mode_amount) if mode_amount else 0,
                'min_amount': float(min_amount) if min_amount else 0,
                'max_amount': float(max_amount) if max_amount else 0,
                'std_deviation': float(std_dev) if std_dev else None,
                'variance': float(variance) if variance else None,
                'category_breakdown': aggregations['category_frequency'],
                'vendor_breakdown': aggregations['vendor_frequency'],
                'monthly_trends': aggregations['monthly_trends'],
                'sliding_window_average': aggregations['sliding_window_average']
            }
            
            # Convert simple frequency distributions to expected format
            if response_data['category_breakdown']:
                formatted_category_breakdown = {}
                for category, count in response_data['category_breakdown'].items():
                    # Calculate total amount for this category
                    category_total = sum(
                        float(record['amount']) for record in records_data 
                        if record.get('category') == category and record.get('amount') is not None
                    )
                    formatted_category_breakdown[category] = {
                        'count': count,
                        'total': category_total
                    }
                response_data['category_breakdown'] = formatted_category_breakdown
            
            if response_data['vendor_breakdown']:
                formatted_vendor_breakdown = {}
                for vendor, count in response_data['vendor_breakdown'].items():
                    # Calculate total amount for this vendor
                    vendor_total = sum(
                        float(record['amount']) for record in records_data 
                        if record.get('vendor') == vendor and record.get('amount') is not None
                    )
                    formatted_vendor_breakdown[vendor] = {
                        'count': count,
                        'total': vendor_total
                    }
                response_data['vendor_breakdown'] = formatted_vendor_breakdown
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Statistics error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SortView(APIView):
    """Sort records using computational algorithms"""
    
    def get(self, request):
        try:
            # Get sorting parameters
            field = request.GET.get('field', 'date')
            algorithm = request.GET.get('algorithm', 'timsort')  # timsort, quicksort, mergesort, heapsort
            reverse = request.GET.get('reverse', 'false').lower() == 'true'
            
            # Get all records
            queryset = Receipt.objects.all()
            records = list(queryset)
            
            # Convert to list of dictionaries for computational analysis
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'vendor': record.vendor,
                    'date': record.date,
                    'amount': record.amount,
                    'category': record.category,
                    'extracted_text': record.extracted_text,
                    'confidence_score': record.confidence_score
                })
            
            # Initialize computational analyzer
            analyzer = ComputationalAnalyzer()
            
            # Sort records using computational algorithms
            sorted_records = analyzer.sort_records(
                records=records_data,
                field=field,
                algorithm=algorithm,
                reverse=reverse
            )
            
            # Convert back to Django queryset for serialization
            result_ids = [r['id'] for r in sorted_records]
            final_queryset = Receipt.objects.filter(id__in=result_ids)
            
            # Maintain sort order
            id_order = {id_val: index for index, id_val in enumerate(result_ids)}
            final_queryset = sorted(final_queryset, key=lambda x: id_order[x.id])
            
            # Serialize results
            serializer = ReceiptSerializer(final_queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Sorting error: {str(e)}'},
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


@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Backend is running',
        'timestamp': timezone.now().isoformat()
    })
