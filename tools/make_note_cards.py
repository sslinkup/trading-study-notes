#!/usr/bin/env python3
"""Render one social card per note from a shared SVG template."""
import html
import sys
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = ROOT / "public_src" / "cards"
PNG_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public_html" / "cards"

CARDS = [
    ("A_foundations", "01", ["FOUNDATIONS"],
     "Mindset, bankroll and journaling", "foundations", "#34d399"),
    ("B_mistakes", "02", ["MISTAKES", "& RISK"],
     "Anti-patterns, stops and profit discipline", "mistakes", "#fb7185"),
    ("C_lessons", "03", ["TRADING", "LESSONS"],
     "Philosophy, edge, leverage and shorting", "lessons", "#fbbf24"),
    ("D_stochastic", "04", ["RSI &", "STOCHASTIC"],
     "Health levels, divergence and the NKED method", "stochastic", "#22d3ee"),
    ("E_indicators", "05", ["INDICATORS", "& CHARTS"],
     "EMAs, Ichimoku, Keltner and volume clusters", "indicators", "#a78bfa"),
    ("F_volume_timing", "06", ["VOLUME", "& TIMING"],
     "Order flow, timeframes and entries", "volume", "#34d399"),
    ("G_patrick_nill", "07", ["PATRICK", "NILL"],
     "Championship range and order-flow methods", "lessons", "#fbbf24"),
]


def visual(kind, accent):
    if kind == "foundations":
        return f"""
    <g stroke="{accent}" stroke-width="3" fill="none" opacity="0.9">
      <rect x="40" y="200" width="360" height="18" rx="9"/>
      <rect x="40" y="150" width="290" height="18" rx="9"/>
      <rect x="40" y="100" width="220" height="18" rx="9"/>
    </g>
    <g fill="{accent}" opacity="0.35">
      <circle cx="330" cy="60" r="26"/><circle cx="370" cy="60" r="26"/>
      <circle cx="350" cy="110" r="26"/>
    </g>"""
    if kind == "mistakes":
        return f"""
    <path d="M220 70 L390 290 L50 290 Z" fill="{accent}" opacity="0.12" stroke="{accent}" stroke-width="3"/>
    <text x="220" y="235" fill="{accent}" font-family="Helvetica, Arial, sans-serif"
          font-size="110" font-weight="bold" text-anchor="middle">!</text>"""
    if kind == "lessons":
        return f"""
    <circle cx="220" cy="180" r="120" fill="none" stroke="{accent}" stroke-width="3" opacity="0.7"/>
    <circle cx="220" cy="180" r="86" fill="none" stroke="{accent}" stroke-width="1" opacity="0.35"/>
    <path d="M220 180 L300 96 L232 172 Z" fill="{accent}"/>
    <circle cx="220" cy="180" r="9" fill="#f8fafc"/>
    <g fill="{accent}"><circle cx="220" cy="60" r="5"/><circle cx="340" cy="180" r="5"/>
      <circle cx="220" cy="300" r="5"/><circle cx="100" cy="180" r="5"/></g>"""
    if kind == "stochastic":
        lines = "".join(
            f'<line x1="30" y1="{y}" x2="410" y2="{y}" stroke="#334155" stroke-dasharray="6 6"/>'
            for y in (90, 150, 210, 270)
        )
        return f"""
    {lines}
    <polyline points="30,260 90,200 150,230 210,120 270,160 330,80 410,110"
              fill="none" stroke="{accent}" stroke-width="4" stroke-linejoin="round"/>
    <polyline points="30,285 90,250 150,265 210,190 270,215 330,150 410,175"
              fill="none" stroke="#f8fafc" stroke-width="2" opacity="0.55" stroke-linejoin="round"/>"""
    if kind == "indicators":
        return f"""
    <path d="M30 250 L110 190 L190 215 L270 120 L350 150 L410 80"
          fill="none" stroke="{accent}" stroke-width="4" stroke-linejoin="round"/>
    <path d="M30 280 L110 230 L190 250 L270 170 L350 195 L410 130"
          fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="7 7"/>
    <path d="M120 130 L200 90 L300 115 L360 80 L360 190 L120 190 Z"
          fill="{accent}" opacity="0.12" stroke="{accent}" stroke-width="1"/>
    <line x1="30" y1="215" x2="410" y2="215" stroke="#22d3ee" stroke-width="2" opacity="0.7"/>"""
    return f"""
    <g fill="{accent}" opacity="0.85">
      <rect x="40" y="220" width="30" height="70" rx="4"/>
      <rect x="90" y="180" width="30" height="110" rx="4"/>
      <rect x="140" y="200" width="30" height="90" rx="4"/>
      <rect x="190" y="130" width="30" height="160" rx="4"/>
      <rect x="240" y="160" width="30" height="130" rx="4"/>
      <rect x="290" y="90" width="30" height="200" rx="4"/>
      <rect x="340" y="120" width="30" height="170" rx="4"/>
    </g>
    <g fill="#fb7185" opacity="0.5">
      <rect x="40" y="180" width="30" height="40" rx="4"/>
      <rect x="140" y="165" width="30" height="35" rx="4"/>
      <rect x="240" y="125" width="30" height="35" rx="4"/>
    </g>"""


