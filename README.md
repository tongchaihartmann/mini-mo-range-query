# mini-mo-range-query

Offline processor for batched range queries that reorders queries by block decomposition to achieve O((N+Q)\u221aN) total cursor movement.

```python
from mini_mo_range_query import MoRangeQuery

data = [1, 1, 2, 3, 2, 1, 4]
mo = MoRangeQuery(data)
mo.add_query(0, 7)   # full range
mo.add_query(2, 5)   # [2, 3, 2] -> 2 distinct

# You own the mutable state and the three callbacks.
counts = {}
def add(i):
    v = data[i]
    counts[v] = counts.get(v, 0) + 1
def remove(i):
    v = data[i]
    counts[v] -= 1
    if counts[v] == 0:
        del counts[v]
def get_answer():
    return len(counts)

mo.run(add, remove, get_answer)
print(mo.answers)  # -> [4, 2]
```

## Why this exists

Given Q queries over an array of size N, a naive cursor that expands/contracts one element at a time costs O(N) per query in the worst case, so O(N\u00d7Q) total. Mo's algorithm partitions queries by the block of their left endpoint and processes them in an order that keeps adjacent left endpoints within the same \u221aN-sized block. The left pointer then moves O(Q\u221aQ) times and the right pointer O(N\u221aN) times across the whole batch, yielding O((N+Q)\u221aN) total work.

The trade-off: you must know all queries upfront (this is an offline algorithm), and you must express your state updates as reversible `add`/`remove` operations. In exchange you avoid segment trees, persistent structures, or per-query scans. For simple problems that already admit a logarithmic online solution, Mo is not the right tool; it earns its keep when the state is expensive to recompute from scratch but cheap to update by one element.

## Queries are half-open

`add_query(l, r)` covers indices `[l, r)` \u2014 `data[l]` through `data[r-1]`. A query with `l == r` is an empty range: the cursor moves to `[l, l)` but `add`/`remove` are never called for it, so `get_answer` should return whatever the user-defined state considers the empty-window answer (e.g., `0` for a distinct-count). If you have inclusive queries `[l, r]`, convert them to `add_query(l, r + 1)`.
