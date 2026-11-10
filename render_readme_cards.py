#!/usr/bin/env python3
"""Renders animated SVG cards for a GitHub profile README.

Usage:
  python scripts/render_readme_cards.py            # live data (needs GH_TOKEN or GITHUB_TOKEN)
  python scripts/render_readme_cards.py --demo     # fake data, no network
  STATIC=1 python scripts/render_readme_cards.py   # no animations (final frame, for screenshots)
"""
import datetime as dt, json, os, random, sys, urllib.request
from html import escape

# ---------------- EDIT THIS ----------------
USERNAME = "Shaurya24k"
FIRST, LAST = "Shaurya", "Sinha"
EYEBROW = "B.TECH CSE · FULL STACK & APPLIED AI"
ABOUT = ["I build India-first products,", "ship fast, and learn in public."]
SITE = "github.com/" + USERNAME
TILES = [  # label, text (2 short lines), colour, text colour, link
    ("BUILD", ["Yatra: India travel discovery", "app, plus utilities in TS."], "#2b4bff", "#ffffff", f"https://github.com/{USERNAME}?tab=repositories"),
    ("LEARN", ["DSA, React, Node, Supabase", "and AI-assisted workflows."], "#f2392b", "#ffffff", f"https://github.com/{USERNAME}"),
    ("CONNECT", ["Open to internships and", "open-source collabs."], "#ffc61a", "#1a1a1a", "https://www.linkedin.com/in/shaurya-sinha-96390b268/"),
]
# -------------------------------------------

INK, PAPER, MUTED, BLUE = "#161616", "#f4f3ee", "#8a8a85", "#2b4bff"
SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
STATIC = os.environ.get("STATIC") == "1"
OUT = os.path.join(os.path.dirname(__file__), "..", "cards")

CSS = f"""
text{{font-family:{MONO}}}
.serif{{font-family:{SERIF}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes pop{{from{{transform:scale(0);opacity:0}}to{{transform:scale(1);opacity:1}}}}
@keyframes swing{{0%{{opacity:0;transform:translateY(40px) rotate(-4deg)}}70%{{transform:translateY(-4px) rotate(1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.fb{{transform-box:fill-box}}
.rise{{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}}
.grow{{transform-origin:bottom;animation:grow .7s cubic-bezier(.2,.7,.2,1) both}}
.pop{{transform-origin:center;animation:pop .35s ease-out both}}
.swing{{transform-origin:center bottom;animation:swing .9s cubic-bezier(.2,.7,.2,1) both}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
""" + ("*{animation:none!important}" if STATIC else "")

def svg(w, h, body, extra_css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<style>{CSS}{extra_css}</style>{body}</svg>')

def d(sec):  # animation delay
    return f'style="animation-delay:{sec:.2f}s"'

# ---------------- data ----------------
def fetch_days():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if "--demo" in sys.argv or not token:
        if "--demo" not in sys.argv:
            print("No token found, using demo data.", file=sys.stderr)
        random.seed(7)
        today = dt.date.today()
        return [(today - dt.timedelta(days=364 - i), 0 if random.random() < .25 else int(random.random() ** 2 * 14))
                for i in range(365)]
    q = ("query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{"
         "weeks{contributionDays{date contributionCount}}}}}}")
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"l": USERNAME}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(dt.date.fromisoformat(x["date"]), x["contributionCount"]) for w in weeks for x in w["contributionDays"]]

def stats(days):
    total = sum(c for _, c in days)
    best_day = max(c for _, c in days)
    active = sum(1 for _, c in days if c)
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, seq = 0, list(days)
    if seq and seq[-1][1] == 0: seq.pop()  # today may not have commits yet
    for _, c in reversed(seq):
        if not c: break
        cur += 1
    months = {}
    for day, c in days:
        months[(day.year, day.month)] = months.get((day.year, day.month), 0) + c
    return dict(total=total, best_day=best_day, active=active, longest=longest, cur=cur,
                months=sorted(months.items())[-12:], span=len(days))

# ---------------- cards ----------------
def hero():
    w, h = 840, 250
    body = f'''<rect width="{w}" height="{h}" rx="14" fill="{PAPER}" stroke="#e2e0d8"/>
<circle cx="36" cy="38" r="4" fill="{BLUE}" class="pulse"/>
<text x="48" y="42" font-size="11" letter-spacing="1.5" fill="{MUTED}" class="rise" {d(0)}>{escape(EYEBROW)}</text>
<defs><linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".45" stop-color="{INK}"/>
<stop offset=".5" stop-color="{BLUE}"/><stop offset=".55" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>
{"" if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="3s" begin="1.4s;sw.end+4s" id="sw" fill="freeze"/>'}
</linearGradient></defs>
<text x="36" y="132" font-size="78" class="serif rise" fill="{INK}" {d(.15)}>{escape(FIRST)}</text>
<text x="36" y="206" font-size="78" font-style="italic" class="serif rise" fill="url(#sh)" {d(.35)}>{escape(LAST)}</text>
<g class="rise" {d(.6)}>
<text x="470" y="120" font-size="15" fill="{INK}">{escape(ABOUT[0])}</text>
<text x="470" y="144" font-size="15" fill="{INK}">{escape(ABOUT[1])}</text>
<text x="470" y="190" font-size="12" fill="{BLUE}">{escape(SITE)} ↗</text></g>'''
    return svg(w, h, body)

