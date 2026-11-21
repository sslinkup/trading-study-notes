# Trading Study Notes

**Live site:** https://trading-study-notes.sanliurfa.workers.dev

A free, non-commercial study guide built from public crypto trading lessons. It reorganises the material by topic, and every timestamp links to the exact moment in the original video so any claim can be verified at the source.

This is an **independent** study guide. It is not affiliated with, endorsed by, or produced by the creator of the source videos. All original prose is released under [CC0 1.0](LICENSE); the videos, their transcripts and artwork are not included and remain the property of their creator.

## What's here

| Path | Purpose |
|---|---|
| `public_src/` | Editable Markdown notes, license, attribution, site URL and card SVGs |
| `docs/` | Built static site (ready to host on GitHub Pages from `/docs`) |
| `tools/md2html.py` | Converts Markdown to HTML, deep-links timestamps, generates sitemap / `llms.txt` |
| `tools/make_note_cards.py` | Renders the six note social cards from SVG |
| `PUBLISH.md` | Full publishing and regeneration instructions |

## Notes

1. [Foundations — mindset, bankroll, journaling](https://trading-study-notes.sanliurfa.workers.dev/notes/A_foundations)
2. [Mistakes, anti-patterns and risk](https://trading-study-notes.sanliurfa.workers.dev/notes/B_mistakes)
3. [Trading lessons and philosophy](https://trading-study-notes.sanliurfa.workers.dev/notes/C_lessons)
4. [Naked RSI, stochastic RSI and the NKED method](https://trading-study-notes.sanliurfa.workers.dev/notes/D_stochastic)
5. [Indicators and chart reading](https://trading-study-notes.sanliurfa.workers.dev/notes/E_indicators)
6. [Volume, order flow and timing](https://trading-study-notes.sanliurfa.workers.dev/notes/F_volume_timing)

## Build locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt cairosvg

python tools/make_note_cards.py docs/cards
python tools/md2html.py public_src docs "Trading Study Notes"
cp public_src/license.md docs/LICENSE.txt
```

`public_src/site.txt` holds the canonical URL used in canonical tags, social cards and the sitemap. Change it before deploying anywhere else.

## Hosting

- **Cloudflare:** `wrangler.jsonc` serves `docs/`. Set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as repository secrets and push to `main`; the included GitHub Action rebuilds and deploys automatically.
- **GitHub Pages:** enable Pages from the `main` branch, `/docs` folder. Set `site.txt` to the GitHub Pages URL first.

## Display

Every page has a dark/light toggle in the top-right corner. The choice is remembered locally and, on a fresh visit, follows your device's `prefers-color-scheme` setting.

## Non-commercial promise

No ads, affiliate links, paywalls, donations or tracking on this site. A ▶ button next to each timestamp loads a YouTube embed only on click; that player is governed by YouTube's terms and may show its own ads or set cookies.

Not financial advice. Trading involves risk.
