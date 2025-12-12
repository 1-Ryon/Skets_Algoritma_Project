"""
Implementasi semua algoritma yang diminta:
- Linear Search
- Binary Search
- Sequential Search
- Bubble Sort
- Insertion Sort
- Selection Sort
- Merge Sort
- Shell Sort
- Time Complexity analysis
"""

from typing import List, Any, Optional
import time
from functools import wraps

# ========== DECORATOR UNTUK MEASURE TIME COMPLEXITY ==========
def measure_time(func):
    """Decorator untuk mengukur waktu eksekusi"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Tambahkan info waktu ke result jika berupa dict
        if isinstance(result, dict):
            result['execution_time_ms'] = execution_time * 1000
            result['time_complexity'] = func.__doc__.split('\n')[0] if func.__doc__ else "Unknown"
        
        print(f"[{func.__name__}] Execution time: {execution_time*1000:.2f} ms")
        return result
    return wrapper

# ========== SEARCHING ALGORITHMS ==========

@measure_time
def linear_search(arr: List[dict], key: str, value: Any) -> Optional[dict]:
    """
    Linear Search - Time Complexity: O(n)
    Mencari elemen dalam array secara sequential
    """
    for item in arr:
        if item.get(key) == value:
            return item
    return None

@measure_time
def binary_search(arr: List[dict], key: str, value: Any) -> Optional[dict]:
    """
    Binary Search - Time Complexity: O(log n)
    REQUIREMENT: Array harus sudah terurut berdasarkan key
    """
    # Sort dulu berdasarkan key
    sorted_arr = sorted(arr, key=lambda x: x.get(key, ""))
    
    low, high = 0, len(sorted_arr) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_arr[mid].get(key)
        
        if mid_val == value:
            return sorted_arr[mid]
        elif mid_val < value:
            low = mid + 1
        else:
            high = mid - 1
    
    return None

@measure_time  
def sequential_search_mahasiswa(arr: List[dict], keyword: str) -> List[dict]:
    """
    Sequential Search untuk mahasiswa - Time Complexity: O(n*m)
    Mencari berdasarkan nama atau NIM
    """
    results = []
    keyword_lower = keyword.lower()
    
    for mhs in arr:
        if (keyword_lower in mhs.get('nama', '').lower() or 
            keyword_lower in mhs.get('nim', '').lower() or
            keyword_lower in mhs.get('jurusan', '').lower()):
            results.append(mhs)
    
    return results

# ========== SORTING ALGORITHMS ==========

@measure_time
def bubble_sort(arr: List[dict], key: str, ascending: bool = True) -> List[dict]:
    """
    Bubble Sort - Time Complexity: O(n²)
    Stable sorting algorithm
    """
    n = len(arr)
    arr_copy = arr.copy()
    
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # Compare berdasarkan key
            val1 = arr_copy[j].get(key, 0)
            val2 = arr_copy[j + 1].get(key, 0)
            
            if ascending:
                condition = val1 > val2
            else:
                condition = val1 < val2
            
            if condition:
                arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                swapped = True
        
        if not swapped:
            break
    
    return arr_copy

@measure_time
def insertion_sort(arr: List[dict], key: str, ascending: bool = True) -> List[dict]:
    """
    Insertion Sort - Time Complexity: O(n²)
    Efisien untuk data yang hampir terurut
    """
    arr_copy = arr.copy()
    
    for i in range(1, len(arr_copy)):
        current = arr_copy[i]
        j = i - 1
        
        while j >= 0:
            val_current = current.get(key, 0)
            val_j = arr_copy[j].get(key, 0)
            
            if ascending:
                condition = val_current < val_j
            else:
                condition = val_current > val_j
            
            if condition:
                arr_copy[j + 1] = arr_copy[j]
                j -= 1
            else:
                break
        
        arr_copy[j + 1] = current
    
    return arr_copy

@measure_time
def selection_sort(arr: List[dict], key: str, ascending: bool = True) -> List[dict]:
    """
    Selection Sort - Time Complexity: O(n²)
    Selalu O(n²) bahkan untuk data yang sudah terurut
    """
    arr_copy = arr.copy()
    n = len(arr_copy)
    
    for i in range(n):
        # Find min/max element
        target_idx = i
        for j in range(i + 1, n):
            val_target = arr_copy[target_idx].get(key, 0)
            val_j = arr_copy[j].get(key, 0)
            
            if ascending:
                condition = val_j < val_target
            else:
                condition = val_j > val_target
            
            if condition:
                target_idx = j
        
        # Swap
        arr_copy[i], arr_copy[target_idx] = arr_copy[target_idx], arr_copy[i]
    
    return arr_copy

@measure_time
def merge_sort(arr: List[dict], key: str, ascending: bool = True) -> List[dict]:
    """
    Merge Sort - Time Complexity: O(n log n)
    Divide and conquer algorithm
    """
    def merge(left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            left_val = left[i].get(key, 0)
            right_val = right[j].get(key, 0)
            
            if ascending:
                condition = left_val <= right_val
            else:
                condition = left_val >= right_val
            
            if condition:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    if len(arr) <= 1:
        return arr.copy()
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, ascending)
    right = merge_sort(arr[mid:], key, ascending)
    
    return merge(left, right)

@measure_time
def shell_sort(arr: List[dict], key: str, ascending: bool = True) -> List[dict]:
    """
    Shell Sort - Time Complexity: O(n log² n) average
    Improved insertion sort dengan gap sequence
    """
    arr_copy = arr.copy()
    n = len(arr_copy)
    
    # Gap sequence (Knuth sequence)
    gap = 1
    while gap < n // 3:
        gap = 3 * gap + 1
    
    while gap >= 1:
        for i in range(gap, n):
            temp = arr_copy[i]
            j = i
            
            while j >= gap:
                val_temp = temp.get(key, 0)
                val_j_gap = arr_copy[j - gap].get(key, 0)
                
                if ascending:
                    condition = val_temp < val_j_gap
                else:
                    condition = val_temp > val_j_gap
                
                if condition:
                    arr_copy[j] = arr_copy[j - gap]
                    j -= gap
                else:
                    break
            
            arr_copy[j] = temp
        
        gap //= 3
    
    return arr_copy

# ========== ALGORITHM MANAGER ==========
class AlgorithmManager:
    """Manager untuk memilih dan menjalankan algoritma"""
    
    SORT_ALGORITHMS = {
        'bubble': bubble_sort,
        'insertion': insertion_sort,
        'selection': selection_sort,
        'merge': merge_sort,
        'shell': shell_sort
    }
    
    SEARCH_ALGORITHMS = {
        'linear': linear_search,
        'binary': binary_search,
        'sequential': sequential_search_mahasiswa
    }
    
    @staticmethod
    def sort_data(data: List[dict], algorithm: str, 
                 key: str = 'nama', ascending: bool = True) -> dict:
        """
        Jalankan algoritma sorting yang dipilih
        Returns: {'sorted_data': [...], 'algorithm': '...', 'time_ms': ...}
        """
        if algorithm not in AlgorithmManager.SORT_ALGORITHMS:
            raise ValueError(f"Algorithm {algorithm} not supported")
        
        sort_func = AlgorithmManager.SORT_ALGORITHMS[algorithm]
        result = sort_func(data, key, ascending)
        
        # Extract execution time dari decorator
        return {
            'sorted_data': result,
            'algorithm': algorithm,
            'key': key,
            'ascending': ascending
        }
    
    @staticmethod
    def search_data(data: List[dict], algorithm: str, 
                   search_key: str = None, search_value: Any = None) -> dict:
        """
        Jalankan algoritma searching yang dipilih
        """
        if algorithm not in AlgorithmManager.SEARCH_ALGORITHMS:
            raise ValueError(f"Algorithm {algorithm} not supported")
        
        search_func = AlgorithmManager.SEARCH_ALGORITHMS[algorithm]
        
        if algorithm == 'sequential':
            result = search_func(data, search_value)
            return {
                'results': result,
                'algorithm': algorithm,
                'keyword': search_value,
                'count': len(result)
            }
        else:
            result = search_func(data, search_key, search_value)
            return {
                'result': result,
                'algorithm': algorithm,
                'key': search_key,
                'value': search_value,
                'found': result is not None
            }
    
    @staticmethod
    def get_time_complexity_info():
        """Return informasi time complexity semua algoritma"""
        return {
            'sorting': {
                'bubble': 'O(n²) - Best: O(n), Worst: O(n²)',
                'insertion': 'O(n²) - Best: O(n), Worst: O(n²)',
                'selection': 'O(n²) - Best/Worst: O(n²)',
                'merge': 'O(n log n) - Best/Worst: O(n log n)',
                'shell': 'O(n log² n) average - Best: O(n log n), Worst: O(n²)'
            },
            'searching': {
                'linear': 'O(n)',
                'binary': 'O(log n) - Requirement: sorted array',
                'sequential': 'O(n*m) - m = panjang keyword'
            }
        }

# Global instance
algo_manager = AlgorithmManager()