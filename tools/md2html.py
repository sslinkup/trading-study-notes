#!/usr/bin/env python3
"""Convert the markdown tree into standalone HTML with clickable, time-linked videos."""
import datetime
import html as html_mod
import json
import os
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/mert/projects/finance/research")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "html"
SITE_TITLE = sys.argv[3] if len(sys.argv) > 3 else "Markdown library"
EXCLUDE = {"public_src", "public_html", "html", "markdown"}


def load_base_url(root):
    site_file = root / "site.txt"
    if site_file.exists():
        value = site_file.read_text(encoding="utf-8").strip()
        if value:
            return value.rstrip("/")
    return os.environ.get("SITE_URL", "https://example.com").rstrip("/")


BASE_URL = sys.argv[4] if len(sys.argv) > 4 else load_base_url(ROOT)

MD = markdown.Markdown(
    extensions=["extra", "toc", "sane_lists"],
    extension_configs={"toc": {"permalink": False}},
)

CSS = """
:root {
  color-scheme: light;
  --bg: #fff; --fg: #1f2328; --muted: #57606a; --border: #d0d7de; --subtle: #f6f8fa;
  --link: #0969da; --link-strong: #0a3069; --ts-bg: #fff8c5; --ts-hover: #ffe66b;
  --note-bg: #ddf4ff; --card-bg: #fff; --btn: #0969da; --btn-hover: #0550ae;
  --btn2-bg: #f6f8fa; --btn2-fg: #1f2328; --shadow: rgba(31,35,40,.12);
}
[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0d1117; --fg: #e6edf3; --muted: #9da7b3; --border: #30363d; --subtle: #161b22;
  --link: #58a6ff; --link-strong: #79c0ff; --ts-bg: #3b2f00; --ts-hover: #5a4600;
  --note-bg: #0d2b45; --card-bg: #161b22; --btn: #1f6feb; --btn-hover: #388bfd;
  --btn2-bg: #21262d; --btn2-fg: #e6edf3; --shadow: rgba(0,0,0,.5);
}
body { max-width: 860px; margin: 0 auto; padding: 2rem 1.5rem 5rem;
       font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       color: var(--fg); background: var(--bg); }
button.theme-toggle { position: fixed; top: 1rem; right: 1rem; z-index: 20; width: 40px;
  height: 40px; border-radius: 50%; border: 1px solid var(--border); background: var(--card-bg);
  color: var(--fg); font-size: 18px; cursor: pointer; box-shadow: 0 2px 8px var(--shadow); }
button.theme-toggle:hover { border-color: var(--link); }
a { color: var(--link); }
a.back { display: inline-block; margin-bottom: 1.5rem; font-size: .9rem; }
a.ts { color: var(--link-strong); background: var(--ts-bg); padding: 0 .25em; border-radius: 4px;
       text-decoration: none; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
       font-size: .9em; white-space: nowrap; }
a.ts:hover, a.ts:focus { text-decoration: underline; background: var(--ts-hover); }
a.ext { word-break: break-all; }
.ts-wrap { display: inline-flex; align-items: center; gap: .25rem; }
button.play { border: 0; background: var(--btn); color: #fff; border-radius: 50%; width: 19px;
              height: 19px; padding: 0; font-size: 9px; line-height: 19px; cursor: pointer; }
button.play:hover { background: var(--btn-hover); }
.embed-slot { display: block; margin: .75rem 0; }
.embed-slot iframe { display: block; width: min(560px, 100%); aspect-ratio: 16 / 9;
                     border: 0; border-radius: 10px; background: #000; }
h1, h2, h3, h4 { line-height: 1.25; margin-top: 1.6em; }
h1 { border-bottom: 1px solid var(--border); padding-bottom: .3em; }
h2 { border-bottom: 1px solid var(--border); padding-bottom: .3em; }
pre { background: var(--subtle); padding: 1rem; overflow-x: auto; border-radius: 6px; }
code { background: var(--subtle); padding: .15em .4em; border-radius: 4px; font-size: .9em; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid var(--border); margin-left: 0; padding-left: 1rem; color: var(--muted); }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid var(--border); padding: .4rem .7rem; text-align: left; }
th { background: var(--subtle); }
img { max-width: 100%; }
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
.note { background: var(--note-bg); border-left: 4px solid var(--link); padding: .7rem 1rem;
        border-radius: 4px; margin: 1rem 0 1.5rem; }
body.index-page { max-width: 1120px; }
.toolbar { display: flex; gap: .75rem; align-items: center; flex-wrap: wrap; margin: 1.25rem 0 1.75rem; }
.toolbar input { flex: 1; min-width: 220px; padding: .7rem .9rem; border: 1px solid var(--border);
                 border-radius: 8px; font-size: 1rem; background: var(--card-bg); color: var(--fg); }
.btn { display: inline-block; padding: .7rem 1.1rem; background: var(--btn); color: #fff;
       border-radius: 8px; text-decoration: none; font-weight: 600; }
.btn.secondary { background: var(--btn2-bg); color: var(--btn2-fg); border: 1px solid var(--border); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.25rem; margin: 1rem 0 2rem; }
.card { display: block; border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
        text-decoration: none; color: inherit; background: var(--card-bg);
        transition: transform .15s, box-shadow .15s, border-color .15s; }
.card:hover, .card:focus { transform: translateY(-2px); box-shadow: 0 6px 18px var(--shadow);
                           border-color: var(--link); }
.card img { display: block; width: 100%; aspect-ratio: 1200 / 630; object-fit: cover;
            border-bottom: 1px solid var(--border); background: #0b1220; }
.card-body { padding: 1rem 1.1rem 1.2rem; }
.card h3 { margin: 0 0 .35rem; font-size: 1.15rem; }
.card p { margin: 0; color: var(--muted); font-size: .9rem; line-height: 1.5;
          display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.quick-links { display: flex; flex-wrap: wrap; gap: .75rem; margin: 1rem 0 2rem; }
.quick-links a { padding: .55rem .85rem; border: 1px solid var(--border); border-radius: 8px;
                 text-decoration: none; background: var(--card-bg); }
.quick-links a:hover { border-color: var(--link); }
.section-title { margin-top: 2.5rem; }
@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
"""

