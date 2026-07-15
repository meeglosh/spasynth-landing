# SPASynth Landing Page — Project Progress

Last updated: 2026-07-06 (HTTPS confirmed live)

## What this is

Static one-page marketing site for **SPASynth** (Silverplatter Audio's hybrid
SFX synthesizer). Plain HTML/CSS/JS, no build step, deployed via GitHub Pages
at the custom domain **spasynth.com**.

- Repo: `github.com/meeglosh/spasynth-landing` (branch `main`)
- Local path: `~/spasynth-landing`
- Content source of truth: `~/arsenal/docs/marketing-brief.md` — the full
  feature list, positioning, brand voice, and palette all come from there.
  **Do not add features, numbers, pricing, or claims that aren't in that
  brief.**

## Current live status

- `https://spasynth.com` — **fully live**. TLS cert approved (expires
  2026-10-04, covers `spasynth.com` + `www.spasynth.com`), Enforce HTTPS is
  on, and `http://spasynth.com` now 301-redirects to HTTPS. Nothing left to
  do on the deployment/infra side.
- GitHub Pages: enabled, source = `main` branch, `/` root. (Had to be turned
  on manually in the GitHub web UI — the `gh` CLI token in this environment
  doesn't have Pages admin scope, `gh api repos/.../pages` POST returns 403.)
- Getting HTTPS to issue required clearing and re-saving the custom domain
  field in Settings → Pages once DNS was corrected (shows up in history as
  the `Delete CNAME` / `Create CNAME` commits) — that forced GitHub to
  re-check DNS and kick off cert provisioning immediately instead of waiting
  on its own schedule.

### DNS (GoDaddy)

- `www.spasynth.com` → CNAME → `meeglosh.github.io` — confirmed working.
- `spasynth.com` (apex) → 4 A records, confirmed clean as of this session:
  `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
  GoDaddy originally auto-added two extra parking-forwarding A records
  (`76.223.105.230`, `13.248.243.5`) that broke cert issuance — those were
  removed. If HTTPS ever breaks again, check for stray A records first.

## Design decisions (so a future session doesn't relitigate these)

- Palette pulled directly from the shipping plugin UI, not invented:
  bg `#0c1114`, panels `#151c21`, text `#e7ecef` / `#7f8d97`, orange accent
  `#f08b3a` (audio), cyan accent `#4fc4d6` (modulation).
- Fonts: **Bricolage Grotesque** (display/headings), **IBM Plex Sans**
  (body), **IBM Plex Mono** (labels, specs, eyebrows) — chosen deliberately
  to avoid generic AI-slop fonts (Inter/Arial/Space Grotesk).
- The hero and Organic Chaos section have a canvas-based animated
  oscilloscope line (random-walk), deliberately echoing the plugin's own
  live telemetry scopes shown in the product screenshots.
- Assets copied in from `~/arsenal`: `docs/spasynth-dark.png`,
  `docs/spasynth-accent.png` (real UI screenshots), and three SVGs from
  `assets/branding/` (Silverplatter Audio logo, banner + square variants).
- No fabricated pricing, testimonials, user counts, or demo videos — the
  brief explicitly forbids this. Editions section shows "Pricing coming
  soon" instead of numbers.
- All em dashes were deliberately removed repo-wide per user preference —
  replaced with contextually correct punctuation (colons, parentheses,
  commas, or split sentences), not a blind character swap. Keep new copy
  dash-free too.

## Section order (index.html)

Hero → Library-is-the-synth (signal diagram) → Randomize/Chaos (WILD knob +
lock chips + Organic Chaos scope) → Feature grid (8 cards) → Accent re-tint
showcase → Editions (Standard/Pro) → No-DRM statement (verbatim blockquote
from the brief) → Specs table → FAQ accordion → Footer.

## Known placeholder / intentionally incomplete

- **Nav CTA button** currently reads "Coming soon" and links to `#editions`.
  This was "Get SPASynth" originally; changed because the Shopify store
  isn't live yet. **Swap the text and href to the real store URL once the
  Shopify listing goes live** — built installer packages already exist
  locally at `~/arsenal/dist/shopify/` (Standard + Pro), so the store side
  may already be in progress separately from this repo.
- Pricing is live: Standard is $149 (intro price $99), Pro is $702.
  $1,264 is the Everything Bundle's list price on Shopify; $702 is what
  the bundle actually sells for after its own discount. Pro is priced
  to exactly match that $702 bundle price, not below it — the pitch is
  "SPASynth comes included at no extra cost," not "cheaper than the
  bundle." Update these numbers here and in the Editions section
  together if they ever change.

## Outstanding tasks (pick up here next session)

1. Once the Shopify store is live, update the nav CTA (text + href) and
   possibly add real "Buy" buttons/links inside the Editions cards.
2. Manual cross-browser check — so far only verified via headless Chrome
   screenshots at 1440px + CSS breakpoint review, not a real device/browser
   pass (mobile nav toggle, canvas animation smoothness, hover states).
3. Deployment/infra is done (HTTPS live and enforced). Everything else is
   content/polish, not blocking.

## Commit history so far

```
f63231b Add CNAME for spasynth.com custom domain
8e411ab Set nav CTA to Coming soon until Shopify store is live
18fb77b Add SPASynth landing page
2474d49 Initial commit
```
