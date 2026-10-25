"""Mo's algorithm for offline batched range queries.

Reorders queries by block decomposition so that the total cost of moving the
window [l, r] across all Q queries is O((N+Q) * sqrt(N)) instead of O(N*Q).

Usage pattern:
    1.  Construct a ``MoRangeQuery`` with the data array.
    2.  Register queries with ``add_query(l, r)`` (half-open, 0 <= l <= r <= N).
    3.  Call ``run(add, remove, get_answer)`` where:
            - ``add(i)``     incorporates ``data[i]`` into the window state.
            - ``remove(i)``  reverts the effect of ``add(i)``.
            - ``get_answer()`` returns the current answer for the window.
    4.  Retrieve results in registration order from ``answers``.

The user owns the mutable state and the three callbacks; this class only
manages query reordering and window movement.

Design decisions
----------------
- ``block = int(N**0.5)``. On r=0 queries (empty range) we still move r to
  make the code uniform, but since l==r the window is empty and add/remove
  are never called.
- Half-open intervals: a query [l, r) with l == r means "no elements",
  a case that arises naturally when transforming inclusive problems.
- Comparator: tie-break ``l`` by descending ``r`` so the right pointer
  sweeps back and forth within a block rather than retracing from the far
  right each time, a standard micro-optimisation.
"""

from __future__ import annotations


class MoRangeQuery:
    """Offline processor that reorders range queries to minimise cursor movement."""

    def __init__(self, data):
        if not isinstance(data, (list, tuple)):
            raise TypeError("data must be a list or tuple")
        self.data = data
        self.n = len(data)
        # int(...) truncates toward zero, which is fine: 0 -> 1, 1 -> 1, 4 -> 2.
        self.block = int(self.n ** 0.5) if self.n > 0 else 1
        if self.block < 1:
            self.block = 1
        self.queries = []
        self.answers = []

    def add_query(self, l, r):
        """Register a half-open range query [l, r).

        Returns the integer index that the answer will occupy in ``answers``.
        Raises ValueError on out-of-bounds indices.
        """
        if l < 0 or r < 0 or l > self.n or r > self.n:
            raise ValueError("query indices out of range")
        if l > r:
            raise ValueError("l must not exceed r")
        idx = len(self.queries)
        self.queries.append((l, r, idx))
        self.answers.append(None)
        return idx

    def _sort_key(self, l, r):
        block = l // self.block
        return (block, -r if block & 1 else r)

    def run(self, add, remove, get_answer):
        """Execute all registered queries in Mo order.

        Parameters
        ----------
        add : callable(int) -> None
            Incorporate ``data[i]`` into the window state.
        remove : callable(int) -> None
            Revert the effect of a prior ``add(i)``.
        get_answer : callable() -> object
            Return the current answer for the window [cur_l, cur_r).
        """
        if len(self.queries) == 0:
            return

        order = sorted(self.queries, key=lambda q: self._sort_key(q[0], q[1]))

        cur_l = 0
        cur_r = 0

        for l, r, original_idx in order:
            # Expand left first so newly added elements are within bounds when
            # right expansion calls add(i).
            while cur_l > l:
                cur_l -= 1
                add(cur_l)
            while cur_r < r:
                add(cur_r)
                cur_r += 1
            while cur_l < l:
                remove(cur_l)
                cur_l += 1
            while cur_r > r:
                cur_r -= 1
                remove(cur_r)

            self.answers[original_idx] = get_answer()
