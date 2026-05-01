<div align="center">

<a href="https://www.luminik.io"><img src="https://www.luminik.io/luminik-logo.svg" alt="Luminik" height="56" /></a>

# Luminik Plugins

Open Claude Code plugins from [Luminik](https://www.luminik.io). <br/>
Practical agents and skills for AEs, SDRs, and event marketers running B2B trade shows and conferences.

[![License: MIT](https://img.shields.io/badge/license-MIT-f63e8c.svg)](LICENSE)
[![Claude Code marketplace](https://img.shields.io/badge/Claude%20Code-marketplace-1e1e1e.svg)](https://docs.claude.com/en/docs/claude-code/plugins)
[![Plugins: 1](https://img.shields.io/badge/plugins-1-2ea043.svg)](#available-plugins)

[**Install**](#install-the-marketplace) · [**Plugins**](#available-plugins) · [**Contributing**](#contributing)

</div>

---

## Install the marketplace

From any Claude Code session:

```bash
/plugin marketplace add luminik-io/claude-plugins
```

That registers this catalogue. From there, install a specific plugin with `/plugin install <name>@luminik-plugins`.

## Available plugins

### event-outbound

> Pre-event outbound sequences for B2B trade shows, conferences, and industry events.

Generate validated multi-channel pre-event outbound sequences for AEs, SDRs, and event marketers working B2B trade shows, conferences, and industry events. Takes an event (RSA, Money20/20, Singapore Fintech Festival), the company you are targeting with attendee personas, and your sender identity. Returns one outreach sequence per persona, distributed across a 4-week lead-time window (configurable 1–8) with email and LinkedIn touches at sensible intervals.

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

| | |
|---|---|
| **Repo** | [github.com/luminik-io/event-outbound-skill](https://github.com/luminik-io/event-outbound-skill) |
| **Site** | [luminik.io/tools/event-outbound](https://www.luminik.io/tools/event-outbound/) |
| **Version** | 0.2.0 |
| **License** | MIT |

**Install:**

```bash
/plugin marketplace add luminik-io/claude-plugins
/plugin install event-outbound@luminik-plugins
```

## Contributing

This marketplace is open. If you build a Claude Code plugin that's useful for the same audience (AEs, SDRs, event marketers, founders running their own event outbound) and want it distributed here, open a PR adding an entry to [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Plugins live as git submodules under `plugins/` so each one stays independently versioned in its own repo.

## License

MIT across this registry. Each plugin is MIT unless its own LICENSE states otherwise.

---

<div align="center">

**[More from Luminik →](https://www.luminik.io)**

Luminik is a product of [DataRavel Inc.](https://www.luminik.io) (Newark, DE).

</div>
