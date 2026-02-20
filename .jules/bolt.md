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
