#!/usr/bin/env python3
"""
Validate & regenerate test cases for algotimesummer2026 Week 10 questions.

For each of the 6 questions this script:
  1. Defines a reference solution.
  2. Sanity-checks the reference solution against the sample cases from the
     problem descriptions (asserts).
  3. Defines a curated list of >=10 test inputs.
  4. Computes the expected output for each input using the reference solution.
  5. Writes those {id, input, output} test cases back into the question JSON.

Run:
    python3 scripts/validate_week10.py
"""

from __future__ import annotations

import bisect
import json
from pathlib import Path
from typing import Any, Callable, List, Tuple


ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "public" / "questions"


# ---------------------------------------------------------------------------
# 1) Limit Occurrences in Sorted Array
# ---------------------------------------------------------------------------
def limit_occurrences(nums: List[int], k: int) -> List[int]:
    out: List[int] = []
    count: dict[int, int] = {}
    for x in nums:
        c = count.get(x, 0)
        if c < k:
            out.append(x)
            count[x] = c + 1
    return out


LIMIT_TESTS = [
    {"nums": [1, 1, 1, 2, 2, 3], "k": 2},
    {"nums": [1, 2, 3], "k": 1},
    {"nums": [1, 1, 1, 1], "k": 1},
    {"nums": [1, 1, 1, 1], "k": 4},
    {"nums": [1, 1, 1, 1], "k": 3},
    {"nums": [5], "k": 1},
    {"nums": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], "k": 2},
    {"nums": [7, 7, 7, 8, 8, 9, 10, 10, 10, 10], "k": 3},
    {"nums": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5], "k": 2},
    {"nums": [100, 100, 100, 100, 100], "k": 2},
    {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "k": 5},
    {"nums": [1, 1, 1, 2, 3, 4, 5, 5, 5, 6, 6, 7], "k": 2},
]


# ---------------------------------------------------------------------------
# 2) N-ary Tree Preorder Traversal
# ---------------------------------------------------------------------------
#
# LeetCode serializes an N-ary tree in level order using `null` to separate
# groups of children. Interpretation of [1, null, 3, 2, 4, null, 5, 6]:
#     root = 1
#     null  -> end of root's own "level" descriptor (LeetCode convention)
#     3,2,4 -> root's children
#     null  -> end of node-3's children
#     5,6   -> node-2's children  (mapped to next parent whose children we read)
# The canonical parser walks a BFS queue and consumes runs of values between
# nulls as the front-of-queue node's children.
class _Node:
    __slots__ = ("val", "children")

    def __init__(self, val: int) -> None:
        self.val = val
        self.children: List["_Node"] = []


def _build_nary(data: List[Any]) -> _Node | None:
    if not data:
        return None
    root = _Node(data[0])
    queue: List[_Node] = [root]
    i = 2  # skip data[0] (root val) and data[1] (null separator)
    while i < len(data):
        parent = queue.pop(0)
        while i < len(data) and data[i] is not None:
            child = _Node(data[i])
            parent.children.append(child)
            queue.append(child)
            i += 1
        i += 1  # skip the null delimiter
    return root


def preorder_traversal(root_ser: List[Any]) -> List[int]:
    root = _build_nary(root_ser)
    out: List[int] = []

    def dfs(node: _Node | None) -> None:
        if node is None:
            return
        out.append(node.val)
        for c in node.children:
            dfs(c)

    dfs(root)
    return out


PREORDER_TESTS = [
    {"root": [1, None, 3, 2, 4, None, 5, 6]},
    {
        "root": [
            1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10,
            None, None, 11, None, 12, None, 13, None, None, 14,
        ]
    },
    {"root": []},
    {"root": [1]},
    {"root": [1, None, 2, 3, 4]},
    {"root": [1, None, 2, None, 3, None, 4, None, 5]},  # left-skewed chain
    {"root": [10, None, 20, 30]},
    {"root": [5, None, 3, 6, 2, None, 1, 4]},
    {"root": [1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8]},
    {"root": [42, None, 1, 2, 3, 4, 5]},
    {"root": [7, None, 8, 9, 10, None, 11, None, 12, None, 13]},
    {"root": [0, None, 1, 2, None, 3, 4, None, 5]},
]


