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

## 2026-03-24 - [Algebraic Consolidation of Shared Bases]
**Learning:** In heavily called scalar formulas like `bartz_equation`, executing multiple separate exponentiations that contain division operations (e.g. `(mu/Dt)**0.2 * (Dt/Rc)**0.1 * (Dt/D)**1.8`) adds unnecessary float division and Python exponentiation overhead. Algebraically grouping these to precompute a single exponentiation for the shared base (e.g. `Dt**1.7`) eliminates the redundant divisions and yields a measurable ~8% performance gain per call without sacrificing mathematical correctness.
**Action:** When a variable is used repeatedly as a base in different fractional power terms of a tight multiplication loop, algebraically group the terms into a single base raised to the sum of the exponents to eliminate intermediate divisions and reduce exponentiation overhead.

## 2026-03-31 - [In-place Exponentiation and Scaling for Arrays]
**Learning:** In tight mathematical array operations like `scan_mixture_ratio`, computing formulas like `isps = max_isp * np.exp(-inv_width_sq * (diff * diff))` sequentially allocates several intermediate NumPy arrays for each step (squaring, scaling, exponentiation, and final scaling). By pre-calculating scalar multipliers and replacing the expression with in-place operations (`diff *= diff`, `diff *= np.where(...)`, `np.exp(diff, out=diff)`), we can avoid allocating intermediate arrays entirely, resulting in ~3.5x faster execution.
**Action:** For performance-critical functions generating final array results through multiple scalar operations, pre-calculate scalar constants and use in-place assignment operators (`*=`, `+=`, `out=arr` in NumPy functions) on a single working array to eliminate intermediate memory allocations.

## 2026-04-05 - [Boolean Array Math over np.where for Constants]
**Learning:** When assigning two constant scalar values to a NumPy array based on a boolean condition, using `np.where(condition, val1, val2)` introduces significant overhead due to function call resolution and general broadcasting logic. Evaluating it as pure boolean math `(condition) * (val1 - val2) + val2` allows NumPy to compute the result directly using fast C-level array operations, reducing execution time by ~50% for large arrays.
**Action:** Replace `np.where` with boolean array math `(condition) * (val1 - val2) + val2` when mapping two known scalar constants based on a condition to improve execution speed.

## 2026-04-10 - [Combining Mathematical Operations Based on Known Sign Properties]
**Learning:** In calculations summing absolute values of differences (e.g., `abs(v_transfer_p - v1) + abs(v2 - v_transfer_a)` in `hohmann_transfer_dv`), knowing that the two differences always share the same sign (both positive for outward transfers, both negative for inward transfers) allows mathematically combining them into a single `abs(A + B)` call. This removes one `abs()` function call and its evaluation overhead, yielding a ~20% performance improvement. Furthermore, locally aliasing `math.sqrt` avoids repeated global/module attribute lookups in tight logic.
**Action:** When working on tight scalar mathematics where multiple components share matching known signs, consolidate absolute value evaluations or exponents mathematically. Also alias heavily used module functions locally inside tight scalar calculations.

## 2026-04-10 - [Avoid np.linspace for simple linear array generation]
**Learning:** `np.linspace` is relatively slow because it performs significant input validation and logic to handle edge cases accurately, allocating multiple intermediate states. Benchmarks showed that generating a 100-element array using `np.arange(100, dtype=float) * step` is ~4x faster than using `np.linspace(start, end, 100)`.
**Action:** Replace `np.linspace` with pre-computed `np.arange(..., dtype=float)` multiplied by the correct scalar step (and adding the start offset) to minimize the overhead for hot calculations.

## 2026-05-15 - [Direct Array Assignment and Memory Allocation Avoidance]
**Learning:** When filtering indices and mapping values, using `np.concatenate` to combine boolean conditions creates an intermediate boolean array and allocates a new concatenated array. Pre-allocating an `np.empty` mask array and using slice assignments avoids these overheads. Additionally, calculating scalar multipliers before index generation and assigning mapped arrays directly (e.g., `mesh[:, 1, 0] = x[indices]`) rather than instantiating intermediate variables like `end_xs` significantly improves execution time by ~40% for large arrays.
**Action:** Use pre-allocated `np.empty` boolean masks for filtering arrays when conditions are complex, and map values directly into their final array slice positions to minimize intermediate array allocations. Extract inline scalar calculations that form elements of index math.

