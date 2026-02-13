# ============================================================
# SORTING AND SEARCH MODULE
# ============================================================
# BENCHMARKING:
#   benchmark_sort()   — compare speed of different sorts
#   benchmark_search() — compare speed of different searches
#
# ============================================================
# WHAT IS Big-O COMPLEXITY?
# ============================================================
#
# Big-O is "GROWTH" of algorithm — how time grows with big data
#
# EXAMPLES (for 1,000,000 elements):
#   O(1)      — 1 operation           ← perfect!
#   O(log n)  — ~20 operations        ← binary search super fast!
#   O(n)      — 1,000,000 operations  ← acceptable
#   O(n log n)— 20,000,000 operations ← merge sort ok
#   O(n²)     — trillion operations!!!  ← VERY SLOW
#   O(2ⁿ)     — infinity              ← NEVER do this!
# ============================================================

import timeit  # Module for measuring execution time
from collections.abc import Callable  # For type hints of function parameter
from typing import Any  # For "any object" type

# ============================================================
# SORTING — MERGE SORT 
# ============================================================

def merge_sort(data: list[Any], key: Callable = lambda x: x) -> list[Any]:
    """MERGE SORT ALGORITHM (Divide and Conquer).
    
    Works on principle:
    1. SPLIT array in half (Divide)
    2. Recursively sort each half (Conquer)
    3. MERGE two sorted halves (Combine)
    
    WHY RECURSION?
    Because if we can sort two parts -
    we can merge them into one sorted part!
    And this works for array of any size.
    
    Args:
        data: List to sort (can contain any objects).
        key: Function that extracts comparison key from element.
            Example: lambda x: x[1] (if elements are tuples, get second element)
            Default: lambda x: x (get the element itself)

    Returns:
        NEW sorted list (original is NOT changed!)

    Complexity:
        Time  — O(n log n) in ALL cases!
        Space — O(n) (need extra memory)
        
    Example:
        >>> merge_sort([3, 1, 4, 1, 5, 9, 2, 6])
        [1, 1, 2, 3, 4, 5, 6, 9]
        
        >>> # With bikes:
        >>> bikes = [('bike1', 150), ('bike2', 50), ('bike3', 200)]
        >>> merge_sort(bikes, key=lambda x: x[1])
        [('bike2', 50), ('bike1', 150), ('bike3', 200)]
    """
    # BASE CASE of recursion:
    # If array contains 0 or 1 element - it is already sorted!
    if len(data) <= 1:
        return list(data)  # Return copy (don't change original)

    # SPLIT STEPS:
    # Find middle of array
    mid = len(data) // 2
    # Recursively sort LEFT half (from start to middle)
    left = merge_sort(data[:mid], key=key)
    # Recursively sort RIGHT half (from middle to end)
    right = merge_sort(data[mid:], key=key)

    # MERGE: Merge two sorted halves into one
    return _merge(left, right, key=key)


def _merge(
    left: list[Any], right: list[Any], key: Callable
) -> list[Any]:
    """HELPER FUNCTION to merge two sorted lists.
    
    Logic: How to mix two sorted decks of cards into one:
    1. Look at top card of each deck
    2. Take the one that is smaller
    3. Put in result
    4. Repeat until both decks are finished
    
    Args:
        left: First sorted list.
        right: Second sorted list.
        key: Function to extract comparison key.

    Returns:
        One combined sorted list.

    Complexity:
        Time  — O(n) where n = len(left) + len(right)
        Space — O(n) for result
        
    Example:
        >>> _merge([1, 3, 5], [2, 4, 6], key=lambda x: x)
        [1, 2, 3, 4, 5, 6]
    """
    # Result - empty list where we collect sorted elements
    result: list[Any] = []
    # Two pointers - positions in left and right lists
    i = j = 0

    # MAIN LOOP: while both decks are not finished
    while i < len(left) and j < len(right):
        # Compare current elements (usually compare keys!)
        if key(left[i]) <= key(right[j]):
            # Element from left deck is smaller - take it
            result.append(left[i])
            i += 1  # Move to next element in left deck
        else:
            # Element from right deck is smaller - take it
            result.append(right[j])
            j += 1  # Move to next element in right deck

    # WHEN ONE DECK IS FINISHED:
    # Remaining elements from left deck (already sorted!)
    result.extend(left[i:])
    # Remaining elements from right deck (already sorted!)
    result.extend(right[j:])
    
    return result

