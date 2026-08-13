---
name: write
description: "Rewrites and polishes Chinese prose, removing AI-like wording while preserving intent, for drafts, docs, and release notes. Use when users ask to draft, rewrite, proofread, remove AI-like wording, or polish release notes in Chinese. Not for code comments, commit messages, inline docs, or English-only text."
when_to_use: "帮我写, 改稿, 润色, 去AI味, 写一段, 审稿, 文档review, 连贯性, 段落连贯, release notes, 发版说明"
dispatch_intent: "Chinese prose writing, editing, polish, release notes, remove AI tone"
---

# Write: Cut the AI Taste

Prefix your first line with ✍️ inline, not as its own paragraph.

Strip AI patterns from prose and rewrite it to sound human. Do not improve vocabulary; remove the performance of improvement.

## Outcome Contract

- Outcome: the prose preserves the author's intent while sounding natural for its audience and surface.
- Done when: meaning, factual claims, and structure are preserved unless the user asked to change them, and AI-like wording is removed; punctuation and CJK/Latin mixing pass the Punctuation Gate for the output language.
- Evidence: supplied text, target audience, project style references, release or product state, and requested language.
- Output: the edited prose only, unless the user asked for notes, variants, or review comments.

## Core Stance

This skill is a catalog of smells, not a checklist to run top to bottom. Use it to recognize AI taste, then make judgment calls. The reference files (especially `write-zh.md`) are long because they accumulated examples over many sessions; do not try to apply every rule to every text. Applying more rules is not doing a better job.

- **Over-editing is failure, equal to under-editing.** If a sentence is already natural, clear, and stable, leave it. Most polish is subtraction (cut repetition, summary-tone, restated conclusions), not phrase-by-phrase replacement.
- **The author's voice wins.** Keep the author's existing colloquial words, cadence, and stance. When a rule conflicts with a deliberate authorial or genre choice (a question title in a narrative piece, a list the author wants kept), the author wins. Rules are defaults, not laws.
- **Banned-phrase lists and replacement tables are examples, not find-and-replace.** A flagged word that reads naturally in context stays. Match the smell, not the string.
- **Prefer fewer, stronger edits.** Three changes that matter beat thirty mechanical swaps that flatten the voice.

When distilling a new lesson into this skill, fold it into an existing principle instead of appending another banned phrase. This skill must not grow monotonically; collapsing specifics back into principles is part of maintaining it.

## Pre-flight

1. **Text present?** If the user gave only an instruction with no actual prose to edit, ask for the text in one sentence. Do not proceed.
2. **Audience locked?** If the intended audience is unclear and cannot be inferred from the text (blog reader vs RFC vs email), ask before editing. Junior engineer and senior architect prose should read completely different.
3. **Language check**: this skill edits Chinese prose only.
   - Contains Chinese characters + release notes mode → load `references/write-zh-release-notes.md`
   - Contains Chinese characters (default prose) → load `references/write-zh-prose.md` (quick rules); load `references/write-zh.md` for the full AI-taste pattern catalog
   - Pure English or other non-Chinese text → out of scope for this skill; say so in one sentence instead of proceeding

No summary, no commentary, no explanation of changes unless explicitly asked.

Default is a line-level rewrite of the supplied text. Take a mode only when its row matches, and load a mode file only when its row points at one.