def card_svg(num, title_lines, subtitle, kind, accent):
    lines = ""
    for i, line in enumerate(title_lines):
        y = 196 + i * 76
        lines += (f'<text x="70" y="{y}" fill="#f8fafc" '
                  f'font-family="Helvetica, Arial, sans-serif" font-size="64" '
                  f'font-weight="bold" letter-spacing="-1">{html.escape(line)}</text>')
    sub_y = 210 + len(title_lines) * 76
    vis = visual(kind, accent)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#111c33"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <g stroke="#22304a" stroke-width="1" opacity="0.55">
    <path d="M0 105H1200 M0 210H1200 M0 315H1200 M0 420H1200 M0 525H1200"/>
    <path d="M200 0V630 M400 0V630 M600 0V630 M800 0V630 M1000 0V630"/>
  </g>
  <rect x="70" y="72" width="146" height="34" rx="17" fill="{accent}" opacity="0.14"/>
  <text x="143" y="95" fill="{accent}" font-family="Helvetica, Arial, sans-serif"
        font-size="16" font-weight="bold" text-anchor="middle" letter-spacing="2">NOTE {num} / 07</text>
  {lines}
  <text x="72" y="{sub_y}" fill="#94a3b8" font-family="Helvetica, Arial, sans-serif"
        font-size="27">{html.escape(subtitle)}</text>
  <text x="72" y="{sub_y + 44}" fill="#64748b" font-family="Helvetica, Arial, sans-serif"
        font-size="19">Click any timestamp to jump to the source video</text>
  <g transform="translate(690,110)">
    <rect x="0" y="0" width="440" height="320" rx="18" fill="#0e1a30" stroke="#1e3a5f"/>
    <g transform="translate(10,10)">{vis}</g>
  </g>
  <g transform="translate(690,472)">
    <line x1="8" y1="34" x2="424" y2="34" stroke="#334155" stroke-width="3"/>
    <line x1="8" y1="34" x2="250" y2="34" stroke="{accent}" stroke-width="3"/>
    <g fill="{accent}"><circle cx="8" cy="34" r="8"/><circle cx="190" cy="34" r="8"/>
      <circle cx="250" cy="34" r="8"/></g>
    <circle cx="250" cy="34" r="15" fill="none" stroke="{accent}" opacity="0.4" stroke-width="2"/>
    <g fill="#64748b" font-family="Helvetica, Arial, sans-serif" font-size="16">
      <text x="8" y="70" text-anchor="middle">00:00</text>
      <text x="190" y="70" text-anchor="middle">01:57</text>
      <text x="250" y="70" text-anchor="middle">03:51</text>
    </g>
  </g>
  <line x1="70" y1="555" x2="1130" y2="555" stroke="#1e3a5f" stroke-width="1"/>
  <text x="70" y="592" fill="#64748b" font-family="Helvetica, Arial, sans-serif"
        font-size="19">trading-study-notes.sanliurfa.workers.dev</text>
  <text x="1130" y="592" fill="#475569" font-family="Helvetica, Arial, sans-serif"
        font-size="17" text-anchor="end">independent study guide - not affiliated with the creator</text>
</svg>
"""


def main():
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for slug, num, lines, subtitle, kind, accent in CARDS:
        svg = card_svg(num, lines, subtitle, kind, accent)
        (SVG_DIR / f"{slug}.svg").write_text(svg, encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(PNG_DIR / f"{slug}.png"),
                         output_width=1200, output_height=630)
        print(f"cards/{slug}.png")


if __name__ == "__main__":
    main()
