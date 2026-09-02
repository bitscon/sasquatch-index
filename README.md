# Sasquatch Index

A free, public, static website that lets people browse shoe styles filtered by
size, focused on the sizes most retailers stop short of — size 13 and up. It
links out to whoever actually stocks each style. It is not a store.

- **Live site:** https://bitscon.github.io/sasquatch-index/
- **How it works:** Hugo (pinned version) builds the site from `data/products.yaml`;
  a GitHub Actions job publishes to GitHub Pages on every push to `main`.
- **Operating contract:** [`SASQUATCH_OS.md`](SASQUATCH_OS.md) — read it before
  changing anything.
- **Session state:** [`HANDOFF.md`](HANDOFF.md) — overwritten at the end of every
  working session.

Product data will come from affiliate product feeds only. No retailer sites are
scraped, and nothing on the site claims first-hand product experience.
