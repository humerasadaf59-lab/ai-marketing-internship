# Troubleshooting

## Python scripts (FL-02, FL-03, FL-04)

**`ANTHROPIC_API_KEY not set`**
Your `.env` file is missing, misnamed, or not in the same folder you're
running the script from. Create `.env` in the repo root:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Confirm `python-dotenv` is installed (`pip install python-dotenv`) and that
you're running the script from the repo root, not from inside `scripts/`.

**`ModuleNotFoundError: No module named 'anthropic'` (or `pandas`, `dotenv`)**
Install dependencies: `pip install anthropic pandas python-dotenv`.
If you use a virtual environment, make sure it's activated first
(`source venv/bin/activate` on Mac/Linux, `venv\Scripts\activate` on Windows).

**`authentication_error` / 401 from the API**
Your API key is invalid, expired, or has extra whitespace/quotes around it
in `.env`. Regenerate a key from the Claude Platform console and paste it
with no quotes: `ANTHROPIC_API_KEY=sk-ant-xxxxx`.

**`rate_limit_error` / 429**
You're sending requests faster than your tier allows. Add a short delay
between calls (`time.sleep(1)`) inside loops like the one in
`fl03_email_drafting.py`, or reduce batch size.

**FL-02: `FileNotFoundError` for the CSV**
Check the `--input` path is relative to where you're running the command,
not relative to the script file. Run `ls` (or `dir` on Windows) to confirm
the file is where you think it is.

**FL-02: report is missing metrics / says "Warning: missing expected columns"**
Your CSV's column headers don't match `date, campaign, impressions, clicks,
conversions, spend`. Either rename your columns to match, or edit the
`required_cols` set and the `summarize_stats()` function to match your
actual column names.

**FL-03: `json.JSONDecodeError` even after the repair pass**
Claude occasionally adds explanatory text outside the JSON despite the
system prompt. Print `raw_text` before parsing to see exactly what came
back, then tighten the system prompt (e.g. add "Do not include any text
before or after the JSON object").

**FL-04: output reads oddly formatted for LinkedIn/Twitter**
Check `FORMAT_SPECS` — if you're getting blog-length output for a
`--format linkedin` request, the model may be ignoring length constraints
on a long topic. Shorten the topic string or add an explicit word-count
reminder in `stage_edit()`'s system prompt.

**Every script: output looks truncated mid-sentence**
`max_tokens` is too low for the content length you asked for. Raise
`MAX_TOKENS` at the top of the script (e.g. from 1500 to 2500 for long
blog posts).

---

## Portfolio site

**Fonts or layout look different from what you expected**
The site loads Google Fonts over the network — if you're viewing the HTML
files locally with no internet connection, fonts will fall back to system
defaults. This doesn't affect layout structure, just typography.

**CSS changes aren't showing up**
Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R) — browsers cache
`style.css` aggressively. Also confirm all four HTML files link to
`style.css` with a relative path (`<link rel="stylesheet" href="style.css">`)
and that `style.css` is in the same folder as the HTML files.

**Nav links (About, Projects, Contact) 404**
This happens if you rename a file but don't update the `href` in every
page's `<nav>`. All four HTML files must live in the same folder for the
relative links (`about.html`, `projects.html`, etc.) to resolve.

**Deploying to GitHub Pages shows a blank page**
In your repo's Settings → Pages, make sure the source folder actually
contains `index.html` at its root (not nested inside `portfolio/portfolio/`
from a bad copy/paste). If your files are inside a `portfolio/` folder,
either set that as the Pages source folder or move the files to repo root.

**Contact form doesn't send anything**
The contact page uses a `mailto:` link by design (no backend/server in this
template) — clicking "Send" opens the visitor's own email client instead of
submitting silently. If you want a real in-page form, you'd need a form
backend service (e.g. Formspree) or a small serverless function; this
template intentionally keeps things static and dependency-free.

---

## Still stuck?
Check the exact error message text — Python errors name the file and line
number where the problem happened. Re-read that specific line before
changing anything else.
