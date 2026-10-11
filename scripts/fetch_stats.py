#!/usr/bin/env python3
"""Fetch profile stats from the GitHub GraphQL API into assets/stats.json.

Standard library only, so the workflow needs no third-party actions or
packages.  It reads a token from GITHUB_TOKEN (the workflow's built-in,
short-lived token is enough) and the account from GH_LOGIN.

    GITHUB_TOKEN=... GH_LOGIN=thesheppard python3 scripts/fetch_stats.py
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com/graphql"
OUT = Path(__file__).resolve().parent.parent / "assets" / "stats.json"

YEAR_FIELDS = """
  totalCommitContributions
  totalPullRequestContributions
  totalPullRequestReviewContributions
  totalIssueContributions
  restrictedContributionsCount
  contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
"""


def graphql(token, query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "arcade-readme-stats",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        messages = "; ".join(e.get("message", "?") for e in payload["errors"])
        raise SystemExit(f"GraphQL error: {messages}")
    return payload["data"]


def fetch_profile(token, login):
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        createdAt
        followers { totalCount }
        contributionsCollection { contributionYears }
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false,
                     first: 100, after: $cursor) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes {
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
      }
    }"""
    cursor, repos, user = None, [], None
    for _ in range(10):  # at most 1000 repos
        data = graphql(token, query, {"login": login, "cursor": cursor})
        user = data["user"]
        if user is None:
            raise SystemExit(f"No such user: {login}")
        page = user["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return user, repos


def fetch_years(token, login, years):
    now = datetime.now(timezone.utc)
    aliases = []
    for y in years:
        start = f"{y}-01-01T00:00:00Z"
        end = now.strftime("%Y-%m-%dT%H:%M:%SZ") if y == now.year else f"{y}-12-31T23:59:59Z"
        aliases.append(f'y{y}: contributionsCollection(from: "{start}", to: "{end}") {{{YEAR_FIELDS}}}')
    query = "query($login: String!) { user(login: $login) { %s } }" % "\n".join(aliases)
    return graphql(token, query, {"login": login})["user"]


def streaks(days):
    """Longest run of active days, and the run ending today (or yesterday)."""
    longest = run = 0
    for _, count in days:
        run = run + 1 if count > 0 else 0
        longest = max(longest, run)
    current = 0
    tail = list(days)
    if tail and tail[-1][1] == 0:  # today isn't over yet
        tail.pop()
    for _, count in reversed(tail):
        if count == 0:
            break
        current += 1
    return current, longest


def main():
    token = os.environ.get("GITHUB_TOKEN")
    login = os.environ.get("GH_LOGIN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", login):
        raise SystemExit("GH_LOGIN is missing or not a valid GitHub login")

    user, repos = fetch_profile(token, login)
    years = sorted(user["contributionsCollection"]["contributionYears"])
    per_year = fetch_years(token, login, years) if years else {}

    totals = dict(commits=0, pull_requests=0, reviews=0, issues=0, private=0, contributions=0)
    calendar = {}
    for y in years:
        c = per_year[f"y{y}"]
        totals["commits"] += c["totalCommitContributions"]
        totals["pull_requests"] += c["totalPullRequestContributions"]
        totals["reviews"] += c["totalPullRequestReviewContributions"]
        totals["issues"] += c["totalIssueContributions"]
        totals["private"] += c["restrictedContributionsCount"]
        totals["contributions"] += c["contributionCalendar"]["totalContributions"]
        for week in c["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                calendar[d["date"]] = d["contributionCount"]

    today = date.today()
    days = sorted((d, n) for d, n in calendar.items() if d <= today.isoformat())
    current, longest = streaks(days)
    year_ago = (today - timedelta(days=365)).isoformat()
    last_year = sum(n for d, n in days if d > year_ago)

    sizes, colours = {}, {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colours[name] = edge["node"]["color"] or "#8b949e"
    total_size = sum(sizes.values()) or 1
    languages = [
        {"name": name, "color": colours[name], "percent": round(size * 100 / total_size, 1)}
        for name, size in sorted(sizes.items(), key=lambda kv: -kv[1])[:8]
    ]

    stats = {
        "login": login,
        "updated": today.isoformat(),
        "member_since": user["createdAt"][:10],
        "followers": user["followers"]["totalCount"],
        "public_repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "contributions_last_year": last_year,
        "current_streak": current,
        "longest_streak": longest,
        **totals,
        "languages": languages,
    }
    OUT.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)}")


if __name__ == "__main__":
    sys.exit(main())
