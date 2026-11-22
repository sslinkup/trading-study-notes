# Publishing the copyright-safe site

`public_html/` is the publishable version. It contains only original prose plus links to the original videos.

## What is in it

- Seven topic notes, a landing page, a license page, and an attribution page.
- 148 clickable timestamps that open the source video at the exact moment.
- Per-page descriptions, canonical URLs, Open Graph and Twitter cards, plus JSON-LD `Article` metadata.
- `sitemap.xml` and `robots.txt` (with explicit allow rules for major AI crawlers).
- `llms.txt`, `llms-full.txt`, and clean Markdown copies under `markdown/` so AI readers can ingest the text directly.
- No transcripts, no verbatim quotes, no third-party images or video files.
- No ads, affiliate links, paywalls, donations, or tracking — the site is deliberately non-commercial, and the text is CC0 so anyone can reuse it freely.
- An original 1200x630 social preview card at `social-card.png`, plus one matching card per note under `cards/`. Each page uses its own card as `og:image` and `twitter:image`.
- A responsive homepage with image cards, a live search box, and compact links to the secondary pages.
- A small ▶ button beside every timestamp that loads a `youtube-nocookie.com` embed at that exact second, only when clicked; clicking it again removes the player.

## What is not in it

- `barenakedcrypto/transcripts/` — full copies of the videos' speech.
- The quote-heavy original notes and combined study guide, which contained long verbatim excerpts.

Those files remain in the project for private study only. They are deliberately excluded from the public build.

## How to publish

**Set your domain first.** `public_src/site.txt` holds the live URL used for canonical URLs, social tags and the sitemap. It is currently set to the deployed address `https://trading-study-notes.sanliurfa.workers.dev`. If you attach a custom domain, change this file and regenerate before redeploying.

**Live site:** https://trading-study-notes.sanliurfa.workers.dev

**Cloudflare deployment (already configured).** `wrangler.jsonc` points to `public_html/`. The site uses clean extensionless URLs (e.g. `/notes/A_foundations`) so Cloudflare serves the underlying `.html` files without redirects. To redeploy after edits:

```
CLOUDFLARE_ACCOUNT_ID=<account-id> CLOUDFLARE_API_TOKEN=<token> \
  npx --yes wrangler deploy
```

The project is on the latest Cloudflare Pages (now part of Cloudflare Workers); use `wrangler deploy` rather than `wrangler pages deploy`.

**GitHub Pages alternative:** create a repository, copy the contents of `public_html/` into it, enable Pages from the `main` branch root, and push. Set `site.txt` to the GitHub Pages URL first.

## Regenerating after edits

Edit the markdown in `public_src/`, then run:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/md2html.py public_src public_html "Trading Study Notes"
cp public_src/license.md public_html/LICENSE.txt
```

The converter rewrites relative `.md` links to clean extensionless URLs, turns timestamps into deep links, and auto-links bare URLs. It needs only the `markdown` package.

To update the social card, edit `public_src/social-card.svg` and regenerate the PNG:

```
/tmp/md2html-venv/bin/python -c "import cairosvg; cairosvg.svg2png(url='public_src/social-card.svg', write_to='public_html/social-card.png', output_width=1200, output_height=630)"
```

`cairosvg` is installed in `/tmp/md2html-venv`; install it in your own venv with `pip install cairosvg` if needed.

To regenerate the six note cards, edit the `CARDS` list in `tools/make_note_cards.py`, then run:

```
/tmp/md2html-venv/bin/python tools/make_note_cards.py
```

The editable SVG sources live in `public_src/cards/`; the rendered PNGs go to `public_html/cards/`.

## License

The original text is released under CC0 1.0 — see `public_html/LICENSE.txt` and `public_html/license.html`. The linked videos and their transcripts are not covered by this license and remain the property of their creator.
