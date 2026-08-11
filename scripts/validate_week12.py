#!/usr/bin/env python3
"""
Validate & regenerate test cases for algotimesummer2026 Week 12 questions.

For each of the 6 questions this script:
  1. Defines a reference solution.
  2. Sanity-checks the reference solution against the sample cases from the
     problem descriptions (asserts).
  3. Defines a curated list of >=10 test inputs.
  4. Computes the expected output for each input using the reference solution.
  5. Writes the solution_code/solution_text (where empty) and the
     {id, input, output} test cases back into the question JSON.

Run:
    python3 scripts/validate_week12.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, List, Tuple


ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "public" / "questions"


# ---------------------------------------------------------------------------
# 1) Roman to Integer
# ---------------------------------------------------------------------------
def roman_to_int(s: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    n = len(s)
    for i in range(n):
        if i + 1 < n and values[s[i]] < values[s[i + 1]]:
            total -= values[s[i]]
        else:
            total += values[s[i]]
    return total


ROMAN_TESTS = [
    {"s": "III"},
    {"s": "IV"},
    {"s": "IX"},
    {"s": "LVIII"},
    {"s": "MCMXCIV"},
    {"s": "XL"},
    {"s": "XC"},
    {"s": "CD"},
    {"s": "CM"},
    {"s": "MMMDCCXLIX"},
]


ROMAN_SOLUTION_CODE = (
    "def romanToInt(s):\n"
    "    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50,\n"
    "              'C': 100, 'D': 500, 'M': 1000}\n"
    "    total = 0\n"
    "    for i in range(len(s)):\n"
    "        if i + 1 < len(s) and values[s[i]] < values[s[i + 1]]:\n"
    "            total -= values[s[i]]\n"
    "        else:\n"
    "            total += values[s[i]]\n"
    "    return total"
)

ROMAN_SOLUTION_TEXT = (
    "<h3>Roman to Integer</h3>"
    "<p><strong>Algorithm:</strong></p>"
    "<ol>"
    "<li>Build a map of each Roman symbol to its integer value</li>"
    "<li>Iterate through the string from left to right</li>"
    "<li>If the current symbol is less than the next symbol, subtract it (subtraction rule)</li>"
    "<li>Otherwise, add it to the total</li>"
    "</ol>"
    "<p><strong>Time Complexity:</strong> O(n) where n is the length of the string</p>"
    "<p><strong>Space Complexity:</strong> O(1) since the symbol map has a fixed size of 7 entries</p>"
    "<p><strong>Key Insights:</strong></p>"
    "<ul>"
    "<li>The subtraction rule only occurs when a smaller value appears before a larger one</li>"
    "<li>Comparing each symbol with the one that follows it handles all six subtraction cases automatically</li>"
    "</ul>"
)


# ---------------------------------------------------------------------------
# 2) Number of Equivalent Domino Pairs
# ---------------------------------------------------------------------------
def num_equiv_domino_pairs(dominoes: List[List[int]]) -> int:
    count: dict[Tuple[int, int], int] = {}
    pairs = 0
    for a, b in dominoes:
        key = (min(a, b), max(a, b))
        pairs += count.get(key, 0)
        count[key] = count.get(key, 0) + 1
    return pairs


DOMINO_TESTS = [
    {"dominoes": [[1, 2], [2, 1], [3, 4], [5, 6]]},
    {"dominoes": [[1, 2], [1, 2], [1, 1], [1, 2], [2, 2]]},
    {"dominoes": [[1, 2]]},
    {"dominoes": [[1, 1], [1, 1], [1, 1]]},
    {"dominoes": [[1, 2], [2, 1]]},
    {"dominoes": [[3, 5], [5, 3], [3, 5], [5, 3]]},
    {"dominoes": [[9, 9], [9, 9], [9, 9], [9, 9]]},
    {"dominoes": [[1, 2], [3, 4], [5, 6], [7, 8]]},
    {"dominoes": [[i % 9 + 1, (i * 3) % 9 + 1] for i in range(20)]},
    {"dominoes": [[a, b] for a in range(1, 5) for b in range(1, 5)]},
]


DOMINO_SOLUTION_CODE = (
    "def numEquivDominoPairs(dominoes):\n"
    "    count = {}\n"
    "    pairs = 0\n"
    "    for a, b in dominoes:\n"
    "        key = (a, b) if a <= b else (b, a)\n"
    "        pairs += count.get(key, 0)\n"
    "        count[key] = count.get(key, 0) + 1\n"
    "    return pairs"
)

DOMINO_SOLUTION_TEXT = (
    "<h3>Number of Equivalent Domino Pairs</h3>"
    "<p><strong>Algorithm:</strong></p>"
    "<ol>"
    "<li>Normalize each domino <code>[a, b]</code> to a canonical form by "
    "sorting its two values, so <code>[a, b]</code> and <code>[b, a]</code> "
    "collapse to the same key.</li>"
    "<li>Sweep the array left to right, maintaining a hash map of how many "
    "times each canonical key has been seen so far.</li>"
    "<li>Before inserting the current domino, add the current count to the "
    "answer — each earlier equivalent domino forms one new pair.</li>"
    "</ol>"
    "<p><strong>Time Complexity:</strong> O(n)</p>"
    "<p><strong>Space Complexity:</strong> O(1) (at most 45 distinct keys "
    "since values are 1..9)</p>"
    "<p><strong>Key Insight:</strong> counting the number of pairs among "
    "<code>k</code> equal items with <code>k*(k-1)/2</code> is equivalent to "
    "summing <code>0 + 1 + 2 + ... + (k-1)</code> incrementally as items are "
    "seen — the one-pass version avoids ever materialising the count.</p>"
)


# ---------------------------------------------------------------------------
# 3) Apply Discount to Prices
# ---------------------------------------------------------------------------
def discount_prices(sentence: str, discount: int) -> str:
    factor = 100 - discount
    words = sentence.split(" ")
    for i, w in enumerate(words):
        if len(w) > 1 and w[0] == "$" and w[1:].isdigit():
            price = int(w[1:])
            cents = price * factor
            dollars, c = divmod(cents, 100)
            words[i] = f"${dollars}.{c:02d}"
    return " ".join(words)


DISCOUNT_TESTS = [
    {"sentence": "there are $1 $2 and 5$ candies in the shop", "discount": 50},
    {"sentence": "1 2 $3 4 $5 $6 7 8$ $9 $10$", "discount": 100},
    {"sentence": "$100", "discount": 0},
    {"sentence": "$100", "discount": 100},
    {"sentence": "buy $10 get one free", "discount": 25},
    {"sentence": "$1 $2 $3 $4", "discount": 10},
    {"sentence": "no prices here", "discount": 50},
    {"sentence": "$abc $123abc $0 $99999", "discount": 33},
    {"sentence": "$1000000000 huge $1", "discount": 75},
    {"sentence": "mix $5 and words $50 done", "discount": 20},
]


DISCOUNT_SOLUTION_CODE = (
    "def discountPrices(sentence, discount):\n"
    "    factor = 100 - discount\n"
    "    words = sentence.split(' ')\n"
    "    for i, w in enumerate(words):\n"
    "        if len(w) > 1 and w[0] == '$' and w[1:].isdigit():\n"
    "            price = int(w[1:])\n"
    "            cents = price * factor\n"
    "            dollars, c = divmod(cents, 100)\n"
    "            words[i] = f'${dollars}.{c:02d}'\n"
    "    return ' '.join(words)"
)

DISCOUNT_SOLUTION_TEXT = (
    "<h3>Apply Discount to Prices</h3>"
    "<p><strong>Algorithm:</strong></p>"
    "<ol>"
    "<li>Split the sentence by single spaces to get individual words.</li>"
    "<li>For each word, treat it as a price only if it starts with "
    "<code>'$'</code> and every remaining character is a digit.</li>"
    "<li>Compute the discounted amount in integer cents to avoid "
    "floating-point rounding surprises for prices with up to 10 digits: "
    "<code>cents = price * (100 - discount)</code>.</li>"
    "<li>Format with exactly two decimals using <code>divmod</code>.</li>"
    "<li>Join the words back with single spaces.</li>"
    "</ol>"
    "<p><strong>Time Complexity:</strong> O(n) in the length of the sentence.</p>"
    "<p><strong>Space Complexity:</strong> O(n) for the split words and the output.</p>"
    "<p><strong>Key Insight:</strong> doing the arithmetic in cents "
    "(<code>price * factor</code>, then <code>divmod(..., 100)</code>) is "
    "exact for the given constraints — using floats risks tiny rounding "
    "errors on large prices.</p>"
)


# ---------------------------------------------------------------------------
# 4) Group Anagrams
# ---------------------------------------------------------------------------
def group_anagrams(strs: List[str]) -> List[List[str]]:
    groups: dict[str, List[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())


def _canonical(groups: List[List[str]]) -> List[List[str]]:
    return sorted(sorted(g) for g in groups)


GROUP_TESTS = [
    {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]},
    {"strs": [""]},
    {"strs": ["a"]},
    {"strs": ["abc", "bca", "cab", "xyz", "zyx", "yxz"]},
    {"strs": ["listen", "silent", "enlist", "google", "gooegl"]},
    {"strs": ["hello", "world", "olleh", "dlrow", "test"]},
    {"strs": ["", "", "a", "a", "b"]},
    {"strs": ["ab", "ba", "abc", "cba", "bca", "cab", "d"]},
    {"strs": ["ddddddddddg", "dgggggggggg"]},
    {"strs": ["rat", "tar", "art", "car", "arc", "cra", "bat", "tab", "abt"]},
]


GROUP_SOLUTION_CODE = (
    "def groupAnagrams(strs):\n"
    "    groups = {}\n"
    "    for s in strs:\n"
    "        key = ''.join(sorted(s))\n"
    "        groups.setdefault(key, []).append(s)\n"
    "    return list(groups.values())"
)

GROUP_SOLUTION_TEXT = (
    "<h3>Group Anagrams</h3>"
    "<p><strong>Algorithm:</strong></p>"
    "<ol>"
    "<li>For each string, build a canonical key that all its anagrams "
    "share. Sorting the letters is the simplest choice.</li>"
    "<li>Bucket strings by that key using a hash map.</li>"
    "<li>Return the map's values — the groups.</li>"
    "</ol>"
    "<p><strong>Time Complexity:</strong> O(n · k log k), where <em>n</em> "
    "is the number of strings and <em>k</em> is the maximum string length.</p>"
    "<p><strong>Space Complexity:</strong> O(n · k) for the map and the "
    "returned groups.</p>"
    "<p><strong>Key Insight:</strong> any invariant that two strings share iff "
    "they are anagrams works as a key — sorted characters, or a 26-length "
    "count tuple. The count-tuple version is O(n · k) and avoids the sort.</p>"
    "<p><em>Note:</em> LeetCode accepts the groups in any order, so the "
    "verifier compares the answer up to group ordering and within-group "
    "ordering.</p>"
)


GROUP_VERIFY = (
    "def verify(actual_output, expected_output):\n"
    "    def canon(groups):\n"
    "        return sorted(sorted(g) for g in groups)\n"
    "    passed = canon(actual_output) == canon(expected_output)\n"
    "    return [passed, str(actual_output)]"
)


# ---------------------------------------------------------------------------
# 5) Reverse Nodes in K-Group (array-level reference solution)
# ---------------------------------------------------------------------------
def reverse_k_group(arr: List[int], k: int) -> List[int]:
    out: List[int] = []
    i = 0
    n = len(arr)
    while i + k <= n:
        out.extend(reversed(arr[i : i + k]))
        i += k
    out.extend(arr[i:])
    return out


REVERSE_TESTS = [
    {"head": [1, 2, 3, 4, 5], "k": 2},
    {"head": [1, 2, 3, 4, 5], "k": 3},
    {"head": [1, 2, 3, 4, 5], "k": 1},
    {"head": [1, 2, 3, 4, 5], "k": 5},
    {"head": [1], "k": 1},
    {"head": [1, 2], "k": 2},
    {"head": [1, 2, 3, 4, 5, 6], "k": 2},
    {"head": [1, 2, 3, 4, 5, 6, 7, 8], "k": 3},
    {"head": [1, 2, 3, 4, 5, 6, 7, 8, 9], "k": 4},
    {"head": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "k": 5},
]


# solution_code / solution_text already present — keep them.


# ---------------------------------------------------------------------------
# 6) Building Boxes
# ---------------------------------------------------------------------------
def minimum_boxes(n: int) -> int:
    # Largest complete pyramid with `k` full layers uses
    #   floor(k*(k+1)*(k+2)/6) boxes and covers k*(k+1)/2 floor tiles.
    k = 1
    while k * (k + 1) * (k + 2) // 6 <= n:
        k += 1
    k -= 1
    used = k * (k + 1) * (k + 2) // 6
    floor = k * (k + 1) // 2
    remaining = n - used
    if remaining == 0:
        return floor
    # Add a partial next layer: place r floor boxes on the next diagonal,
    # supporting r*(r+1)/2 boxes on top; find smallest r with r*(r+1)/2 >= remaining.
    r = 1
    while r * (r + 1) // 2 < remaining:
        r += 1
    return floor + r


BOXES_TESTS = [
    {"n": 3},
    {"n": 4},
    {"n": 10},
    {"n": 1},
    {"n": 2},
    {"n": 15},
    {"n": 20},
    {"n": 100},
    {"n": 1000},
    {"n": 1000000000},
]


BOXES_SOLUTION_CODE = (
    "def minimumBoxes(n):\n"
    "    # A complete pyramid with k layers uses k*(k+1)*(k+2)//6 boxes\n"
    "    # and occupies k*(k+1)//2 floor tiles.\n"
    "    k = 1\n"
    "    while k * (k + 1) * (k + 2) // 6 <= n:\n"
    "        k += 1\n"
    "    k -= 1\n"
    "    used = k * (k + 1) * (k + 2) // 6\n"
    "    floor = k * (k + 1) // 2\n"
    "    remaining = n - used\n"
    "    if remaining == 0:\n"
    "        return floor\n"
    "    # Extend by one diagonal on the next layer: r floor boxes support\n"
    "    # r*(r+1)//2 boxes on top. Find the smallest r that fits.\n"
    "    r = 1\n"
    "    while r * (r + 1) // 2 < remaining:\n"
    "        r += 1\n"
    "    return floor + r"
)

BOXES_SOLUTION_TEXT = (
    "<h3>Building Boxes</h3>"
    "<p><strong>Observation:</strong> to minimize the floor footprint, boxes "
    "should be stacked in a corner as a triangular pyramid. A pyramid with "
    "<code>k</code> complete layers uses "
    "<code>k(k+1)(k+2)/6</code> boxes and occupies "
    "<code>k(k+1)/2</code> floor tiles.</p>"
    "<p><strong>Algorithm:</strong></p>"
    "<ol>"
    "<li>Find the largest <code>k</code> such that the full pyramid "
    "<code>k(k+1)(k+2)/6</code> is at most <code>n</code>. That fixes the base "
    "footprint <code>k(k+1)/2</code>.</li>"
    "<li>Let <code>remaining = n - k(k+1)(k+2)/6</code>. Extend by one "
    "diagonal of the next layer: <code>r</code> new floor boxes support a "
    "triangle of <code>r(r+1)/2</code> boxes above (stacked as a wedge).</li>"
    "<li>Return <code>k(k+1)/2 + r</code> where <code>r</code> is the smallest "
    "positive integer with <code>r(r+1)/2 &ge; remaining</code>.</li>"
    "</ol>"
    "<p><strong>Time Complexity:</strong> O(n^{1/3}) for the outer search and "
    "O(n^{1/2}) for the inner one — trivial for <code>n &le; 10<sup>9</sup></code>. "
    "Both can be replaced with a closed-form quadratic solve for O(1).</p>"
    "<p><strong>Space Complexity:</strong> O(1).</p>"
)


# ---------------------------------------------------------------------------
# Runner helpers
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
    # 1) roman
    assert roman_to_int("III") == 3
    assert roman_to_int("LVIII") == 58
    assert roman_to_int("MCMXCIV") == 1994
    assert roman_to_int("MMMDCCXLIX") == 3749

    # 2) domino
    assert num_equiv_domino_pairs([[1, 2], [2, 1], [3, 4], [5, 6]]) == 1
    assert num_equiv_domino_pairs([[1, 2], [1, 2], [1, 1], [1, 2], [2, 2]]) == 3

    # 3) discount
    assert (
        discount_prices("there are $1 $2 and 5$ candies in the shop", 50)
        == "there are $0.50 $1.00 and 5$ candies in the shop"
    )
    assert (
        discount_prices("1 2 $3 4 $5 $6 7 8$ $9 $10$", 100)
        == "1 2 $0.00 4 $0.00 $0.00 7 8$ $0.00 $10$"
    )
    assert discount_prices("$100", 0) == "$100.00"

    # 4) group anagrams — compare canonically
    got = _canonical(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    exp = _canonical([["bat"], ["nat", "tan"], ["ate", "eat", "tea"]])
    assert got == exp
    assert _canonical(group_anagrams([""])) == [[""]]
    assert _canonical(group_anagrams(["a"])) == [["a"]]

    # 5) reverse k-group
    assert reverse_k_group([1, 2, 3, 4, 5], 2) == [2, 1, 4, 3, 5]
    assert reverse_k_group([1, 2, 3, 4, 5], 3) == [3, 2, 1, 4, 5]
    assert reverse_k_group([1, 2, 3, 4, 5], 1) == [1, 2, 3, 4, 5]

    # 6) building boxes — LeetCode sample cases + a spot check on a full
    # pyramid (k=4: 20 boxes → 4*5/2 = 10 floor tiles) and the boundary
    # where the next diagonal saturates.
    assert minimum_boxes(1) == 1
    assert minimum_boxes(3) == 3
    assert minimum_boxes(4) == 3
    assert minimum_boxes(10) == 6
    assert minimum_boxes(20) == 10
    # n=11: one extra box beyond the k=3 pyramid → floor = 6 + 1 = 7.
    assert minimum_boxes(11) == 7

    print("[sanity] all reference solutions match sample outputs")


# ---------------------------------------------------------------------------
# Per-problem drivers
# ---------------------------------------------------------------------------
def write_problem(
    name: str,
    inputs: List[dict],
    solver: Callable[..., Any],
    unpack: Callable[[dict], tuple],
    *,
    solution_code: str | None = None,
    solution_text: str | None = None,
    verify: str | None = None,
) -> None:
    assert len(inputs) >= 10, f"{name} has only {len(inputs)} inputs, need 10+"
    cases = build_cases(inputs, solver, unpack)
    data = load_json(name)
    if solution_code is not None:
        data["solution_code"] = solution_code
    if solution_text is not None:
        data["solution_text"] = solution_text
    if verify is not None:
        data["verify"] = verify
    data["test_cases"] = cases
    save_json(name, data)
    preview = ", ".join(str(c["output"])[:40] for c in cases[:3])
    print(f"[wrote] {name}: {len(cases)} cases  (first outputs: {preview}, ...)")


def main() -> None:
    sanity_checks()

    write_problem(
        "roman-to-integer",
        ROMAN_TESTS,
        roman_to_int,
        lambda t: (t["s"],),
        solution_code=ROMAN_SOLUTION_CODE,
        solution_text=ROMAN_SOLUTION_TEXT,
    )
    write_problem(
        "number-of-equivalent-domino-pairs",
        DOMINO_TESTS,
        num_equiv_domino_pairs,
        lambda t: ([list(d) for d in t["dominoes"]],),
        solution_code=DOMINO_SOLUTION_CODE,
        solution_text=DOMINO_SOLUTION_TEXT,
    )
    write_problem(
        "apply-discount-to-prices",
        DISCOUNT_TESTS,
        discount_prices,
        lambda t: (t["sentence"], t["discount"]),
        solution_code=DISCOUNT_SOLUTION_CODE,
        solution_text=DISCOUNT_SOLUTION_TEXT,
    )
    write_problem(
        "group-anagrams",
        GROUP_TESTS,
        group_anagrams,
        lambda t: (list(t["strs"]),),
        solution_code=GROUP_SOLUTION_CODE,
        solution_text=GROUP_SOLUTION_TEXT,
        verify=GROUP_VERIFY,
    )
    write_problem(
        "reverse-nodes-in-k-group",
        REVERSE_TESTS,
        reverse_k_group,
        lambda t: (list(t["head"]), t["k"]),
    )
    write_problem(
        "building-boxes",
        BOXES_TESTS,
        minimum_boxes,
        lambda t: (t["n"],),
        solution_code=BOXES_SOLUTION_CODE,
        solution_text=BOXES_SOLUTION_TEXT,
    )

    print("[done] all week12 questions updated")


if __name__ == "__main__":
    main()
