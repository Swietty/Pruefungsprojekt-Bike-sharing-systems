import timeit
from collections.abc import Callable
from typing import Any

# Sorting — Merge Sort

def merge_sort(data: list[Any], key: Callable = lambda x: x) -> list[Any]:
    """
    Sort *data* using the merge-sort algorithm.

    Args:
        data: List of items to sort.
        key: Function that extracts a comparison key from each item.

    Returns:
        A new sorted list (original list is not modified).

    Complexity:
        Time  — O(n log n) in all cases
        Space — O(n)
    """
    if len(data) <= 1:
        return list(data)

    mid = len(data) // 2
    left = merge_sort(data[:mid], key=key)
    right = merge_sort(data[mid:], key=key)

    return _merge(left, right, key=key)


def _merge(left: list[Any], right: list[Any], key: Callable) -> list[Any]:
    """
    Merge two sorted lists into a single sorted list.

    Args:
        left: Sorted list.
        right: Sorted list.
        key: Function to extract comparison key.

    Returns:
        Merged sorted list.

    Complexity:
        Time  — O(n) where n = len(left) + len(right)
        Space — O(n)
    """
    result: list[Any] = []
    i = j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Sorting — Insertion Sort

def insertion_sort(data: list[Any], key: Callable = lambda x: x) -> list[Any]:
    """
    Sort *data* using the insertion-sort algorithm.

    Args:
        data: List of items to sort.
        key: Function that extracts a comparison key from each item.

    Returns:
        A new sorted list (original list is not modified).

    Complexity:
        Time  — O(n^2) worst/average, O(n) best (already sorted)
        Space — O(n) for the copy
    """
    sorted_list = data.copy()
    for i in range(1, len(sorted_list)):
        current = sorted_list[i]
        j = i - 1
        while j >= 0 and key(sorted_list[j]) > key(current):
            sorted_list[j + 1] = sorted_list[j]
            j -= 1
        sorted_list[j + 1] = current
    return sorted_list

# ---------------------------------------------------------------------------
# Searching — Binary Search
# ---------------------------------------------------------------------------

def binary_search(sorted_data: list[Any], target: Any, key: Callable = lambda x: x) -> int | None:
    """
    Search for *target* in a sorted list using binary search.

    Args:
        sorted_data: List sorted in ascending order by *key*.
        target: Value to search for.
        key: Function to extract comparison key from items.

    Returns:
        Index of the found item, or None if not found.

    Complexity:
        Time  — O(log n)
        Space — O(1)
    """
    low, high = 0, len(sorted_data) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = key(sorted_data[mid])
        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
    return None

# ---------------------------------------------------------------------------
# Searching — Linear Search
# ---------------------------------------------------------------------------

def linear_search(data: list[Any], target: Any, key: Callable = lambda x: x) -> int | None:
    """
    Search for *target* by scanning every element in *data*.

    Args:
        data: List of items (does not need to be sorted).
        target: Value to search for.
        key: Function to extract comparison key from items.

    Returns:
        Index of the first matching item, or None if not found.

    Complexity:
        Time  — O(n)
        Space — O(1)
    """
    for i, item in enumerate(data):
        if key(item) == target:
            return i
    return None

# ---------------------------------------------------------------------------
# Benchmarking helpers
# ---------------------------------------------------------------------------

def benchmark_sort(data: list[Any], key: Callable = lambda x: x, repeats: int = 5) -> dict:
    """
    Compare custom merge_sort and insertion_sort vs Python's built-in sorted().

    Args:
        data: List to sort.
        key: Function to extract comparison key.
        repeats: Number of times to repeat timing for averaging.

    Returns:
        Dictionary with average execution times in milliseconds.
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
    """
    Compare custom binary_search and linear_search vs Python's 'in' operator.

    Args:
        data: List of items (will be sorted for binary_search).
        target: Value to search for.
        key: Function to extract comparison key.
        repeats: Number of times to repeat timing for averaging.

    Returns:
        Dictionary with average execution times in milliseconds.
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

