import hashlib
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
import statistics
from collections import defaultdict, Counter
import heapq
import bisect
import re
import logging

logger = logging.getLogger(__name__)


class SearchAlgorithms:
    """Advanced search algorithms for receipt data"""
    
    @staticmethod
    def linear_search(records: List[Dict], query: str, field: str) -> List[Dict]:
        """
        Linear search implementation - O(n) time complexity
        Searches through all records linearly for exact or partial matches
        """
        results = []
        query_lower = query.lower()
        
        for record in records:
            field_value = str(record.get(field, '')).lower()
            if query_lower in field_value:
                results.append(record)
        
        return results
    
    @staticmethod
    def binary_search_sorted(records: List[Dict], query: str, field: str) -> List[Dict]:
        """
        Binary search for sorted data - O(log n) time complexity
        Requires records to be pre-sorted by the search field
        """
        results = []
        query_lower = query.lower()
        
        # Binary search implementation
        left, right = 0, len(records) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_value = str(records[mid].get(field, '')).lower()
            
            if query_lower == mid_value:
                # Found exact match, collect all matches
                results.append(records[mid])
                
                # Check left side for more matches
                i = mid - 1
                while i >= 0 and str(records[i].get(field, '')).lower() == query_lower:
                    results.append(records[i])
                    i -= 1
                
                # Check right side for more matches
                i = mid + 1
                while i < len(records) and str(records[i].get(field, '')).lower() == query_lower:
                    results.append(records[i])
                    i += 1
                
                break
            elif query_lower < mid_value:
                right = mid - 1
            else:
                left = mid + 1
        
        return results
    
    @staticmethod
    def hash_based_search(records: List[Dict], query: str, field: str) -> List[Dict]:
        """
        Hash-based search using pre-built index - O(1) average case
        Creates a hash table for fast lookups
        """
        # Build hash index
        hash_index = defaultdict(list)
        
        for record in records:
            field_value = str(record.get(field, '')).lower()
            # Create hash key from field value
            hash_key = hashlib.md5(field_value.encode()).hexdigest()
            hash_index[hash_key].append(record)
        
        # Search using hash
        query_lower = query.lower()
        query_hash = hashlib.md5(query_lower.encode()).hexdigest()
        
        return hash_index.get(query_hash, [])
    
    @staticmethod
    def pattern_based_search(records: List[Dict], pattern: str, field: str) -> List[Dict]:
        """
        Pattern-based search using regex - O(n*m) where n=records, m=pattern length
        Supports regex patterns for advanced searching
        """
        results = []
        
        try:
            regex_pattern = re.compile(pattern, re.IGNORECASE)
            
            for record in records:
                field_value = str(record.get(field, ''))
                if regex_pattern.search(field_value):
                    results.append(record)
        
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return []
        
        return results
    
    @staticmethod
    def range_search(records: List[Dict], min_val: float, max_val: float, field: str) -> List[Dict]:
        """
        Range-based search for numerical fields - O(n) time complexity
        """
        results = []
        
        for record in records:
            field_value = record.get(field)
            if field_value is not None:
                try:
                    # Convert to float for comparison
                    if isinstance(field_value, Decimal):
                        field_value = float(field_value)
                    elif isinstance(field_value, str):
                        field_value = float(field_value)
                    
                    if min_val <= field_value <= max_val:
                        results.append(record)
                
                except (ValueError, TypeError):
                    continue
        
        return results
    
    @staticmethod
    def fuzzy_search(records: List[Dict], query: str, field: str, threshold: float = 0.8) -> List[Dict]:
        """
        Fuzzy search using Levenshtein distance - O(n*m) where n=records, m=query length
        """
        def levenshtein_distance(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        results = []
        query_lower = query.lower()
        
        for record in records:
            field_value = str(record.get(field, '')).lower()
            
            # Calculate similarity
            max_len = max(len(query_lower), len(field_value))
            if max_len == 0:
                continue
            
            distance = levenshtein_distance(query_lower, field_value)
            similarity = 1 - (distance / max_len)
            
            if similarity >= threshold:
                results.append(record)
        
        return results


class SortingAlgorithms:
    """Advanced sorting algorithms for receipt data"""
    
    @staticmethod
    def quicksort(records: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        Quicksort implementation - O(n log n) average case, O(n²) worst case
        """
        if len(records) <= 1:
            return records
        
        def get_field_value(record: Dict) -> Any:
            """Get field value for comparison"""
            value = record.get(field)
            if value is None:
                return float('-inf') if not reverse else float('inf')
            
            # Handle different data types
            if isinstance(value, (int, float, Decimal)):
                return float(value)
            elif isinstance(value, (str, date, datetime)):
                return str(value)
            else:
                return str(value)
        
        # Choose pivot (middle element)
        pivot_idx = len(records) // 2
        pivot = get_field_value(records[pivot_idx])
        
        # Partition
        left, equal, right = [], [], []
        
        for record in records:
            value = get_field_value(record)
            if value < pivot:
                left.append(record)
            elif value == pivot:
                equal.append(record)
            else:
                right.append(record)
        
        # Recursively sort
        if reverse:
            return (SortingAlgorithms.quicksort(right, field, reverse) + 
                   equal + 
                   SortingAlgorithms.quicksort(left, field, reverse))
        else:
            return (SortingAlgorithms.quicksort(left, field, reverse) + 
                   equal + 
                   SortingAlgorithms.quicksort(right, field, reverse))
    
    @staticmethod
    def mergesort(records: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        Mergesort implementation - O(n log n) time complexity
        """
        if len(records) <= 1:
            return records
        
        def get_field_value(record: Dict) -> Any:
            """Get field value for comparison"""
            value = record.get(field)
            if value is None:
                return float('-inf') if not reverse else float('inf')
            
            if isinstance(value, (int, float, Decimal)):
                return float(value)
            elif isinstance(value, (str, date, datetime)):
                return str(value)
            else:
                return str(value)
        
        def merge(left: List[Dict], right: List[Dict]) -> List[Dict]:
            """Merge two sorted lists"""
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                left_val = get_field_value(left[i])
                right_val = get_field_value(right[j])
                
                if reverse:
                    if left_val >= right_val:
                        result.append(left[i])
                        i += 1
                    else:
                        result.append(right[j])
                        j += 1
                else:
                    if left_val <= right_val:
                        result.append(left[i])
                        i += 1
                    else:
                        result.append(right[j])
                        j += 1
            
            # Add remaining elements
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        # Divide
        mid = len(records) // 2
        left = SortingAlgorithms.mergesort(records[:mid], field, reverse)
        right = SortingAlgorithms.mergesort(records[mid:], field, reverse)
        
        # Conquer
        return merge(left, right)
    
    @staticmethod
    def heapsort(records: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        Heapsort implementation - O(n log n) time complexity
        """
        def get_field_value(record: Dict) -> Any:
            """Get field value for comparison"""
            value = record.get(field)
            if value is None:
                return float('-inf') if not reverse else float('inf')
            
            if isinstance(value, (int, float, Decimal)):
                return float(value)
            elif isinstance(value, (str, date, datetime)):
                return str(value)
            else:
                return str(value)
        
        # Create heap with field values
        heap = [(get_field_value(record), i, record) for i, record in enumerate(records)]
        
        # Build heap
        heapq.heapify(heap)
        
        # Extract elements
        result = []
        while heap:
            _, _, record = heapq.heappop(heap)
            result.append(record)
        
        # Reverse if needed
        if reverse:
            result.reverse()
        
        return result
    
    @staticmethod
    def timsort(records: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
        """
        Timsort implementation (Python's built-in sort algorithm)
        O(n log n) time complexity, adaptive and stable
        """
        def get_field_value(record: Dict) -> Any:
            """Get field value for comparison"""
            value = record.get(field)
            if value is None:
                return float('-inf') if not reverse else float('inf')
            
            if isinstance(value, (int, float, Decimal)):
                return float(value)
            elif isinstance(value, (str, date, datetime)):
                return str(value)
            else:
                return str(value)
        
        # Use Python's built-in sort with custom key
        sorted_records = records.copy()
        sorted_records.sort(key=get_field_value, reverse=reverse)
        return sorted_records


class AggregationFunctions:
    """Statistical aggregation functions for receipt data"""
    
    @staticmethod
    def calculate_sum(records: List[Dict], field: str = 'amount') -> Decimal:
        """Calculate sum of numerical field"""
        total = Decimal('0.0')
        for record in records:
            value = record.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    total += value
                except (ValueError, TypeError):
                    continue
        return total
    
    @staticmethod
    def calculate_mean(records: List[Dict], field: str = 'amount') -> Optional[Decimal]:
        """Calculate arithmetic mean"""
        values = []
        for record in records:
            value = record.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    values.append(value)
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return None
        
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_median(records: List[Dict], field: str = 'amount') -> Optional[Decimal]:
        """Calculate median value"""
        values = []
        for record in records:
            value = record.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return None
        
        return Decimal(str(statistics.median(values)))
    
    @staticmethod
    def calculate_mode(records: List[Dict], field: str = 'amount') -> Optional[Decimal]:
        """Calculate mode (most frequent value)"""
        values = []
        for record in records:
            value = record.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return None
        
        try:
            mode_value = statistics.mode(values)
            return Decimal(str(mode_value))
        except statistics.StatisticsError:
            return None
    
    @staticmethod
    def calculate_frequency_distribution(records: List[Dict], field: str = 'vendor') -> Dict[str, int]:
        """Calculate frequency distribution (histogram)"""
        frequency = Counter()
        
        for record in records:
            value = record.get(field)
            if value is not None:
                frequency[str(value)] += 1
        
        return dict(frequency)
    
    @staticmethod
    def calculate_time_series_aggregation(records: List[Dict], 
                                        date_field: str = 'date',
                                        value_field: str = 'amount',
                                        interval: str = 'month') -> Dict[str, Decimal]:
        """Calculate time-series aggregations"""
        time_series = defaultdict(Decimal)
        
        for record in records:
            date_value = record.get(date_field)
            value = record.get(value_field)
            
            if date_value and value is not None:
                try:
                    # Parse date if it's a string
                    if isinstance(date_value, str):
                        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                    
                    # Format date based on interval
                    if interval == 'month':
                        key = date_value.strftime('%Y-%m')
                    elif interval == 'year':
                        key = date_value.strftime('%Y')
                    elif interval == 'week':
                        key = f"{date_value.year}-W{date_value.isocalendar()[1]:02d}"
                    else:
                        key = date_value.strftime('%Y-%m-%d')
                    
                    # Add value to aggregation
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    
                    time_series[key] += value
                
                except (ValueError, TypeError):
                    continue
        
        return dict(time_series)
    
    @staticmethod
    def calculate_sliding_window_average(records: List[Dict],
                                       date_field: str = 'date',
                                       value_field: str = 'amount',
                                       window_size: int = 3) -> List[Tuple[str, Decimal]]:
        """Calculate sliding window average"""
        # Sort records by date
        sorted_records = SortingAlgorithms.timsort(records, date_field)
        
        # Group by date and calculate daily totals
        daily_totals = defaultdict(Decimal)
        for record in sorted_records:
            date_value = record.get(date_field)
            value = record.get(value_field)
            
            if date_value and value is not None:
                try:
                    if isinstance(date_value, str):
                        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                    
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    
                    daily_totals[date_value] += value
                
                except (ValueError, TypeError):
                    continue
        
        # Calculate sliding window average
        dates = sorted(daily_totals.keys())
        sliding_averages = []
        
        for i in range(len(dates) - window_size + 1):
            window_dates = dates[i:i + window_size]
            window_total = sum(daily_totals[date] for date in window_dates)
            average = window_total / window_size
            
            # Use middle date as key
            middle_date = window_dates[window_size // 2]
            sliding_averages.append((middle_date.strftime('%Y-%m-%d'), average))
        
        return sliding_averages
    
    @staticmethod
    def calculate_statistical_summary(records: List[Dict], field: str = 'amount') -> Dict[str, Any]:
        """Calculate comprehensive statistical summary"""
        values = []
        for record in records:
            value = record.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        value = Decimal(value)
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return {
                'count': 0,
                'sum': Decimal('0'),
                'mean': None,
                'median': None,
                'mode': None,
                'min': None,
                'max': None,
                'std_dev': None,
                'variance': None
            }
        
        return {
            'count': len(values),
            'sum': Decimal(str(sum(values))),
            'mean': Decimal(str(statistics.mean(values))),
            'median': Decimal(str(statistics.median(values))),
            'mode': Decimal(str(statistics.mode(values))) if len(set(values)) < len(values) else None,
            'min': Decimal(str(min(values))),
            'max': Decimal(str(max(values))),
            'std_dev': Decimal(str(statistics.stdev(values))) if len(values) > 1 else None,
            'variance': Decimal(str(statistics.variance(values))) if len(values) > 1 else None
        }


class ComputationalAnalyzer:
    """Main computational analyzer that combines all algorithms"""
    
    def __init__(self):
        self.search_algorithms = SearchAlgorithms()
        self.sorting_algorithms = SortingAlgorithms()
        self.aggregation_functions = AggregationFunctions()
    
    def advanced_search(self, records: List[Dict], 
                       query: str = None,
                       pattern: str = None,
                       field: str = 'vendor',
                       search_type: str = 'linear',
                       min_amount: float = None,
                       max_amount: float = None,
                       date_from: date = None,
                       date_to: date = None) -> List[Dict]:
        """
        Advanced search with multiple algorithms and filters
        """
        results = records.copy()
        
        # Apply keyword/pattern search
        if query:
            if search_type == 'linear':
                results = self.search_algorithms.linear_search(results, query, field)
            elif search_type == 'binary':
                # Sort first for binary search
                sorted_records = self.sorting_algorithms.timsort(results, field)
                results = self.search_algorithms.binary_search_sorted(sorted_records, query, field)
            elif search_type == 'hash':
                results = self.search_algorithms.hash_based_search(results, query, field)
            elif search_type == 'fuzzy':
                results = self.search_algorithms.fuzzy_search(results, query, field)
        
        # Apply pattern search
        if pattern:
            pattern_results = self.search_algorithms.pattern_based_search(results, pattern, field)
            results = [r for r in results if r in pattern_results]
        
        # Apply amount range filter
        if min_amount is not None or max_amount is not None:
            min_val = min_amount if min_amount is not None else float('-inf')
            max_val = max_amount if max_amount is not None else float('inf')
            amount_results = self.search_algorithms.range_search(results, min_val, max_val, 'amount')
            results = [r for r in results if r in amount_results]
        
        # Apply date range filter
        if date_from or date_to:
            date_results = []
            for record in results:
                record_date = record.get('date')
                if record_date:
                    if isinstance(record_date, str):
                        try:
                            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
                        except ValueError:
                            continue
                    
                    if date_from and record_date < date_from:
                        continue
                    if date_to and record_date > date_to:
                        continue
                    
                    date_results.append(record)
            results = date_results
        
        return results
    
    def sort_records(self, records: List[Dict], 
                    field: str = 'date',
                    algorithm: str = 'timsort',
                    reverse: bool = False) -> List[Dict]:
        """
        Sort records using specified algorithm
        """
        if algorithm == 'quicksort':
            return self.sorting_algorithms.quicksort(records, field, reverse)
        elif algorithm == 'mergesort':
            return self.sorting_algorithms.mergesort(records, field, reverse)
        elif algorithm == 'heapsort':
            return self.sorting_algorithms.heapsort(records, field, reverse)
        else:  # timsort (default)
            return self.sorting_algorithms.timsort(records, field, reverse)
    
    def calculate_aggregations(self, records: List[Dict]) -> Dict[str, Any]:
        """
        Calculate comprehensive aggregations
        """
        return {
            'statistical_summary': self.aggregation_functions.calculate_statistical_summary(records),
            'vendor_frequency': self.aggregation_functions.calculate_frequency_distribution(records, 'vendor'),
            'category_frequency': self.aggregation_functions.calculate_frequency_distribution(records, 'category'),
            'monthly_trends': self.aggregation_functions.calculate_time_series_aggregation(records, 'date', 'amount', 'month'),
            'sliding_window_average': self.aggregation_functions.calculate_sliding_window_average(records)
        } 