# 🟣 Ashby Job Board API: jobs, companies, and salary data

A Python and MCP quick-start for the **Ashby job board API** on Apify. Scrape Ashby jobs from any Ashby-hosted board, find companies that use Ashby, check whether a company has a board at all, and get the employer's own published salary ranges on every row, all without an API key or a login.

- Actor: [Ashby Job Board API on Apify](https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3)
- Input schema: [input parameters](https://apify.com/johnvc/ashby-job-board-scraper/input-schema?fpr=9n7kx3)
- Get a free API token: [apify.com](https://apify.com?fpr=9n7kx3)

Ashby is the ATS behind the careers pages of many of the fastest-growing companies, including OpenAI, Ramp, Notion, Linear, and Cerebras. This Actor reads the public API that powers every jobs.ashbyhq.com board live at run time, so every row reflects what the employer's board says right now, not what an index remembered last week. Give it company names, board slugs, or URLs, or give it nothing and let it sweep a bundled directory of 2,700+ verified boards.

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The **Ashby job board API** takes company names ("Black Semiconductor"), board slugs (cerebras), or any jobs.ashbyhq.com URL, and returns structured job rows: `title`, `companyName`, `department`, `team`, `employmentType`, `workplaceType`, `isRemote`, `location`, `countriesDerived`, `datePublished`, `compensationSummary`, flat `salaryMin` / `salaryMax` / `salaryCurrency` / `salaryPeriod` columns, an `offersEquity` flag, and the description as Markdown by default. Set `publishedAfter` to a window like `25h` and only postings added since then come back, which is how the "Track New Ashby Job Postings Daily" task turns a schedule into a new-roles feed with zero state. Switch `outputMode` to `companiesOnly` and you get one row per company hiring through Ashby with a live open-jobs count, the fastest way to find companies that use Ashby. Filters run before billing, so a filtered job costs nothing.

## Quick Start

Prerequisites: Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and a free Apify API token from [apify.com](https://apify.com?fpr=9n7kx3).

```bash
git clone https://github.com/johnisanerd/Apify-Ashby-Job-Board-API.git
cd Apify-Ashby-Job-Board-API
uv sync
cp .env.example .env          # paste your token into .env
uv run python ashby-job-board-api-example.py
```

Each example is a separate flag:

```bash
uv run python ashby-job-board-api-example.py --example jobs       # full job records
uv run python ashby-job-board-api-example.py --example companies  # company discovery
uv run python ashby-job-board-api-example.py --example check      # does this company use Ashby?
uv run python ashby-job-board-api-example.py --example new-jobs   # new-postings feed
uv run python ashby-job-board-api-example.py --example markdown   # LLM-ready descriptions
uv run python ashby-job-board-api-example.py --example salary     # postings with pay data
uv run python ashby-job-board-api-example.py --example all
```

Every example asks for a small number of rows on purpose. You pay per row delivered, so confirm the shape of the data first, then raise `maxJobs`.

## Why use this API

**Live, not indexed.** One request per board against the public API means every row is what the employer's board says right now. No stale index, no ghost jobs.

**Salary data on the base row.** Ashby employers publish structured compensation. Every job row carries the raw structure (`salaryRaw`), a normalized range (`salaryDerived`), flat `salaryMin` / `salaryMax` / `salaryCurrency` / `salaryPeriod` columns ready for CSV, per-tier ranges (`salaryTiers`), and an `offersEquity` flag.

**Company checking with did-you-mean.** Type a company name the way you know it; the Actor matches it to its board slug automatically, and a miss returns a clear not-found row with the closest known slugs.

**Discovery built in.** A bundled directory of 2,700+ verified Ashby boards powers `companiesOnly` mode and empty-input sweeps. Nobody else combines the directory and the live reader in one tool.

**New postings without state.** Every Ashby job carries the employer's own publish timestamp, so `publishedAfter: "25h"` on a daily schedule is a complete new-roles feed. No seen-lists, no delta stores.

**Pay for exactly what you receive.** No start fee, no minimum. The base job record is one event, salary data included; Markdown, HTML, text, the company-data enrichment, and the run report are add-ons billed only on rows that carry them.

## Recipes

Ready-made configurations with their own Store landing pages:

- [Find Companies That Use Ashby ATS](https://apify.com/johnvc/ashby-job-board-scraper/examples/find-companies-using-ashby?fpr=9n7kx3)
- [Scrape Ashby Jobs With Salary Data](https://apify.com/johnvc/ashby-job-board-scraper/examples/ashby-jobs-with-salary-data?fpr=9n7kx3)
- [Track New Ashby Job Postings Daily](https://apify.com/johnvc/ashby-job-board-scraper/examples/track-new-ashby-jobs-daily?fpr=9n7kx3)
- [Ashby Jobs as Markdown for AI Agents](https://apify.com/johnvc/ashby-job-board-scraper/examples/ashby-jobs-markdown-ai-agents?fpr=9n7kx3)
- [Check If a Company Has an Ashby Job Board](https://apify.com/johnvc/ashby-job-board-scraper/examples/check-company-ashby-board?fpr=9n7kx3)

**Schedule tip.** Save your input as a Task in the [Apify Console](https://console.apify.com), set `publishedAfter` to `25h`, and schedule it daily. From then on the dataset only ever contains postings added since the last run, so the pipeline stays current without anyone touching it.

## Usage Examples

Basic, matching the default run:

```json
{
  "companies": ["cerebras", "ramp"],
  "titleKeywords": ["engineer"],
  "maxJobs": 10
}
```

Advanced, remote roles with the company-data enrichment and a report:

```json
{
  "companies": ["openai", "ramp", "deel"],
  "remoteOnly": true,
  "employmentTypes": ["FullTime"],
  "includeCompanyData": true,
  "report": "markdown",
  "maxJobs": 100
}
```

## Input Parameters

Every parameter is optional.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `companies` | array | `["cerebras"]` | Company names, board slugs, or any board, embed, or single-job URL, mixed freely. Empty sweeps the bundled directory. |
| `startUrls` | array | empty | Same values in URL-list form; merged with `companies`. |
| `outputMode` | string | `jobs` | `jobs` for full records, `urlsOnly` for the cheap index, `companiesOnly` for discovery. |
| `discoveryQuery` | string | empty | Text match over the company directory for discovery and sweeps. |
| `verifyCompanies` | boolean | `true` | Live-probe each discovered company; dead boards are never billed. |
| `titleKeywords` | array | empty | Keep jobs whose title contains any of these. Runs before billing. |
| `departments` | array | empty | Keep jobs in matching departments or teams. |
| `locationKeywords` | array | empty | Keep jobs in matching locations or addresses. |
| `employmentTypes` | array | empty | Keep only these types: FullTime, PartTime, Intern, Contract, Temporary. |
| `remoteOnly` | boolean | `false` | Keep only jobs the board marks as remote. |
| `publishedAfter` | string | empty | New postings: `24h`, `7d`, `2w`, or an ISO date. |
| `includeDescriptionMarkdown` | boolean | `true` | Add the description as Markdown (paid add-on). |
| `includeDescriptionHtml` | boolean | `false` | Add the original HTML (paid add-on). |
| `includeDescriptionText` | boolean | `false` | Add the board's plain text (paid add-on). |
| `includeCompanyData` | boolean | `false` | Enrich rows from the job page: company website, logo, remote-eligibility countries, deadline, direct-apply (paid add-on). |
| `report` | string | `none` | Write a Markdown or HTML run report to the key-value store (paid add-on). |
| `maxCompanies` | integer | `25` | Cap on companies in sweeps and discovery. |
| `maxJobsPerCompany` | integer | `0` | Per-board cap, 0 means all. |
| `maxJobs` | integer | `100` | Whole-run cap, the main cost control. |
| `maxConcurrency` | integer | `5` | Parallel discovery and enrichment requests. |
| `proxyConfiguration` | object | direct | Optional Apify Proxy settings; direct connections work. |

## Output Format

A full job record:

```json
{
  "resultType": "job",
  "id": "34413f8d-26bf-4bbc-8ade-eb309a0e2245",
  "title": "Security Engineer, Cloud",
  "companyName": "Ramp",
  "boardToken": "ramp",
  "url": "https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245",
  "applyUrl": "https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245/application",
  "department": "Engineering",
  "team": "Backend",
  "location": "New York, NY (HQ)",
  "countriesDerived": ["United States", "Canada"],
  "isRemote": true,
  "workplaceType": "Hybrid",
  "employmentType": "FullTime",
  "datePublished": "2026-04-07",
  "compensationSummary": "$211.4K - $290.6K",
  "salaryMin": 211400,
  "salaryMax": 290600,
  "salaryCurrency": "USD",
  "salaryPeriod": "year",
  "offersEquity": true,
  "descriptionMarkdown": "# About Ramp\n\nRamp is building...",
  "source": "ashby",
  "scrapedAt": "2026-08-27T16:00:00Z"
}
```

A discovered company row:

```json
{
  "resultType": "company",
  "boardToken": "ramp",
  "boardUrl": "https://jobs.ashbyhq.com/ramp",
  "companyName": "Ramp",
  "jobCount": 135,
  "live": true,
  "verifiedAt": "2026-08-27T16:00:00Z"
}
```

<!-- ask-ai:start -->
## 🤖 Ask an AI assistant about this Actor

Open a ready-to-send prompt about the Ashby Job Board API in the AI of your choice:

- 💬 [ChatGPT](https://chatgpt.com/?q=Using%20the%20Ashby%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Scrape%20Ashby%20Jobs%20With%20Salary%20Data%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🧠 [Claude](https://claude.ai/new?q=Using%20the%20Ashby%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Scrape%20Ashby%20Jobs%20With%20Salary%20Data%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🔍 [Perplexity](https://www.perplexity.ai/search?q=Using%20the%20Ashby%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Scrape%20Ashby%20Jobs%20With%20Salary%20Data%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🅒 [Copilot](https://copilot.microsoft.com/?q=Using%20the%20Ashby%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Scrape%20Ashby%20Jobs%20With%20Salary%20Data%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
<!-- ask-ai:end -->

## People also search for

### Is this an Ashby scraper?

Under the hood it reads the same public endpoint a scraper would. What you get is an API: structured JSON on demand, filters, stable field names, and no HTML unless you ask for it. If you have been maintaining your own scrape of Ashby boards, this is the version where someone else maintains the parser.

### What is jobs.ashbyhq.com?

The domain where Ashby hosts its customers' public job boards; every company on Ashby gets a page at jobs.ashbyhq.com/companyname. Paste any of those URLs into this Actor, board or single job, and it returns the structured data behind the page.

### Do I need an Ashby API key?

No. Ashby's authenticated APIs are for employers. This Actor uses only the public job posting layer, so there is nothing to sign up for.

### How do I find companies that use Ashby?

Set `outputMode` to `companiesOnly`. You get one row per company with its board slug, a live open-jobs count, and the board URL. The `--example companies` script does exactly this, and `--example check` verifies a specific list of names.

### How do I get Ashby salary data?

It is on the base row. Employers that display compensation publish structured ranges; those arrive as flat `salaryMin` / `salaryMax` / `salaryCurrency` / `salaryPeriod` columns plus `offersEquity`, with the raw structure in `salaryRaw`. The `--example salary` script prints a pay table.

### How do I get only new job postings?

Set `publishedAfter` to a window like `24h` or an ISO date. The Actor uses the employer's own publish timestamps, so there is no state to manage between runs.

### How do I use the Ashby job board API from Python?

Clone this repo, run `uv sync`, put your Apify token in `.env`, and run the example. The `rows()` helper shows the whole pattern: call the Actor, then iterate the dataset.

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Ashby Job Board API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Ashby Job Board API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Ashby Job Board API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/ashby-job-board-scraper`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper`, using OAuth when prompted.
5. Ask Claude to run the Ashby Job Board API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Ashby Job Board API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

Made with care by [johnvc on Apify](https://apify.com/johnvc?fpr=9n7kx3).

Last Updated: 2026.09.28