YT_RE = re.compile(r"youtube\.com/watch\?v=([\w-]+)|youtu\.be/([\w-]+)", re.I)
TS = r"(\d{1,3}):([0-5]\d)(?::([0-5]\d))?"
CODE_TS_RE = re.compile(r"`\[?(" + TS + r")\]?`")
BRACKET_TS_RE = re.compile(r"\[(" + TS + r")\]")
URL_RE = re.compile(r"https?://[^\s<>\"'`]+", re.I)
LINK_RE = re.compile(r'(<a\s+[^>]*?href=")([^"]+\.md(?:#[^"]*)?)(")', re.I)
IMG_RE = re.compile(r'(<img\s+[^>]*?src=")([^"]+)(")', re.I)


def seconds(a, b, c):
    if c is None:  # M:SS
        return int(a) * 60 + int(b)
    return int(a) * 3600 + int(b) * 60 + int(c)  # H:MM:SS


def yt_url(video_id, sec):
    return f"https://www.youtube.com/watch?v={video_id}&t={sec}s"


def anchor(video_id, sec, label):
    return (
        f'<span class="ts-wrap">'
        f'<a class="ts" href="{yt_url(video_id, sec)}" '
        f'target="_blank" rel="noopener">{label}</a>'
        f'<button class="play" type="button" title="Watch this moment inline" '
        f'aria-label="Watch this moment inline" '
        f'onclick="toggleEmbed(this)" '
        f'data-video="{html_mod.escape(video_id, quote=True)}" data-start="{sec}">&#9654;</button>'
        f'</span>'
    )


def first_id(text):
    m = YT_RE.search(text)
    return (m.group(1) or m.group(2)) if m else None


def link_timestamps(src, default_id):
    """Turn timestamps in the markdown source into deep links."""
    placeholders = {}

    # 1) code-span timestamps (`[00:04]` chapters and `[03:13]` markers)
    def code_repl(m):
        h, mm, ss = m.group(2), m.group(3), m.group(4)
        if not default_id:
            return m.group(0)
        sec = seconds(h, mm, ss)
        label = f"[{m.group(1)}]" if m.group(0).startswith("`[") else m.group(1)
        key = f"\x00TS{len(placeholders)}\x00"
        placeholders[key] = anchor(default_id, sec, label)
        return key

    src = CODE_TS_RE.sub(code_repl, src)

    # 2) plain bracket timestamps in prose/citations, e.g. [03:13]
    def bracket_repl(m):
        after = src[m.end():m.end() + 250]
        before = src[max(0, m.start() - 400):m.start()]
        vid = first_id(after) or first_id(before) or default_id
        if not vid:
            return m.group(0)
        return anchor(vid, seconds(m.group(2), m.group(3), m.group(4)), m.group(0))

    src = BRACKET_TS_RE.sub(bracket_repl, src)

    for key, value in placeholders.items():
        src = src.replace(key, value)
    return src


def clean_url(url):
    url = url.rstrip(".,;:!?")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url.rstrip(".,;:!?")


