# Copilot Instructions — jetson-orin-assistant

## AI Credit Usage (Cost Optimization)

Under token-based billing, every token in the context window is re-sent each turn and output is billed several times more than input. Minimize both automatically.

**Output (most expensive):**
- **Answer only what was asked.** No preamble, no restating the question, no filler, no closing summaries unless requested.
- **Code/result first.** Return the value or code directly; explain only if requested or needed for correctness.
- **Don't re-dump unchanged content.** Show only changed lines or a short diff — never paste back whole files or large blocks.
- **Keep explanations short.** A sentence or two over a paragraph; a short list over prose.
- **Default to Medium reasoning effort.** Reserve High/Max for hard debugging or novel design — not "just in case".

**Context intake (don't bloat the window):**
- **Discover, don't dump.** Use grep/glob to fetch only matching snippets; read specific line ranges, never whole files or repos "just in case".
- **Trim tool output.** Pipe long command output through `Select-String`/grep/`head` before reading; don't ingest verbose logs verbatim.
- **Prefer CLIs and code over chat.** For find/count/filter/aggregate use `rg`/`jq`/`git`/`gh` one-liners; batch related reads/edits into one turn.
- **Audit tools.** Keep only the MCP servers/tools a task needs enabled — each ships its full schema every request.

**Session hygiene:**
- **One task per session.** Long sessions re-send growing context every turn; start fresh for a new task, and compact before the window fills.
- **Roll back, don't steer.** When the agent goes wrong, restart/clear rather than correcting mid-session — bad assumptions linger and bias every later turn.
- **Research → plan → implement as phases.** Let a `plan.md` carry only the needed context between phases instead of dragging research debris through every turn.
- **Lean on deterministic guardrails.** Give the agent the repo's test/lint commands and let pass/fail gate correctness instead of re-explaining.

**Keep these instruction files cheap:** they re-enter context every turn and are cache-discounted only when byte-identical. Keep them small — capture non-obvious watch-outs, not facts derivable from the repo — and free of volatile content (dates, ticket IDs, sprint focus), which belongs in per-task prompts.
