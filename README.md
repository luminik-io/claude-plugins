# Luminik Plugins

Open Claude Code plugins from [Luminik](https://www.luminik.io). Practical agents and skills for solo founders, GTM operators, and B2B event marketers.

## Install the marketplace

```bash
# From any Claude Code session
/plugin marketplace add luminik-io/claude-plugins
```

## Available plugins

### event-outbound

Generate cold-outbound sequences for B2B event marketers. Takes an event URL + your company URL + a target attendee profile and produces multi-touch email + LinkedIn sequences across a parameterised lead time (1–8 weeks).

Grounded in publicly-taught cold-outbound frameworks and published benchmark research. Every generated touch is validated against hard rules before it's emitted:

- Subject lines ≤ 4 words, all-lowercase, priority-based (no buzzwords, no social-proof stuffing)
- Body 50–100 words, 3–4 sentences, structure *Personalization → Problem → Solution → CTA*
- Zero pitch-speak ("transform", "revolutionary", "unlock" and ~15 other banned words, with retry-3 and a `quality_flag` fallback)
- Pronoun ratio favouring the reader ("you/your" > "we/our")
- CTA pattern favouring concrete offers over meeting-asks (per Gong data: "make offer" +28% reply rate, "ask for meeting" −44%)

**Repo:** https://github.com/luminik-io/event-outbound-skill

**Install:**

```bash
/plugin install event-outbound@luminik-plugins
```

## Contributing

This marketplace is open. If you build a Claude Code plugin that's useful for the same audience (solo B2B founders, event marketers, GTM ops teams) and want it distributed here, open a PR adding an entry to `.claude-plugin/marketplace.json`.

## Licence

MIT across this registry and each plugin unless stated otherwise.
