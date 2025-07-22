#!/usr/bin/env python3
"""
Test script for computational algorithms in Receipt Analyzer
Demonstrates search algorithms, sorting algorithms, and aggregation functions
"""

import requests
import json
import time
from datetime import datetime, date
from decimal import Decimal

# API Configuration
BASE_URL = "http://localhost:8000/api"

def test_search_algorithms():
    """Test various search algorithms"""
    print("🔍 Testing Search Algorithms")
    print("=" * 50)
    
    # Test linear search
    print("\n1. Linear Search (O(n) time complexity)")
    params = {
        'keyword': 'grocery',
        'search_type': 'linear',
        'search_field': 'vendor'
    }
    response = requests.get(f"{BASE_URL}/search/", params=params)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Linear search found {len(results)} results")
        for result in results[:3]:  # Show first 3 results
            print(f"   - {result.get('vendor', 'N/A')}: ${result.get('amount', 'N/A')}")
    else:
        print(f"❌ Linear search failed: {response.status_code}")
    
    # Test fuzzy search
    print("\n2. Fuzzy Search (O(n*m) time complexity)")
    params = {
        'keyword': 'grocer',
        'search_type': 'fuzzy',
        'search_field': 'vendor'
    }
    response = requests.get(f"{BASE_URL}/search/", params=params)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Fuzzy search found {len(results)} results")
        for result in results[:3]:
            print(f"   - {result.get('vendor', 'N/A')}: ${result.get('amount', 'N/A')}")
    else:
        print(f"❌ Fuzzy search failed: {response.status_code}")
    
    # Test pattern-based search
    print("\n3. Pattern-based Search (Regex)")
    params = {
        'pattern': r'^[A-Z].*store',
        'search_field': 'vendor'
    }
    response = requests.get(f"{BASE_URL}/search/", params=params)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Pattern search found {len(results)} results")
        for result in results[:3]:
            print(f"   - {result.get('vendor', 'N/A')}: ${result.get('amount', 'N/A')}")
    else:
        print(f"❌ Pattern search failed: {response.status_code}")
    
    # Test range search
    print("\n4. Range Search (Amount range)")
    params = {
        'min_amount': '10.00',
        'max_amount': '100.00'
    }
    response = requests.get(f"{BASE_URL}/search/", params=params)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Range search found {len(results)} results")
        for result in results[:3]:
            print(f"   - {result.get('vendor', 'N/A')}: ${result.get('amount', 'N/A')}")
    else:
        print(f"❌ Range search failed: {response.status_code}")


def test_sorting_algorithms():
    """Test various sorting algorithms"""
    print("\n\n📊 Testing Sorting Algorithms")
    print("=" * 50)
    
    algorithms = ['timsort', 'quicksort', 'mergesort', 'heapsort']
    fields = ['date', 'amount', 'vendor', 'category']
    
    for algorithm in algorithms:
        print(f"\n{algorithm.upper()} Algorithm (O(n log n) average case)")
        for field in fields:
            start_time = time.time()
            params = {
                'field': field,
                'algorithm': algorithm,
                'reverse': 'false'
            }
            response = requests.get(f"{BASE_URL}/sort/", params=params)
            end_time = time.time()
            
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ {field.capitalize()} field: {len(results)} records sorted in {end_time - start_time:.4f}s")
                if results:
                    print(f"      First: {results[0].get(field, 'N/A')}")
                    print(f"      Last: {results[-1].get(field, 'N/A')}")
            else:
                print(f"   ❌ {field.capitalize()} field failed: {response.status_code}")


def test_aggregation_functions():
    """Test aggregation functions"""
    print("\n\n📈 Testing Aggregation Functions")
    print("=" * 50)
    
    # Get comprehensive statistics
    response = requests.get(f"{BASE_URL}/stats/")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistical Aggregations:")
        print(f"   - Total Receipts: {stats.get('total_receipts', 0)}")
        print(f"   - Total Amount: ${stats.get('total_amount', 0):,.2f}")
        print(f"   - Mean Amount: ${stats.get('mean_amount', 0):,.2f}")
        print(f"   - Median Amount: ${stats.get('median_amount', 0):,.2f}")
        print(f"   - Mode Amount: ${stats.get('mode_amount', 0):,.2f}")
        print(f"   - Min Amount: ${stats.get('min_amount', 0):,.2f}")
        print(f"   - Max Amount: ${stats.get('max_amount', 0):,.2f}")
        print(f"   - Standard Deviation: ${stats.get('std_deviation', 0):,.2f}")
        print(f"   - Variance: ${stats.get('variance', 0):,.2f}")
        
        # Show frequency distributions
        vendor_freq = stats.get('vendor_breakdown', {})
        if vendor_freq:
            print("\n   📊 Vendor Frequency Distribution (Histogram):")
            for vendor, count in list(vendor_freq.items())[:5]:
                print(f"      {vendor}: {count} receipts")
        
        category_freq = stats.get('category_breakdown', {})
        if category_freq:
            print("\n   📊 Category Frequency Distribution:")
            for category, count in category_freq.items():
                print(f"      {category}: {count} receipts")
        
        # Show time series data
        monthly_trends = stats.get('monthly_trends', {})
        if monthly_trends:
            print("\n   📈 Monthly Spending Trends (Time-series):")
            for month, amount in list(monthly_trends.items())[:5]:
                print(f"      {month}: ${amount:,.2f}")
        
        sliding_window = stats.get('sliding_window_average', [])
        if sliding_window:
            print("\n   📈 Sliding Window Average (3-month):")
            for date_str, avg_amount in sliding_window[:5]:
                print(f"      {date_str}: ${avg_amount:,.2f}")
    else:
        print(f"❌ Statistics failed: {response.status_code}")