def autolink(html_text):
    """Link bare URLs in text nodes and make external links open in a new tab."""
    parts = re.split(r"(<[^>]+>)", html_text)
    for i in range(0, len(parts), 2):  # text nodes only
        def repl(m):
            url = clean_url(m.group(0))
            if not url:
                return m.group(0)
            href = html_mod.escape(html_mod.unescape(url), quote=True)
            tail = m.group(0)[len(url):]
            return f'<a class="ext" href="{href}" target="_blank" rel="noopener">{url}</a>{tail}'
        parts[i] = URL_RE.sub(repl, parts[i])
    for i in range(1, len(parts), 2):  # tags only
        tag = parts[i]
        if tag.startswith("<a ") and 'href="http' in tag and "target=" not in tag:
            tag = tag.replace("<a ", '<a target="_blank" rel="noopener" ', 1)
            parts[i] = tag
    return "".join(parts)


def rewrite(src_file: Path, dst_file: Path, html: str) -> str:
    def fix_link(m):
        url = m.group(2)
        if re.match(r"^[a-z]+:", url, re.I) or url.startswith("/"):
            return m.group(0)
        url = re.sub(r"\.md(?=#|$)", "", url)
        return m.group(1) + url + m.group(3)

    html = LINK_RE.sub(fix_link, html)

    def fix_img(m):
        url = m.group(2)
        if re.match(r"^[a-z]+:", url, re.I) or url.startswith("/"):
            return m.group(0)
        target = (src_file.parent / url.split("#")[0]).resolve()
        if target.exists():
            rel = os.path.relpath(target, dst_file.parent)
            return m.group(1) + rel + m.group(3)
        return m.group(0)

    return IMG_RE.sub(fix_img, html)


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def web_path(dst_rel: Path) -> str:
    """Extensionless URL path served by Cloudflare static assets."""
    path = dst_rel.with_suffix("").as_posix()
    return "" if path == "index" else path


BOILERPLATE = re.compile(
    r"linked videos|original sources|remain their authors|click any timestamp|click a timestamp",
    re.I,
)


def make_description(body: str, fallback: str) -> str:
    text = plain(re.sub(r"<h[1-3][^>]*>.*?</h[1-3]>", "", body, flags=re.S))
    if not text:
        return fallback
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if not BOILERPLATE.search(s)]
    text = " ".join(sentences).strip() or text
    text = re.sub(r"^Original (study|reference) notes\.\s*", "", text, flags=re.I)
    if len(text) > 160:
        text = text[:160].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
    return text


def page(title: str, body: str, rel_index: str, description: str, url: str, date: str,
         rel_llms: str, image_url: str, body_class: str = "") -> str:
    t = html_mod.escape(plain(title), quote=True)
    d = html_mod.escape(description, quote=True)
    u = html_mod.escape(url, quote=True)
    logo_obj = {"@type": "ImageObject", "url": BASE_URL + "/logo-512.png"}
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": plain(title),
        "description": description,
        "datePublished": date,
        "dateModified": date,
        "image": BASE_URL + "/logo-512.png",
        "author": {"@type": "Organization", "name": SITE_TITLE, "logo": logo_obj},
        "publisher": {"@type": "Organization", "name": SITE_TITLE, "logo": logo_obj},
        "mainEntityOfPage": url,
        "inLanguage": "en",
    }, ensure_ascii=False)
    back_html = ("" if body_class == "index-page"
                 else f'<a class="back" href="{rel_index}">&larr; Index</a>\n')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<link rel="icon" type="image/png" sizes="32x32" href="{rel_index}favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{rel_index}favicon-16.png">
