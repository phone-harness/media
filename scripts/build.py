"""Build the README header images in phone-harness/: the cycling tagline (live
GitHub stars and PyPI downloads), the Cloud and Docs buttons, and the social
icons from phone-harness.com. Light and dark variants of each. Stdlib only;
the scheduled workflow runs it daily and commits what changed."""
import json, os, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "phone-harness"
RED, INK, INK_DARK, MUTED, MUTED_DARK = "#ff4438", "#20231e", "#ecede6", "#64695f", "#a3a69c"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

def get(url):
    headers = {"User-Agent": "phone-harness-media", "Accept": "application/json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"   # unauthenticated calls hit the 60/hour limit
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def stats():
    stars = get("https://api.github.com/repos/ShawnPana/phone-harness")["stargazers_count"]
    downloads = get("https://pepy.tech/api/v2/projects/phone-harness")["total_downloads"]
    return stars, downloads

def tagline(stars, downloads, ink, muted):
    floor = lambda n: f"{n // 100 * 100:,}+" if n >= 100 else f"{n}"   # round down; changes only per hundred
    lines = [("Let your agent ", "use your phone."),
             (floor(stars), " stars on GitHub"),
             (floor(downloads), " downloads on PyPI")]
    n, hold = len(lines), 3.2
    total = n * hold
    css = []
    for i in range(n):
        a, b = i * hold / total * 100, (i + 1) * hold / total * 100
        fade = 0.35 / total * 100
        css.append(f"@keyframes l{i}{{0%,{max(0,a-0.01):.2f}%{{opacity:0;transform:translateY(10px)}}"
                   f"{a+fade:.2f}%,{b-fade:.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{b:.2f}%,100%{{opacity:0;transform:translateY(-10px)}}}}"
                   f".l{i}{{animation:l{i} {total}s infinite;opacity:0}}")
    texts = []
    for i, (lead, rest) in enumerate(lines):
        first, second = (muted, RED) if i == 0 else (RED, muted)
        texts.append(f'<text class="l{i}" x="300" y="32" text-anchor="middle">'
                     f'<tspan fill="{first}">{lead}</tspan><tspan fill="{second}">{rest}</tspan></text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="48" viewBox="0 0 600 48" role="img" '
            f'aria-label="Let your agent use your phone. {stars // 100 * 100:,}+ stars on GitHub, {downloads // 100 * 100:,}+ downloads on PyPI.">'
            f'<style>text{{font:300 24px {FONT};letter-spacing:0px}}{"".join(css)}</style>{"".join(texts)}</svg>\n')

SITE_FONT = "Arial, Helvetica, sans-serif"   # phone-harness.com's --sans

def button(label, icon_path, fill, text, stroke, width):
    """phone-harness.com's .btn: 3 px corners, Arial 14 px regular, a 16 px outline icon, 10 px gap."""
    icon = (f'<g transform="translate(18 12)" fill="none" stroke="{text}" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round"><g transform="scale(0.6667)"><path d="{icon_path}"/></g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="40" viewBox="0 0 {width} 40" role="img" aria-label="{label}">'
            f'<rect x="0.5" y="0.5" width="{width-1}" height="39" rx="3" fill="{fill}" stroke="{stroke}"/>{icon}'
            f'<text x="44" y="24.8" fill="{text}" style="font:400 14px {SITE_FONT}">{label}</text></svg>\n')

ICONS = {  # exactly the paths on phone-harness.com (frontend BrandChrome.tsx), 24-unit boxes
    "x": ("0 0 24 24", "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.64 7.584H.47l8.6-9.835L0 1.154h7.594l5.243 6.932 6.064-6.933Zm-1.29 19.49h2.039L6.487 3.24H4.3l13.31 17.403Z"),
    "github": ("0 0 24 24", "M12 1C5.923 1 1 5.923 1 12c0 4.867 3.149 8.979 7.521 10.436.55.096.756-.233.756-.522 0-.262-.013-1.128-.013-2.049-2.764.509-3.479-.674-3.699-1.292-.124-.317-.66-1.293-1.128-1.554-.385-.207-.935-.715-.014-.729.866-.014 1.485.797 1.691 1.128.99 1.663 2.571 1.196 3.204.907.096-.715.385-1.196.701-1.471-2.448-.275-5.005-1.224-5.005-5.431 0-1.196.426-2.186 1.128-2.956-.11-.275-.495-1.402.11-2.915 0 0 .921-.289 3.025 1.128.88-.247 1.815-.371 2.75-.371.935 0 1.87.124 2.75.371 2.104-1.43 3.025-1.128 3.025-1.128.605 1.513.22 2.64.11 2.915.701.77 1.128 1.746 1.128 2.956 0 4.221-2.571 5.156-5.019 5.431.399.344.743 1.004.743 2.035 0 1.471-.014 2.654-.014 3.025 0 .289.206.632.756.522C19.851 20.979 23 16.854 23 12c0-6.077-4.922-11-11-11Z"),
    "linkedin": ("2.8 3.8 18.2 18.2", "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452z"),
    "discord": ("0 0 24 24", "M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"),
}

def social(name, color):
    """A small plain icon in a 32x40 frame, so it centers on the 40 px buttons' line."""
    box, d = ICONS[name]
    bx, by, bw, bh = (float(v) for v in box.split())
    k = 18 / max(bw, bh)
    tx, ty = 16 - (bx + bw / 2) * k, 20 - (by + bh / 2) * k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40" role="img" aria-label="{name}">'
            f'<path fill="{color}" transform="translate({tx:.3f} {ty:.3f}) scale({k:.4f})" d="{d}"/></svg>\n')

