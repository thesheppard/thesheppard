#!/usr/bin/env python3
"""Generate the arcade-style SVG art used by the profile README.

Everything is drawn with a tiny built-in 5x7 pixel font, so the SVGs render
identically on GitHub (which blocks web fonts and scripts inside images).

Live numbers come from assets/stats.json, which scripts/fetch_stats.py
writes (the "Arcade stats" workflow runs both scripts daily).  Without that
file the scoreboards render with dashes.

Edit the CONFIG section below, then run:

    python3 scripts/build_arcade.py

and commit the regenerated files in assets/.
"""
import json
import re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- CONFIG ---
PLAYER = "THESHEPPARD"
TAGLINE = "SOFTWARE ENGINEER"
GITHUB_USER = "thesheppard"

# Each cartridge: (file slug, title line 1, title line 2, label colour A,
# label colour B, sprite name, GitHub language filter)
CARTRIDGES = [
    ("php", "PHP", "QUEST", "#4f5d95", "#a7b0ff", "sword", "php"),
    ("javascript", "JS", "JUMPER", "#f7df1e", "#ff9f1c", "bolt", "javascript"),
    ("typescript", "TYPESCRIPT", "TURBO", "#3178c6", "#00d4ff", "ship", "typescript"),
    ("vue", "VUE", "FIGHTER", "#41b883", "#35495e", "gem", "vue"),
    ("css", "CSS", "CRUSADER", "#e44d9b", "#663399", "heart", "css"),
    ("shell", "SHELL", "SHOCK", "#89e051", "#1e7a1e", "skull", "shell"),
    ("mql5", "MQL5", "MARKET RAID", "#ff3864", "#ffb000", "coin", "mql5"),
    ("html", "HTML", "HERO", "#e34c26", "#f06529", "star", "html"),
]

# Fighter-select stat bars, 0-10.  Purely for fun.
STATS = [
    ("BACKEND", 9),
    ("FRONTEND", 8),
    ("DEBUGGING", 9),
    ("CODE REVIEW", 10),
    ("COFFEE", 10),
]
MOVES = [
    "SPECIAL  SHIP IT    > > A",
    "COMBO    REFACTOR   v > B",
    "ULTRA    ZERO BUGS  < v > A+B",
]
# ------------------------------------------------------------------------

OUT = Path(__file__).resolve().parent.parent / "assets"
STATS_FILE = OUT / "stats.json"


