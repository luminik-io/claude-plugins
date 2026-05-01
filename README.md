# Luminik Plugins

Open Claude Code plugins from [Luminik](https://www.luminik.io). Practical agents and skills for AEs, SDRs, and event marketers running pre-event outbound and dinner/side-event invites at B2B trade shows and conferences. Founders doing their own event outbound, welcome too.

## Install the marketplace

```bash
# From any Claude Code session
/plugin marketplace add luminik-io/claude-plugins
```

## Available plugins

### event-outbound

Generate multi-channel pre-event outbound sequences for AEs, SDRs, and event marketers working B2B trade shows, conferences, and industry events. Takes an event (RSA, Money20/20, Singapore Fintech Festival), the company you are targeting with attendee personas, and your sender identity. Returns one outreach sequence per persona, distributed across a 4-week lead-time window (configurable 1–8) with email and LinkedIn touches at sensible intervals.

Built on 20k+ personalised touches across 50+ events that sourced $6M+ in pipeline across fintech (identity verification), cybersecurity, and B2B SaaS.

**Every touch is validated before it lands:**

- Subject lines ≤ 4 words, all-lowercase, no digits, no buzzwords (53-phrase blocklist)
- Body channel-aware: 50–100 words / 3–5 sentences for cold email, 18–35 words for LinkedIn connection requests, separate bands for LinkedIn DMs, post-connect, post-event, meeting requests
- Pronoun ratio favouring the reader ("you/your" > "we/our")
- Illumination question on first-touch + post-connect (the "how / what / why are / do / is you / your" shape)
- Lean-back, permission-based CTAs ("worth a look?", "open to comparing notes?") over meeting-asks
- No leading questions, exclamation marks, emoji, or em-dashes
- 195-phrase, 10-category LLM-cliche blocklist: performative empathy, generic compliments, sales-speak openers, manufactured intimacy, marketing buzzwords, cold-email-overused, lazy-generalization openers, LLM transition tics, GPT vocabulary, hedge softeners. Sources cited inline (Stanford CRFM, GPTZero, Lavender Live transcript, Gong / 30MPC / Outbound Squad 85M-email "Ultimate Cold Email Data Report")
- Specificity check: every touch must reference a concrete event detail, persona priority, or pain point

Failures retry up to 3× with temperature jitter; touches that exhaust retries ship with `quality_flag: 'rules_violated'` for human review. Output is a markdown sequence with per-touch quality score (0–5, banded `top-tier` / `ship` / `review` / `rewrite`) plus a sequence summary (average quality, score-band counts, CTA mix, illumination-question coverage).

Two fully-rendered worked examples ship in the repo (RSA Conference 2026 cybersecurity, Money20/20 Europe 2026 fintech) plus an input-fixture set for Singapore Fintech Festival 2026.

**Repo:** https://github.com/luminik-io/event-outbound-skill
**Site:** https://www.luminik.io/tools/event-outbound/

**Install:**

```bash
/plugin marketplace add luminik-io/claude-plugins
/plugin install event-outbound@luminik-plugins
```

## Contributing

This marketplace is open. If you build a Claude Code plugin that's useful for the same audience (AEs, SDRs, event marketers, founders running their own event outbound) and want it distributed here, open a PR adding an entry to `.claude-plugin/marketplace.json`.

## Licence

MIT across this registry and each plugin unless stated otherwise.

---

Luminik is a product of DataRavel Inc. (Newark, DE). More at [luminik.io](https://www.luminik.io).