# ============================================================
# SORTING — INSERTION SORT 
# ============================================================

def insertion_sort(data: list[Any], key: Callable = lambda x: x) -> list[Any]:
    """INSERTION SORT ALGORITHM (like manually sorting cards).
    
    Works by:
    1. Starting with the second element (first is already "sorted")
    2. For each element:
       a) Go backward through the sorted part
       b) Shift larger elements to the right
       c) Insert current element in the correct position
    
    ADVANTAGES:
    - O(n) if data is already partially sorted
    - O(1) extra memory (no need to copy!)
    - Works like people sort cards manually
    
    DISADVANTAGES:
    - O(n²) on average and worst case
    - Slower than merge_sort on large data
    
    Args:
        data: List to sort (can contain any objects).
        key: Function that extracts comparison key from element.

    Returns:
        NEW sorted list (original is NOT modified!)
        
    Complexity:
        Time  — O(n²) on average/worst case
               O(n) on best case (already sorted)
        Space — O(n) for copy (we do .copy())
        
    Example:
        >>> insertion_sort([3, 1, 4, 1, 5, 9, 2, 6])
        [1, 1, 2, 3, 4, 5, 6, 9]
        
        >>> # With bikes:
        >>> bikes = [('bike1', 150), ('bike2', 50), ('bike3', 200)]
        >>> insertion_sort(bikes, key=lambda x: x[1])
        [('bike2', 50), ('bike1', 150), ('bike3', 200)]
    """
    # CREATE A COPY of original list
    # So we don't modify source data
    sorted_list = data.copy()
    
    # MAIN LOOP: start from second element (index 1)
    for i in range(1, len(sorted_list)):
        # Current element to insert in correct position
        current = sorted_list[i]
        # Pointer to element left of current
        j = i - 1
        
        # HELPER LOOP: go BACKWARD through sorted part
        # while: 1) we haven't gone past the beginning (j >= 0)
        #        2) and while current element is larger (key(sorted_list[j]) > key(current))
        while j >= 0 and key(sorted_list[j]) > key(current):
            # Shift larger element RIGHT (one position)
            sorted_list[j + 1] = sorted_list[j]
            # Move to previous element
            j -= 1
        
        # INSERT current element at found position
        # After while loop, j points to position WHERE to insert
        # (or -1 if we need to insert at the beginning)
        sorted_list[j + 1] = current
    
    return sorted_list

# ============================================================
# SEARCH — BINARY SEARCH 
# ============================================================

