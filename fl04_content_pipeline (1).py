"""
FL-04: Content Pipeline
=========================
Template for a multi-stage content generation pipeline: brief -> outline ->
draft -> edit/polish -> formatted output (Markdown, ready to paste into a
CMS or social scheduler).

This is the textbook WORKFLOW example from Anthropic's "Building Effective
Agents": prompt chaining. Each stage is a separate, fixed call to Claude,
and the output of one stage becomes the input of the next. The pipeline
itself never decides to skip a stage, add a new one, or call an external
tool — a human (or FL-02/FL-03) pre-defined the whole path.

This is the pipeline referenced in FL-05: to turn it into an AGENT, you'd
let the model decide things like "does this topic need a fact-check web
search before drafting?" or "should this go through a second edit pass?"
dynamically, rather than always running the same four fixed stages.

Setup
-----
    pip install anthropic python-dotenv

    # .env
    ANTHROPIC_API_KEY=sk-ant-...

Usage
-----
    python fl04_content_pipeline.py --topic "5 signs your team needs an AI workflow audit" \
        --format blog --out content/post_01.md
"""

import argparse
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"
MAX_TOKENS = 1500

FORMAT_SPECS = {
    "blog": "a 600-800 word blog post with an H1, 3-4 H2 subheadings, and a short CTA at the end",
    "linkedin": "a LinkedIn post, 150-250 words, short punchy paragraphs, no hashtag spam (max 3)",
    "twitter": "a 5-tweet thread, each tweet under 280 characters, numbered 1/ 2/ 3...",
}


def stage_outline(client: Anthropic, topic: str, content_format: str) -> str:
    """Stage 1: outline. Fixed step — always runs first, always the same shape."""
    spec = FORMAT_SPECS[content_format]
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system="You are a content strategist. Produce a tight bullet-point outline only — no prose.",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\nTarget format: {spec}\n\n"
                       f"Write an outline: a hook idea, 3-5 main points, and a closing CTA idea.",
        }],
    )
    return "".join(b.text for b in message.content if b.type == "text")


def stage_draft(client: Anthropic, topic: str, content_format: str, outline: str) -> str:
    """Stage 2: draft. Always runs second, always fed the outline from stage 1."""
    spec = FORMAT_SPECS[content_format]
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="You are a marketing copywriter. Write in a clear, confident, non-hypey voice.",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\nFormat: {spec}\n\nOutline to follow:\n{outline}\n\n"
                       f"Write the full first draft now, following the outline.",
        }],
    )
    return "".join(b.text for b in message.content if b.type == "text")


def stage_edit(client: Anthropic, draft: str, content_format: str) -> str:
    """Stage 3: edit/polish. Always runs third, always a fixed editing pass."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=(
            "You are a strict copy editor. Tighten wording, cut filler and clichés "
            "(no 'in today's fast-paced world', no 'unlock', no 'game-changer'), "
            "fix any format spec violations, and keep the meaning intact. "
            "Return only the final edited text."
        ),
        messages=[{
            "role": "user",
            "content": f"Format target: {FORMAT_SPECS[content_format]}\n\nDraft to edit:\n{draft}",
        }],
    )
    return "".join(b.text for b in message.content if b.type == "text")


def stage_format(edited_text: str, topic: str, content_format: str) -> str:
    """Stage 4: formatting. Deterministic — no model call needed, just templating."""
    header = f"<!-- topic: {topic} | format: {content_format} -->\n\n"
    return header + edited_text.strip() + "\n"


def run_pipeline(client: Anthropic, topic: str, content_format: str) -> str:
    print("Stage 1/4: outline...")
    outline = stage_outline(client, topic, content_format)

    print("Stage 2/4: draft...")
    draft = stage_draft(client, topic, content_format, outline)

    print("Stage 3/4: edit...")
    edited = stage_edit(client, draft, content_format)

    print("Stage 4/4: format...")
    final = stage_format(edited, topic, content_format)

    return final


def main():
    parser = argparse.ArgumentParser(description="FL-04 Content Pipeline")
    parser.add_argument("--topic", required=True, help="Content topic / brief")
    parser.add_argument("--format", choices=FORMAT_SPECS.keys(), default="blog")
    parser.add_argument("--out", default="content/output.md")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set. Add it to your .env file or environment.")

    client = Anthropic(api_key=api_key)
    final_text = run_pipeline(client, args.topic, args.format)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_text, encoding="utf-8")
    print(f"Saved final content to {out_path}")


if __name__ == "__main__":
    main()
