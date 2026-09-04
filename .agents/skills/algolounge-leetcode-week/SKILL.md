---
name: algolounge-leetcode-week
description: Import or refresh a six-question LeetCode batch for the AlgoLounge repository with canonical descriptions, exactly 10 verified test cases per question, and beginner-friendly Python solutions. Use when the user supplies six LeetCode problems for a course week or asks to complete the same AlgoLounge question workflow.
---

# AlgoLounge LeetCode Week

Turn the user's six LeetCode questions into complete AlgoLounge question entries. Preserve unrelated repository changes and existing exercise wiring.

## Resolve the batch

- Resolve exactly six unique LeetCode slugs from the supplied titles or URLs.
- Infer the target course and week from the conversation or existing course file when clear. Ask only when placement materially cannot be inferred.
- Inspect `public/courses`, `public/questions`, `scripts/scrape.js`, and nearby question files before editing so new data follows the current schema.

## Fetch canonical question data

Use LeetCode's GraphQL `questionData` request with the same endpoint, headers, variables, and problem Referer as `scripts/scrape.js`. Do not use a rendered page, search snippet, or a hand-written paraphrase as the source of the description.

Run the bundled read-only helper when useful:

```bash
node .agents/skills/algolounge-leetcode-week/scripts/fetch-details.mjs <slug> [...slugs]
```

Network access may require user approval. Never substitute a random problem when a requested slug cannot be fetched.

Convert `content` using the current `convertLeetCodeHTML` behavior from `scripts/scrape.js`. Confirm that the saved description includes the canonical statement, examples, explanations, constraints, and follow-up text. Compare every `<img>` in the raw response with the converted description and preserve its `src` and useful `alt` text. If the description renderer cannot display canonical images or nested example content, fix the shared renderer and verify it on localhost.

Premium questions can return `content: null` without authentication. In that case, use canonical content from an authenticated response supplied by the user or an authorized signed-in browser session. Do not invent premium content; report the missing access if no canonical source is available.

When a question file already exists, refresh only fields that need canonical question data or requested enrichment. Preserve its filename, index integration, function contract, and intentional local behavior unless a verified correction is required.

## Create exactly 10 correct tests

Each question must have exactly 10 test cases with IDs 1 through 10.

- Keep correct canonical examples.
- Add cases that exercise boundaries and distinct algorithmic behaviors: minimum sizes, duplicates, absent results, ordering, negative or zero values when allowed, long runs, overlaps, cascades, disconnected graphs, and similar problem-specific risks.
- Keep every input within the canonical constraints and contractual guarantees. For example, Two Sum cases must have exactly one valid pair.
- Avoid ten cosmetic variants of the same behavior.
- Compute all expected outputs with a separate reference implementation or oracle written for validation. Do not derive expected results by trusting the solution that will be published.
- For outputs allowing multiple orders or representations, make `verify` compare semantic equivalence rather than a single incidental ordering.

After the independent oracle check, execute the stored `solution_code` through the question's actual `prepare` and `verify` functions against all tests. The bundled validator performs this second check:

```bash
python3 .agents/skills/algolounge-leetcode-week/scripts/validate-question-files.py <slug> [...slugs]
```

The validator passing is necessary but not a replacement for the independent oracle check.

## Write the teaching solution

Populate both `solution_text` and `solution_code` for every question, including files that already have a thin solution.

The explanation should be understandable to a beginner and include:

- the central idea in plain language;
- a step-by-step algorithm whose names match the code;
- the important invariant or a concise explanation of why it works;
- time and space complexity with variables defined;
- clarification of the main pitfall when the problem has one.

Use complete, readable Python matching `entry_function` and the provided template signature. Prefer descriptive names and a few comments at the decisions a beginner may not understand. Avoid clever shortcuts that make the explanation and code diverge.

## Integrate and verify

- Add or update the requested course/week entries and source links when placement is part of the request.
- Run `npm run sync-index` when question or course files were added or filenames changed.
- Parse every changed JSON file, run the independent oracle checks, run the bundled solution validator, and run `git diff --check`.
- Run `npm run build`.
- Spot-check all six localhost question pages. Confirm headings, example counts, constraints, and solution content. For questions with images, confirm each image is loaded with a nonzero natural width.
- Report the six updated questions, the 10/10 test status for each, any premium-source caveat, and the build result.

