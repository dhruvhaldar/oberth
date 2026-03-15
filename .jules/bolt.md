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

## 2026-02-26 - [Pre-serializing Cached FastAPI Responses]
**Learning:** Caching dictionaries with `lru_cache` in FastAPI still incurs significant serialization overhead on every cache hit, as FastAPI must run `jsonable_encoder` and `json.dumps` on the identical dictionary repeatedly. For large arrays (like mesh data), this overhead can be up to ~6x slower than raw string returns.
**Action:** For cached API responses returning large static structures, use `json.dumps(dict, separators=(',', ':'))` inside the cached function and return a FastAPI `Response(content=json_str, media_type="application/json")` directly. This entirely bypasses Pydantic and JSON encoding on cache hits.

## 2026-02-27 - [JavaScript String Concatenation Bottleneck in SVG Rendering]
**Learning:** Iteratively concatenating large strings using `+=` inside a loop (like building complex SVG `d` paths from thousands of coordinate pairs) causes excessive memory reallocation in JavaScript engines. Benchmarks showed O(N) concatenation for 50k segments takes ~108ms.
**Action:** Use `Array.prototype.map()` to generate an array of sub-strings, followed by `.join('')`. This allows the JS engine to allocate the exact memory needed once, executing in ~48ms (~55% faster) for large datasets.

## 2026-03-05 - [NumPy Array Exponentiation Overhead]
**Learning:** Using the `**` operator for squaring NumPy arrays (e.g., `(x - length)**2`) carries significant overhead due to intermediate array allocations and general power function processing, making it measurably slower than direct array multiplication (e.g., `diff * diff`).
**Action:** For simple powers like squaring NumPy arrays, calculate the base array once and use direct multiplication (`arr * arr`) instead of the `**` operator to improve performance and reduce memory allocations.

## 2026-03-05 - [Mathematical Micro-Optimizations via Algebraic Refactoring]
**Learning:** Core calculation loops like `isentropic_area_ratio` and `hohmann_transfer_dv` present significant cumulative overhead due to repeatedly computing constant intermediate divisors (`(gamma + 1) / 2`) or values like `1/a_transfer`, as well as general power operator (`**`) usage instead of simple multiplication. Refactoring them to compute intermediate states (e.g. `g_plus_1 * 0.5`) and replacing `mach**2` with `mach * mach` avoids division and scalar exponentiation overhead entirely, leading to ~40% latency reductions per function call.
**Action:** When working on tight mathematical functions repeatedly called in simulations (especially those returning scalars), inline constant combinations, replace `/ 2` with `* 0.5`, compute inverses upfront (e.g. `1/a_transfer` -> `2.0/(r1+r2)`), and replace the `**` operator with direct scalar multiplication for simple powers like squares.

## 2026-03-05 - [Mathematical Formula Grouping for Python Overhead]
**Learning:** Breaking down tight math formulas like `bartz_equation` into multiple assigned intermediary variables (e.g. `term1`, `term2`) adds significant Python local variable assignment and instruction overhead. Grouping the entire expression into a single returned mathematical product block yielded a ~20% latency reduction.
**Action:** When working on heavily called mathematical equations that produce a single scalar, minimize assignment statements and group the formula into a single, clean return statement to avoid variable assignment overhead.

## 2026-03-06 - [Avoid Intermediate Array Allocations in Index Calculations]
**Learning:** When generating integer indices mapping to an array (e.g. `((np.arange(N) + 1) / N * length).astype(int)`), Python evaluates operations sequentially, allocating new temporary NumPy arrays for the result of `+ 1` and `/ N`. By algebraically rearranging the scalar operations to `np.arange(1, N + 1) * (length / N)`, we avoid allocating the temporary array for `+ 1`, providing a ~3x speedup for this tight visualization logic loop.
**Action:** Refactor operations mapping constant offsets and scales onto `np.arange` to minimize the number of intermediate array allocations. Compute scalar operations (e.g. `length / N`) independently so they are multiplied directly.

## 2026-03-06 - [Pre-computing Common Divisors and Redundant math.sqrt Inputs]
**Learning:** In heavily used scalar math functions like `hohmann_transfer_dv`, redundant calculations such as `mu / r1` inside multiple `math.sqrt` calls cause measurable overhead. Pre-computing scalar multiplications like `mu_r1 = mu / r1` outside the `math.sqrt` and keeping intermediate assignments minimal improves performance by ~15% per call.
**Action:** Pre-compute shared subexpressions passed into `math` module functions or other tight mathematical logic loops to reduce Python division and assignment overhead.

## 2026-03-12 - [O(1) Dictionary Lookup for Propellant Aliases]
**Learning:** Sequential `if/elif` string comparisons for mapping aliases to properties (e.g. `get_propellant`) add linear overhead per call due to Python instruction parsing. Flattening aliases into a single predefined lookup dictionary achieves O(1) time complexity and reduces execution time by ~20%.
**Action:** Use unified dictionary mapping for enum-like alias resolution instead of sequential conditional checks to minimize Python evaluation overhead.

## 2026-03-15 - [NumPy Precomputing Scalar Inverses for Arrays]
**Learning:** When applying conditional scaling to a NumPy array using `np.where(condition, scalar_A, scalar_B)`, performing an array division `array / np.where(...)` involves allocating an intermediate array for the divisor and performing an expensive array-wide division. Pre-computing the scalar inverses (or their squares) and using `array * np.where(...)` eliminates the array division and significantly improves execution time (e.g., in `scan_mixture_ratio`).
**Action:** Always pre-compute scalar inverses for conditional array operations and use multiplication instead of division.

## 2026-03-15 - [Algebraic Refactoring of Float Math]
**Learning:** In tight scalar mathematical functions like `isentropic_area_ratio`, expressions like `(1.0 + x * 0.5) / (y * 0.5)` can be algebraically simplified to `(2.0 + x) / y`. This identical mathematical operation removes an unnecessary float multiplication step, yielding a measurable ~10% latency reduction in Python.
**Action:** Refactor algebraic expressions in performance-critical scalar math to minimize the total number of floating-point operations.

## 2026-03-17 - [Avoid NumPy Type Promotion Overheads]
**Learning:** Generating an integer index array and then multiplying it by a scalar float (e.g., `np.arange(...) * float_factor`) causes NumPy to allocate the integer array, promote the integers to floats in an intermediate array during multiplication, and then evaluate. Initializing the array as floats explicitly via `np.arange(..., dtype=float)` avoids the integer array allocation entirely, speeding up this operation by ~4x (from ~0.43s to ~0.11s for 50k elements).
**Action:** Always provide explicit type kwargs like `dtype=float` to NumPy generation functions (like `np.arange`) when the resulting array will immediately be used in floating point math, to avoid unnecessary array allocations and type promotions.