<link rel="shortcut icon" href="{rel_index}favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="{rel_index}apple-touch-icon.png">
<meta name="description" content="{d}">
<meta name="author" content="{html_mod.escape(SITE_TITLE, quote=True)}">
<meta name="robots" content="index, follow, max-snippet:-1">
<link rel="canonical" href="{u}">
<link rel="alternate" type="text/plain" href="{rel_llms}">
<script type="application/ld+json">{json_ld}</script>
<meta property="og:type" content="article">
<meta property="og:site_name" content="{html_mod.escape(SITE_TITLE, quote=True)}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{html_mod.escape(image_url, quote=True)}">
<meta property="og:image:alt" content="Trading Study Notes - free CC0 guide with clickable video timestamps">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{html_mod.escape(image_url, quote=True)}">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<script>
(function() {{
  function isDark() {{ return document.documentElement.getAttribute('data-theme') === 'dark'; }}
  function apply(dark) {{
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    try {{ localStorage.setItem('study-theme', dark ? 'dark' : 'light'); }} catch (e) {{}}
    var b = document.getElementById('themeToggle');
    if (b) {{
      b.textContent = dark ? '☀' : '☾';
      b.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
      b.setAttribute('aria-label', b.title);
    }}
  }}
  try {{
    var saved = localStorage.getItem('study-theme');
    var dark = saved === 'dark' ||
      (!saved && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    apply(dark);
  }} catch (e) {{ apply(false); }}
  document.addEventListener('DOMContentLoaded', function() {{
    var b = document.getElementById('themeToggle');
    if (b) b.addEventListener('click', function() {{ apply(!isDark()); }});
  }});
}})();
</script>
<style>{CSS}</style>
<script>
function toggleEmbed(btn) {{
  var wrap = btn.closest('.ts-wrap');
  var slot = wrap && wrap.nextElementSibling;
  if (slot && slot.classList && slot.classList.contains('embed-slot')) {{
    slot.remove();
    return;
  }}
  var frame = document.createElement('iframe');
  frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(btn.dataset.video) +
              '?start=' + encodeURIComponent(btn.dataset.start) + '&autoplay=1';
  frame.title = 'Embedded video at ' + btn.dataset.start + ' seconds';
  frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
  frame.allowFullscreen = true;
  frame.referrerPolicy = 'strict-origin-when-cross-origin';
  var box = document.createElement('div');
  box.className = 'embed-slot';
  box.appendChild(frame);
  wrap.insertAdjacentElement('afterend', box);
}}
</script>
</head>
<body class="{body_class}">
<button class="theme-toggle" id="themeToggle" type="button" title="Toggle dark mode"
        aria-label="Toggle dark mode">☾</button>
{back_html}{body}
<footer style="margin-top:3rem;padding-top:1rem;border-top:1px solid var(--border);font-size:.85rem;color:var(--muted)">
<a href="{rel_llms}">llms.txt</a> · <a href="{rel_index}">index</a> · original text released under CC0
</footer>
</body>
</html>
"""


def write_discovery(entries):
    """Write sitemap.xml and robots.txt for search engines."""
    today = datetime.date.today().isoformat()
    urls = [(f"{BASE_URL}/", today), (f"{BASE_URL}/llms.txt", today)] + [
        (url, datetime.datetime.fromtimestamp(Path(p).stat().st_mtime, datetime.timezone.utc).date().isoformat())
        for p, url in entries
    ]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        sitemap.append(
            f"  <url>\n    <loc>{html_mod.escape(loc)}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n  </url>"
        )
    sitemap.append("</urlset>\n")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
    bots = [
        "User-agent: *", "Allow: /", "",
        "# AI crawlers are welcome to read and cite these pages.",
    ]
    for bot in ["GPTBot", "OAI-SearchBot", "ClaudeBot", "Claude-Web",
                "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]:
        bots += [f"User-agent: {bot}", "Allow: /", ""]
    bots += [f"Sitemap: {BASE_URL}/sitemap.xml", ""]
    (OUT / "robots.txt").write_text("\n".join(bots), encoding="utf-8")


def write_llms(entries):
    """Write llms.txt / llms-full.txt and publish the raw markdown for AI readers."""
    md_dir = OUT / "markdown"
    md_dir.mkdir(exist_ok=True)
    for rel, _, _, _, _ in entries:
        target = md_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")

    index_lines = [
        f"# {SITE_TITLE}",
        "",
        "> Original study notes summarising public trading lessons. "
        "Every timestamp in the linked pages opens the original video at that moment.",
        "",
        "These pages are licensed CC0 1.0. The linked videos are not included "
        "and remain the property of their creator.",
        "",
        "## Pages",
        "",
    ]
    for _, dst_rel, title, description, url in entries:
        loc = web_path(dst_rel)
        index_lines.append(f"- [{title}]({loc}): {description}")
        index_lines.append(f"  - Plain text: markdown/{dst_rel.with_suffix('.md').as_posix()}")
    index_lines += [
        "",
        "## Complete text",
        "",
        f"- [llms-full.txt](llms-full.txt) — every page in one plain-text file",
        "",
    ]
    (OUT / "llms.txt").write_text("\n".join(index_lines), encoding="utf-8")

    full = [f"# {SITE_TITLE}", "", f"Canonical site: {BASE_URL}/", ""]
    for rel, _, title, _, url in entries:
        full += [f"## {title}", f"Source: {url}", "",
                 (ROOT / rel).read_text(encoding="utf-8").strip(), ""]
    (OUT / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")


def main():
    files = sorted(
        p for p in ROOT.rglob("*.md")
        if OUT not in p.parents and not (set(p.relative_to(ROOT).parts) & EXCLUDE)
    )
    OUT.mkdir(exist_ok=True)
    entries = []
    discovery = []
    for src in files:
        rel = src.relative_to(ROOT)
        dst = OUT / rel.with_suffix(".html")
        dst.parent.mkdir(parents=True, exist_ok=True)

        text = src.read_text(encoding="utf-8")
        default_id = first_id(text)
        text = link_timestamps(text, default_id)

        MD.reset()
        body = MD.convert(text)
        body = autolink(body)
        body = rewrite(src, dst, body)
        first = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = re.sub(r"<[^>]+>", "", first.group(1)) if first else rel.stem
        rel_index = os.path.relpath(OUT, dst.parent).replace(os.sep, "/") + "/"
        description = make_description(body, f"Study notes: {title}")
        path = web_path(dst.relative_to(OUT))
        url = f"{BASE_URL}/{path}" if path else f"{BASE_URL}/"
        date = datetime.datetime.fromtimestamp(
            src.stat().st_mtime, datetime.timezone.utc
        ).date().isoformat()
        rel_llms = os.path.relpath(OUT / "llms.txt", dst.parent)
        image_url = (f"{BASE_URL}/cards/{rel.stem}.png"
                     if rel.parts and rel.parts[0] == "notes"
                     else f"{BASE_URL}/social-card.png")
        dst.write_text(page(title, body, rel_index, description, url, date, rel_llms, image_url),
                       encoding="utf-8")
        entries.append((rel, dst.relative_to(OUT), title, description, url))
        discovery.append((src, url))

    groups = {}
    for rel, dst_rel, title, description, _ in entries:
        folder = str(rel.parent) if str(rel.parent) != "." else "Root"
        image = (f"cards/{rel.stem}.png"
                 if rel.parts and rel.parts[0] == "notes" else "social-card.png")
        groups.setdefault(folder, []).append((dst_rel, title, description, image))

    lines = [
        f"<h1>{SITE_TITLE}</h1>",
        '<div class="note">Click any <strong>highlighted timestamp</strong> to open '
        "the video at that exact moment. No ads, no tracking, free to reuse.</div>",
        '<div class="toolbar">',
        '<input id="q" type="search" placeholder="Search pages..." '
        'aria-label="Search pages" oninput="filterCards()">',
        '<a class="btn" href="start_here">Start here</a>',
        '<a class="btn secondary" href="llms.txt">Plain text / AI</a>',
        "</div>",
        "<script>",
        "function filterCards(){const q=document.getElementById('q').value.toLowerCase().trim();"
        "document.querySelectorAll('.card,.quick-links a').forEach(c=>{c.style.display="
        "c.textContent.toLowerCase().includes(q)?'':'none';});}",
        "</script>",
    ]
    labels = {"notes": "Study notes", "Root": "Other pages"}
    ordered = sorted(groups, key=lambda f: (0 if f == "notes" else 1, f))
    for folder in ordered:
        label = labels.get(folder, folder.replace(os.sep, " / "))
        lines.append(f'<h2 class="section-title">{html_mod.escape(label)}</h2>')
        if folder == "notes":
            lines.append('<div class="grid">')
            for dst_rel, title, description, image in sorted(groups[folder]):
                t = html_mod.escape(plain(title), quote=True)
                d = html_mod.escape(description, quote=True)
                lines.append(
                    f'<a class="card" href="{web_path(dst_rel)}">'
                    f'<img src="{image}" alt="{t} preview" loading="lazy">'
                    f'<div class="card-body"><h3>{t}</h3><p>{d}</p></div></a>'
                )
            lines.append("</div>")
        else:
            lines.append('<div class="quick-links">')
            for dst_rel, title, _, _ in sorted(groups[folder]):
                t = html_mod.escape(plain(title), quote=True)
                lines.append(f'<a href="{web_path(dst_rel)}">{t}</a>')
            lines.append("</div>")
    index_desc = (
        f"{SITE_TITLE}: original study notes with clickable timestamp links "
        "to the original videos."
    )
    (OUT / "index.html").write_text(
        page(SITE_TITLE, "\n".join(lines), "./", index_desc,
             f"{BASE_URL}/", datetime.date.today().isoformat(), "llms.txt",
             f"{BASE_URL}/social-card.png", body_class="index-page"),
        encoding="utf-8",
    )
    write_discovery(discovery)
    write_llms(entries)
    print(f"Converted {len(entries)} files into {OUT}")
    print(f"Open: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
