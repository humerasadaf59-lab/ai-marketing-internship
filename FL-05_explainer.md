# Agent Concepts and MCP Basics — FL-05

**Umaira Sadaf | FlyRank AI Marketing Internship | General AI Fluency Track**

## What's the difference between a workflow and an agent?

A workflow is a pipeline where a human decides the steps in advance, and the
LLM's only job is to fill in the content of each step. The path is fixed
before the first prompt ever runs: step 1 always leads to step 2, step 2
always leads to step 3, no matter what the model outputs along the way. The
model is doing the thinking *inside* each step, but it never decides which
step comes next, whether to skip one, or whether to call an outside tool —
that structure is locked in by whoever built the pipeline.

An agent is different because the model itself controls the path. Instead
of following a script, it plans its own next move based on what just
happened: it can decide to call a tool, read the result, and then decide
*again* what to do next, looping for as many steps as the task needs. The
sequence isn't known in advance — it emerges from the model's own reasoning
as it goes. That autonomy is also the risk: an agent can take a wrong
turn a workflow never could, because nothing is constraining it to a
pre-approved sequence.

## Classifying my FL-04 pipeline

My FL-04 project, the Content Pipeline script, is a **workflow**, not an
agent. It runs four fixed stages in the same order every single time:

1. **Outline** — Claude turns a topic into a bullet-point structure
2. **Draft** — Claude writes a full draft following that outline
3. **Edit** — Claude tightens and polishes the draft
4. **Format** — the script wraps the final text with a header (no model
   call at all — pure templating)

Each stage's output feeds directly into the next stage's input, but the
*order itself* is hardcoded in Python (`stage_outline` → `stage_draft` →
`stage_edit` → `stage_format`). Claude never decides to skip the edit
pass, add a fifth stage, or go back and rewrite the outline if the draft
isn't working. That's the textbook definition of prompt chaining — a
workflow pattern — not agentic behavior.

## What is MCP?

MCP (Model Context Protocol) is the standard that lets an AI model connect
to outside tools and data instead of only working with what's typed into
the chat. The official docs describe it as the "USB-C port for AI
applications" — one common connector instead of a custom integration for
every single service. MCP exposes three kinds of things to a model:

- **Tools** — actions the model can trigger (query an API, send a message,
  run a search)
- **Resources** — data the model can read (files, database rows, documents)
- **Prompts** — reusable prompt templates the server offers for common
  tasks

Without MCP, a model like Claude only knows what's in the conversation. With
an MCP server connected, it can actually reach out and *do* something —
read a real file, pull live data, take an action — and then reason about
the result.

## What FL-04 would need to become an agent

The concrete upgrade: **let the model decide which content format and
which topic angle to pursue, instead of me hardcoding `--topic` and
`--format` as command-line arguments.**

Right now I choose the format (blog, LinkedIn, thread) and hand it a topic
before the script even starts. An agentic version would instead give the
model access to a tool — say, an MCP connector to a shared drive of
campaign briefs or trending keyword data — and let *it* decide: which
topic is worth writing about this week, which format best fits that
topic, and whether the draft needs a second edit pass based on how it
reads. The model would be looping (check the data → decide a topic →
decide a format → draft → self-review → decide if another pass is needed)
instead of running my four fixed stages in a row. That's the shift from
"I chose the path, the model filled it in" to "the model chose the path."

## MCP connector — evidence

I connected the **Google Drive connector** to Claude (claude.ai →
Settings → Connectors) and ran three tasks that required live tool
access rather than chat alone:

1. **"List the files in my Google Drive"** — Claude returned my actual
   recent files and folders with real names, file types, sizes, and
   modified dates (e.g. `FlyRank-Content-Pack-FINAL.md`, 11 KB, updated
   July 23, 2026; a folder shared with me by tutor.saad@gmail.com on
   July 24, 2026). None of this could be guessed — it required a live
   API call into my actual Drive.
2. **"What's in FlyRank-Content-Pack-FINAL.md?"** — Claude opened that
   specific file and summarized its real content (a content marketing
   playbook built from an April 2026 data report analyzing 342,257
   content pieces, with 7 key findings). This proves it can read a
   file's actual contents, not just its name.
3. **"Which of these files was modified most recently?"** — Claude
   pulled the real `modifiedTime` values across my files and correctly
   ranked them, down to the second (e.g. `FlyRank-Content-Pack-FINAL.md`
   Google Doc version at 11:36:54 AM UTC on July 23, 2026), noting
   explicitly that it was reading live metadata rather than guessing.

Screenshots of all three tool calls are attached with this submission.
