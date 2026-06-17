const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const PAGE_SIZE = 500;
const QUESTIONS_DIR = path.join(__dirname, "../public/questions");

const [,, courseArg, weekArg] = process.argv;
if (!courseArg || !weekArg) {
  console.error("Usage: node scripts/scrape.js <course-filename> <week-number>");
  console.error("  e.g. node scripts/scrape.js algotimesummer2026 6");
  process.exit(1);
}
const COURSE_FILE = path.join(__dirname, `../public/courses/${courseArg}.json`);
const WEEK_NUM = parseInt(weekArg, 10);
if (!fs.existsSync(COURSE_FILE)) {
  console.error(`Course file not found: ${COURSE_FILE}`);
  process.exit(1);
}
if (isNaN(WEEK_NUM) || WEEK_NUM < 1) {
  console.error(`Invalid week number: ${weekArg}`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// GraphQL queries
// ---------------------------------------------------------------------------

const LIST_QUERY = `
  query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
    problemsetQuestionList: questionList(
      categorySlug: $categorySlug
      limit: $limit
      skip: $skip
      filters: $filters
    ) {
      total: totalNum
      questions: data {
        questionId
        title
        titleSlug
        difficulty
        isPaidOnly
        topicTags { name }
      }
    }
  }
`;

const DETAIL_QUERY = `
  query questionData($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
      content
      exampleTestcaseList
      metaData
      codeSnippets { langSlug code }
    }
  }
`;

// ---------------------------------------------------------------------------
// Problem class
// ---------------------------------------------------------------------------

class Problem {
  constructor({ id, title, slug, difficulty, tags, description, sampleTestCases, metaData, pythonTemplate }) {
    this.id = id;
    this.title = title;
    this.slug = slug;
    this.difficulty = difficulty;
    this.tags = tags;
    this.description = description;
    this.sampleTestCases = sampleTestCases;
    this.metaData = metaData;             // parsed object: { name, params, return }
    this.pythonTemplate = pythonTemplate; // raw Python3 snippet from LeetCode
  }
}

// ---------------------------------------------------------------------------
// Fetching
// ---------------------------------------------------------------------------

async function graphql(query, variables, referer) {
  const body = JSON.stringify({ query, variables });
  const res = await fetch("https://leetcode.com/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0",
      Referer: referer ?? "https://leetcode.com/problemset/all/",
    },
    body,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function fetchPage(skip) {
  const json = await graphql(LIST_QUERY, { categorySlug: "algorithms", limit: PAGE_SIZE, skip, filters: {} });
  const list = json?.data?.problemsetQuestionList;
  if (!list) throw new Error(`Unexpected list response: ${JSON.stringify(json).slice(0, 300)}`);
  return list;
}

async function fetchDetail(slug) {
  const json = await graphql(
    DETAIL_QUERY,
    { titleSlug: slug },
    `https://leetcode.com/problems/${slug}/`
  );
  const q = json?.data?.question;
  if (!q) throw new Error(`No detail data for ${slug}`);

  const pythonSnippet = q.codeSnippets?.find((s) => s.langSlug === "python3")?.code ?? "";
  let metaData = {};
  try { metaData = JSON.parse(q.metaData ?? "{}"); } catch (_) {}

  return {
    description: q.content,
    sampleTestCases: q.exampleTestcaseList ?? [],
    metaData,
    pythonTemplate: pythonSnippet,
  };
}

async function getNonPremiumQuestions() {
  const all = [];
  let skip = 0;
  let total = Infinity;

  while (skip < total) {
    const { total: t, questions } = await fetchPage(skip);
    total = t;
    all.push(...questions);
    skip += PAGE_SIZE;
    process.stderr.write(`Fetched ${all.length} / ${total}\n`);
  }

  return all
    .filter((q) => !q.isPaidOnly)
    .map((q) => ({
      id: parseInt(q.questionId, 10),
      title: q.title,
      slug: q.titleSlug,
      difficulty: q.difficulty,
      tags: q.topicTags.map((t) => t.name),
    }))
    .sort((a, b) => a.id - b.id);
}

function validateProblem(problem) {
  const params = problem.metaData?.params ?? [];
  const testCases = buildTestCases(problem.description ?? "", problem.sampleTestCases, params);
  if (testCases.length === 0) return false;
  return testCases.every(
    (tc) => tc.output !== "" && tc.output !== null && tc.output !== undefined
  );
}

async function enrichWithRetry(candidate, allQuestions, usedSlugs) {
  const tried = new Set();
  let current = candidate;

  while (true) {
    tried.add(current.slug);
    const detail = await fetchDetail(current.slug);
    const problem = new Problem({ ...current, ...detail });

    if (validateProblem(problem)) return problem;

    process.stderr.write(`${current.slug}: failed to parse test cases, finding replacement...\n`);

    const pool = allQuestions.filter(
      (q) => q.difficulty === candidate.difficulty && !tried.has(q.slug) && !usedSlugs.has(q.slug)
    );
    if (pool.length === 0) {
      process.stderr.write(`Warning: no valid replacement for ${current.difficulty}, keeping ${current.slug} as-is.\n`);
      return problem;
    }

    current = pool[Math.floor(Math.random() * pool.length)];
    usedSlugs.add(current.slug);
  }
}

async function enrichQuestions(picked, allQuestions) {
  const usedSlugs = new Set(picked.map((q) => q.slug));
  return Promise.all(picked.map((q) => enrichWithRetry(q, allQuestions, usedSlugs)));
}

// ---------------------------------------------------------------------------
// Seen list
// ---------------------------------------------------------------------------

function loadSeen() {
  const seenPath = path.join(__dirname, "seen.txt");
  if (!fs.existsSync(seenPath)) return new Set();
  return new Set(
    fs.readFileSync(seenPath, "utf8").split("\n").map((l) => l.trim()).filter(Boolean)
  );
}

// ---------------------------------------------------------------------------
// Picking
// ---------------------------------------------------------------------------

function pickTwo(pool, seen) {
  const shuffle = (arr) => arr.sort(() => Math.random() - 0.5);
  const fresh = shuffle(pool.filter((q) => !seen.has(q.slug)));
  const stale = shuffle(pool.filter((q) => seen.has(q.slug)));
  const picked = fresh.slice(0, 2);
  if (picked.length < 2) picked.push(...stale.slice(0, 2 - picked.length));
  return picked;
}

function pickWeekQuestions(allQuestions) {
  const seen = loadSeen();
  const byDifficulty = (d) => allQuestions.filter((q) => q.difficulty === d);
  const picked = [
    ...pickTwo(byDifficulty("Easy"), seen),
    ...pickTwo(byDifficulty("Medium"), seen),
    ...pickTwo(byDifficulty("Hard"), seen),
  ];
  const freshCount = picked.filter((q) => !seen.has(q.slug)).length;
  if (freshCount < 3) {
    process.stderr.write("Warning: could not guarantee 3 fresh questions; retrying.\n");
    return pickWeekQuestions(allQuestions);
  }
  return picked;
}

// ---------------------------------------------------------------------------
// Question JSON generation
// ---------------------------------------------------------------------------

const BUILDERS = {
  TreeNode: `\
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def _build_tree(vals):
    if not vals:
        return None
    root = TreeNode(vals[0])
    queue = [root]
    i = 1
    while queue and i < len(vals):
        node = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root`,

  Node: `\
class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children or []

def _build_nary(vals):
    if not vals:
        return None
    root = Node(vals[0])
    queue = [root]
    i = 2  # skip root value and first null separator
    while queue and i < len(vals):
        node = queue.pop(0)
        while i < len(vals) and vals[i] is not None:
            child = Node(vals[i])
            node.children.append(child)
            queue.append(child)
            i += 1
        i += 1  # skip null separator
    return root`,

  ListNode: `\
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def _build_list(vals):
    if not vals:
        return None
    head = ListNode(vals[0])
    curr = head
    for v in vals[1:]:
        curr.next = ListNode(v)
        curr = curr.next
    return head`,
};

const BUILDER_CALL = {
  TreeNode: (name) => `_build_tree(test_case_input['${name}'])`,
  Node:     (name) => `_build_nary(test_case_input['${name}'])`,
  ListNode: (name) => `_build_list(test_case_input['${name}'])`,
};

function generatePrepare(metaData) {
  const params = metaData.params ?? [];
  if (params.length === 0) return "def prepare(test_case_input):\n    return ()";

  const usedBuilders = new Set();
  const argExprs = params.map((p) => {
    const baseType = p.type?.replace(/\[\]$/, ""); // strip [] suffix
    if (BUILDER_CALL[baseType]) {
      usedBuilders.add(baseType);
      return BUILDER_CALL[baseType](p.name);
    }
    return `test_case_input['${p.name}']`;
  });

  // Trailing comma required for single-param tuples
  const trailing = params.length === 1 ? "," : "";
  const parts = [...usedBuilders].map((t) => BUILDERS[t]);
  parts.push(`def prepare(test_case_input):\n    return (${argExprs.join(", ")}${trailing})`);
  return parts.join("\n\n");
}

function generateTemplate(metaData) {
  const name = metaData.name ?? "solution";
  const params = (metaData.params ?? []).map((p) => p.name).join(", ");
  return `def ${name}(${params}):\n    `;
}

function toKeywords(title, tags) {
  const words = title.toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter(Boolean);
  const tagWords = tags.flatMap((t) => t.toLowerCase().split(/\s+/));
  return [...new Set([...words, ...tagWords])];
}

// Converts LeetCode's HTML format to the structure expected by description.component.ts:
//   <h2>Title</h2> + <p> description + <h3>Examples:</h3><ul><li>...</li></ul>
//   + <h3>Constraints:</h3><ul>...</ul>
// LeetCode uses <pre> blocks for examples and <p><strong>Constraints:</strong></p> headings.
function convertLeetCodeHTML(html, title) {
  // Remove empty &nbsp; spacer paragraphs
  let out = html.replace(/<p>\s*(?:&nbsp;| )\s*<\/p>/gi, "");

  const exampleItems = [];

  // New format: <p><strong class="example">Example N:</strong></p><div class="example-block">...</div>
  const newExampleRe =
    /<p[^>]*>\s*<strong[^>]*>Example\s*\d+[.:]*<\/strong>[^<]*<\/p>\s*<div[^>]*class="example-block"[^>]*>([\s\S]*?)<\/div>/gi;
  let m;
  while ((m = newExampleRe.exec(out)) !== null) {
    // Extract Input/Output/Explanation from the block's <p> tags
    const block = m[1];
    const inputM = block.match(/<strong>Input:<\/strong>\s*(?:<span[^>]*>)?([^\n<]+)/i);
    const outputM = block.match(/<strong>Output:<\/strong>\s*(?:<span[^>]*>)?([^\n<]+)/i);
    const explanationM = block.match(/<strong>Explanation:<\/strong>([\s\S]*?)(?=<p><strong>|$)/i);
    let li = "";
    if (inputM) li += `<strong>Input:</strong> ${inputM[1].trim()}<br>`;
    if (outputM) li += `<strong>Output:</strong> ${outputM[1].trim()}<br>`;
    if (explanationM) li += `<strong>Explanation:</strong>${explanationM[1].trim()}`;
    exampleItems.push(`<li>${li}</li>`);
  }
  out = out.replace(
    /<p[^>]*>\s*<strong[^>]*>Example\s*\d+[.:]*<\/strong>[^<]*<\/p>\s*<div[^>]*class="example-block"[^>]*>[\s\S]*?<\/div>/gi,
    ""
  );

  // Old format: <p><strong>Example N:</strong></p> followed by <pre>...</pre>
  const oldExampleRe =
    /<p[^>]*>\s*<strong[^>]*>Example\s*\d+[.:]*<\/strong>[^<]*<\/p>\s*(<img[^>]*\/?>\s*)?<pre>\n?([\s\S]*?)<\/pre>/gi;
  while ((m = oldExampleRe.exec(out)) !== null) {
    const img = m[1] ?? "";
    const preContent = m[2]
      .replace(/\r?\n/g, "<br>")
      .replace(/^<br>/, "")
      .replace(/<br>$/, "")
      .trim();
    exampleItems.push(`<li>${img}${preContent}</li>`);
  }
  out = out.replace(
    /<p[^>]*>\s*<strong[^>]*>Example\s*\d+[.:]*<\/strong>[^<]*<\/p>\s*(?:<img[^>]*\/?>\s*)?<pre>[\s\S]*?<\/pre>/gi,
    ""
  );

  // Convert <p><strong>Constraints:</strong></p> -> <h3>Constraints:</h3>
  out = out.replace(/<p[^>]*>\s*<strong[^>]*>Constraints[.:]*<\/strong>\s*<\/p>/gi, "<h3>Constraints:</h3>");

  const examplesHTML =
    exampleItems.length > 0 ? `<h3>Examples:</h3><ul>${exampleItems.join("")}</ul>` : "";

  out = out.includes("<h3>Constraints:</h3>")
    ? out.replace("<h3>Constraints:</h3>", `${examplesHTML}<h3>Constraints:</h3>`)
    : out + examplesHTML;

  return `<h2>${title}</h2>${out}`;
}

function decodeHTMLEntities(str) {
  return str
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#39;|&apos;/g, "'");
}

function buildTestCases(rawHtml, sampleTestCases, params) {
  // Extract Output: values from <pre> blocks before the HTML is converted
  const outputs = [];
  // Handles both formats:
  //   old: <strong>Output:</strong> [0,1]
  //   new: <strong>Output:</strong> <span class="example-io">true</span>
  const outputRe = /<strong>Output:<\/strong>\s*(?:<span[^>]*>)?([^\n<]+)/gi;
  let m;
  while ((m = outputRe.exec(rawHtml)) !== null) {
    const raw = decodeHTMLEntities(m[1].trim());
    try {
      const parsed = JSON.parse(raw);
      // Store booleans as strings — JSON true/false are invalid Python literals
      outputs.push(typeof parsed === "boolean" ? String(parsed) : parsed);
    }
    catch { outputs.push(raw); }
  }

  const count = Math.min(sampleTestCases.length, outputs.length);
  return Array.from({ length: count }, (_, i) => {
    const lines = sampleTestCases[i].split("\n");
    const input = {};
    params.forEach((p, j) => {
      try { input[p.name] = JSON.parse(lines[j] ?? "null"); }
      catch { input[p.name] = lines[j] ?? null; }
    });
    return { id: i + 1, input, output: outputs[i] };
  });
}

function buildQuestionJSON(problem) {
  const entryFunction = problem.metaData?.name ?? problem.slug.replace(/-/g, "_");
  return {
    filename: problem.slug,
    title: problem.title,
    difficulty: problem.difficulty,
    tags: [problem.tags[0]].filter(Boolean), // only first tag
    keywords: toKeywords(problem.title, problem.tags),
    description: convertLeetCodeHTML(problem.description ?? "", problem.title),
    entry_function: entryFunction,
    template: generateTemplate(problem.metaData ?? {}),
    solution_text: "",
    solution_code: "",
    prepare: generatePrepare(problem.metaData ?? {}),
    verify: (problem.metaData?.return?.type === "boolean")
      ? "def verify(actual_output, expected_output):\n    if isinstance(expected_output, str):\n        expected_output = expected_output.lower() == 'true'\n    passed = bool(actual_output) == bool(expected_output)\n    return [passed, 'true' if actual_output else 'false']"
      : "def verify(actual_output, expected_output):\n    passed = actual_output == expected_output\n    return [passed, str(actual_output)]",
    test_cases: buildTestCases(problem.description ?? "", problem.sampleTestCases, problem.metaData?.params ?? []),
  };
}

function writeQuestionFiles(problems) {
  for (const p of problems) {
    const dest = path.join(QUESTIONS_DIR, `${p.slug}.json`);
    if (fs.existsSync(dest)) {
      process.stderr.write(`Skipping ${p.slug}.json (already exists)\n`);
      continue;
    }
    fs.writeFileSync(dest, JSON.stringify(buildQuestionJSON(p), null, 2));
    process.stderr.write(`Wrote ${p.slug}.json\n`);
  }
}

// ---------------------------------------------------------------------------
// Course JSON update
// ---------------------------------------------------------------------------

function buildWeekUnit(problems, weekNum) {
  return {
    title: `Week ${weekNum}`,
    description: `Week ${weekNum} — ${problems.map((p) => p.title).join(", ")}.`,
    questions: problems.map((p) => ({
      filename: p.slug,
      urls: [
        {
          url: `https://leetcode.com/problems/${p.slug}/`,
          tooltip: "LeetCode Problem",
          color: "#f59e0b",
          visibleString: "LeetCode",
        },
      ],
      tags: [p.difficulty, p.tags[0]].filter(Boolean), // only first tag
    })),
  };
}

function updateSeen(problems) {
  const seenPath = path.join(__dirname, "seen.txt");
  const existing = fs.existsSync(seenPath)
    ? fs.readFileSync(seenPath, "utf8").trimEnd()
    : "";
  const newSlugs = problems.map((p) => p.slug).join("\n");
  fs.writeFileSync(seenPath, existing ? `${existing}\n${newSlugs}\n` : `${newSlugs}\n`);
  process.stderr.write(`Updated seen.txt with ${problems.length} slugs.\n`);
}

function addWeekToCourse(problems) {
  const courseJSON = JSON.parse(fs.readFileSync(COURSE_FILE, "utf8"));
  if (courseJSON.units?.[`week${WEEK_NUM}`]) {
    process.stderr.write(`Warning: week${WEEK_NUM} already exists in ${path.basename(COURSE_FILE)}, overwriting.\n`);
  }
  courseJSON.units = { [`week${WEEK_NUM}`]: buildWeekUnit(problems, WEEK_NUM), ...courseJSON.units };
  fs.writeFileSync(COURSE_FILE, JSON.stringify(courseJSON, null, 2));
  process.stderr.write(`Added week${WEEK_NUM} to ${path.basename(COURSE_FILE)}\n`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

getNonPremiumQuestions()
  .then(async (allQuestions) => {
    const picked = pickWeekQuestions(allQuestions);
    process.stderr.write(`\nPicked: ${picked.map((q) => q.slug).join(", ")}\n`);

    process.stderr.write("Fetching question details...\n");
    const problems = await enrichQuestions(picked, allQuestions);

    writeQuestionFiles(problems);
    updateSeen(problems);
    addWeekToCourse(problems);

    process.stderr.write("Running sync-index...\n");
    execSync("npm run sync-index", { cwd: path.join(__dirname, ".."), stdio: "inherit" });

    process.stderr.write(`\nDone — added week${WEEK_NUM} to ${courseArg} with ${problems.length} questions.\n`);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