def test_performance_comparison():
    """Compare performance of different algorithms"""
    print("\n\n⚡ Performance Comparison")
    print("=" * 50)
    
    # Test search performance
    search_types = ['linear', 'fuzzy', 'hash']
    test_keyword = 'grocery'
    
    print("🔍 Search Algorithm Performance:")
    for search_type in search_types:
        start_time = time.time()
        params = {
            'keyword': test_keyword,
            'search_type': search_type,
            'search_field': 'vendor'
        }
        response = requests.get(f"{BASE_URL}/search/", params=params)
        end_time = time.time()
        
        if response.status_code == 200:
            results = response.json()
            print(f"   {search_type.capitalize()} Search: {len(results)} results in {end_time - start_time:.4f}s")
        else:
            print(f"   {search_type.capitalize()} Search: Failed")
    
    # Test sorting performance
    print("\n📊 Sorting Algorithm Performance:")
    algorithms = ['timsort', 'quicksort', 'mergesort', 'heapsort']
    test_field = 'amount'
    
    for algorithm in algorithms:
        start_time = time.time()
        params = {
            'field': test_field,
            'algorithm': algorithm
        }
        response = requests.get(f"{BASE_URL}/sort/", params=params)
        end_time = time.time()
        
        if response.status_code == 200:
            results = response.json()
            print(f"   {algorithm.capitalize()}: {len(results)} records in {end_time - start_time:.4f}s")
        else:
            print(f"   {algorithm.capitalize()}: Failed")


def test_algorithm_complexity():
    """Demonstrate algorithm complexity analysis"""
    print("\n\n🧮 Algorithm Complexity Analysis")
    print("=" * 50)
    
    print("📊 Time Complexity Analysis:")
    print("   Search Algorithms:")
    print("     - Linear Search: O(n)")
    print("     - Binary Search: O(log n) [requires sorted data]")
    print("     - Hash-based Search: O(1) average case")
    print("     - Fuzzy Search: O(n*m) where m is query length")
    print("     - Pattern Search: O(n*m) with regex matching")
    print("     - Range Search: O(n)")
    
    print("\n   Sorting Algorithms:")
    print("     - Timsort: O(n log n) average and worst case")
    print("     - Quicksort: O(n log n) average, O(n²) worst case")
    print("     - Mergesort: O(n log n) guaranteed")
    print("     - Heapsort: O(n log n) guaranteed")
    
    print("\n   Aggregation Functions:")
    print("     - Sum/Mean: O(n)")
    print("     - Median: O(n log n) [due to sorting]")
    print("     - Mode: O(n)")
    print("     - Frequency Distribution: O(n)")
    print("     - Time-series Aggregation: O(n)")
    print("     - Sliding Window: O(n*w) where w is window size")


def main():
    """Run all computational algorithm tests"""
    print("🚀 Receipt Analyzer - Computational Algorithms Test")
    print("=" * 60)
    
    try:
        # Test all computational features
        test_search_algorithms()
        test_sorting_algorithms()
        test_aggregation_functions()
        test_performance_comparison()
        test_algorithm_complexity()
        
        print("\n\n✅ All computational algorithm tests completed!")
        print("\n📋 Summary of Implemented Features:")
        print("   🔍 Search Algorithms:")
        print("     - Linear Search (O(n))")
        print("     - Binary Search (O(log n))")
        print("     - Hash-based Search (O(1) average)")
        print("     - Fuzzy Search (O(n*m))")
        print("     - Pattern-based Search (Regex)")
        print("     - Range Search (O(n))")
        
        print("\n   📊 Sorting Algorithms:")
        print("     - Timsort (O(n log n))")
        print("     - Quicksort (O(n log n) average)")
        print("     - Mergesort (O(n log n))")
        print("     - Heapsort (O(n log n))")
        
        print("\n   📈 Aggregation Functions:")
        print("     - Sum, Mean, Median, Mode")
        print("     - Frequency Distributions (Histograms)")
        print("     - Time-series Aggregations")
        print("     - Sliding Window Averages")
        print("     - Statistical Summaries")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Django backend.")
        print("   Please ensure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")


if __name__ == "__main__":
    main() 