def binary_search(
    sorted_data: list[Any],
    target: Any,
    key: Callable = lambda x: x,
) -> int | None:
    """ALGORITHM BINARY SEARCH (search in sorted array).
    
    Works by "Divide in half" principle:
    1. Start from left and right ends of array
    2. Look at middle
    3. If middle == target — FOUND!
    4. If middle < target — search in RIGHT half
    5. If middle > target — search in LEFT half
    6. Repeat until we find it or run out of options
    
    ⚠️ IMPORTANT: sorted_data must be SORTED by key!
    If data is not sorted — result is WRONG!
    
    Args:
        sorted_data: List SORTED in ascending order by key.
                     ❌ ERROR if not sorted!
        target: Value we're looking for.
        key: Function to extract comparison key from element.
            Default: lambda x: x (use element itself)

    Returns:
        int: Index of found element in list
        None: If element is NOT found
        
    Complexity:
        Time  — O(log n) super fast! (for 1M elements ~20 operations)
        Space — O(1) no extra memory
        
    Example:
        >>> # Simple numbers
        >>> sorted_nums = [1, 3, 5, 7, 9, 11, 13]
        >>> binary_search(sorted_nums, 7)
        3  (element at [3] is number 7)
        >>> binary_search(sorted_nums, 6)
        None  (no such element)
        
        >>> # With bikes (distances must be sorted!)
        >>> distances = [50, 150, 200, 500]
        >>> binary_search(distances, 150)
        1  (second trip, 150km)
    """
    # INITIALIZE search boundaries
    low = 0  # Left boundary (start of array)
    high = len(sorted_data) - 1  # Right boundary (end of array)

    # MAIN LOOP: while boundaries haven't crossed
    while low <= high:
        # FIND MIDDLE of array between low and high
        # (low + high) // 2 is integer division
        mid = (low + high) // 2
        # Get value at position mid using key function
        mid_val = key(sorted_data[mid])

        # COMPARE value at middle with target
        if mid_val == target:
            # FOUND! Return index
            return mid
        elif mid_val < target:
            # Value at middle is LESS than target
            # So target is in RIGHT half (if it exists)
            # Shift left boundary right
            low = mid + 1
        else:
            # Value at middle is MORE than target
            # So target is in LEFT half (if it exists)
            # Shift right boundary left
            high = mid - 1

    # LOOP ENDED but we didn't find it
    # This means target is NOT in array
    return None

# ============================================================
# SEARCH — LINEAR SEARCH 
# ============================================================

def linear_search(
    data: list[Any],
    target: Any,
    key: Callable = lambda x: x,
) -> int | None:
    """ALGORITHM LINEAR SEARCH (scan all elements).
    
    Works VERY SIMPLY:
    1. Go through array from start to end
    2. For each element check: is this the target?
    3. If match — FOUND! Return index
    4. If reached end without match — NOT FOUND
    
    ✅ WORKS on unsorted data
    ✅ WORKS on any data type
    ❌ SLOW on large data (O(n))
    
    ADVANTAGES:
    - Simple logic (easy to understand and debug)
    - Works on unsorted data
    - Finds FIRST match
    
    DISADVANTAGES:
    - O(n) slow on large data
    - For sorted data binary_search is 50x+ faster!
    
    Args:
        data: Any list (sorted or not, doesn't matter!)
        target: Value we're looking for.
        key: Function to extract comparison key.
            Default: lambda x: x (use element itself)

    Returns:
        int: Index of FIRST match
        None: If element NOT found
        
    Complexity:
        Time  — O(n) in worst and average case
               (best case O(1) if first element is target!)
        Space — O(1) no extra memory
        
    Example:
        >>> # Unsorted numbers
        >>> nums = [3, 5, 1, 7, 9]
        >>> linear_search(nums, 7)
        3  (element [3] is number 7)
        >>> linear_search(nums, 10)
        None  (no such element)
        
        >>> # With bikes (can be in any order!)
        >>> distances = [200, 50, 500, 150]
        >>> linear_search(distances, 150)
        3  (fourth element is 150km)
    """
    # MAIN LOOP: go through each element with index
    for i, item in enumerate(data):
        # Extract comparison key from current element
        # and compare with target value
        if key(item) == target:
            # FOUND! Return index
            return i
    
    # LOOP ENDED but we didn't find a match
    # This means target is NOT in array
    return None

# ---------------------------------------------------------------------------
# Benchmarking helpers
# ---------------------------------------------------------------------------

