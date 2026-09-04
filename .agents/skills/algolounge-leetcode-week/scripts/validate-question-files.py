#!/usr/bin/env python3

import copy
import json
import sys
from pathlib import Path


if len(sys.argv) < 2:
    raise SystemExit(
        "Usage: python3 validate-question-files.py <slug> [...slugs]"
    )


repo_root = Path(__file__).resolve().parents[4]
questions_dir = repo_root / "public" / "questions"


for slug in sys.argv[1:]:
    path = questions_dir / f"{slug}.json"
    question = json.loads(path.read_text())
    cases = question.get("test_cases", [])

    if len(cases) != 10:
        raise AssertionError(f"{slug}: expected 10 tests, found {len(cases)}")

    ids = [case.get("id") for case in cases]
    if ids != list(range(1, 11)):
        raise AssertionError(f"{slug}: test IDs must be 1 through 10, found {ids}")

    if not question.get("solution_text", "").strip():
        raise AssertionError(f"{slug}: solution_text is empty")
    if not question.get("solution_code", "").strip():
        raise AssertionError(f"{slug}: solution_code is empty")

    namespace = {}
    exec(question["prepare"], namespace)
    exec(question["solution_code"], namespace)
    exec(question["verify"], namespace)

    entry_function = question["entry_function"]
    solution = namespace.get(entry_function)
    if not callable(solution):
        raise AssertionError(
            f"{slug}: solution_code does not define {entry_function}"
        )

    prepare = namespace["prepare"]
    verify = namespace["verify"]

    for case in cases:
        test_input = copy.deepcopy(case["input"])
        expected = copy.deepcopy(case["output"])
        actual = solution(*prepare(test_input))
        verdict = verify(actual, expected)

        if not verdict or not verdict[0]:
            rendered = verdict[1] if verdict and len(verdict) > 1 else repr(actual)
            raise AssertionError(
                f"{slug} case {case['id']} failed: {rendered}; expected {expected!r}"
            )

    print(f"{slug}: 10/10 solution tests passed")