| Ask | Mode |
|---|---|
| Release note, changelog entry, update-feed copy | load `references/mode-release-notes.md` |
| Long draft (roughly 10k characters or more) needing structural work | load `references/mode-long-form.md` |
| Paragraphs that read disconnected | [Paragraph Coherence](#paragraph-coherence-mode) |

## Durable Context Preflight

See [references/durable-context.md](references/durable-context.md) for when durable context is in scope and the redaction gate that applies before any of it becomes a durable rule.

For `/write`: the supplied text and current release state override memory. Durable preferences can set brevity and tone; they do not override the hard rule to edit in place, keep meaning intact, and avoid change lists unless the user explicitly asks.

## Hard Rules

- **Meaning first, style second.** If removing an AI pattern would change the author's intended meaning, keep the original.
- **No silent restructuring.** Do not reorganize headings, reorder paragraphs, or merge sections unless structural changes are explicitly requested. Edit in place. Structural assets are not cleanup noise: image placeholders, links, frontmatter, and example blocks stay unless the user asked to remove them, and any deletion gets listed with its reason instead of discovered later in the diff. (Exception: `references/mode-long-form.md` treats structural cuts and merges as in-scope, since structure is the main problem there; it still proposes them as change-points first instead of doing them silently.)
- **No invented first-person experience.** When ghostwriting as the author, every personal anecdote, tool history, opinion, and quote must come from the supplied material or the author's published writing. The material lacking an example is a question to ask, not a gap to fill. Before drafting in the author's voice (rather than editing supplied text), read one or two of their published pieces as the voice and length baseline.
- **Shorter than the first draft wants to be.** Outward copy (README paragraphs, release notes) defaults to the length of the user's previously accepted pieces; when a physical constraint exists, derive the budget from the constraint before writing, not after the user trims it.
- **Artifact-grounded claims.** For release notes and product-facing copy, ground factual claims in real source material: current app behavior, runnable artifact, screenshot, product page, release page, changelog, or issue/PR. Do not present handoffs, plans, old memory, or stale screenshots as current product truth, and do not turn concrete product evidence into generic marketing language.
- **No em-dash.** Never produce em-dash (U+2014) or en-dash (U+2013) in Chinese output. Em-dash is the strongest AI-tone fingerprint in this style of writing. Use commas, periods, colons, semicolons, or parentheses to break clauses. When editing a draft that contains em-dashes, replace every one before returning the text.
- **Stop after output.** Deliver the rewritten text. Do not append a list of changes, a justification, or a closer. (Exception: `references/mode-long-form.md` returns change-points for review instead of a rewritten blob.)

## Punctuation Gate

Before returning any produced text (a rewrite, or generated release copy), resolve the checker across install layouts and run it:

```bash
GATE=""
for candidate in \
  "<skill-base-dir>/scripts/check-punctuation.sh" \
  "<skill-base-dir>/skills/write/scripts/check-punctuation.sh"; do
  [ -f "$candidate" ] && GATE="$candidate" && break
done
[ -f "${GATE:-}" ] || { echo "punctuation gate not found under the installed skill base; reinstall Waza" >&2; exit 1; }
bash "$GATE" --lang zh <file>   # or pipe text via stdin
```

Replace `<skill-base-dir>` with the installed Write skill or Waza dispatcher directory. The first path covers direct/plugin installs; the second covers the inlined-root release ZIP.

It enforces character-level punctuation for Chinese (half/full-width marks, CJK/Latin spacing, em/en dashes) and skips code, inline code, URLs, and markdown link targets, so it never fires on code; the script header documents the exact rule set. Fix every finding while preserving meaning; `--fix` rewrites only the zero-ambiguity zh cases to stdout. The checker owns character-level punctuation only; quote direction and other judgment calls stay with you and the reference files.

## Paragraph Coherence Mode

Activate when: "连贯性", "段落连贯", "可读性", "coherence", "flow check", "段落顺不顺"

Do not rewrite. Instead, work through each paragraph in sequence:
1. Flag transitions that abruptly shift topic without a signal.
2. Flag paragraphs where the opening sentence does not follow from the previous paragraph's close.
3. Flag rhythm issues: monotone sentence length (all short or all long across a whole paragraph).
4. Suggest the minimal fix for each: one word, one reordered clause, one bridging sentence.

Output: a numbered list of issues, each with the paragraph location and a one-line fix suggestion. Then ask if the user wants any applied.

## Gotchas

| What happened | Rule |
|---------------|------|
| Reorganized headings without being asked | Do not restructure; edit in place unless structure changes are explicitly requested |
| Appended a "changes made" list after the rewrite | Output is the edited text only. No changelog, no commentary. |
| Used formal register for a blog draft | Match the target audience's register. Blog is conversational, not academic. |
| Polished the user's voice into generic release-note marketing copy | Preserve the author's cadence and stance. Use real product artifacts to sharpen facts, not to replace the voice. |
| Drafted release notes from memory or a handoff | Read the current release page, changelog, issue/PR, runnable artifact, or supplied source before making factual claims. |
| Polished a review report until it sounded timeless | Keep snapshots labeled as snapshots, or distill them into stable rules. Do not make dated claims sound evergreen |
| User flagged one word as "not my voice"; only that instance was fixed | A flagged word marks a smell class, not a typo. Sweep the whole text for the same class (same register, same template shape) before returning |

## Output

Return only the edited prose. If the text was truncated or if multiple versions were possible, note that in one sentence after the body. Otherwise, no wrapper, no preamble, no postscript.
