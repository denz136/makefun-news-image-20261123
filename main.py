# rev1: 23 November 2026 layout
#!/usr/bin/env python3
"""Writes /output/entry.png — a one-image summary of world news for Monday 23 November 2026.

Pure Python standard library: the PNG is rasterised and encoded here with zlib only.

    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import math
import os
import struct
import zlib

W = H = 1024

# ---------------------------------------------------------------- palette
BG = (12, 17, 28)
PANEL = (22, 30, 45)
PANEL_EDGE = (38, 49, 70)
INK = (242, 246, 252)
INK_DIM = (176, 190, 210)
RED = (226, 74, 74)
ORANGE = (240, 152, 62)
BLUE = (74, 144, 236)
GREEN = (74, 190, 126)
YELLOW = (238, 206, 92)
STEEL = (92, 99, 114)
SEA = (44, 66, 104)
WATER = (54, 86, 138)

# ---------------------------------------------------------------- canvas
pix = bytearray()
_row = bytearray(BG) * W
for _ in range(H):
    pix += _row

CLIP = None

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        if CLIP is not None:
            cx0, cy0, cx1, cy1 = CLIP
            if not (cx0 <= x < cx1 and cy0 <= y < cy1):
                return
        i = (y * W + x) * 3
        pix[i] = c[0]; pix[i + 1] = c[1]; pix[i + 2] = c[2]

def rect(x0, y0, x1, y1, c):
    x0 = max(0, int(x0)); y0 = max(0, int(y0))
    x1 = min(W, int(x1)); y1 = min(H, int(y1))
    if x1 <= x0 or y1 <= y0:
        return
    row = bytearray(c) * (x1 - x0)
    for y in range(y0, y1):
        o = (y * W + x0) * 3
        pix[o:o + len(row)] = row

def line(x0, y0, x1, y1, c, w=2):
    x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy)) or 1
    h = w // 2
    for i in range(steps + 1):
        x = x0 + dx * i / steps
        y = y0 + dy * i / steps
        for oy in range(-h, h + 1):
            for ox in range(-h, h + 1):
                px(int(x) + ox, int(y) + oy, c)

def mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))

def arc(cx, cy, r, a0, a1, c, w=2):
    steps = max(8, int(abs(a1 - a0) * r / 40) + 8)
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        circle(cx + r * math.cos(a), cy + r * math.sin(a), w / 2.0, c, True)

def arrow(x0, y0, x1, y1, c, w=2, head=8):
    line(x0, y0, x1, y1, c, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    for d in (2.5, -2.5):
        line(x1, y1, x1 - head * math.cos(ang + d / 2.6 * 1.2),
             y1 - head * math.sin(ang + d / 2.6 * 1.2), c, w)

def circle(cx, cy, r, c, fill=True, thick=3):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if fill:
                if d2 <= r * r:
                    px(x, y, c)
            else:
                inner = (r - thick) ** 2
                if inner <= d2 <= r * r:
                    px(x, y, c)

# ---------------------------------------------------------------- bitmap font 5x7
FONT = {
    '0': ("111", "101", "101", "101", "111"),
    '1': ("010", "110", "010", "010", "111"),
    '2': ("111", "001", "111", "100", "111"),
    '3': ("111", "001", "111", "001", "111"),
    '4': ("101", "101", "111", "001", "001"),
    '5': ("111", "100", "111", "001", "111"),
    '6': ("111", "100", "111", "101", "111"),
    '7': ("111", "001", "010", "010", "010"),
    '8': ("111", "101", "111", "101", "111"),
    '9': ("111", "101", "111", "001", "111"),
    'A': ("111", "101", "111", "101", "101"),
    'B': ("110", "101", "110", "101", "110"),
    'C': ("111", "100", "100", "100", "111"),
    'D': ("110", "101", "101", "101", "110"),
    'E': ("111", "100", "111", "100", "111"),
    'F': ("111", "100", "111", "100", "100"),
    'G': ("111", "100", "101", "101", "111"),
    'H': ("101", "101", "111", "101", "101"),
    'I': ("111", "010", "010", "010", "111"),
    'J': ("001", "001", "001", "101", "111"),
    'K': ("101", "101", "110", "101", "101"),
    'L': ("100", "100", "100", "100", "111"),
    'M': ("101", "111", "111", "101", "101"),
    'N': ("110", "101", "101", "101", "101"),
    'O': ("111", "101", "101", "101", "111"),
    'P': ("111", "101", "111", "100", "100"),
    'Q': ("111", "101", "101", "111", "011"),
    'R': ("111", "101", "110", "101", "101"),
    'S': ("111", "100", "111", "001", "111"),
    'T': ("111", "010", "010", "010", "010"),
    'U': ("101", "101", "101", "101", "111"),
    'V': ("101", "101", "101", "101", "010"),
    'W': ("101", "101", "111", "111", "101"),
    'X': ("101", "101", "010", "101", "101"),
    'Y': ("101", "101", "010", "010", "010"),
    'Z': ("111", "001", "010", "100", "111"),
    ' ': ("000", "000", "000", "000", "000"),
    '.': ("000", "000", "000", "000", "010"),
    ',': ("000", "000", "000", "010", "100"),
    ':': ("000", "010", "000", "010", "000"),
    '-': ("000", "000", "111", "000", "000"),
    '/': ("001", "001", "010", "100", "100"),
    '!': ("010", "010", "010", "000", "010"),
    "'": ("010", "010", "000", "000", "000"),
    '%': ("101", "001", "010", "100", "101"),
    '+': ("000", "010", "111", "010", "000"),
    '(': ("010", "100", "100", "100", "010"),
    ')': ("010", "001", "001", "001", "010"),
    '"': ("101", "101", "000", "000", "000"),
    '&': ("110", "100", "111", "101", "111"),
    '$': ("111", "110", "111", "011", "111"),
}
ADV = 6

def text_width(s, scale):
    return len(s) * ADV * scale

def draw_text(s, x, y, c, scale=2):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[' '])
        for gy, row in enumerate(glyph):
            for gx, v in enumerate(row):
                if v == '1':
                    rect(cx + gx * scale, y + gy * scale,
                         cx + gx * scale + scale, y + gy * scale + scale, c)
        cx += ADV * scale

def fit_scale(s, max_w, preferred):
    sc = preferred
    while sc > 1 and text_width(s, sc) > max_w:
        sc -= 1
    return sc

def wrap(s, max_w, scale):
    words, lines, cur = s.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ================================================================ content
STORIES = [
    dict(kicker='MIDDLE EAST',
         head="GULF WAR WIDENS AGAIN",
         body=["HOUTHIS HIT SAUDI RABIGH REFINERY;",
               "IRGC FIRES ON US RADARS IN BAHRAIN,",
               "SHOOTS DOWN PREDATOR OVER HORMUZ;",
               "TRUMP: STRIKES IF NO DEAL BY NEW YEAR"],
         color=RED, art='gulf'),
    dict(kicker='UKRAINE',
         head="DYMER TOLL RISES TO NINE",
         body=["RUSSIAN DRONE LEVELS FLATS BLOCK",
               "NEAR KYIV; 12 DEAD IN REGION OVERNIGHT,",
               "RESCUERS DIG THROUGH RUBBLE, A CHILD",
               "PULLED OUT ALIVE; SLOVIANSK SHELLED"],
         color=ORANGE, art='kyiv'),
    dict(kicker='MARKETS',
         head="AI SELLOFF SHAKES ASIA",
         body=["KOSPI DOWN 5 PCT, SEOUL STARTS",
               "STABILISATION FUND; TOKYO CLOSED",
               "FOR LABOR THANKSGIVING; NIKKEI FELL",
               "5 PCT LAST WEEK; NASDAQ -10 PCT"],
         color=BLUE, art='chart'),
    dict(kicker='CLIMATE',
         head="COP31 ENDS WITH NO PACT",
         body=["ANTALYA TALKS COLLAPSE OVER FOSSIL",
               "FUEL PHASE-OUT WORDING; LONGEST COP",
               "ON RECORD CLOSES EMPTY-HANDED;",
               "GUTERRES: NO AMBIGUITY IN SCIENCE"],
         color=GREEN, art='cop'),
]

# ---------------------------------------------------------------- header
rect(0, 0, W, 128, (9, 13, 22))
rect(0, 126, W, 130, RED)
draw_text('WORLD NEWS', 48, 26, INK, 7)
draw_text('MONDAY 23 NOVEMBER 2026', 50, 82, (150, 185, 232), 4)

PX0, PY0, PW, PH = 40, 142, 460, 300
GAPX, GAPY = 24, 14
arts = []

def panel_box(x, y, w, h):
    rect(x, y, x + w, y + h, PANEL)
    rect(x, y, x + w, y + 3, PANEL_EDGE)
    rect(x, y + h - 1, x + w, y + h, (32, 42, 60))
    rect(x, y, x + 3, y + h, PANEL_EDGE)

for idx, st in enumerate(STORIES):
    col, row = idx % 2, idx // 2
    x = PX0 + col * (PW + GAPX)
    y = PY0 + row * (PH + GAPY)
    panel_box(x, y, PW, PH)
    ks = 2
    kw = text_width(st['kicker'], ks) + 20
    rect(x + 18, y + 14, x + 18 + kw, y + 14 + 7 * ks + 12, st['color'])
    draw_text(st['kicker'], x + 28, y + 20, (14, 18, 28), ks)
    hw = PW - 42
    hs = fit_scale(st['head'], hw, 3)
    hlines = wrap(st['head'], hw, hs)
    hy = y + 48
    for ln in hlines[:2]:
        draw_text(ln, x + 20, hy, INK, hs)
        hy += 7 * hs + 8
    rect(x + 20, hy + 2, x + PW - 24, hy + 3, (48, 62, 88))
    hy += 12
    bs = 2
    for ln in st['body'][:4]:
        draw_text(ln, x + 20, hy, INK_DIM, bs)
        hy += 7 * bs + 5
    arts.append((st['art'], x, y, PW, PH))

# ---------------------------------------------------------------- artwork per panel
ART_Z0 = 172

# --- Panel 1 (MIDDLE EAST): Persian Gulf map, refinery + radar strikes
ax, ay = arts[0][1], arts[0][2]
CLIP = (ax + 4, ay + ART_Z0, ax + PW - 4, ay + PH - 4)
gx0, gy0 = ax + 240, ay + ART_Z0
rect(gx0, gy0, gx0 + 196, gy0 + 124, (28, 38, 56))
rect(gx0, gy0, gx0 + 196, gy0 + 2, (40, 52, 74))
for i in range(48):
    rect(gx0 + 18 + i, gy0 + 24 + i, gx0 + 26 + i, gy0 + 104 - i, WATER)
draw_text('GULF', gx0 + 28, gy0 + 56, (150, 190, 240), 2)
rect(gx0 + 128, gy0 + 12, gx0 + 192, gy0 + 116, (44, 52, 44))
draw_text('IRAN', gx0 + 136, gy0 + 52, (168, 180, 150), 2)
circle(gx0 + 136, gy0 + 26, 5, RED, True)
draw_text('QESHM', gx0 + 144, gy0 + 20, RED, 1)
circle(gx0 + 42, gy0 + 34, 5, RED, True)
draw_text('BAHRAIN', gx0 - 2, gy0 + 44, RED, 1)
circle(gx0 + 34, gy0 + 84, 6, ORANGE, True)
draw_text('RABIGH', gx0 - 4, gy0 + 94, ORANGE, 1)
arrow(gx0 + 126, gy0 + 32, gx0 + 52, gy0 + 36, RED, 2)
arrow(gx0 + 120, gy0 + 40, gx0 + 44, gy0 + 86, RED, 2)
for bx, by in ((gx0 + 42, gy0 + 30), (gx0 + 34, gy0 + 80)):
    arc(bx, by, 11, 0, 360, YELLOW, 2)
draw_text('REFINERY HIT + RADARS STRUCK', gx0 + 40, gy0 + 104, YELLOW, 1)

# --- Panel 2 (UKRAINE): collapsed apartment block, rescuers digging
ax, ay = arts[1][1], arts[1][2]
CLIP = (ax + 4, ay + ART_Z0, ax + PW - 4, ay + PH - 4)
bx0, by0 = ax + 24, ay + ART_Z0 + 4
# intact left half, collapsed right
rect(bx0, by0 + 12, bx0 + 180, by0 + 104, (60, 68, 84))
for r in range(4):
    rect(bx0 + 8, by0 + 22 + r * 20, bx0 + 172, by0 + 28 + r * 20, (34, 42, 58))
    for w_ in range(0, 160, 26):
        rect(bx0 + 14 + w_, by0 + 22 + r * 20, bx0 + 32 + w_, by0 + 28 + r * 20, YELLOW)
# rubble mound on the right
for i in range(60):
    rect(bx0 + 190 + i, by0 + 104 - int(i * 0.9), bx0 + 420, by0 + 104, mix((96, 84, 72), (40, 36, 32), i / 60))
rect(bx0 + 190, by0 + 58, bx0 + 420, by0 + 104, (52, 46, 42))
# rescuers
for rx, rc in ((bx0 + 220, ORANGE), (bx0 + 260, ORANGE), (bx0 + 310, ORANGE)):
    rect(rx, by0 + 84, rx + 10, by0 + 100, rc)
    circle(rx + 5, by0 + 80, 6, rc, True)
draw_text('DYMER, KYIV REGION', bx0 + 240, by0 + 4, (232, 128, 96), 2)
draw_text('RESCUE ONGOING', bx0 + 250, by0 + 108, INK_DIM, 1)

# --- Panel 3 (MARKETS): falling line chart + stabilization fund note
ax, ay = arts[2][1], arts[2][2]
CLIP = (ax + 4, ay + ART_Z0, ax + PW - 4, ay + PH - 4)
cx0, cy0 = ax + 30, ay + ART_Z0 + 8
rect(cx0, cy0, cx0 + 400, cy0 + 118, (24, 30, 44))
pts = [(0, 20), (60, 34), (120, 30), (180, 52), (240, 58), (300, 88), (360, 104), (398, 100)]
for i in range(len(pts) - 1):
    line(cx0 + pts[i][0], cy0 + pts[i][1], cx0 + pts[i + 1][0], cy0 + pts[i + 1][1], RED, 3)
rect(cx0, cy0 + 116, cx0 + 400, cy0 + 118, STEEL)
draw_text('KOSPI -5 PCT', cx0 + 12, cy0 + 8, INK, 2)
draw_text('SEOUL STABILISATION FUND ON', cx0 + 12, cy0 + 96, BLUE, 2)
draw_text('NASDAQ -10 PCT LAST WEEK', cx0 + 220, cy0 + 72, ORANGE, 1)

# --- Panel 4 (CLIMATE): COP31 broken gavel + deadlocked globe
ax, ay = arts[3][1], arts[3][2]
CLIP = (ax + 4, ay + ART_Z0, ax + PW - 4, ay + PH - 4)
gx_, gy_ = ax + 268, ay + ART_Z0 + 62
circle(gx_, gy_, 62, GREEN, False, 3)
circle(gx_, gy_, 42, (46, 92, 72), False, 2)
rect(gx_ - 30, gy_ - 34, gx_ - 4, gy_ - 18, (52, 110, 84))
rect(gx_ + 2, gy_ - 40, gx_ + 30, gy_ - 26, (52, 110, 84))
rect(gx_ - 18, gy_ + 6, gx_ + 14, gy_ + 26, (52, 110, 84))
rect(gx_ + 18, gy_ + 14, gx_ + 34, gy_ + 34, (52, 110, 84))
draw_text('COP31', gx_ - text_width('COP31', 2) // 2, gy_ - 8, GREEN, 2)
draw_text('ANTALYA', gx_ - text_width('ANTALYA', 1) // 2, gy_ + 20, INK_DIM, 1)
# broken-gavel: split X over the globe
line(gx_ - 78, gy_ - 44, gx_ - 18, gy_ + 16, RED, 4)
line(gx_ - 12, gy_ + 22, gx_ - 66, gy_ + 56, RED, 4)
draw_text('NO DEAL', ax + 90, gy_ - 30, RED, 3)
draw_text('FOSSIL FUEL WORDING DEADLOCKED', ax + 60, gy_ + 16, INK_DIM, 2)
draw_text('LONGEST COP ON RECORD', ax + 80, gy_ + 40, (110, 126, 152), 1)

# ---------------------------------------------------------------- briefs
BRIEFS = [
    ('ME', 'IRGC DOWNS US PREDATOR OVER HORMUZ', RED),
    ('ME', 'BRAHIM GHALLOUGHI - see ME, oil at $92.29', RED),
    ('ME', 'EGYPT: SUEZ LOST $20BN TO THE WAR', RED),
    ('UA', 'MERKURY CORVETTE SUNK OFF BENGHAZI', ORANGE),
    ('UA', 'ODESA, DNIPRO POWER GRID TARGETED', ORANGE),
    ('AS', 'TAIWAN TIGHTENS SHORT-SELLING RULES', BLUE),
    ('AS', 'US AI-CHIP CURBS HIT CHINA TECH STOCKS', BLUE),
    ('AF', 'THAILAND TO BAN RARE-EARTH CHEMICAL EXPORTS', YELLOW),
    ('EU', 'FLASH PMIS DUE ACROSS EUROPE TODAY', GREEN),
    ('EU', 'DOLLAR NEAR 19-MONTH HIGH', GREEN),
    ('AM', 'US LOSES MEASLES ELIMINATION STATUS', BLUE),
    ('AM', 'PELTOLA FLIPS ALASKA SENATE SEAT', BLUE),
]
BX0, BY0 = 40, PY0 + 2 * PH + GAPY + 14
BCOLW = 448
BROWH = 22
for i, (tag, txt, col) in enumerate(BRIEFS):
    bx = BX0 + (i % 2) * (BCOLW + 24)
    by = BY0 + (i // 2) * BROWH
    rect(bx, by, bx + BCOLW, by + 1, (46, 58, 78))
    draw_text(tag, bx + 8, by + 9, col, 2)
    draw_text(txt, bx + 44, by + 9, INK_DIM, 2)

# ---------------------------------------------------------------- footer strip
CLIP = None
FY0 = BY0 + 6 * BROWH + 10
rect(40, FY0, 984, FY0 + 40, PANEL)
rect(40, FY0, 984, FY0 + 3, RED)
draw_text('GULF WAR: TWO MORE SHIPS HIT NEAR HORMUZ, OIL HOLDS AT $92', 56, FY0 + 14, YELLOW, 2)

FY2 = FY0 + 52
rect(40, FY2, 984, FY2 + 40, PANEL)
rect(40, FY2, 984, FY2 + 3, ORANGE)
draw_text('KC CURRENT WIN FIRST NWSL TITLE 2-1 OFF DIBERNADO OLIMPICO', 60, FY2 + 14, ORANGE, 2)

draw_text('SOURCES: REUTERS AP AFP GUARDIAN BBC | AI AGENT FOR MAKE.FUN',
          40, FY2 + 50, (104, 118, 140), 1)

# ---------------------------------------------------------------- PNG encode
def chunk(tag, data):
    body = tag + data
    return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

raw = bytearray()
stride = W * 3
for y in range(H):
    raw.append(0)
    raw += pix[y * stride:(y + 1) * stride]

png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
png += chunk(b'IEND', b'')

out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
if not os.path.isdir(out_dir):
    os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'entry.png'), 'wb') as fh:
    fh.write(png)