def benchmark_sort(data: list[Any], key: Callable = lambda x: x, repeats: int = 5) -> dict:
    """SORTING BENCHMARK: Compare speed of different algorithms.
    
    This function:
    1. Runs merge_sort several times with same data
    2. Runs insertion_sort several times
    3. Runs built-in sorted() several times
    4. Measures time for each
    5. Returns results in milliseconds
    
    WHY MULTIPLE TIMES?
    Because one measurement can be inaccurate:
    - Another process might start during test
    - CPU cache can affect result
    - So we take average value (number=repeats times)
    
    Args:
        data: List to sort (will not be modified).
        key: Function to extract comparison key.
        repeats: How many times to repeat each algorithm (more = more accurate but slower).
                 Default 5 times.

    Returns:
        dict with three numbers (in milliseconds):
        {
            "merge_sort_ms": 1.23,      ← merge sort in ms
            "insertion_sort_ms": 2.45,  ← insertion sort in ms
            "builtin_sorted_ms": 0.50,  ← built-in sorted in ms
        }
        
    Example:
        >>> data = list(range(1000, 0, -1))  ← data in reverse order (worst case)
        >>> results = benchmark_sort(data, repeats=5)
        >>> results
        {
            'merge_sort_ms': 1.52,
            'insertion_sort_ms': 2.84,  ← insertion slower on large data!
            'builtin_sorted_ms': 0.31,  ← built-in function is fastest!
        }
    """
    custom_time = timeit.timeit(lambda: merge_sort(data, key=key), number=repeats)
    insertion_time = timeit.timeit(lambda: insertion_sort(data, key=key), number=repeats)
    builtin_time = timeit.timeit(lambda: sorted(data, key=key), number=repeats)
    return {
        "merge_sort_ms": round(custom_time / repeats * 1000, 2),
        "insertion_sort_ms": round(insertion_time / repeats * 1000, 2),
        "builtin_sorted_ms": round(builtin_time / repeats * 1000, 2),
    }


def benchmark_search(data: list[Any], target: Any, key: Callable = lambda x: x, repeats: int = 5) -> dict:
    """SEARCH BENCHMARK: Compare speed of different search algorithms.
    
    This function:
    1. Prepares data (sorts for binary_search)
    2. Runs binary_search several times
    3. Runs linear_search several times
    4. Runs built-in 'in' operator several times
    5. Measures time for each
    6. Returns results in milliseconds
    
    ⚠️ IMPORTANT: data will be SORTED for binary_search!
    If data is unsorted, binary_search can give WRONG result!
    
    WHY SORTING?
    - binary_search requires sorted data
    - so we sort once at start
    - then use for both search algorithms
    
    Args:
        data: List to search (will be SORTED).
        target: Value to search for.
        key: Function to extract comparison key.
        repeats: How many times to repeat measurement (more = more accurate).

    Returns:
        dict with three numbers (in milliseconds):
        {
            "binary_search_ms": 0.001,   ← binary very fast!
            "linear_search_ms": 5.234,   ← linear slower on large data!
            "builtin_in_ms": 0.003,      ← built-in in operator
        }
        
    Example:
        >>> data = list(range(1, 100001))  ← 100,000 elements
        >>> results = benchmark_search(data, target=75000, repeats=5)
        >>> results
        {
            'binary_search_ms': 0.001,   ← super fast!
            'linear_search_ms': 2.341,   ← 2000x slower!
            'builtin_in_ms': 0.002,
        }
        
    THEORY vs PRACTICE:
        On 1,000,000 elements:
        - linear_search: ~500,000 comparisons on average
        - binary_search: ~20 comparisons always!
        - Difference: 25,000x FASTER!
    """
    sorted_data = merge_sort(data, key=key)
    binary_time = timeit.timeit(lambda: binary_search(sorted_data, target, key=key), number=repeats)
    linear_time = timeit.timeit(lambda: linear_search(data, target, key=key), number=repeats)
    builtin_time = timeit.timeit(lambda: target in sorted_data, number=repeats)
    return {
        "binary_search_ms": round(binary_time / repeats * 1000, 2),
        "linear_search_ms": round(linear_time / repeats * 1000, 2),
        "builtin_in_ms": round(builtin_time / repeats * 1000, 2),
    }