## 2026-05-20 - [Avoid Intermediate Array Allocations with Slice References]
**Learning:** When performing operations on a sequence to generate coordinates for a multi-dimensional array, computing the values into an intermediate array (e.g., `diff = x - length`) and then assigning that array to a slice of the pre-allocated result array (`contour_array[:, 1] = diff`) performs an unnecessary intermediate allocation. By referencing the slice directly (`y = contour_array[:, 1]`) and using in-place operations with `out` parameters (e.g., `np.subtract(x, length, out=y)`), we can avoid the intermediate array allocation entirely, speeding up execution and reducing memory usage.
**Action:** Always prefer to reference slices of pre-allocated target arrays and compute values directly into them using `out` parameters or in-place operators, rather than generating intermediate arrays and copying.

## 2026-05-25 - [Avoid D3 Scale Function Overhead and Intermediate Path Allocations]
**Learning:** When generating paths in D3 for visually symmetric elements, making redundant calls to a linear scale function like `yScale(-y)` inside a tight map loop of thousands of items introduces measurable overhead due to the scale's internal interpolation and clamping logic. Because the scale domain is symmetric around 0 (`[-domain, +domain]`), we can exploit linearity mathematically: `yScale(-y) = 2 * yScale(0) - yScale(y)`. Pre-computing `const y0 = yScale(0)` outside the loop entirely eliminates the function call overhead. Furthermore, mapping an entire source dataset to invert coordinates (`data.map(d => [d[0], -d[1]])`) prior to rendering creates O(N) intermediate array allocations; using a dedicated `d3.line` generator with an inverted accessor (`.y(d => yScale(-d[1]))`) computes the path directly.
**Action:** Exploit mathematical symmetry to avoid redundant D3 scale function evaluations within tight coordinate generation loops. Prevent intermediate array allocations in JS by implementing dedicated path generators with transformed accessors instead of pre-mapping data.

## 2026-06-10 - [Avoid Unnecessary Float Multiplications by Refactoring]
**Learning:** In heavily called mathematical loops like `hohmann_transfer_dv` or `isentropic_area_ratio`, refactoring equations mathematically to reduce operations (such as calculating `mu_a = mu / (r1 + r2)` instead of `(mu * 2.0) / (r1 + r2)` and multiplying by 2 later, or replacing `(1.0 / x) * (y)` with `(y) / x`) reduces the number of instructions executed by Python and can net an ~7-8% performance improvement without breaking exactness.
**Action:** Always scan pure mathematical Python formulas for simple associative or distributive properties that can remove a float multiplication or division.

## 2026-06-10 - [Precompute Mathematical Constants in Classes]
**Learning:** `Stage.delta_v()` recalculates the effective exhaust velocity `ve = isp * g0` on every call, taking a measurable toll when iterating over flight profiles or staging checks. By simply precomputing `self._ve` inside the `__init__` constructor, `delta_v()` executes ~16% faster because it avoids an unnecessary multiplication every loop iteration.
**Action:** When working on classes mapping physical constants (like mission staging), precalculate unchanging products and constants inside the `__init__` constructor instead of computing them inside frequently called methods.

## 2026-06-15 - [Skip Array Deduplication When Mathematically Impossible]
**Learning:** In `oberth/nozzle.py`, `MethodOfCharacteristics.solve()` was using boolean filtering (which allocates an intermediate boolean array and concatenates elements) to remove duplicates from an index array generated by `(np.arange(...) * factor).astype(int)`. However, when `factor > 1.0`, consecutive elements differ by more than `1.0` before truncation and are mathematically guaranteed to never round to the same integer. Removing the redundant masking logic improved mesh generation speed by ~35% without altering behavior.
**Action:** When mapping indices from a float array to an integer array via multiplication by a step factor, check if the factor is mathematically guaranteed to be > 1.0. If so, O(N) duplicate filtering logic can be safely removed to eliminate intermediate allocations.
