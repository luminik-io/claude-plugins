# Luminik Plugins

Open Claude Code plugins from [Luminik](https://www.luminik.io). Practical agents and skills for AEs, SDRs, and event marketers running pre-event outbound and dinner/side-event invites at B2B trade shows and conferences. Founders doing their own event outbound, welcome too.

## Install the marketplace

```bash
# From any Claude Code session
/plugin marketplace add luminik-io/claude-plugins
```

## Available plugins

### event-outbound

Generate multi-channel outbound sequences for AEs, SDRs, and event marketers working B2B trade shows, conferences, and industry events. Takes an event URL + your company URL + a target attendee profile and produces multi-touch email + LinkedIn sequences across a parameterised lead time (1–8 weeks).

Built on 20k+ personalised touches across 50+ events that sourced $6M+ in pipeline across fintech (identity verification), cybersecurity, and B2B SaaS. Every generated touch is validated against hard rules before it's emitted:

- Subject lines ≤ 4 words, all-lowercase, priority-based (no buzzwords, no social-proof stuffing)
- Body 50–100 words, 3–4 sentences, structure *Personalization → Problem → Solution → CTA*
- Zero pitch-speak (a banned-words blocklist with retry-3 and a `quality_flag` fallback)
- Pronoun ratio favouring the reader ("you/your" > "we/our")
- CTA pattern favouring concrete offers over meeting-asks

**Repo:** https://github.com/luminik-io/event-outbound-skill

**Install:**

```bash
/plugin install event-outbound@luminik-plugins
```

## Contributing

This marketplace is open. If you build a Claude Code plugin that's useful for the same audience (AEs, SDRs, event marketers, founders running their own event outbound) and want it distributed here, open a PR adding an entry to `.claude-plugin/marketplace.json`.

## Licence

MIT across this registry and each plugin unless stated otherwise.

---

Luminik is a product of DataRavel Inc. (Newark, DE). More at [luminik.io](https://www.luminik.io).
