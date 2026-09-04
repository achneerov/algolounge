const slugs = process.argv.slice(2);

if (slugs.length === 0) {
  console.error("Usage: node fetch-details.mjs <slug> [...slugs]");
  process.exit(1);
}

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

async function graphql(query, variables, referer) {
  const body = JSON.stringify({ query, variables });
  const response = await fetch("https://leetcode.com/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0",
      Referer: referer ?? "https://leetcode.com/problemset/all/",
    },
    body,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

const details = [];

for (const slug of slugs) {
  const json = await graphql(
    DETAIL_QUERY,
    { titleSlug: slug },
    `https://leetcode.com/problems/${slug}/`
  );
  const question = json?.data?.question;

  if (!question) {
    throw new Error(`No detail data for ${slug}`);
  }

  details.push({ slug, ...question });
}

process.stdout.write(`${JSON.stringify(details, null, 2)}\n`);

