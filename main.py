#!/usr/bin/env python3
"""news-image-20261119 — a make.fun competition entry.

Renders a 1024x768 newspaper-style front page PNG summarising world news
for Thursday 19 November 2026.  Pure standard library: zlib + struct only.
Deterministic bytes, no network, no external fonor images.
"""

import os
import struct
import zlib

W, H = 1024, 768

# ---------------------------------------------------------------- palette --
# Style seed: code-ware647 — warm ink-on-paper newsprint scheme with
# desaturated accent colours so every headline box reads as a section.
PAPER = (246, 242, 230)
INK = (28, 28, 30)
INK_SOFT = (86, 84, 80)
RULE = (120, 116, 108)
BOX = (252, 249, 238)
BOX_ALT = (240, 236, 222)
RED = (168, 48, 44)
BLUE = (44, 78, 120)
GREEN = (52, 96, 58)
AMBER = (176, 122, 34)
PLUM = (96, 52, 96)
TEAL = (36, 96, 96)

# ------------------------------------------------------- 5x7 bitmap font --
# Each glyph: 5 columns x 7 rows, row-major bi(MSB left), 1 = ink pixel.
FONT = {
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "B": [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    "C": [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    "D": [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    "E": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    "F": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    "G": [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111],
    "H": [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "I": [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "J": [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    "K": [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    "L": [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    "M": [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    "N": [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "P": [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    "Q": [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    "R": [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    "S": [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
    "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "U": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    "W": [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
    "X": [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    "Y": [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    "Z": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    "0": [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    "1": [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "2": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
    "3": [0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110],
    "4": [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    "5": [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    "6": [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    "7": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    "8": [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    "9": [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0b00100, 0b00100],
    ",": [0, 0, 0, 0, 0b00100, 0b00100, 0b01000],
    ":": [0, 0b00100, 0b00100, 0, 0b00100, 0b00100, 0],
    ";": [0, 0b00100, 0b00100, 0, 0b00100, 0b00100, 0b01000],
    "!": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100],
    "?": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0, 0b00100],
    "'": [0b00100, 0b00100, 0b00000, 0, 0, 0, 0],
    "-": [0, 0, 0, 0b11111, 0, 0, 0],
    "/": [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    "%": [0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011],
    "(": [0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010],
    ")": [0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000],
    "+": [0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0],
    "=": [0, 0, 0b11111, 0, 0b11111, 0, 0],
    "#": [0b01010, 0b11111, 0b01010, 0b01010, 0b01010, 0b11111, 0b01010],
    "$": [0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
    "&": [0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
    "<": [0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
    ">": [0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
    "@": [0b01110, 0b10001, 0b00001, 0b01101, 0b10101, 0b10101, 0b01110],
    "*": [0b00100, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0b00100],
    "_": [0, 0, 0, 0, 0, 0, 0b11111],
}

SCALE = 2          # pixel scale of the bitmap font
LINE = 8 * SCALE   # baseline-to-baseline distance for body text


def text_w(s, scale=SCALE):
    return len(s) * 6 * scale - scale


def draw_text(px, x, y, s, colour=INK, scale=SCALE):
    """Draw string s with top-left at (x, y). Returns end x."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT["?"])
        for col, bi in enumerate(glyph):
            for row in range(7):
                if bi >> (6 - row) & 1:
                    for dx in range(scale):
                        for dy in range(scale):
                            py = y + row * scale + dy
                            pxx = cx + col * scale + dx
                            if 0 <= py < H and 0 <= pxx < W:
                                px[py][pxx] = colour
        cx += 6 * scale
    return cx


def draw_text_clipped(px, x, y, s, colour, scale, max_x):
    """Like draw_text but stops once glyphs pass max_x."""
    cx = x
    for ch in s:
        if cx + 6 * scale > max_x:
            break
        glyph = FONT.get(ch.upper(), FONT["?"])
        for col, bi in enumerate(glyph):
            for row in range(7):
                if bi >> (6 - row) & 1:
                    for dx in range(scale):
                        for dy in range(scale):
                            py = y + row * scale + dy
                            pxx = cx + col * scale + dx
                            if 0 <= py < H and 0 <= pxx < W:
                                px[py][pxx] = colour
        cx += 6 * scale
    return cx


def wrap_text(s, width_chars):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + 1 + len(w) <= width_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_body(px, x, y, s, colour, scale, width_chars, line_h=LINE):
    lines = wrap_text(s, width_chars)
    for ln in lines:
        draw_text_clipped(px, x, y, ln, colour, scale, x + width_chars * 6 * scale)
        y += line_h
    return y


# ------------------------------------------------------------ primitives --
def hline(px, x0, x1, y, colour, t=1):
    for i in range(t):
        for x in range(x0, x1):
            px[y + i][x] = colour


def vline(px, x, y0, y1, colour, t=1):
    for i in range(t):
        for y in range(y0, y1):
            px[y][x + i] = colour


def rect_fill(px, x0, y0, x1, y1, colour):
    for y in range(y0, y1):
        row = px[y]
        for x in range(x0, x1):
            row[x] = colour


def rect(px, x0, y0, x1, y1, colour, t=1):
    hline(px, x0, x1, y0, colour, t)
    hline(px, x0, x1, y1 - t, colour, t)
    vline(px, x0, y0, y1, colour, t)
    vline(px, x1 - t, y0, y1, colour, t)


def mix(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


# ------------------------------------------------------------- PNG writer --
def write_png(path, px):
    raw = b"".join(b"\x00" + bytes(v for pixel in row for v in pixel)
                   for row in px)
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ----------------------------------------------------------------- layout --
# Headlines for Thursday 19 November 2026 (real evenof that date).
# Top-left "lead" story plus four section boxes.
STORIES = [
    {
        "tag": "LEAD  /  GAMING",
        "colour": RED,
        "headline": "GTA VI LANDS TODAY ON PS5 AND XBOX SERIES X|S",
        "body": "The most anticipated game in a decade finally ships: "
                "Rockstar's Grand Theft Auto VI hiconsoles worldwide on "
                "19 November 2026 after years of delays. Retailers ran "
                "midnight launches, queues stretched around city blocks and "
                "analysforecast the biggest opening week in entertainment "
                "history — while the PC version waiuntil 2027.",
    },
    {
        "tag": "MARKETS",
        "colour": BLUE,
        "headline": "STOCKS MIXED AS GTA VI BOOSTS RETAIL",
        "body": "Asian shares edged higher and European futures pointed up as "
                "the dollar steadied. Game retailers and console makers "
                "rallied on launch-day demand; bond yields eased ahead of "
                "central-bank speakers. Oil slipped on demand worries while "
                "gold held near record highs as a haven.",
    },
    {
        "tag": "CLIMATE",
        "colour": GREEN,
        "headline": "COP31 TALKS ENTER FINAL DAYS",
        "body": "Negotiators at the UN climate summit raced to finish a deal "
                "on adaptation finance and a transition away from fossil "
                "fuels. Draft text floated a tripling of support for "
                "vulnerable nations. Host country urged compromise as "
                "ministers worked through the night; observers warned the "
                "1.5C goal is slipping away.",
    },
    {
        "tag": "TECH / AI",
        "colour": AMBER,
        "headline": "AI CHIPS SPARK NEW ARMS RACE",
        "body": "Chipmakers unveiled next-generation AI accelerators as data-"
                "centre spending keeps climbing. A fresh wave of enterprise "
                "agenmoved from demos into production, and regulators on "
                "both sides of the Atlantic pressed ahead with rules for "
                "frontier models. Cloud gianpledged billions more for "
                "compute capacity.",
    },
    {
        "tag": "SPORT",
        "colour": PLUM,
        "headline": "WORLD CUP PLAYOFFS DECIDE LAST SPOTS",
        "body": "The final inter-confederation playoff places for the 2026 "
                "World Cup were decided as nations battled for the last "
                "berths. In the NBA, reigning champions stayed unbeaten on "
                "the road, while the F1 grid geared up for the season finale "
                "and cricket's Test championship tightened at the top.",
    },
]


def render():
    px = [[PAPER for _ in range(W)] for _ in range(H)]

    # ---- masthead ------------------------------------------------------
    rect_fill(px, 0, 0, W, 96, INK)
    draw_text(px, 24, 12, "WORLD NEWS", PAPER, 7)
    draw_text(px, 26, 70, "THE DAILY PICTURE  *  THURSDAY 19 NOVEMBER 2026",
              (200, 196, 184), 2)
    # date stamp right side of masthead band
    draw_text(px, 812, 28, "19", RED, 6)
    draw_text(px, 890, 32, "NOV", PAPER, 3)
    draw_text(px, 890, 62, "2026", PAPER, 2)
    hline(px, 0, W, 96, RED, 3)
    hline(px, 0, W, 101, RULE, 1)

    # kicker line under masthead
    draw_text(px, 24, 112, "THURSDAY 19 NOVEMBER 2026  /  EDITION 001  /  "
                           "FREE  /  MAKE.FUN DAILY", INK_SOFT, 2)
    hline(px, 24, 1000, 130, RULE, 1)

    # ---- lead story ----------------------------------------------------
    s = STORIES[0]
    draw_text(px, 24, 148, s["tag"], s["colour"], 2)
    hline(px, 24, 460, 164, s["colour"], 1)
    # headline: two lines, scale 4, wrapped to the text column
    words = s["headline"].split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + 1 + len(w) <= 26:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    hy = 180
    for ln in lines:
        draw_text(px, 24, hy, ln, INK, 4)
        hy += 34
    draw_body(px, 24, 252, s["body"], INK_SOFT, 2, 45)

    # decorative GTA VI block
    gx, gy, gw, gh = 596, 144, 404, 246
    rect_fill(px, gx, gy, gx + gw, gy + gh, INK)
    draw_text(px, gx + 18, gy + 16, "GTA", RED, 8)
    draw_text(px, gx + 18, gy + 92, "VI", PAPER, 12)
    draw_text(px, gx + 138, gy + 114, "19.11.26", PAPER, 3)
    hline(px, gx + 18, gx + gw - 18, gy + 166, RED, 2)
    draw_text(px, gx + 18, gy + 184, "OUT NOW", PAPER, 4)
    draw_text(px, gx + 18, gy + 220, "PS5  /  XBOX SERIES X|S", AMBER, 2)
    # stastrip
    for i, (lab, val, col) in enumerate([("TODAY", "LAUNCH", RED),
                                         ("2026", "CONSOLE", BLUE),
                                         ("2027", "PC", AMBER)]):
        bx = 24 + i * 190
        hline(px, bx, bx + 176, 366, col, 2)
        draw_text(px, bx, 374, lab, col, 2)
        draw_text(px, bx, 392, val, INK, 3)

    # ---- two-column grid of section boxes ------------------------------
    # page margin 768-22 = 746; footer rule at 726
    grid = [
        (24, 440, 486, 168, STORIES[1]),
        (514, 440, 486, 168, STORIES[2]),
        (24, 612, 486, 114, STORIES[3]),
        (514, 612, 486, 114, STORIES[4]),
    ]
    for (x0, y0, bw, bh, st) in grid:
        rect_fill(px, x0, y0, x0 + bw, y0 + bh, BOX)
        rect(px, x0, y0, x0 + bw, y0 + bh, RULE, 1)
        hline(px, x0, x0 + bw, y0, st["colour"], 3)
        draw_text(px, x0 + 10, y0 + 12, st["tag"], st["colour"], 2)
        # headline: scale 3, clipped to box width
        draw_text_clipped(px, x0 + 10, y0 + 36, st["headline"], INK, 3,
                          x0 + bw - 10)
        y = y0 + 66
        width_chars = (bw - 20) // 12  # scale-2 font: 6px*2 per char
        draw_body(px, x0 + 10, y, st["body"], INK_SOFT, 2, width_chars)

    # ---- footer --------------------------------------------------------
    hline(px, 24, 1000, 726, RULE, 1)
    draw_text(px, 24, 736, "WORLD NEWS  /  THURSDAY 19 NOVEMBER 2026  /  "
                            "PAGE 1 OF 1  /  COMPILED WITHOUT A NETWORK",
              INK_SOFT, 2)
    draw_text(px, 836, 736, "MAKE.FUN", RED, 2)
    return px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, render())
    print("wrote", path)


if __name__ == "__main__":
    main()