## 2024-05-22 - [Vectorization for Mesh Generation]
**Learning:** Python loops for mesh generation (even O(N)) become a bottleneck when N scales (e.g. 50k lines). NumPy vectorization provided ~2.4x speedup.
**Action:** Prefer `np.stack` and array indexing over appending to lists in loops for geometric data generation.

## 2024-05-22 - [Optimized JSON Serialization of NumPy Arrays]
**Learning:** Iterating over NumPy arrays using Python's `list()` constructor for JSON serialization is significantly slower (~4x) than using the optimized C-implementation `.tolist()`.
**Action:** Always use `.tolist()` on NumPy arrays when preparing data for API responses, instead of `list()`.
