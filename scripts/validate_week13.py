#!/usr/bin/env python3
"""Populate and execute Algotime Summer 2026 Week 13 solutions/tests."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "public" / "questions"
MOD = 1_000_000_007


def digit_frequency_score(n):
    score = 0
    while n:
        score += n % 10
        n //= 10
    return score


def detect_capital_use(word):
    capitals = sum('A' <= ch <= 'Z' for ch in word)
    return capitals == 0 or capitals == len(word) or (
        capitals == 1 and 'A' <= word[0] <= 'Z'
    )


def min_deletion(nums):
    deletions = 0
    kept = []
    for value in nums:
        if len(kept) % 2 == 0 or kept[-1] != value:
            kept.append(value)
        else:
            deletions += 1
    return deletions + len(kept) % 2


def moves_to_make_zigzag(nums):
    def cost(parity):
        moves = 0
        for i in range(parity, len(nums), 2):
            left = nums[i - 1] if i > 0 else float('inf')
            right = nums[i + 1] if i + 1 < len(nums) else float('inf')
            moves += max(0, nums[i] - min(left, right) + 1)
        return moves
    return min(cost(0), cost(1))


def number_of_ways(s, t, k):
    n = len(s)
    pattern = t + '#'+ s + s[:-1]
    prefix = [0] * len(pattern)
    matches = 0
    for i in range(1, len(pattern)):
        j = prefix[i - 1]
        while j and pattern[i] != pattern[j]:
            j = prefix[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        prefix[i] = j
        if i > n and j == n:
            matches += 1

    def multiply(a, b):
        return [[sum(a[i][x] * b[x][j] for x in range(2)) % MOD
                 for j in range(2)] for i in range(2)]

    matrix = [[0, n - 1], [1, n - 2]]
    power = [[1, 0], [0, 1]]
    while k:
        if k & 1:
            power = multiply(power, matrix)
        matrix = multiply(matrix, matrix)
        k >>= 1
    same, different = power[0][0], power[1][0]
    if s == t:
        return (same + (matches - 1) * different) % MOD
    return matches * different % MOD


def box_delivering(boxes, portsCount, maxBoxes, maxWeight):
    del portsCount  # Port labels matter only when adjacent labels differ.
    n = len(boxes)
    weight = [0] * (n + 1)
    changes = [0] * (n + 1)
    for i, (port, box_weight) in enumerate(boxes, 1):
        weight[i] = weight[i - 1] + box_weight
        changes[i] = changes[i - 1]
        if i > 1 and port != boxes[i - 2][0]:
            changes[i] += 1

    dp = [0] * (n + 1)
    candidates = deque([(0, 0)])
    for i in range(1, n + 1):
        while (i - candidates[0][0] > maxBoxes or
               weight[i] - weight[candidates[0][0]] > maxWeight):
            candidates.popleft()
        dp[i] = changes[i] + 2 + candidates[0][1]
        if i < n:
            value = dp[i] - changes[i + 1]
            while candidates and candidates[-1][1] >= value:
                candidates.pop()
            candidates.append((i, value))
    return dp[n]


SPECS = {
    "digit-frequency-score": {
        "function": digit_frequency_score,
        "solution_code": """def digitFrequencyScore(n):
    score = 0
    while n:
        score += n % 10
        n //= 10
    return score""",
        "solution_text": "<h3>Digit Frequency Score</h3><p>Add every decimal digit of <code>n</code>. This is equivalent to summing <code>d * freq(d)</code>, because each occurrence contributes its digit once.</p><p><strong>Time:</strong> O(log n). <strong>Space:</strong> O(1).</p>",
        "tests": [{"n": x} for x in [1, 10, 122, 101, 999999999, 1000000000, 123456789, 5050505, 808, 42]],
    },
    "detect-capital": {
        "function": detect_capital_use,
        "solution_code": """def detectCapitalUse(word):
    capitals = sum('A' <= ch <= 'Z' for ch in word)
    return (capitals == 0 or capitals == len(word) or
            (capitals == 1 and 'A' <= word[0] <= 'Z'))""",
        "solution_text": "<h3>Detect Capital</h3><p>Count uppercase letters. Valid words have zero uppercase letters, all uppercase letters, or exactly one uppercase letter at index 0.</p><p><strong>Time:</strong> O(n). <strong>Space:</strong> O(1).</p>",
        "tests": [{"word": x} for x in ["USA", "FlaG", "leetcode", "Google", "g", "Z", "mL", "LeetCode", "PYTHON", "Python"]],
    },
    "minimum-deletions-to-make-array-beautiful": {
        "function": min_deletion,
        "solution_code": """def minDeletion(nums):
    deletions = 0
    kept = []
    for value in nums:
        if len(kept) % 2 == 0 or kept[-1] != value:
            kept.append(value)
        else:
            deletions += 1
    return deletions + len(kept) % 2""",
        "solution_text": "<h3>Minimum Deletions to Make Array Beautiful</h3><p>Greedily build the longest valid subsequence. At every even kept index, keep the value; at every odd kept index, keep only a value different from its partner. If the result has odd length, remove its final element.</p><p><strong>Time:</strong> O(n). <strong>Space:</strong> O(n).</p>",
        "tests": [{"nums": x} for x in [[1], [1, 2], [1, 1], [1, 1, 2, 3, 5], [1, 1, 2, 2, 3, 3], [1, 2, 3, 4], [7, 7, 7, 7], [1, 2, 2, 3], [0, 0, 0, 1, 1, 2, 2], [1, 1, 1, 2, 2, 2, 3]]],
    },
    "decrease-elements-to-make-array-zigzag": {
        "function": moves_to_make_zigzag,
        "solution_code": """def movesToMakeZigzag(nums):
    def cost(parity):
        moves = 0
        for i in range(parity, len(nums), 2):
            left = nums[i - 1] if i > 0 else float('inf')
            right = nums[i + 1] if i + 1 < len(nums) else float('inf')
            moves += max(0, nums[i] - min(left, right) + 1)
        return moves
    return min(cost(0), cost(1))""",
        "solution_text": "<h3>Decrease Elements To Make Array Zigzag</h3><p>Try each possible valley parity. Every valley is independent because only valley elements need to be decreased. Lower each to one less than its smaller neighbor and sum the costs; return the smaller parity cost.</p><p><strong>Time:</strong> O(n). <strong>Space:</strong> O(1).</p>",
        "tests": [{"nums": x} for x in [[1], [1, 2], [2, 1], [1, 2, 3], [9, 6, 1, 6, 2], [1, 1, 1], [10, 1, 10, 1], [5, 5, 4, 4, 3], [1000, 1, 1000], [2, 7, 10, 9, 8, 9]]],
    },
    "string-transformation": {
        "function": number_of_ways,
        "solution_code": """def numberOfWays(s, t, k):
    MOD = 1000000007
    n = len(s)
    text = t + '#' + s + s[:-1]
    prefix = [0] * len(text)
    matches = 0
    for i in range(1, len(text)):
        j = prefix[i - 1]
        while j and text[i] != text[j]:
            j = prefix[j - 1]
        if text[i] == text[j]:
            j += 1
        prefix[i] = j
        if i > n and j == n:
            matches += 1

    def mul(a, b):
        return [[sum(a[i][x] * b[x][j] for x in range(2)) % MOD
                 for j in range(2)] for i in range(2)]

    matrix = [[0, n - 1], [1, n - 2]]
    power = [[1, 0], [0, 1]]
    while k:
        if k & 1:
            power = mul(power, matrix)
        matrix = mul(matrix, matrix)
        k >>= 1
    same, different = power[0][0], power[1][0]
    if s == t:
        return (same + (matches - 1) * different) % MOD
    return matches * different % MOD""",
        "solution_text": "<h3>String Transformation</h3><p>Use KMP on <code>s + s[:-1]</code> to count rotations equal to <code>t</code>. All nonzero rotations have the same number of operation sequences. Track two states: ways to reach rotation 0 and ways to reach any particular nonzero rotation. Their transition matrix is <code>[[0,n-1],[1,n-2]]</code>; raise it to <code>k</code> by binary exponentiation.</p><p><strong>Time:</strong> O(n + log k). <strong>Space:</strong> O(n).</p>",
        "tests": [{"s": s, "t": t, "k": k} for s, t, k in [("abcd", "cdab", 2), ("ababab", "ababab", 1), ("ab", "ab", 1), ("ab", "ba", 1), ("abc", "abc", 2), ("abc", "bca", 1), ("aaaa", "aaaa", 3), ("abc", "acb", 5), ("abab", "baba", 2), ("abcde", "deabc", 10)]],
    },
    "delivering-boxes-from-storage-to-ports": {
        "function": box_delivering,
        "solution_code": """def boxDelivering(boxes, portsCount, maxBoxes, maxWeight):
    from collections import deque
    n = len(boxes)
    weight = [0] * (n + 1)
    changes = [0] * (n + 1)
    for i, (port, box_weight) in enumerate(boxes, 1):
        weight[i] = weight[i - 1] + box_weight
        changes[i] = changes[i - 1]
        if i > 1 and port != boxes[i - 2][0]:
            changes[i] += 1

    dp = [0] * (n + 1)
    candidates = deque([(0, 0)])
    for i in range(1, n + 1):
        while (i - candidates[0][0] > maxBoxes or
               weight[i] - weight[candidates[0][0]] > maxWeight):
            candidates.popleft()
        dp[i] = changes[i] + 2 + candidates[0][1]
        if i < n:
            value = dp[i] - changes[i + 1]
            while candidates and candidates[-1][1] >= value:
                candidates.pop()
            candidates.append((i, value))
    return dp[n]""",
        "solution_text": "<h3>Delivering Boxes from Storage to Ports</h3><p>Use dynamic programming with prefix weights and prefix port-change counts. For each endpoint, valid previous endpoints form a sliding window under both ship limits. A monotonic deque stores the minimum adjusted DP value in that window, making every candidate enter and leave once.</p><p><strong>Time:</strong> O(n). <strong>Space:</strong> O(n).</p>",
        "tests": [{"boxes": b, "portsCount": p, "maxBoxes": mb, "maxWeight": mw} for b, p, mb, mw in [([[1, 1]], 1, 1, 1), ([[1, 1], [1, 1]], 1, 2, 2), ([[1, 1], [2, 1], [1, 1]], 2, 3, 3), ([[1, 2], [3, 3], [3, 1], [3, 1], [2, 4]], 3, 3, 6), ([[1, 4], [1, 2], [2, 1], [2, 1], [3, 2], [3, 4]], 3, 6, 7), ([[1, 1], [2, 1]], 2, 1, 10), ([[1, 5], [1, 5], [1, 5]], 1, 3, 10), ([[1, 2], [2, 2], [2, 2], [3, 2]], 3, 4, 8), ([[1, 3], [2, 3], [2, 3], [1, 3]], 2, 3, 6), ([[1, 1], [1, 1], [2, 1], [2, 1], [1, 1]], 2, 5, 5)]],
    },
}


def populate():
    for filename, spec in SPECS.items():
        path = QDIR / f"{filename}.json"
        data = json.loads(path.read_text())
        data["solution_code"] = spec["solution_code"]
        data["solution_text"] = spec["solution_text"]
        outputs = [spec["function"](**case) for case in spec["tests"]]
        data["test_cases"] = [
            {"id": i, "input": case, "output": output}
            for i, (case, output) in enumerate(zip(spec["tests"], outputs), 1)
        ]
        path.write_text(json.dumps(data, indent=2) + "\n")


def execute_stored_solutions():
    for filename in SPECS:
        data = json.loads((QDIR / f"{filename}.json").read_text())
        namespace = {}
        exec(data["solution_code"], namespace)
        exec(data["prepare"], namespace)
        exec(data["verify"], namespace)
        solution = namespace[data["entry_function"]]
        for case in data["test_cases"]:
            args = namespace["prepare"](case["input"])
            actual = solution(*args)
            passed, display = namespace["verify"](actual, case["output"])
            assert passed, f"{filename} case {case['id']}: got {display}"
        assert len(data["test_cases"]) == 10
        print(f"PASS {filename}: 10/10")


if __name__ == "__main__":
    populate()
    execute_stored_solutions()
