#!/usr/bin/env python3
"""Fetch YouTube's most-popular chart and compute velocity metrics.

Cumulative view counts cannot distinguish a video that exploded overnight
from one that accumulated views over a week, so this script normalizes by
time since publication. Standard library only, so it runs in any sandbox.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://www.googleapis.com/youtube/v3/videos"
# The API rejects maxResults above 50 per page.
PAGE_LIMIT = 50


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def to_int(value):
    # Channels can hide like/comment counts; the field is then absent.
    return int(value) if value is not None else None


def ratio(part, whole):
    if part is None or not whole:
        return None
    return round(part / whole, 4)


def compute_metrics(item, now):
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    views = to_int(stats.get("viewCount"))
    likes = to_int(stats.get("likeCount"))
    comments = to_int(stats.get("commentCount"))
    published = parse_time(snippet["publishedAt"])
    # Floor at one hour so a just-published video does not divide by ~0.
    hours = max((now - published).total_seconds() / 3600, 1.0)
    return {
        "video_id": item.get("id"),
        "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        "title": snippet.get("title"),
        "channel": snippet.get("channelTitle"),
        "published_at": snippet.get("publishedAt"),
        "hours_since_publish": round(hours, 1),
        "views": views,
        "likes": likes,
        "comments": comments,
        "views_per_hour": round(views / hours) if views is not None else None,
        "like_rate": ratio(likes, views),
        "comment_rate": ratio(comments, views),
    }


def fetch_items(api_key, region, limit):
    items = []
    page_token = None
    while len(items) < limit:
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": min(PAGE_LIMIT, limit - len(items)),
        }
        if page_token:
            params["pageToken"] = page_token
        # Send the key as a header so it never appears in URLs or proxy logs.
        request = urllib.request.Request(
            f"{API_URL}?{urllib.parse.urlencode(params)}",
            headers={"X-Goog-Api-Key": api_key, "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        items.extend(payload.get("items", []))
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return items[:limit]


def build_rows(items, now):
    rows = [compute_metrics(item, now) for item in items]
    rows.sort(key=lambda row: row["views_per_hour"] or 0, reverse=True)
    return rows


def format_table(rows):
    def pct(value):
        return "-" if value is None else f"{value * 100:.1f}%"

    def num(value):
        return "-" if value is None else f"{value:,}"

    lines = [
        "| # | views/hour | views | hours | like rate | title | channel | url |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(rows, 1):
        title = (row["title"] or "").replace("|", "/")
        channel = (row["channel"] or "").replace("|", "/")
        lines.append(
            f"| {index} | {num(row['views_per_hour'])} | {num(row['views'])} "
            f"| {row['hours_since_publish']} | {pct(row['like_rate'])} "
            f"| {title} | {channel} | {row['url']} |"
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List YouTube most-popular videos ranked by views per hour."
    )
    parser.add_argument("--region", default="KR", help="ISO 3166-1 region code (default: KR)")
    parser.add_argument("--max", type=int, default=50, help="number of videos (default: 50)")
    parser.add_argument("--format", choices=["json", "table"], default="json")
    parser.add_argument(
        "--input",
        help="read a saved videos.list JSON response instead of calling the API",
    )
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            items = json.load(handle).get("items", [])[: args.max]
    else:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            print(
                "YOUTUBE_API_KEY is not set. Skip this script and collect "
                "trends with web search instead.",
                file=sys.stderr,
            )
            return 2
        try:
            items = fetch_items(api_key, args.region, args.max)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            print(f"YouTube API error {error.code}: {detail}", file=sys.stderr)
            return 1
        except urllib.error.URLError as error:
            print(f"Network error: {error.reason}", file=sys.stderr)
            return 1

    rows = build_rows(items, now)
    if args.format == "table":
        print(format_table(rows))
    else:
        print(json.dumps(
            {"fetched_at": now.isoformat(), "region": args.region, "videos": rows},
            ensure_ascii=False,
            indent=2,
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