def tile(i, label, lines, bg, fg, delay):
    w, h = 270, 150
    t = "".join(f'<text x="18" y="{100 + 20 * k}" font-size="12" fill="{fg}" opacity=".92">{escape(l)}</text>' for k, l in enumerate(lines))
    body = f'''<g class="swing" {d(delay)}><rect width="{w}" height="{h}" rx="12" fill="{bg}"/>
<text x="18" y="30" font-size="11" letter-spacing="1.5" fill="{fg}">{label}</text>
<text x="{w-28}" y="30" font-size="14" fill="{fg}">→</text>{t}</g>'''
    return svg(w, h, body)

def activity(s):
    w, h = 840, 250
    months = s["months"]; mx = max(c for _, c in months) or 1
    bx0, base, bh, bw, gap = 36, 196, 110, 36, 12
    best = max(range(len(months)), key=lambda i: months[i][1])
    bars = ""
    for i, ((y, m), c) in enumerate(months):
        x = bx0 + i * (bw + gap); bhh = max(4, c / mx * bh)
        col = BLUE if i == best else INK
        bars += f'<rect class="grow fb" {d(.3 + i * .05)} x="{x}" y="{base - bhh:.1f}" width="{bw}" height="{bhh:.1f}" rx="3" fill="{col}"/>'
        bars += f'<text x="{x + bw / 2}" y="{base + 18}" font-size="10" fill="{MUTED}" text-anchor="middle">{dt.date(y, m, 1):%b}</text>'
        if i == best:
            bars += f'<text class="rise" {d(1)} x="{x + bw / 2}" y="{base - bhh - 8:.1f}" font-size="11" fill="{BLUE}" text-anchor="middle">{c:,}</text>'
    rx = 650
    def stat(y, big, small, delay):
        return (f'<g class="rise" {d(delay)}><text x="{rx}" y="{y}" font-size="34" class="serif" fill="{INK}">{big}</text>'
                f'<text x="{rx}" y="{y + 18}" font-size="10" fill="{MUTED}">{small}</text></g>')
    body = f'''<rect width="{w}" height="{h}" rx="14" fill="{PAPER}" stroke="#e2e0d8"/>
<text x="36" y="38" font-size="10" letter-spacing="1.5" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text x="36" y="84" font-size="44" class="serif rise" fill="{INK}">{s["total"]:,} <tspan font-style="italic">contributions</tspan></text>
{bars}
{stat(88, f'{s["cur"]} <tspan font-style="italic">days</tspan>', f'current streak · longest {s["longest"]}', .4)}
{stat(146, f'{s["active"]} <tspan fill="{MUTED}">/ {s["span"]}</tspan>', 'days with a commit', .55)}
{stat(204, f'{s["best_day"]}', 'on the busiest day', .7)}'''
    return svg(w, h, body)

def graph(days):
    w, h = 840, 200
    start = days[0][0]
    offset = (start.weekday() + 1) % 7          # GitHub weeks start on Sunday
    mx = max(c for _, c in days) or 1
    shades = ["#e4e7f7", "#b9c3fb", "#8497fa", "#5470ff", "#2b4bff"]
    cells = ""
    for i, (day, c) in enumerate(days):
        col, row = (i + offset) // 7, (i + offset) % 7
        lvl = 0 if c == 0 else min(4, 1 + int(c / mx * 3.999))
        cells += (f'<rect class="pop fb" {d(.3 + col * .025)} x="{36 + col * 14}" y="{56 + row * 14}" '
                  f'width="11" height="11" rx="2" fill="{shades[lvl]}"/>')
    labels, last = "", None
    for i, (day, _) in enumerate(days):
        if day.month != last and (i + offset) // 7 < 51:
            labels += f'<text x="{36 + ((i + offset) // 7) * 14}" y="176" font-size="10" fill="{MUTED}">{day:%b}</text>'
        last = day.month
    body = f'''<rect width="{w}" height="{h}" rx="14" fill="{PAPER}" stroke="#e2e0d8"/>
<text x="36" y="36" font-size="22" class="serif rise" fill="{INK}">Every day, <tspan font-style="italic" fill="{BLUE}">in blue</tspan></text>
<text x="{w-36}" y="34" font-size="10" letter-spacing="1.5" fill="{MUTED}" text-anchor="end">REFRESHED DAILY</text>
{cells}{labels}'''
    return svg(w, h, body)

def main():
    os.makedirs(OUT, exist_ok=True)
    days = fetch_days(); s = stats(days)
    files = {"hero.svg": hero(), "activity.svg": activity(s), "graph.svg": graph(days)}
    for i, (label, lines, bg, fg, _) in enumerate(TILES):
        files[f"tile-{i + 1}.svg"] = tile(i, label, lines, bg, fg, .9 + i * .15)
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"Wrote {len(files)} cards. {s['total']} contributions, streak {s['cur']}.")

if __name__ == "__main__":
    main()
