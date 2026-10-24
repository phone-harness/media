#!/bin/sh
# Rerender every README header image and make GitHub show it.
#
#   scripts/render.sh            rebuild, commit, push, bump the README's ?v=
#   scripts/render.sh --no-logo  skip the logo (needs fonttools + Arial Bold)
#
# The README links images as .../phone-harness/<file>.svg?v=<commit>. GitHub's
# image proxy caches by URL, so the last step rewrites ?v= to this commit in
# the phone-harness checkout and pushes that branch; without it GitHub can keep
# showing the old image.
set -eu
cd "$(dirname "$0")/.."
README_REPO="${PHONE_HARNESS_REPO:-$HOME/Projects/phone-harness}"
[ -n "${GITHUB_TOKEN:-}" ] || GITHUB_TOKEN=$(gh auth token 2>/dev/null || true); export GITHUB_TOKEN

[ "${1:-}" = "--no-logo" ] || uv run --quiet --with fonttools python scripts/logo.py
python3 scripts/build.py

git add -A
if git diff --cached --quiet; then echo "images unchanged"; else
  git commit -q -m "Rerender header images"
  git pull -q --rebase
  git push -q
fi
V=$(git rev-parse --short HEAD)

cd "$README_REPO"
python3 - "$V" <<'PY'
import pathlib, re, sys
p = pathlib.Path("README.md"); s = p.read_text()
s2, n = re.subn(r'(raw\.githubusercontent\.com/phone-harness/media/main/phone-harness/[\w.-]+\.svg)(\?v=\w+)?', rf'\1?v={sys.argv[1]}', s)
p.write_text(s2); print(f"README: {n} image URLs now ?v={sys.argv[1]}")
PY
if git diff --quiet README.md; then echo "README already current"; else
  git commit -q -m "README: header images at media@$V" README.md && git push -q
  echo "pushed $(git rev-parse --abbrev-ref HEAD)"
fi
