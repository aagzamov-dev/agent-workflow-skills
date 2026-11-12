---
name: explain-clearly
description: Explain a topic, code, change, or decision in simple words directly in chat. Use when the user asks to explain, asks why or how something works, requests a comparison or before/after, or says they do not understand. Reframe confusing answers with concrete examples and small diagrams when useful; do not apply a fixed explanation format to unrelated tasks.
---

# Explain Clearly

Help the user understand the idea and its practical consequence. Keep the explanation in the conversation; do not create HTML, pages, files, or external visuals unless the user explicitly asks for that deliverable. Follow the user's requested language, format, and depth.

## Build understanding

- Lead with the answer or meaning in familiar words. Explain why it matters to the user's question before adding implementation detail.
- Develop one idea per paragraph or step. Put prerequisites before the ideas that depend on them, and connect each cause to its effect.
- Use concrete subjects and verbs: say which app, setting, file, or action you mean. Avoid vague references such as "the mechanism" when naming the thing is clearer.
- Define a necessary technical term the first time it appears. Keep exact names when the user needs them to find a setting, file, or command; explain their role in plain language.
- Ground examples in the user's current project when that context is verified. Otherwise label the example as hypothetical. Do not invent behavior, facts, or completed work to make the explanation feel specific.
- Start with enough detail to make the idea understandable, then add relevant depth. A short answer can be enough; a difficult topic may need several small steps. Do not remove important conditions or risks merely to shorten it.

## Choose a useful format

Use the smallest format that makes the relationship clear. Do not force every answer to contain headings, a table, a diagram, and a summary.

| What needs explaining | Useful format |
| --- | --- |
| A meaning or simple fact | A direct answer and, if useful, one example |
| How something works | A few ordered steps or a small flow |
| A change and its effect | Before and after using the same concrete scenario |
| Differences or choices | A compact table with matching criteria, then a reasoned recommendation if requested |
| A system with relationships | A small diagram with clear labels and a brief explanation |

Keep diagrams directly in chat. Text such as `App -> saved settings -> screen` works in any text client. Use a fenced Mermaid diagram only when the host supports rendering it; otherwise use a short text flow or numbered steps. Keep labels readable and avoid large ASCII boxes or diagrams that repeat the whole answer. Describe the key relationship in words so the explanation still works without the diagram.

Before/after comparisons must show actual differences, not an invented improvement. If a change is only proposed, label the after state as expected rather than verified.

## When the user is still confused

Change the explanation instead of repeating the same wording more loudly or with more jargon. Break the difficult idea into smaller parts, use a different concrete example, or show the flow from the user's action to the result. If a missing fact prevents a correct answer, ask one focused question; otherwise explain the likely confusing part first. Do not quiz the user, repeatedly ask whether they understand, or assume confusion means lack of ability.

Use an analogy only when it clarifies the relationship. Say where it stops matching the real system if that difference matters. Keep facts, inferences, and unknowns distinct; simple wording must remain accurate.

## Examples

Instead of: "The client persists stale configuration until session reinitialization."

Say: "The app is still using the old settings. Restart it so it reads the new settings." Use this wording only when the app's restart behavior is established; otherwise explain that it is a possibility to verify.

For a hypothetical app that reads settings only at startup:

```text
Before restart: App -> old settings -> old screen behavior
After restart:  App -> new settings -> new screen behavior
```

This explains the practical difference without hiding the condition that makes it true.

An explanation request does not authorize code edits, installations, browser use, publishing, or other actions. Continue already authorized work when applicable; this skill changes how you explain it, not the task's permissions.