# ---------------------------------------------------------------------------
# 3) Steps to Make Array Non-decreasing
# ---------------------------------------------------------------------------
def total_steps(nums: List[int]) -> int:
    # Monotonic decreasing stack. For each element x, elements <= x that are
    # currently on top get "absorbed"; the surviving x's dying step is
    # max(popped steps) + 1 (or 0 if the stack is empty when we settle).
    stack: List[Tuple[int, int]] = []  # (value, step_when_removed)
    ans = 0
    for x in nums:
        max_step = 0
        while stack and stack[-1][0] <= x:
            max_step = max(max_step, stack.pop()[1])
        step = max_step + 1 if stack else 0
        ans = max(ans, step)
        stack.append((x, step))
    return ans


def total_steps_brute(nums: List[int]) -> int:
    """Simulator used only for cross-validation on small inputs."""
    cur = list(nums)
    steps = 0
    while True:
        keep = [cur[0]] if cur else []
        for i in range(1, len(cur)):
            if cur[i - 1] <= cur[i]:
                keep.append(cur[i])
        if len(keep) == len(cur):
            return steps
        cur = keep
        steps += 1


STEPS_TESTS = [
    {"nums": [5, 3, 4, 4, 7, 3, 6, 11, 8, 5, 11]},
    {"nums": [4, 5, 7, 7, 13]},
    {"nums": [1]},
    {"nums": [10, 1, 2, 3, 4, 5]},
    {"nums": [5, 4, 3, 2, 1]},
    {"nums": [1, 2, 3, 4, 5]},
    {"nums": [7, 14, 4, 14, 13, 2, 6, 13]},
    {"nums": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]},
    {"nums": [1, 1, 1, 1]},
    {"nums": [100, 50, 60, 40, 80, 20, 70]},
    {"nums": [3, 3, 3, 2, 2, 2, 1, 1, 1, 4]},
    {"nums": [2, 1, 3, 1, 4, 1, 5, 1]},
]


# ---------------------------------------------------------------------------
# 4) Maximum Number of Distinct Elements After Operations
# ---------------------------------------------------------------------------
def max_distinct_elements(nums: List[int], k: int) -> int:
    # Sort, then greedily place each value at the smallest slot >= x - k that
    # is also > previously placed slot. If that slot is outside [x-k, x+k],
    # this element must collide with the previous placed value (no gain).
    prev = float("-inf")
    count = 0
    for x in sorted(nums):
        target = max(prev + 1, x - k)
        if target <= x + k:
            count += 1
            prev = target
    return count


MAX_DISTINCT_TESTS = [
    {"nums": [1, 2, 2, 3, 3, 4], "k": 2},
    {"nums": [4, 4, 4, 4], "k": 1},
    {"nums": [1], "k": 0},
    {"nums": [1, 1, 1, 1, 1], "k": 0},
    {"nums": [1, 1, 1, 1, 1], "k": 2},
    {"nums": [1, 2, 3, 4, 5], "k": 0},
    {"nums": [5, 5, 5, 5, 5, 5, 5], "k": 3},
    {"nums": [10, 20, 30, 40], "k": 5},
    {"nums": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5], "k": 1},
    {"nums": [100, 100, 100], "k": 1000000000},
    {"nums": [7, 7, 7, 7, 7, 7, 7, 7, 7, 7], "k": 5},
    {"nums": [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], "k": 2},
]


# ---------------------------------------------------------------------------
# 5) Maximum Height by Stacking Cuboids
# ---------------------------------------------------------------------------
def max_height_cuboids(cuboids: List[List[int]]) -> int:
    # Rotating a cuboid freely lets us WLOG sort each cuboid's dims ascending
    # (proof: for any stackable pair, orienting both with dims ascending
    # preserves stackability). Then LIS over 3 dims maximizing sum of heights.
    boxes = [sorted(c) for c in cuboids]
    boxes.sort()
    n = len(boxes)
    dp = [b[2] for b in boxes]
    for i in range(n):
        for j in range(i):
            if (
                boxes[j][0] <= boxes[i][0]
                and boxes[j][1] <= boxes[i][1]
                and boxes[j][2] <= boxes[i][2]
            ):
                if dp[j] + boxes[i][2] > dp[i]:
                    dp[i] = dp[j] + boxes[i][2]
    return max(dp) if dp else 0


