"""
FL-02: Report Automation
=========================
Template for turning raw marketing/campaign data (CSV) into a written,
AI-generated performance report (Markdown, optionally exported to PDF/DOCX).

This is a WORKFLOW, not an agent: the steps below always run in the same
fixed order (load -> summarize stats -> prompt Claude -> save). Claude fills
in each step, but the pipeline itself does not decide its own path.

Setup
-----
    pip install anthropic pandas python-dotenv

    # .env file (never commit this):
    ANTHROPIC_API_KEY=sk-ant-...

Usage
-----
    python fl02_report_automation.py --input data/campaign_data.csv --out reports/weekly_report.md
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"          # swap to claude-haiku-4-5-20251001 for a cheaper/faster draft pass
MAX_TOKENS = 2000

REPORT_SYSTEM_PROMPT = """You are a marketing analyst writing a concise, plain-English
performance report for a non-technical stakeholder. Structure your output as:

1. Headline summary (2-3 sentences, lead with the single most important trend)
2. Key metrics table (in Markdown)
3. What went well
4. What needs attention
5. One recommended action for next week

Be specific and cite the actual numbers you were given. Do not invent data
that isn't in the input. Keep the whole report under 500 words."""


def load_data(input_path: str) -> pd.DataFrame:
    """Step 1: load and validate the raw data."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Input CSV is empty — nothing to report on.")

    required_cols = {"date", "campaign", "impressions", "clicks", "conversions", "spend"}
    missing = required_cols - set(df.columns.str.lower())
    if missing:
        print(f"Warning: missing expected columns {missing}. "
              f"Continuing with whatever columns are present.", file=sys.stderr)

    return df


def summarize_stats(df: pd.DataFrame) -> str:
    """Step 2: compute deterministic summary stats BEFORE calling the model.

    Doing the arithmetic in Python (not asking the LLM to add up numbers)
    keeps the report accurate — Claude explains and contextualizes the
    numbers, it doesn't calculate them.
    """
    lines = [f"Rows: {len(df)}", f"Date range: {df['date'].min()} to {df['date'].max()}"
             if "date" in df.columns else "Date range: n/a"]

    for col in ["impressions", "clicks", "conversions", "spend"]:
        if col in df.columns:
            lines.append(f"Total {col}: {df[col].sum():,.2f}")

    if {"clicks", "impressions"}.issubset(df.columns) and df["impressions"].sum() > 0:
        ctr = df["clicks"].sum() / df["impressions"].sum() * 100
        lines.append(f"Overall CTR: {ctr:.2f}%")

    if {"conversions", "clicks"}.issubset(df.columns) and df["clicks"].sum() > 0:
        cvr = df["conversions"].sum() / df["clicks"].sum() * 100
        lines.append(f"Overall conversion rate: {cvr:.2f}%")

    if "campaign" in df.columns:
        top = df.groupby("campaign")["conversions"].sum().sort_values(ascending=False).head(3)
        lines.append("Top campaigns by conversions:")
        lines.extend(f"  - {name}: {val:,.0f}" for name, val in top.items())

    return "\n".join(lines)


def generate_report(stats_summary: str, client: Anthropic) -> str:
    """Step 3: send the pre-computed stats to Claude to turn into prose."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=REPORT_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here is this period's campaign data summary:\n\n{stats_summary}\n\n"
                           f"Write the report.",
            }
        ],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def save_report(report_text: str, out_path: str) -> None:
    """Step 4: save with a timestamp header."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = f"# Marketing Performance Report\n*Generated {datetime.now():%Y-%m-%d %H:%M}*\n\n"
    out.write_text(header + report_text, encoding="utf-8")
    print(f"Report saved to {out}")


def main():
    parser = argparse.ArgumentParser(description="FL-02 Report Automation")
    parser.add_argument("--input", required=True, help="Path to campaign data CSV")
    parser.add_argument("--out", default="reports/report.md", help="Output Markdown path")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set. Add it to your .env file or environment.")

    client = Anthropic(api_key=api_key)

    df = load_data(args.input)
    stats_summary = summarize_stats(df)
    print("--- Stats fed to Claude ---")
    print(stats_summary)
    print("---------------------------")

    report = generate_report(stats_summary, client)
    save_report(report, args.out)


if __name__ == "__main__":
    main()
