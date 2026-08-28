"""Ashby Job Board API: example client.

Pulls live jobs from any Ashby-hosted job board, discovers companies hiring
through Ashby, checks whether a company has an Ashby board at all, and returns
the employer's own published salary data on every row. No API key from the
job boards and no login: give it company names, board slugs, or URLs, or
nothing at all and let it sweep its bundled company directory.

Get a free Apify API token: https://apify.com?fpr=9n7kx3
Actor: https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3

Run it:
    uv sync
    cp .env.example .env      # then paste your token into .env
    uv run python ashby-job-board-api-example.py

Pick one example:
    uv run python ashby-job-board-api-example.py --example jobs
    uv run python ashby-job-board-api-example.py --example companies
    uv run python ashby-job-board-api-example.py --example check
    uv run python ashby-job-board-api-example.py --example new-jobs
    uv run python ashby-job-board-api-example.py --example markdown
    uv run python ashby-job-board-api-example.py --example salary
    uv run python ashby-job-board-api-example.py --example all
"""

import argparse
import os
import sys

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/ashby-job-board-scraper"

# Every run below asks for a small number of rows on purpose. You pay per row
# delivered, so keep the first run cheap, confirm the shape of the data, then
# raise maxJobs once you know it is what you want.
SMALL = 10


def client() -> ApifyClient:
    token = os.getenv("APIFY_TOKEN")
    if not token or token == "your_apify_api_token_here":
        sys.exit(
            "Set APIFY_TOKEN first. Copy .env.example to .env and paste your token.\n"
            "Get one free: https://apify.com?fpr=9n7kx3"
        )
    return ApifyClient(token)


def rows(api: ApifyClient, run_input: dict, limit: int = 5) -> list[dict]:
    """Run the Actor and return the first rows of its dataset.

    apify-client 3.x returns a typed Run object here, not a dict, so the
    dataset id is an attribute. On 2.x this was run["defaultDatasetId"].
    """
    run = api.actor(ACTOR_ID).call(run_input=run_input)
    return list(api.dataset(run.default_dataset_id).iterate_items(limit=limit))


def run_jobs(api: ApifyClient) -> None:
    """Full job records from named boards, filtered before billing.

    Title filters run before anything is charged, so filtered jobs cost
    nothing. Boards accept slugs, company names, or jobs.ashbyhq.com URLs.
    """
    print("\n=== Full job records ===")
    results = rows(api, {
        "companies": ["cerebras", "ramp"],
        "titleKeywords": ["engineer"],
        "maxJobs": SMALL,
    })
    for job in results:
        location = job.get("location") or "location not stated"
        remote = " [remote]" if job.get("isRemote") else ""
        print(f"\n{job.get('title')}{remote}")
        print(f"  {job.get('companyName')} | {location} | {job.get('employmentType')}")
        print(f"  published {str(job.get('datePublished'))[:10]} | pay: {job.get('compensationSummary') or 'not displayed'}")
        print(f"  apply: {job.get('applyUrl')}")
        description = job.get("descriptionMarkdown") or ""
        if description:
            print(f"  {description[:140].strip()}...")


def run_companies(api: ApifyClient) -> None:
    """Discover companies hiring through Ashby, live-verified.

    Mirrors the "Find Companies That Use Ashby ATS" task. Each row carries a
    current open-jobs count; dead boards are skipped and never billed.
    """
    print("\n=== Companies hiring through Ashby ===")
    results = rows(api, {
        "outputMode": "companiesOnly",
        "maxCompanies": SMALL,
        "maxJobs": SMALL,
    }, limit=SMALL)
    for company in results:
        print(f"{company.get('boardToken'):<28} {str(company.get('jobCount')):>5} open  {company.get('boardUrl')}")


def run_check(api: ApifyClient) -> None:
    """Check whether specific companies have an Ashby job board.

    Mirrors the "Check If a Company Has an Ashby Job Board" task. Plain
    company names are matched to board slugs automatically; a miss returns an
    in-band not-found row with did-you-mean suggestions instead of an error.
    """
    print("\n=== Does this company use Ashby? ===")
    results = rows(api, {
        "companies": ["Black Semiconductor", "Ramp", "Notarealcompany Xyz"],
        "outputMode": "companiesOnly",
    }, limit=SMALL)
    for row in results:
        if row.get("resultType") == "company":
            print(f"YES  {row.get('companyName'):<28} {row.get('jobCount')} open jobs  {row.get('boardUrl')}")
        else:
            hint = f"  did you mean: {', '.join(row['didYouMean'])}" if row.get("didYouMean") else ""
            print(f"NO   {row.get('boardToken') or row.get('sourceUrl')}{hint}")


def run_new_jobs(api: ApifyClient) -> None:
    """Only jobs published in the last week, with zero state to manage.

    Mirrors the "Track New Ashby Job Postings Daily" task. The cutoff
    compares against the employer's own publishedAt timestamp, so a daily
    schedule with publishedAfter set to 25h becomes a new-roles feed.
    """
    print("\n=== Jobs published in the last 7 days ===")
    results = rows(api, {
        "companies": ["openai", "ramp", "notion"],
        "publishedAfter": "7d",
        "maxJobs": SMALL,
    }, limit=SMALL)
    if not results:
        print("No postings published in the window. Widen publishedAfter and rerun.")
    for job in results:
        print(f"{str(job.get('datePublished'))[:10]}  {job.get('title')}  ({job.get('companyName')})")


def run_markdown(api: ApifyClient) -> None:
    """Descriptions as clean Markdown, ready for an LLM.

    Mirrors the "Ashby Jobs as Markdown for AI Agents" task. Markdown is the
    default format; hand the rows straight to a model without stripping HTML
    first.
    """
    print("\n=== Markdown descriptions for AI pipelines ===")
    results = rows(api, {
        "companies": ["openai"],
        "includeDescriptionMarkdown": True,
        "maxJobs": 3,
    }, limit=3)
    for job in results:
        print(f"\n## {job.get('title')} ({job.get('companyName')})")
        print((job.get("descriptionMarkdown") or "")[:300].strip(), "...")


def run_salary(api: ApifyClient) -> None:
    """Postings with the employer's own published pay ranges.

    Mirrors the "Scrape Ashby Jobs With Salary Data" task. Ashby boards
    publish structured compensation; every row carries flat salaryMin,
    salaryMax, salaryCurrency, and salaryPeriod columns plus an offersEquity
    flag, so there is nothing to parse.
    """
    print("\n=== Jobs with salary data ===")
    results = rows(api, {
        "companies": ["ramp", "deel"],
        "maxJobs": 20,
    }, limit=20)
    for job in results:
        if job.get("salaryMin") is None:
            continue
        equity = " + equity" if job.get("offersEquity") else ""
        band = (f"{job.get('salaryCurrency') or ''} {job.get('salaryMin'):,.0f} - "
                f"{job.get('salaryMax'):,.0f} per {job.get('salaryPeriod')}{equity}")
        print(f"{job.get('title')[:48]:<50} {band}")


EXAMPLES = {
    "jobs": run_jobs,
    "companies": run_companies,
    "check": run_check,
    "new-jobs": run_new_jobs,
    "markdown": run_markdown,
    "salary": run_salary,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ashby Job Board API examples")
    parser.add_argument("--example", choices=[*EXAMPLES, "all"], default="jobs",
                        help="Which example to run (default: jobs)")
    args = parser.parse_args()

    api = client()
    chosen = list(EXAMPLES) if args.example == "all" else [args.example]
    for name in chosen:
        EXAMPLES[name](api)


if __name__ == "__main__":
    main()
