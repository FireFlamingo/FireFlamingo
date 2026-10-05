"""Build self-contained, animated profile SVGs using Python's standard library.

Only public GitHub contribution data is used. No credentials or third-party
stats service required. On upstream/parse failure, existing assets stay intact.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER = "FireFlamingo"
PALETTE = dict(bg="#111214", text="#eeece6", muted="#a6a5a2", line="#393a3d",
               raised="#1b1c1f", raised2="#222326", accent="#d3a087",
               cells=["#222326", "#55463f", "#806453", "#aa826c", "#d3a087"])
# The requested dark artwork is intentionally identical in both GitHub themes.
THEMES = {"dark": PALETTE, "light": PALETTE}


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tooltips = {}
        self.tip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-date") and "data-level" in attrs:
            self.cells[attrs["id"]] = {
                "date": attrs["data-date"], "level": int(attrs["data-level"])
            }
        if tag == "tool-tip":
            self.tip = attrs.get("for")
            if self.tip:
                self.tooltips[self.tip] = ""

    def handle_data(self, data):
        if self.tip:
            self.tooltips[self.tip] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tip = None

    def days(self):
        result = []
        for key, cell in self.cells.items():
            tip = self.tooltips.get(key, "").strip()
            match = re.match(r"(No|[\d,]+) contributions? on\b", tip)
            if not match:
                raise ValueError(f"Missing or unexpected contribution count for {cell['date']}")
            count = 0 if match[1] == "No" else int(match[1].replace(",", ""))
            if cell["level"] not in range(5) or (count == 0) != (cell["level"] == 0):
                raise ValueError("Contribution count/level mismatch")
            date.fromisoformat(cell["date"])
            result.append({**cell, "count": count})
        result.sort(key=lambda day: day["date"])
        if not 350 <= len(result) <= 371:
            raise ValueError(f"Expected a full calendar; got {len(result)} days")
        dates = [date.fromisoformat(day["date"]) for day in result]
        if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
            raise ValueError("Contribution calendar contains gaps or duplicate dates")
        return result


def svg_open(height, theme, title, description):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<style>
text{{font-family:Arial,Helvetica,sans-serif;fill:{theme['text']}}}
.mono{{font-family:'Courier New',monospace;font-size:12px;letter-spacing:1px;fill:{theme['muted']}}}
.muted{{fill:{theme['muted']}}}.accent{{fill:{theme['accent']}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.scan,.packet,.cipher,.cursor{{display:none}}}}
</style>
<rect width="960" height="{height}" fill="{theme['bg']}"/>
'''


def header(t):
    s = svg_open(408, t, "FireFlamingo / ff7", "FireFlamingo resolves from hexadecimal characters. Web application security, digital forensics, CTFs. A copper wireframe flamingo is drawn beside the name.")
    s += f'''<defs>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{t['line']}" stroke-width=".5" opacity=".35"/></pattern>
</defs><style>
@keyframes resolve{{0%{{opacity:0;transform:translateY(6px)}}100%{{opacity:1;transform:translateY(0)}}}}
@keyframes cipher{{0%,65%{{opacity:.8}}100%{{opacity:0}}}}
@keyframes draw{{from{{stroke-dashoffset:900}}to{{stroke-dashoffset:0}}}}
@keyframes cursor{{0%{{transform:translateX(0);opacity:0}}5%,88%{{opacity:1}}100%{{transform:translateX(590px);opacity:0}}}}
@keyframes flow{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-360}}}}
.letter{{animation:resolve .35s ease-out both}}.cipher{{opacity:0;animation:cipher .4s step-end both}}
.wire{{stroke-dasharray:900;animation:draw 2.6s ease-out both}}
.cursor{{opacity:0;animation:cursor 2.5s .2s ease-out both}}
.packet{{stroke-dasharray:12 348;animation:flow 8s linear infinite}}
</style>
<rect x="1" y="1" width="958" height="406" fill="url(#grid)" stroke="{t['line']}"/>
<rect x="1" y="1" width="958" height="45" fill="{t['raised']}"/>
<path d="M1 46H959M32 337H928" stroke="{t['line']}"/>
<rect x="24" y="19" width="8" height="8" fill="{t['accent']}"/>
<text class="mono" x="44" y="27">FF / 0x07</text>
<text class="mono" x="936" y="27" text-anchor="end">SECURITY RESEARCH &amp; ENGINEERING</text>
<text class="mono accent" x="36" y="88">[ IDENTITY ]</text>
<rect x="32" y="104" width="612" height="91" fill="{t['bg']}" opacity=".9"/>
'''
    for i, c in enumerate(USER):
        delay = .2 + i * .14
        x = 34 + i * 46
        s += f'<text class="cipher" x="{x}" y="167" style="font-family:monospace;font-size:65px;fill:{t["accent"]};animation-delay:{delay:.2f}s">{format(ord(c), "x")[-1]}</text>'
        s += f'<text class="letter" x="{x}" y="167" style="font-family:monospace;font-size:76px;font-weight:700;letter-spacing:-4px;animation-delay:{delay+.3:.2f}s">{c}</text>'
    s += f'''<rect class="cursor" x="32" y="107" width="2" height="84" fill="{t['accent']}"/>
<text x="36" y="224" font-size="22" font-weight="600">Web application security &amp; digital forensics.</text>
<text x="36" y="256" font-size="16" class="muted">I build tools to inspect traffic, understand systems,</text>
<text x="36" y="280" font-size="16" class="muted">and work through security problems.</text>
<path d="M665 73V310" stroke="{t['line']}" stroke-dasharray="3 6"/>
<g fill="none" stroke="{t['line']}">
<circle cx="800" cy="189" r="100"/><circle cx="800" cy="189" r="77"/>
<path d="M686 189H914M800 75V303M726 115L874 263M726 263L874 115"/>
</g>
<g class="wire" fill="none" stroke="{t['accent']}" stroke-width="2" stroke-linejoin="bevel">
<path d="M728 197L759 171L801 177L815 158L808 124L828 103L854 107L866 127L842 137L827 127L833 118L848 119M842 137L839 159L856 183L829 213L778 224L728 197L785 194L801 177M759 171L778 224L815 205L856 183M785 194L815 205L829 213M795 221L787 263L814 263M818 217L840 242L816 270"/>
</g>
<circle cx="846" cy="117" r="2.5" fill="{t['text']}"/>
<g fill="{t['bg']}" stroke="{t['accent']}"><rect x="725" y="194" width="6" height="6"/><rect x="775" y="221" width="6" height="6"/><rect x="853" y="180" width="6" height="6"/></g>
<text class="mono" x="800" y="317" text-anchor="middle">FIG. 01 / FLAMINGO</text>
<path class="packet" d="M36 302H330L348 320H620" stroke="{t['accent']}" fill="none"/>
<text class="mono" x="36" y="364">46 69 72 65 46 6c 61 6d 69 6e 67 6f</text>
<text class="mono accent" x="924" y="364" text-anchor="end">WEB / DFIR / CTF</text>
<text class="mono" x="36" y="387" style="font-size:10px">ASCII / FireFlamingo</text>
<path d="M1 14V1H14M946 1H959V14M1 394V407H14M946 407H959V394" fill="none" stroke="{t['accent']}" stroke-width="2"/>
</svg>'''
    return s


def project_card(t, number, name, category, lines, glyph):
    s = svg_open(164, t, name, " ".join(lines))
    s += f'''<rect x="1" y="1" width="958" height="162" fill="{t['raised']}" stroke="{t['line']}"/>
<path d="M1 1H5V163H1" fill="{t['accent']}"/>
<text class="mono accent" x="28" y="36">{number}</text>
<text class="mono" x="76" y="33">{escape(category)}</text>
<text x="76" y="73" font-size="30" font-weight="600" letter-spacing="-.5">{escape(name)}</text>
<text x="76" y="109" font-size="16" class="muted">{escape(lines[0])}</text>
<text x="76" y="134" font-size="16" class="muted">{escape(lines[1])}</text>
<path d="M732 20V144" stroke="{t['line']}"/>
<text class="mono accent" x="925" y="35" text-anchor="end">↗</text>
<g transform="translate(776 52)" fill="none" stroke="{t['accent']}" stroke-width="1.5">{glyph}</g>
</svg>'''
    return s


def project_label(t):
    return svg_open(68, t, "Selected projects", "01 / Selected projects. Open any project to view its repository.") + f'''<text class="mono accent" x="8" y="42">01 /</text><text x="76" y="43" font-size="24" font-weight="600">Selected projects</text><path d="M306 36H755" stroke="{t['line']}"/><text class="mono" x="952" y="41" text-anchor="end">SOURCE AVAILABLE ↗</text></svg>'''


def toolkit(t):
    s = svg_open(188, t, "Toolkit", "Web: Burp Suite, HTTP, authentication. Forensics: Wireshark, Volatility, Ghidra. Code: Python, Bash, JavaScript, C and C++.")
    s += f'''<text class="mono accent" x="8" y="39">02 /</text><text x="76" y="40" font-size="24" font-weight="600">Working stack</text><path d="M281 33H952" stroke="{t['line']}"/>
<rect x="1" y="65" width="958" height="122" fill="{t['raised']}" stroke="{t['line']}"/>
<path d="M321 65V187M641 65V187" stroke="{t['line']}"/>
'''
    for x, title, l1, l2 in [(25,"HTTP / APPLICATION","Burp Suite · HTTP","Authentication"),(345,"BYTES / ARTIFACTS","Wireshark · Volatility","Ghidra"),(665,"CODE / AUTOMATION","Python · Bash","JavaScript · C / C++")]:
        s += f'<text class="mono accent" x="{x}" y="96">{title}</text><text x="{x}" y="130" font-size="17">{l1}</text><text x="{x}" y="156" font-size="17" class="muted">{l2}</text>'
    return s + '</svg>'


def footer(t):
    return svg_open(62, t, "All public repositories", "Browse all public FireFlamingo repositories on GitHub.") + f'''<path d="M1 1H959" stroke="{t['line']}"/><text class="mono" x="8" y="37">FireFlamingo / ff7</text><text class="mono accent" x="952" y="37" text-anchor="end">EXPLORE ALL REPOSITORIES ↗</text></svg>'''


def calendar(t, days, refreshed):
    last = date.fromisoformat(days[-1]["date"])
    first = date.fromisoformat(days[0]["date"])
    sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    total = sum(d["count"] for d in days)
    active = sum(d["count"] > 0 for d in days)
    peak = max(d["count"] for d in days)
    title = f"{USER}: {total:,} GitHub contributions over the last year"
    s = svg_open(322, t, title, f"{first} through {last}. {active} active days. Peak {peak} contributions in one day. Refreshed {refreshed}. Left-to-right reveal plays once.")
    s += f'''<style>
@keyframes reveal{{0%{{opacity:.12}}65%{{opacity:1;fill:{t['accent']}}}100%{{opacity:1}}}}
@keyframes sweep{{0%{{transform:translateX(0);opacity:0}}5%{{opacity:.6}}95%{{opacity:.6}}100%{{transform:translateX(848px);opacity:0}}}}
.reveal{{animation:reveal .55s ease-out both}}.scan{{opacity:0;animation:sweep 2.6s .18s linear both}}
</style>
<text class="mono" x="32" y="36">01 / CONTRIBUTION TRACE</text>
<text class="mono" x="928" y="36" text-anchor="end">{first:%d %b %Y} — {last:%d %b %Y}</text>
<text x="32" y="82" font-size="32" font-weight="700" letter-spacing="-1">{total:,}<tspan dx="9" font-size="14" font-weight="400" letter-spacing="0" class="muted">contributions</tspan></text>
<text x="928" y="79" font-size="13" class="muted" text-anchor="end">{active} active days / {peak} most in a day</text>
'''
    x0, y0, pitch = 80, 128, 16
    seen_months = set()
    for day in days:
        d = date.fromisoformat(day["date"])
        offset = (d - sunday).days
        col, row = divmod(offset, 7)
        x, y = x0 + col * pitch, y0 + row * pitch
        month_key = (d.year, d.month)
        # Label complete month starts; skip a cramped trailing label.
        if month_key not in seen_months and d.day <= 7 and row == 0 and col < 51:
            s += f'<text class="mono" x="{x}" y="116">{d:%b}</text>\n'
            seen_months.add(month_key)
        delay = .18 + col * .044 + row * .009
        s += f'<rect class="reveal" x="{x}" y="{y}" width="12" height="12" rx="2" fill="{t["cells"][day["level"]]}" style="animation-delay:{delay:.3f}s"><title>{d}: {day["count"]} contributions</title></rect>\n'
    for row, label in [(1, "MON"), (3, "WED"), (5, "FRI")]:
        s += f'<text class="mono" x="32" y="{y0+row*pitch+10}">{label}</text>\n'
    s += f'<rect class="scan" x="78" y="125" width="2" height="113" fill="{t["accent"]}"/>\n'
    updated = datetime.fromisoformat(refreshed.replace("Z", "+00:00")).strftime("%d %b %Y %H:%M").upper()
    s += f'<text class="mono" x="32" y="267">UPDATED {updated} UTC</text><text class="mono" x="760" y="267">LESS</text>'
    for i, color in enumerate(t["cells"]):
        s += f'<rect x="{804+i*16}" y="257" width="12" height="12" rx="2" fill="{color}"/>'
    s += '<text class="mono" x="890" y="267">MORE</text><text class="mono" x="32" y="307" style="font-size:11px">GITHUB CONTRIBUTIONS / COMMITS, PULL REQUESTS, ISSUES &amp; REVIEWS / REFRESH EVERY 30 MIN</text></svg>'
    return s


def seamless_panel(svg, top=0, bottom=0):
    """Bake spacing into images so adjacent README images share one canvas."""
    height = int(re.search(r'height="(\d+)"', svg)[1])
    scaled_height = height * .95
    outer_height = top + scaled_height + bottom
    inner = svg.replace('width="960"', 'x="24" y="' + str(top) + '" width="912"', 1)
    inner = inner.replace(f'height="{height}"', f'height="{scaled_height:g}"', 1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{outer_height:g}" '
            f'viewBox="0 0 960 {outer_height:g}">'
            f'<rect width="960" height="{outer_height:g}" fill="#111214"/>' + inner + '</svg>')


def fetch_calendar():
    """Retry transient upstream errors; never replace a failed fetch with zeros."""
    for attempt in range(3):
        req = Request(f"https://github.com/users/{USER}/contributions?refresh={int(time.time())}",
                      headers={"User-Agent": "FireFlamingo-profile", "Accept-Language": "en-US",
                               "Cache-Control": "no-cache"})
        try:
            with urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8")
        except (URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))


def version_calendar_image(readme, svg):
    """Give GitHub's image proxy a new URL when the graphic changes."""
    version = hashlib.sha256(svg.encode("utf-8")).hexdigest()[:16]
    updated, count = re.subn(r'(src="assets/contributions-dark\.svg)(?:\?[^"\s]*)?(\")',
                             lambda match: f'{match[1]}?v={version}{match[2]}', readme)
    if count != 1:
        raise ValueError("Expected exactly one contribution image in README")
    return updated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-html", type=Path, help="Build from a saved GitHub calendar for offline verification")
    args = parser.parse_args()
    if args.from_html:
        raw = args.from_html.read_text(encoding="utf-8")
    else:
        raw = fetch_calendar()
    parsed = CalendarParser()
    parsed.feed(raw)
    days = parsed.days()
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    today = now.date()
    refreshed = now.isoformat().replace("+00:00", "Z")
    last = date.fromisoformat(days[-1]["date"])
    if not 0 <= (today - last).days <= 2:
        raise ValueError(f"Calendar is stale or future-dated: {last}")
    # Compute everything before touching any published assets.
    output = {}
    for name, theme in THEMES.items():
        output[f"header-{name}.svg"] = header(theme)
        output[f"contributions-{name}.svg"] = calendar(theme, days, refreshed)
    t = PALETTE
    output["projects-label.svg"] = project_label(t)
    output["project-mosaic.svg"] = project_card(t, "01", "MOSAIC", "AI ARTIFACT RISK GATEWAY / TYPESCRIPT",
        ["Explainable risk checks for packages, skills, MCP servers, and URLs.", "A local review queue, policy controls, and audit trail."],
        '<rect x="4" y="0" width="30" height="30"/><rect x="45" y="0" width="30" height="30"/><rect x="86" y="0" width="30" height="30"/><rect x="4" y="41" width="30" height="30"/><rect x="45" y="41" width="30" height="30"/><path d="M88 56l9 9 23-27"/>')
    output["project-hasheger.svg"] = project_card(t, "02", "Hasheger", "PASSWORD MANAGER / TYPESCRIPT",
        ["A web vault, backend, app, and browser extension.", "Source code in the Commit repository."],
        '<rect x="33" y="28" width="62" height="46"/><path d="M46 28V17a18 18 0 0 1 36 0v11"/><circle cx="64" cy="47" r="5"/><path d="M64 52V62M17 38H5M17 58H5M111 38H123M111 58H123"/>')
    output["project-sodyx.svg"] = project_card(t, "03", "Sodyx", "ENCRYPTED ANDROID MESSAGING / KOTLIN",
        ["One-to-one encrypted text through a relay you host.", "Verified contact cards and separate identities for each connection."],
        '<path d="M4 4h80v43H43L24 63V47H4Z"/><path d="M99 22h21v44h-20L82 79V66H56V57"/><circle cx="28" cy="26" r="3"/><circle cx="44" cy="26" r="3"/><circle cx="60" cy="26" r="3"/>')
    output["toolkit.svg"] = toolkit(t)
    output["footer.svg"] = footer(t)
    output["projects-label.svg"] = output["projects-label.svg"].replace('01 /', '02 /')
    output["toolkit.svg"] = output["toolkit.svg"].replace('02 /', '03 /')
    for name in list(output):
        top = 24 if name.startswith("header-") else 0
        bottom = 24 if name == "footer.svg" else 12
        output[name] = seamless_panel(output[name], top=top, bottom=bottom)
    output["contributions.json"] = json.dumps({"user": USER, "refreshed": refreshed,
        "source": f"https://github.com/users/{USER}/contributions",
        "periodStart": days[0]["date"], "periodEnd": days[-1]["date"],
        "totalContributions": sum(day["count"] for day in days), "days": days}, indent=2) + "\n"
    readme_path = ROOT / "README.md"
    readme = version_calendar_image(readme_path.read_text(encoding="utf-8"), output["contributions-dark.svg"])
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for name, value in output.items():
        temp = assets / (name + ".tmp")
        temp.write_text(value, encoding="utf-8")
        temp.replace(assets / name)
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Built {len(output)} assets from {len(days)} real contribution days.")


if __name__ == "__main__":
    main()