def load_stats():
    try:
        return json.loads(STATS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


DATA = load_stats()


def num(key, digits=None):
    value = DATA.get(key)
    if not isinstance(value, int):
        return "-" * (digits or 4)
    return str(value).zfill(digits) if digits else str(value)


def days(key):
    return num(key) + (" DAY" if DATA.get(key) == 1 else " DAYS")


def level():
    """Years on GitHub, arcade style."""
    since = DATA.get("member_since")
    if not isinstance(since, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", since):
        return "--"
    return str(max(1, (date.today() - date.fromisoformat(since)).days // 365)).zfill(2)

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000"] * 7,
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "/": ["00001", "00001", "00010", "00100", "01000", "10000", "10000"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    "<": ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    "v": ["00000", "00000", "10001", "10001", "01010", "01010", "00100"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "©": ["01110", "10001", "10111", "10101", "10111", "10001", "01110"],
}

SPRITES = {
    "invader": ["00100000100", "00010001000", "00111111100", "01101110110",
                "11111111111", "10111111101", "10100000101", "00011011000"],
    "invader2": ["00100000100", "10010001001", "10111111101", "11101110111",
                 "11111111111", "01111111110", "00100000100", "01000000010"],
    "sword": ["000000011", "000000111", "000001110", "100011100", "010111000",
              "001110000", "011100000", "110010000", "100001000"],
    "bolt": ["0001111", "0011110", "0111100", "1111111", "0001110", "0011100",
             "0111000", "0110000", "1100000"],
    "ship": ["000010000", "000111000", "000111000", "001111100", "011111110",
             "111111111", "110111011", "100010001"],
    "gem": ["001111100", "011111110", "111111111", "011111110", "001111100",
            "000111000", "000010000"],
    "heart": ["011000110", "111101111", "111111111", "111111111", "011111110",
              "001111100", "000111000", "000010000"],
    "skull": ["011111110", "111111111", "110010011", "110010011", "111111111",
              "011101110", "001010100", "001111100"],
    "coin": ["001111100", "011000110", "110010011", "110111011", "110010011",
             "110010011", "011000110", "001111100"],
    "star": ["000010000", "000111000", "111111111", "011111110", "001111100",
             "011101110", "110000011"],
    "joystick": ["0011100", "0111110", "0111110", "0011100", "0001000",
                 "0001000", "1111111", "1111111"],
}


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def text_width(text, scale, spacing=1):
    return len(text) * (5 + spacing) * scale - spacing * scale


def bitmap_path(rows, x, y, scale):
    """Turn a bitmap into one compact SVG path, merging horizontal runs."""
    parts = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == "1":
                start = c
                while c < len(row) and row[c] == "1":
                    c += 1
                parts.append(
                    f"M{x + start * scale:g} {y + r * scale:g}"
                    f"h{(c - start) * scale:g}v{scale:g}h{-(c - start) * scale:g}z"
                )
            else:
                c += 1
    return "".join(parts)


def pixel_text(text, x, y, scale, spacing=1, anchor="start"):
    if anchor == "middle":
        x -= text_width(text, scale, spacing) / 2
    elif anchor == "end":
        x -= text_width(text, scale, spacing)
    out = []
    for i, ch in enumerate(text):
        glyph = FONT.get(ch, FONT.get(ch.upper(), FONT["?"]))
        out.append(bitmap_path(glyph, x + i * (5 + spacing) * scale, y, scale))
    return "".join(out)


def svg(width, height, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(title, {chr(34): "&quot;"})}">'
        f"<title>{escape(title)}</title>{body}</svg>\n"
    )


SCANLINES = (
    '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="2" fill="#000" opacity=".28"/></pattern>'
)
GLOW = (
    '<filter id="glow" x="-20%" y="-40%" width="140%" height="180%">'
    '<feGaussianBlur stdDeviation="{s}" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
    "</filter>"
)


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote assets/{name} ({len(content.encode()) // 1024 or 1} KB)")


# ----------------------------------------------------------------- MARQUEE --
def marquee():
    W, H = 1000, 340
    import random

    rnd = random.Random(7)
    stars = "".join(
        f'<rect class="tw" x="{rnd.randrange(0, W)}" y="{rnd.randrange(0, 200)}" '
        f'width="{s}" height="{s}" style="animation-delay:-{rnd.random() * 3:.2f}s"/>'
        for s in (rnd.choice((2, 2, 3)) for _ in range(70))
    )
    # synthwave floor: perspective verticals + scrolling horizontals
    horizon = 250
    verticals = "".join(
        f'<line x1="{W / 2 + i * 22}" y1="{horizon}" x2="{W / 2 + i * 140}" y2="{H}"/>'
        for i in range(-12, 13)
    )
    horizontals = "".join(
        f'<line class="hz" x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" '
        f'style="animation-delay:-{i * 0.5:.1f}s"/>'
        for i in range(4)
    )
    title_scale = 10
    title_y = 80
    title = pixel_text(PLAYER, W / 2, title_y, title_scale, anchor="middle")
    tag = pixel_text(TAGLINE, W / 2, title_y + 7 * title_scale + 22, 4, anchor="middle")
    coin = pixel_text("INSERT COIN", W / 2, 292, 4, anchor="middle")
    # 1UP = contributions in the last year, HI-SCORE = all time, LVL = years on GitHub
    hud_l = pixel_text("1UP", 40, 20, 3)
    hud_l2 = pixel_text(num("contributions_last_year", 6), 40, 46, 3)
    hud_c = pixel_text("HI-SCORE", W / 2, 20, 3, anchor="middle")
    hud_c2 = pixel_text(num("contributions", 6), W / 2, 46, 3, anchor="middle")
    hud_r = pixel_text("LVL " + level(), W - 40, 20, 3, anchor="end")
    inv = "".join(
        f'<g class="bob" style="animation-delay:-{i * 0.25}s">'
        f'<path class="inv{i % 2}" d="{bitmap_path(SPRITES["invader" if i % 2 else "invader2"], 0, 0, 3)}" '
        f'transform="translate({90 + i * 70} 0)"/></g>'
        for i in range(12)
    )
    body = f"""
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#07001a"/><stop offset=".65" stop-color="#2b0a4a"/><stop offset="1" stop-color="#4a0d55"/></linearGradient>
<linearGradient id="neon" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#fff35c"/><stop offset=".45" stop-color="#ff8a3d"/><stop offset="1" stop-color="#ff2e88"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#ffd23f"/><stop offset="1" stop-color="#ff2e88"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#2b0a4a" stop-opacity="1"/><stop offset=".35" stop-color="#2b0a4a" stop-opacity="0"/></linearGradient>
<clipPath id="floor"><rect x="0" y="{horizon}" width="{W}" height="{H - horizon}"/></clipPath>
{SCANLINES}{GLOW.format(s=4)}
</defs>
<style>
.tw{{fill:#fff;animation:tw 3s steps(3) infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.grid line{{stroke:#ff2e88;stroke-width:2;opacity:.7}}
.hz{{animation:hz 2s linear infinite}}
@keyframes hz{{0%{{transform:translateY(0);opacity:.2}}100%{{transform:translateY({H - horizon}px);opacity:1}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
.flicker{{animation:flicker 6s infinite}}
@keyframes flicker{{0%,19%,21%,62%,64%,100%{{opacity:1}}20%,63%{{opacity:.55}}}}
.bob{{animation:bob 1.2s steps(2) infinite}}
@keyframes bob{{0%{{transform:translate(0,0)}}50%{{transform:translate(0,6px)}}}}
.march{{animation:march 8s steps(16) infinite alternate}}
@keyframes march{{from{{transform:translateX(-40px)}}to{{transform:translateX(40px)}}}}
.inv0{{fill:#3cf0ff}}.inv1{{fill:#a5ff3c}}
.hud{{fill:#ff2e88}}.hud2{{fill:#fff}}
</style>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars}
<g transform="translate(0 222)" opacity=".9"><g class="march">{inv}</g></g>
<circle cx="{W / 2}" cy="{horizon}" r="120" fill="url(#sun)" opacity=".35"/>
<g clip-path="url(#floor)"><rect x="0" y="{horizon}" width="{W}" height="{H - horizon}" fill="#12002b"/>
<g class="grid">{verticals}{horizontals}</g><rect x="0" y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#fade)"/></g>
<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="#ff2e88" stroke-width="3" filter="url(#glow)"/>
<path class="hud" d="{hud_l}{hud_c}{hud_r}"/>
<path class="hud2" d="{hud_l2}{hud_c2}"/>
<g class="flicker" filter="url(#glow)">
<path d="{title}" fill="#5a1a8a" transform="translate(6 6)"/>
<path d="{title}" fill="url(#neon)"/>
</g>
<path d="{tag}" fill="#3cf0ff" filter="url(#glow)"/>
<path class="blink" d="{coin}" fill="#fff" filter="url(#glow)"/>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="18" fill="none" stroke="#ff2e88" stroke-width="6"/>
<rect x="12" y="12" width="{W - 24}" height="{H - 24}" rx="12" fill="none" stroke="#3cf0ff" stroke-width="2" opacity=".6"/>
"""
    write("marquee.svg", svg(W, H, body, f"{PLAYER} - {TAGLINE}"))


# --------------------------------------------------------- SECTION HEADERS --
def header(slug, text, colour):
    W, H = 1000, 70
    t = pixel_text(text, W / 2, 21, 4, anchor="middle")
    tw = text_width(text, 4)
    arrow = bitmap_path(FONT[">"], 0, 0, 4)
    lx = W / 2 - tw / 2 - 60
    rx = W / 2 + tw / 2 + 40
    body = f"""
<defs>{GLOW.format(s=3)}</defs>
<style>
.a{{animation:nudge .8s steps(2) infinite}}
@keyframes nudge{{0%{{transform:translateX(0)}}50%{{transform:translateX(8px)}}}}
.b{{animation:nudge2 .8s steps(2) infinite}}
@keyframes nudge2{{0%{{transform:translateX(0)}}50%{{transform:translateX(-8px)}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0b0221"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="9" fill="none" stroke="{colour}" stroke-width="3" stroke-dasharray="12 6"/>
<g filter="url(#glow)" fill="{colour}">
<path d="{t}"/>
<g class="a"><path d="{arrow}" transform="translate({lx} 21)"/></g>
<g class="b"><path d="{arrow}" transform="translate({rx + 20} 21) scale(-1 1)"/></g>
</g>
"""
    write(f"header-{slug}.svg", svg(W, H, body, text))


# --------------------------------------------------------------- CARTRIDGE --
def cartridge(slug, line1, line2, c1, c2, sprite, _lang):
    W, H = 220, 250
    # plastic shell with the classic notched top and grip ridges
    shell = (
        f"M14 0H{W - 14}Q{W} 0 {W} 14V{H - 30}L{W - 14} {H - 30}V{H - 6}"
        f"Q{W - 14} {H} {W - 20} {H}H20Q14 {H} 14 {H - 6}V{H - 30}L0 {H - 30}V14Q0 0 14 0Z"
    )
    ridges = "".join(
        f'<rect x="{30 + i * 18}" y="10" width="8" height="22" rx="2" fill="#000" opacity=".25"/>'
        for i in range(9)
    )
    lx, ly, lw, lh = 22, 44, W - 44, 150
    sp = SPRITES[sprite]
    sscale = 5
    spw = len(sp[0]) * sscale
    sprite_d = bitmap_path(sp, W / 2 - spw / 2, ly + 16, sscale)
    s1 = 4 if text_width(line1, 4) <= lw - 16 else 3
    s2 = 3 if text_width(line2, 3) <= lw - 16 else 2
    t1 = pixel_text(line1, W / 2, ly + 78, s1, anchor="middle")
    t2 = pixel_text(line2, W / 2, ly + 78 + 7 * s1 + 10, s2, anchor="middle")
    footer = pixel_text("16-BIT", W / 2, ly + lh + 18, 2, anchor="middle")
    body = f"""
<defs>
<linearGradient id="plastic" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#4a4a58"/><stop offset="1" stop-color="#26262f"/></linearGradient>
<linearGradient id="label" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="lc"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="6"/></clipPath>
<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="#fff" opacity=".12"/></pattern>
</defs>
<style>
.sh{{animation:sh 4s ease-in-out infinite}}
@keyframes sh{{0%,60%{{transform:translateX(-160px)}}100%{{transform:translateX(260px)}}}}
.fl{{animation:fl 1.6s steps(2) infinite}}
@keyframes fl{{0%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
</style>
<path d="{shell}" fill="url(#plastic)"/>
<path d="{shell}" fill="none" stroke="#000" stroke-opacity=".5" stroke-width="2"/>
{ridges}
<rect x="{lx - 4}" y="{ly - 4}" width="{lw + 8}" height="{lh + 8}" rx="8" fill="#15151c"/>
<g clip-path="url(#lc)">
<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="url(#label)"/>
<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="url(#dots)"/>
<rect x="{lx}" y="{ly + 68}" width="{lw}" height="{lh - 68}" fill="#0b0221" opacity=".55"/>
<g class="fl"><path d="{sprite_d}" fill="#000" opacity=".35" transform="translate(3 3)"/><path d="{sprite_d}" fill="#fff"/></g>
<path d="{t1}" fill="#000" opacity=".5" transform="translate(2 2)"/><path d="{t1}" fill="#fff"/>
<path d="{t2}" fill="{max((c1, c2), key=luminance)}"/>
<g class="sh"><rect x="{lx}" y="{ly}" width="60" height="{lh}" fill="url(#shine)" transform="skewX(-20)"/></g>
</g>
<path d="{footer}" fill="#9a9aab"/>
"""
    write(f"cart-{slug}.svg", svg(W, H, body, f"{line1} {line2}"))


# ----------------------------------------------------------- PLAYER SELECT --
def player_card():
    W, H = 1000, 330
    stats = []
    y = 70
    for i, (name, val) in enumerate(STATS):
        stats.append(f'<path d="{pixel_text(name, 420, y, 3)}" fill="#fff"/>')
        for b in range(10):
            on = b < val
            stats.append(
                f'<rect class="{"seg" if on else ""}" x="{640 + b * 30}" y="{y - 2}" width="24" height="25" '
                f'fill="{"#a5ff3c" if on and b < 6 else "#ffd23f" if on and b < 9 else "#ff2e88" if on else "#2b1a45"}" '
                f'style="animation-delay:{b * 0.06 + i * 0.1:.2f}s"/>'
            )
        y += 40
    moves = "".join(
        f'<path d="{pixel_text(m, 60, 268 + i * 20, 2)}" fill="{("#3cf0ff", "#ffd23f", "#ff2e88")[i % 3]}"/>'
        for i, m in enumerate(MOVES)
    )
    hero = bitmap_path(SPRITES["invader"], 110, 60, 14)
    body = f"""
<defs>{SCANLINES}{GLOW.format(s=3)}
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0221"/><stop offset="1" stop-color="#1d0638"/></linearGradient>
</defs>
<style>
.seg{{animation:fill .5s steps(1) both}}
@keyframes fill{{0%{{opacity:0}}100%{{opacity:1}}}}
.sel{{animation:sel 1s steps(1) infinite}}
@keyframes sel{{0%{{stroke:#ffd23f}}50%{{stroke:#ff2e88}}}}
.hero{{animation:bob 1s steps(2) infinite}}
@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
<rect class="sel" x="40" y="24" width="320" height="220" rx="6" fill="#12002b" stroke-width="5"/>
<path d="{pixel_text("P1", 56, 38, 3)}" fill="#ffd23f"/>
<path d="{pixel_text("LVL " + level(), 344, 38, 3, anchor="end")}" fill="#3cf0ff"/>
<g class="hero" filter="url(#glow)"><path d="{hero}" fill="#a5ff3c"/></g>
<path d="{pixel_text(PLAYER, 200, 204, 3, anchor="middle")}" fill="#fff"/>
<path d="{pixel_text("CLASS: " + TAGLINE, 420, 30, 2)}" fill="#ff2e88"/>
{"".join(stats)}
{moves}
<rect width="{W}" height="{H}" fill="url(#scan)"/>
"""
    write("player-select.svg", svg(W, H, body, f"Player 1: {PLAYER}"))


# ----------------------------------------------------------------- CONTINUE --
def continue_screen():
    W, H = 1000, 200
    digits = "".join(
        f'<path class="d" style="animation-delay:-{d + 1}s" d="{pixel_text(str(d), 680, 40, 10)}"/>'
        for d in range(9, -1, -1)
    )
    body = f"""
<defs>{SCANLINES}{GLOW.format(s=4)}</defs>
<style>
.d{{fill:#ffd23f;opacity:0;animation:cd 10s steps(1,end) infinite}}
@keyframes cd{{0%{{opacity:1}}10%,100%{{opacity:0}}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="#07001a"/>
<g filter="url(#glow)">
<path d="{pixel_text("CONTINUE?", 230, 52, 7)}" fill="#ff2e88"/>
{digits}
</g>
<path class="blink" d="{pixel_text("PRESS START TO FOLLOW", W / 2, 140, 3, anchor="middle")}" fill="#fff"/>
<path d="{pixel_text("THANKS FOR PLAYING", W / 2, 172, 2, anchor="middle")}" fill="#3cf0ff"/>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
"""
    write("continue.svg", svg(W, H, body, "Continue? Press start to follow"))


# ------------------------------------------------------------- HIGH SCORES --
ORDINALS = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH"]
ROW_COLOURS = ["#ffd23f", "#ff8a3d", "#ff2e88", "#e44dff", "#3cf0ff", "#a5ff3c", "#ffffff", "#9a9aab"]


def high_scores():
    # GitHub only reports private work as one total, so commit and PR
    # counts are public-only and the private total gets its own row.
    rows = [
        ("CONTRIBUTIONS", "contributions"),
        ("PRIVATE WORK", "private"),
        ("LAST 365 DAYS", "contributions_last_year"),
        ("PUBLIC COMMITS", "commits"),
        ("PUBLIC PRS", "pull_requests"),
        ("PUBLIC REPOS", "public_repos"),
        ("FOLLOWERS", "followers"),
        ("STARS EARNED", "stars"),
    ]
    # rank like a real high-score table: biggest number first
    rows.sort(key=lambda r: -DATA[r[1]] if isinstance(DATA.get(r[1]), int) else 0)
    W, H = 1000, 580
    out = []
    y = 120
    for i, (label, key) in enumerate(rows):
        colour = ROW_COLOURS[i]
        cls = "row top" if i == 0 else "row"
        score = num(key, 6)
        dots_from = 260 + text_width(label, 4) + 16
        dots_to = 870 - text_width(score, 4) - 12
        dots = "".join(
            f'<rect x="{x}" y="{y + 18}" width="4" height="4"/>' for x in range(dots_from, dots_to, 14)
        )
        out.append(
            f'<g class="{cls}" fill="{colour}" style="animation-delay:{i * 0.12:.2f}s">'
            f'<path d="{pixel_text(ORDINALS[i], 140, y, 4)}"/>'
            f'<path d="{pixel_text(label, 260, y, 4)}"/>'
            f'<g opacity=".5">{dots}</g>'
            f'<path d="{pixel_text(score, 870, y, 4, anchor="end")}"/></g>'
        )
        y += 44
    private = DATA.get("private", 0)
    note = "ALL TIME  -  CONTRIBUTIONS INCLUDE PRIVATE REPOS" if isinstance(private, int) and private > 0 else "ALL TIME  -  PUBLIC ACTIVITY"
    updated = DATA.get("updated", "")
    updated = updated if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(updated)) else "NEVER"
    combo = (
        f'<path d="{pixel_text("COMBO " + days("current_streak"), 140, 488, 3)}" fill="#a5ff3c"/>'
        f'<path d="{pixel_text("BEST COMBO " + days("longest_streak"), 870, 488, 3, anchor="end")}" fill="#ffd23f"/>'
    )
    body = f"""
<defs>{SCANLINES}{GLOW.format(s=3)}
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07001a"/><stop offset="1" stop-color="#1d0638"/></linearGradient>
</defs>
<style>
.row{{animation:in .4s steps(1) both}}
@keyframes in{{0%{{opacity:0}}100%{{opacity:1}}}}
.top{{animation:in .4s steps(1) both,flash 1.2s steps(1) .4s infinite}}
@keyframes flash{{0%{{opacity:1}}50%{{opacity:.35}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
<g filter="url(#glow)">
<path d="{pixel_text("RANK", 140, 70, 3)}" fill="#3cf0ff"/>
<path d="{pixel_text("STAT", 260, 70, 3)}" fill="#3cf0ff"/>
<path d="{pixel_text("SCORE", 870, 70, 3, anchor="end")}" fill="#3cf0ff"/>
{"".join(out)}
{combo}
</g>
<path d="{pixel_text(note, W / 2, 528, 2, anchor="middle")}" fill="#9a9aab"/>
<path d="{pixel_text("LAST UPDATED " + updated, W / 2, 548, 2, anchor="middle")}" fill="#5c5c70"/>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="12" fill="none" stroke="#3cf0ff" stroke-width="4"/>
"""
    write("high-scores.svg", svg(W, H, body, "High scores: " + ", ".join(
        f"{label.title()} {num(key)}" for label, key in rows)))


# --------------------------------------------------------------- POWER-UPS --
def safe_colour(value):
    return value if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) else "#8b949e"


def power_ups():
    langs = [
        l for l in DATA.get("languages", [])
        if isinstance(l, dict) and isinstance(l.get("name"), str) and isinstance(l.get("percent"), (int, float))
    ][:8]
    W = 1000
    H = 150 + max(len(langs), 1) * 40
    # stacked "health bar" across the top
    bar, x, bw = [], 140, 730
    for l in langs:
        w = bw * l["percent"] / 100
        bar.append(f'<rect x="{x:.1f}" y="70" width="{w:.1f}" height="24" fill="{safe_colour(l.get("color"))}"/>')
        x += w
    rows, y = [], 124
    top = max((l["percent"] for l in langs), default=1) or 1
    for i, l in enumerate(langs):
        colour = safe_colour(l.get("color"))
        segs = round(16 * l["percent"] / top)
        blocks = "".join(
            f'<rect x="{500 + b * 15}" y="{y}" width="11" height="21"/>' for b in range(segs)
        )
        rows.append(
            f'<g class="row" style="animation-delay:{i * 0.1:.1f}s">'
            f'<rect x="140" y="{y}" width="21" height="21" fill="{colour}"/>'
            f'<path d="{pixel_text(l["name"].upper()[:16], 180, y, 3)}" fill="#fff"/>'
            f'<g fill="{colour}">{blocks}</g>'
            f'<path d="{pixel_text("%.1f%%" % l["percent"], 870, y, 3, anchor="end")}" fill="#ffd23f"/></g>'
        )
        y += 40
    if not langs:
        rows.append(f'<path d="{pixel_text("NO DATA YET", W / 2, y, 3, anchor="middle")}" fill="#9a9aab"/>')
    body = f"""
<defs>{SCANLINES}{GLOW.format(s=2)}</defs>
<style>
.row{{animation:in .4s steps(1) both}}
@keyframes in{{0%{{opacity:0}}100%{{opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="#0b0221"/>
<path d="{pixel_text("POWER-UPS  /  LANGUAGES BY CODE SIZE", 140, 34, 3)}" fill="#a5ff3c" filter="url(#glow)"/>
<rect x="136" y="66" width="{bw + 8}" height="32" fill="none" stroke="#fff" stroke-width="3"/>
{"".join(bar)}
{"".join(rows)}
<rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="12" fill="none" stroke="#a5ff3c" stroke-width="4"/>
"""
    write("power-ups.svg", svg(W, H, body, "Top languages: " + ", ".join(
        f'{l["name"]} {l["percent"]}%' for l in langs)))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    marquee()
    header("select-game", "SELECT GAME", "#ffd23f")
    header("player-1", "PLAYER 1", "#a5ff3c")
    header("high-scores", "HIGH SCORES", "#3cf0ff")
    for cart in CARTRIDGES:
        cartridge(*cart)
    player_card()
    high_scores()
    power_ups()
    continue_screen()
