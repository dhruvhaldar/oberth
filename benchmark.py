import timeit
import numpy as np

_X_NORMALIZED = np.arange(100, dtype=float) / 99.0
_NORMALIZED_PARABOLA = (_X_NORMALIZED - 1.0)**2

def old_way():
    rt = 1.0
    re = 5.0
    length = 10.0
    x = _X_NORMALIZED * length
    y = np.empty(100)
    A = (rt - re) / (length * length)
    np.subtract(x, length, out=y)
    y *= y
    y *= A
    y += re
    return y

def new_way():
    rt = 1.0
    re = 5.0
    y = np.empty(100)
    np.multiply(_NORMALIZED_PARABOLA, rt - re, out=y)
    y += re
    return y

# Verify correctness
np.testing.assert_allclose(old_way(), new_way())

n = 100000
t_old = timeit.timeit(old_way, number=n)
t_new = timeit.timeit(new_way, number=n)

print(f"Old way: {t_old:.4f} s")
print(f"New way: {t_new:.4f} s")
print(f"Improvement: {((t_old - t_new) / t_old) * 100:.1f}%")
