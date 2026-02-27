## 2024-05-22 - [Vectorization for Mesh Generation]
**Learning:** Python loops for mesh generation (even O(N)) become a bottleneck when N scales (e.g. 50k lines). NumPy vectorization provided ~2.4x speedup.
**Action:** Prefer `np.stack` and array indexing over appending to lists in loops for geometric data generation.

## 2024-05-22 - [Optimized JSON Serialization of NumPy Arrays]
**Learning:** Iterating over NumPy arrays using Python's `list()` constructor for JSON serialization is significantly slower (~4x) than using the optimized C-implementation `.tolist()`.
**Action:** Always use `.tolist()` on NumPy arrays when preparing data for API responses, instead of `list()`.

## 2024-05-23 - [Lazy Loading Heavy Visualization Libraries]
**Learning:** `matplotlib.pyplot` is a heavy dependency that significantly slows down module import time (~1.7s penalty), affecting serverless cold starts.
**Action:** Import `matplotlib.pyplot` inside plotting functions only, especially when the module is used in performance-critical API paths that don't need visualization.

## 2026-02-19 - [Avoid Redundant Mesh Lines in Visualization]
**Learning:** When mapping a high number of requested visualization lines to a lower-resolution underlying simulation grid, integer index mapping can create duplicate entries.
**Action:** Use `np.unique()` on the index array to filter out duplicates before generating the final mesh, reducing payload size and rendering overhead.

## 2026-02-20 - [Avoid Oversampling in Mesh Generation]
**Learning:** Generating a large linspace and then reducing it with `np.unique` when the requested resolution exceeds data resolution is O(N) where N is the requested resolution. It should be O(M) where M is the data resolution.
**Action:** Check if requested resolution >= data resolution and short-circuit to `np.arange(data_len)` to avoid unnecessary allocation and sorting.

## 2026-02-21 - [Optimized Unique Filtering for Sorted Arrays]
**Learning:** `np.unique()` performs an O(N log N) sort even on already sorted arrays. For strictly sorted indices (e.g. from mesh generation), using boolean masking `indices[1:] != indices[:-1]` is O(N) and ~20x faster.
**Action:** Use boolean masking to filter duplicates when data is known to be sorted.

## 2026-02-22 - [GZip Compression for Repetitive Data]
**Learning:** API responses containing geometric mesh data (lists of coordinates) are highly repetitive and compressible. Enabling GZip compression reduced payload size by ~3.8x (9KB -> 2KB for small meshes), significantly improving response times.
**Action:** Enable `GZipMiddleware` in FastAPI for endpoints returning large JSON arrays or geometric data.

## 2026-02-23 - [In-Place Rounding for Payload Reduction]
**Learning:** Returning full-precision floats in JSON API responses significantly inflates payload size (e.g., ~19KB vs ~10KB for 1000 points). Additionally, using `arr.round()` creates a copy of the array. Using `np.round(arr, decimals=N, out=arr)` performs rounding in-place, avoiding memory allocation.
**Action:** Always round floating-point data for visualization APIs (e.g., to 5 decimals) and prefer in-place operations (`out=arr`) to minimize memory overhead.

## 2026-02-24 - [Avoid np.column_stack for Simple Arrays]
**Learning:** `np.column_stack` carries significant overhead for small to medium arrays (~15% slower than pre-allocation for N=100-100k).
**Action:** For simple 2D array construction where dimensions are known, prefer `np.empty((N, M))` followed by direct column assignment over `np.column_stack`.

## 2026-02-25 - [Caching Expensive API Computations]
**Learning:** API endpoints for interactive visualization tools (like nozzle contour or performance mapping) often receive rapid sequential requests with identical parameters from a single user tweaking UI sliders. Recomputing geometric coordinates or chemistry datasets repeatedly adds significant latency.
**Action:** Use `functools.lru_cache` to memoize the core computational functions in FastAPI endpoints. Remember to convert unhashable parameters like lists or dicts to tuples before passing them to the cached function to satisfy Python's hashing requirements.
