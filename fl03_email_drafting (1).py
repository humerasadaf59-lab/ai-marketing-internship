"""
FL-03: Email Drafting
======================
Template for batch-drafting marketing emails from a campaign brief +
a list of audience segments. Reads a JSON brief, calls Claude once per
segment, and writes each draft to its own file plus a combined CSV
for easy review/export.

Like FL-02, this is a WORKFLOW: brief -> loop over segments -> draft ->
save. The sequence is fixed; Claude only fills in the content of each step.

Setup
-----
    pip install anthropic python-dotenv

    # .env
    ANTHROPIC_API_KEY=sk-ant-...

Usage
-----
    python fl03_email_drafting.py --brief campaign_brief.json --out drafts/
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"
MAX_TOKENS = 900

EMAIL_SYSTEM_PROMPT = """You are a marketing copywriter drafting a single
promotional email. Rules:

- Output valid JSON only: {"subject": "...", "preview_text": "...", "body": "..."}
- Subject line under 60 characters, no clickbait or ALL CAPS
- Body: 120-180 words, one clear call to action
- Match the requested tone exactly
- Personalize using the segment's stated pain point / interest
- Never invent discounts, prices, or claims not present in the brief"""


# Example campaign_brief.json shape:
# {
#   "product": "AI-powered CRM dashboard",
#   "offer": "14-day free trial, no credit card",
#   "tone": "confident, friendly, not salesy",
#   "cta_url": "https://example.com/trial",
#   "segments": [
#     {"name": "cold_leads", "pain_point": "manually tracking leads in spreadsheets"},
#     {"name": "trial_expired", "pain_point": "lost momentum after their free trial ended"},
#     {"name": "warm_demo_booked", "pain_point": "wants to confirm the demo is worth their time"}
#   ]
# }


def load_brief(brief_path: str) -> dict:
    path = Path(brief_path)
    if not path.exists():
        raise FileNotFoundError(f"Brief not found: {brief_path}")
    brief = json.loads(path.read_text(encoding="utf-8"))
    for field in ("product", "offer", "tone", "cta_url", "segments"):
        if field not in brief:
            raise ValueError(f"Brief is missing required field: {field}")
    if not brief["segments"]:
        raise ValueError("Brief has no audience segments to draft for.")
    return brief


def build_user_prompt(brief: dict, segment: dict) -> str:
    return (
        f"Product: {brief['product']}\n"
        f"Offer: {brief['offer']}\n"
        f"Tone: {brief['tone']}\n"
        f"CTA URL: {brief['cta_url']}\n"
        f"Audience segment: {segment['name']}\n"
        f"Segment pain point / context: {segment['pain_point']}\n\n"
        f"Draft the email for this segment now."
    )


def draft_email(client: Anthropic, brief: dict, segment: dict) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=EMAIL_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(brief, segment)}],
    )
    raw_text = "".join(block.text for block in message.content if block.type == "text")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Model occasionally wraps JSON in prose or code fences — do one cheap repair pass
        cleaned = raw_text.strip().strip("`").replace("json\n", "", 1)
        return json.loads(cleaned)


def save_drafts(drafts: list[dict], out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    csv_path = out / "all_drafts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["segment", "subject", "preview_text", "body"])
        writer.writeheader()
        for d in drafts:
            writer.writerow(d)
            individual_path = out / f"{d['segment']}.txt"
            individual_path.write_text(
                f"Subject: {d['subject']}\nPreview: {d['preview_text']}\n\n{d['body']}",
                encoding="utf-8",
            )

    print(f"Saved {len(drafts)} drafts to {out}/ (see all_drafts.csv)")


def main():
    parser = argparse.ArgumentParser(description="FL-03 Email Drafting")
    parser.add_argument("--brief", required=True, help="Path to campaign_brief.json")
    parser.add_argument("--out", default="drafts/", help="Output directory")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set. Add it to your .env file or environment.")

    client = Anthropic(api_key=api_key)
    brief = load_brief(args.brief)

    drafts = []
    for segment in brief["segments"]:
        print(f"Drafting for segment: {segment['name']}...")
        draft = draft_email(client, brief, segment)
        draft["segment"] = segment["name"]
        drafts.append(draft)

    save_drafts(drafts, args.out)


if __name__ == "__main__":
    main()