CUBOID_TESTS = [
    {"cuboids": [[50, 45, 20], [95, 37, 53], [45, 23, 12]]},
    {"cuboids": [[38, 25, 45], [76, 35, 3]]},
    {
        "cuboids": [
            [7, 11, 17], [7, 17, 11], [11, 7, 17], [11, 17, 7],
            [17, 7, 11], [17, 11, 7],
        ]
    },
    {"cuboids": [[1, 1, 1]]},
    {"cuboids": [[100, 100, 100]]},
    {"cuboids": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
    {"cuboids": [[10, 20, 30], [10, 20, 30], [10, 20, 30]]},
    {"cuboids": [[5, 5, 5], [4, 4, 4], [3, 3, 3], [2, 2, 2], [1, 1, 1]]},
    {"cuboids": [[100, 1, 1], [1, 100, 1], [1, 1, 100]]},
    {"cuboids": [[2, 3, 5], [3, 5, 2], [5, 2, 3]]},
    {"cuboids": [[50, 50, 50], [40, 45, 60], [30, 40, 55]]},
    {"cuboids": [[10, 10, 10], [20, 20, 20], [30, 30, 30], [40, 40, 40]]},
]


# ---------------------------------------------------------------------------
# 6) Shortest Matching Substring (pattern has exactly two '*')
# ---------------------------------------------------------------------------
def shortest_matching_substring(s: str, p: str) -> int:
    parts = p.split("*")
    assert len(parts) == 3, "pattern must contain exactly two '*'"
    a, b, c = parts
    n = len(s)
    la, lb, lc = len(a), len(b), len(c)

    def kmp_all(pat: str) -> List[int]:
        # Empty pattern is treated as matching at every position 0..n.
        if not pat:
            return list(range(n + 1))
        m = len(pat)
        fail = [0] * m
        k = 0
        for i in range(1, m):
            while k > 0 and pat[k] != pat[i]:
                k = fail[k - 1]
            if pat[k] == pat[i]:
                k += 1
            fail[i] = k
        occ: List[int] = []
        j = 0
        for i in range(n):
            while j > 0 and pat[j] != s[i]:
                j = fail[j - 1]
            if pat[j] == s[i]:
                j += 1
            if j == m:
                occ.append(i - m + 1)
                j = fail[j - 1]
        return occ

    A = kmp_all(a)
    B = kmp_all(b)
    C = kmp_all(c)
    if not A or not B or not C:
        return -1

    best = -1
    for i in A:
        # first B occurrence that starts at or after i + la
        idx_b = bisect.bisect_left(B, i + la)
        if idx_b == len(B):
            continue
        j = B[idx_b]
        # first C occurrence at or after j + lb
        idx_c = bisect.bisect_left(C, j + lb)
        if idx_c == len(C):
            continue
        k = C[idx_c]
        end = k + lc  # exclusive
        if end > n and lc > 0:
            continue
        length = end - i
        if length < 0:
            continue
        if best == -1 or length < best:
            best = length
    return best


SHORTEST_TESTS = [
    {"s": "abaacbaecebce", "p": "ba*c*ce"},
    {"s": "baccbaadbc", "p": "cc*baa*adb"},
    {"s": "a", "p": "**"},
    {"s": "madlogic", "p": "*adlogi*"},
    {"s": "abcabcabc", "p": "a*b*c"},
    {"s": "helloworld", "p": "he*wo*ld"},
    {"s": "aaaaaaaa", "p": "a*a*a"},
    {"s": "banana", "p": "b*n*a"},
    {"s": "abcdefg", "p": "*cd*fg"},
    {"s": "mississippi", "p": "m*ss*pi"},
    {"s": "abcdef", "p": "z*z*z"},
    {"s": "algolounge", "p": "*lo*ge"},
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def load_json(name: str) -> dict:
    with open(QDIR / f"{name}.json", "r") as f:
        return json.load(f)


def save_json(name: str, data: dict) -> None:
    with open(QDIR / f"{name}.json", "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def build_cases(
    inputs: List[dict],
    solver: Callable[..., Any],
    unpack: Callable[[dict], tuple],
) -> List[dict]:
    cases: List[dict] = []
    for i, inp in enumerate(inputs, start=1):
        args = unpack(inp)
        out = solver(*args)
        cases.append({"id": i, "input": inp, "output": out})
    return cases


def sanity_checks() -> None:
    # 1) limit occurrences
    assert limit_occurrences([1, 1, 1, 2, 2, 3], 2) == [1, 1, 2, 2, 3]
    assert limit_occurrences([1, 2, 3], 1) == [1, 2, 3]

    # 2) n-ary preorder
    assert preorder_traversal([1, None, 3, 2, 4, None, 5, 6]) == [1, 3, 5, 6, 2, 4]
    ex2 = [
        1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10,
        None, None, 11, None, 12, None, 13, None, None, 14,
    ]
    assert preorder_traversal(ex2) == [1, 2, 3, 6, 7, 11, 14, 4, 8, 12, 5, 9, 13, 10]
    assert preorder_traversal([]) == []
    assert preorder_traversal([1]) == [1]

    # 3) total steps: cross-check optimised vs brute
    assert total_steps([5, 3, 4, 4, 7, 3, 6, 11, 8, 5, 11]) == 3
    assert total_steps([4, 5, 7, 7, 13]) == 0
    for case in STEPS_TESTS:
        nums = case["nums"]
        if len(nums) <= 20:
            assert total_steps(nums) == total_steps_brute(nums), nums

    # 4) max distinct
    assert max_distinct_elements([1, 2, 2, 3, 3, 4], 2) == 6
    assert max_distinct_elements([4, 4, 4, 4], 1) == 3

    # 5) max height cuboids
    assert max_height_cuboids([[50, 45, 20], [95, 37, 53], [45, 23, 12]]) == 190
    assert max_height_cuboids([[38, 25, 45], [76, 35, 3]]) == 76
    assert max_height_cuboids([
        [7, 11, 17], [7, 17, 11], [11, 7, 17], [11, 17, 7],
        [17, 7, 11], [17, 11, 7],
    ]) == 102

    # 6) shortest matching substring
    assert shortest_matching_substring("abaacbaecebce", "ba*c*ce") == 8
    assert shortest_matching_substring("baccbaadbc", "cc*baa*adb") == -1
    assert shortest_matching_substring("a", "**") == 0
    assert shortest_matching_substring("madlogic", "*adlogi*") == 6

    print("[sanity] all reference solutions match sample outputs")


PROBLEMS = [
    (
        "limit-occurrences-in-sorted-array",
        LIMIT_TESTS,
        limit_occurrences,
        lambda t: (list(t["nums"]), t["k"]),
    ),
    (
        "n-ary-tree-preorder-traversal",
        PREORDER_TESTS,
        preorder_traversal,
        lambda t: (list(t["root"]),),
    ),
    (
        "steps-to-make-array-non-decreasing",
        STEPS_TESTS,
        total_steps,
        lambda t: (list(t["nums"]),),
    ),
    (
        "maximum-number-of-distinct-elements-after-operations",
        MAX_DISTINCT_TESTS,
        max_distinct_elements,
        lambda t: (list(t["nums"]), t["k"]),
    ),
    (
        "maximum-height-by-stacking-cuboids",
        CUBOID_TESTS,
        max_height_cuboids,
        lambda t: ([list(c) for c in t["cuboids"]],),
    ),
    (
        "shortest-matching-substring",
        SHORTEST_TESTS,
        shortest_matching_substring,
        lambda t: (t["s"], t["p"]),
    ),
]


def main() -> None:
    sanity_checks()

    for name, inputs, solver, unpack in PROBLEMS:
        assert len(inputs) >= 10, f"{name} has only {len(inputs)} inputs, need 10+"
        cases = build_cases(inputs, solver, unpack)
        data = load_json(name)
        data["test_cases"] = cases
        save_json(name, data)
        preview = ", ".join(str(c["output"])[:40] for c in cases[:3])
        print(f"[wrote] {name}: {len(cases)} cases  (first outputs: {preview}, ...)")

    print("[done] all week10 questions updated")


if __name__ == "__main__":
    main()
