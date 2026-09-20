"""
Weekly job: pull real estate agent topics from Reddit's public API and public
RSS feeds, then append unused rows to Control Hub > Content Ideas.

Does not scrape Zillow, Realtor.com, or MLS-derived data.

Required GitHub Actions secrets:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
  GOOGLE_SERVICE_ACCOUNT_JSON, CONTROL_HUB_SHEET_ID
"""

import json
import os
import re

import feedparser
import gspread
import praw
from google.oauth2.service_account import Credentials

SUBREDDITS = ["realtors", "RealEstate", "realtorsofinstagram"]
POST_LIMIT_PER_SUBREDDIT = 25
RSS_FEEDS = []
KEYWORDS = [
    "lead",
    "listing",
    "closing",
    "buyer",
    "seller",
    "commission",
    "contract",
    "inspection",
    "appraisal",
    "referral",
    "follow up",
    "crm",
    "transaction",
    "pipeline",
]
CONTENT_IDEAS_TAB = "Content Ideas"


def is_relevant(title: str) -> bool:
    lower = title.lower()
    return any(keyword in lower for keyword in KEYWORDS)


def clean_title(title: str) -> str:
    return re.sub(r"^\[.*?\]\s*", "", title).strip()


def fetch_reddit_topics() -> list[str]:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ.get("REDDIT_USER_AGENT", "content-idea-fetcher/1.0"),
    )
    topics = []
    for sub_name in SUBREDDITS:
        for post in reddit.subreddit(sub_name).top(
            time_filter="week", limit=POST_LIMIT_PER_SUBREDDIT
        ):
            title = post.title
            if title and is_relevant(title):
                topics.append(clean_title(title))
    return topics


def fetch_rss_topics() -> list[str]:
    topics = []
    for feed_url in RSS_FEEDS:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            title = getattr(entry, "title", "")
            if title and is_relevant(title):
                topics.append(clean_title(title))
    return topics


def get_sheet_client():
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    return gspread.authorize(creds)


def main():
    all_topics = fetch_reddit_topics() + fetch_rss_topics()
    client = get_sheet_client()
    sheet = client.open_by_key(os.environ["CONTROL_HUB_SHEET_ID"])
    worksheet = sheet.worksheet(CONTENT_IDEAS_TAB)

    existing_rows = worksheet.get_all_records()
    existing_topics = {
        row["Topic"].strip().lower() for row in existing_rows if row.get("Topic")
    }

    seen = set()
    new_rows = []
    next_id = len(existing_rows) + 1
    for topic in all_topics:
        key = topic.strip().lower()
        if key and key not in existing_topics and key not in seen:
            seen.add(key)
            new_rows.append([f"T{next_id:04d}", topic, "No", ""])
            next_id += 1

    if new_rows:
        worksheet.append_rows(new_rows, value_input_option="USER_ENTERED")
        print(f"Added {len(new_rows)} new content ideas.")
    else:
        print("No new, relevant topics found this run.")


if __name__ == "__main__":
    main()
