# Umaira Sadaf — AI Marketing Internship Portfolio

AI Marketing Intern, FlyRank Student Internship Program 2026.
BS Computer Science, Government Graduate College, Vehari.

This repo is the hub for my internship track work: automation scripts,
an AI agent build, and the portfolio site that presents all of it.

**Live site:** https://humerasadaf59-lab.github.io/ai-marketing-internship/
**Contact:** humerasadaf59@gmail.com

---

## Track progress

| Code | Assignment | Type | Status |
|------|------------|------|--------|
| FL-02 | Report Automation | Script | ✅ Complete |
| FL-03 | Email Drafting | Script | ✅ Complete |
| FL-04 | Content Pipeline | Script (workflow) | ✅ Complete |
| FL-05 | Agent Concepts & MCP Basics | Explainer + MCP build | ✅ Complete |

---

## Repo structure

```
.
├── README.md
├── TROUBLESHOOTING.md
├── scripts/
│   ├── fl02_report_automation.py    # CSV data -> AI-written performance report
│   ├── fl03_email_drafting.py       # Campaign brief -> batch-drafted emails per segment
│   └── fl04_content_pipeline.py     # Topic -> outline -> draft -> edit -> formatted content
└── portfolio/
    ├── index.html
    ├── about.html
    ├── projects.html
    ├── contact.html
    └── style.css
```

## Project summaries

### FL-02 — Report Automation
Reads campaign performance data (CSV), computes the stats in Python
(so numbers are always correct), then prompts Claude to turn that summary
into a plain-English report with a headline, key metrics, and one
recommended action. **Pattern:** deterministic math + LLM for narrative.

```bash
python scripts/fl02_report_automation.py --input data/campaign_data.csv --out reports/weekly.md
```

### FL-03 — Email Drafting
Reads a single campaign brief (product, offer, tone, CTA) plus a list of
audience segments, and drafts one personalized email per segment in a
loop, saving both individual files and a combined CSV for review.
**Pattern:** one brief, fan-out to N structured outputs.

```bash
python scripts/fl03_email_drafting.py --brief campaign_brief.json --out drafts/
```

### FL-04 — Content Pipeline
A four-stage prompt chain: outline → draft → edit → format. Each stage's
output feeds the next stage's input, and the sequence is fixed — this is
the canonical **workflow** (not agent) pattern referenced in FL-05.

```bash
python scripts/fl04_content_pipeline.py --topic "Your topic" --format blog --out content/post.md
```

### FL-05 — Agent Concepts & MCP Basics
Explainer covering the workflow-vs-agent distinction (using FL-04 as the
worked example) and a working MCP connector setup, evidenced by screenshots
of tool calls the model couldn't do from chat alone.

---

## Setup (for all scripts)

```bash
pip install anthropic pandas python-dotenv
```

Create a `.env` file in the repo root (never commit this):

```
ANTHROPIC_API_KEY=sk-ant-...
```

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) if a script fails to run.

## Skills

`AI Fluency` · `Marketing` · `LLM` · `ML` · `Prompt Chaining` · `MCP` ·
`Python` · `C++` (OOP, Data Structures)

## License

MIT — feel free to adapt these templates for your own internship track.