# Lucide-style 24-unit outline icons, like the ones on the site's buttons.
CLOUD = "M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"
BOOK = "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
PAPER, PAPER_DARK, LINE, LINE_DARK, INK_SITE_DARK = "#f6f7f1", "#191c19", "#c7cbc0", "#42483e", "#e5e9df"

def callout(text_color):
    """'Try your own cloud Android phone for free!' with a hand-drawn arrow curving back to the Cloud button."""
    arrow = (f'<g fill="none" stroke="{RED}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M44 26 C34 30 22 28 13 20"/><path d="M12 27 L12.5 19.5 L20 19"/></g>')
    style = f"font:400 13px {SITE_FONT}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="230" height="40" viewBox="0 0 230 40" role="img" '
            f'aria-label="Try your own cloud Android phone for free!">{arrow}'
            f'<text x="50" y="17" fill="{text_color}" style="{style}">Try your own cloud</text>'
            f'<text x="50" y="33" fill="{text_color}" style="{style}">Android phone <tspan fill="{RED}">for free!</tspan></text></svg>\n')

def main():
    stars, downloads = stats()
    files = {
        "tagline.svg": tagline(stars, downloads, INK, MUTED),
        "tagline-dark.svg": tagline(stars, downloads, INK_DARK, MUTED_DARK),
        "button-cloud.svg": button("Cloud", CLOUD, INK, PAPER, INK, 104),
        "button-cloud-dark.svg": button("Cloud", CLOUD, RED, PAPER_DARK, RED, 104),
        "button-docs.svg": button("Docs", BOOK, "none", INK, LINE, 98),
        "button-docs-dark.svg": button("Docs", BOOK, "none", INK_SITE_DARK, LINE_DARK, 98),
    }
    files["callout.svg"] = callout(MUTED)
    files["callout-dark.svg"] = callout(MUTED_DARK)
    for name in ICONS:
        files[f"icon-{name}.svg"] = social(name, MUTED)
        files[f"icon-{name}-dark.svg"] = social(name, MUTED_DARK)
    for name, body in files.items():
        (OUT / name).write_text(body)
    print(f"stars {stars:,}, downloads {downloads:,}; wrote {len(files)} files")

if __name__ == "__main__":
    main()
