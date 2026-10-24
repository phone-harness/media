# media

Images for Phone Harness READMEs and docs, linked by raw URL so they render on GitHub and PyPI alike.

- `phone-harness/logo-animated.svg`, `logo-animated-dark.svg`: the animated logo (vector, plays once).
- `phone-harness/banner-light.png`, `banner-dark.png`: the 1600x500 README banner.
- `phone-harness/tagline*.svg`: "Let your agent use your phone." cycling with live GitHub stars and PyPI downloads. Rebuilt every 6 hours by `.github/workflows/refresh.yml` running `scripts/build.py`.
- `phone-harness/button-*.svg`, `icon-*.svg`: the Cloud and Docs buttons and the social icons from phone-harness.com.

## Rerender

`scripts/render.sh` rebuilds every image (logo, tagline, buttons, icons), commits and pushes them, then bumps the `?v=` on the image URLs in the phone-harness README so GitHub's image proxy fetches the new files. Set `PHONE_HARNESS_REPO` to the checkout whose README to bump (default `~/Projects/phone-harness`). The 6-hourly workflow only refreshes the stats, which GitHub re-fetches on its own within five minutes.
- `phone-harness/demo-waymo.gif`: the README demo ("Buy me a Waymo to Delah Coffee"), 800 px, 12 fps, from phone-harness-demo.mp4.
