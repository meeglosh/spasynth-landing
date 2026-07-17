# SPASynth Landing Page — Project Progress

Last updated: 2026-07-17

## What this is

Static one-page marketing site for **SPASynth** (Silverplatter Audio's hybrid
SFX synthesizer). Plain HTML/CSS/JS, no build step, deployed via GitHub Pages
at the custom domain **spasynth.com**.

- Repo: `github.com/meeglosh/spasynth-landing` (branch `main`)
- Local path: `~/spasynth-landing`
- Content source of truth: `~/spasynth/docs/marketing-brief.md` — the full
  feature list, positioning, brand voice, and palette all come from there.
  **Do not add features, numbers, pricing, or claims that aren't in that
  brief** (pricing is now an exception, see below — it came directly from
  Mike, not the brief). This path has moved once already (`~/arsenal/docs/`
  → `~/spasynth/docs/`); if it's stale again, it's probably moved again.
- Shopify product-listing copy (Standard/Pro/Upgrade descriptions, SEO,
  shared FAQ) lives at `~/spasynth/docs/shopify-listings.md` — useful for
  copy alignment and is the source for exact pricing.
- Product screenshots for updating site assets live at `~/spasynth/docs/`
  (`spasynth-dark.png`, `spasynth-accent.png`, `spasynth-loading.png`,
  `spasynth-marketing.png` as of this session). These get refreshed
  periodically as the plugin UI evolves; check dates/content against what's
  in `assets/images/` before assuming they're current.

## Current live status

- `https://spasynth.com` — **fully live**. TLS cert approved (expires
  2026-10-04, covers `spasynth.com` + `www.spasynth.com`), Enforce HTTPS is
  on, and `http://spasynth.com` now 301-redirects to HTTPS. Nothing left to
  do on the deployment/infra side.
- GitHub Pages: enabled, source = `main` branch, `/` root. (Had to be turned
  on manually in the GitHub web UI — the `gh` CLI token in this environment
  doesn't have Pages admin scope, `gh api repos/.../pages` POST returns 403.)

### DNS (GoDaddy)

- `www.spasynth.com` → CNAME → `meeglosh.github.io` — confirmed working.
- `spasynth.com` (apex) → 4 A records: `185.199.108.153`, `185.199.109.153`,
  `185.199.110.153`, `185.199.111.153`. GoDaddy previously auto-added two
  stray parking-forwarding A records that broke cert issuance; if HTTPS
  ever breaks again, check for stray A records first.

## Design decisions (so a future session doesn't relitigate these)

- Palette pulled directly from the shipping plugin UI, not invented:
  bg `#0c1114`, panels `#151c21`, text `#e7ecef` / `#7f8d97`, orange accent
  `#f08b3a` (audio), cyan accent `#4fc4d6` (modulation). The plugin's own
  *default* theme is actually a single teal accent now (not split
  orange/cyan) — the retint copy was corrected to reflect that, but the
  site's own orange/cyan scheme is the site's own branding choice and
  stays as-is.
- Fonts: **Bricolage Grotesque** (display/headings), **IBM Plex Sans**
  (body), **IBM Plex Mono** (labels, specs, eyebrows). A Montserrat swap
  (to match Silverplatter Audio's own brand font, with light/bold weight
  mixing) was tried and explicitly reverted by Mike — don't re-suggest it
  without being asked.
- No em dashes anywhere in copy, ever — replaced with colons, parentheses,
  commas, or split sentences. Keep new copy dash-free.
- Hero has two animation layers, both respecting `prefers-reduced-motion`:
  1. A canvas oscilloscope background (`js/main.js`, `makeScope`) with a
     scroll-linked parallax: the title/subtitle drift slightly faster than
     scroll, the canvas lags behind (`.hero-copy` / `#hero-scope` in
     `js/main.js` + `css/styles.css`).
  2. An animated preset-drawer overlay (see below).

### Hero preset-drawer animation (non-obvious, read before touching)

- `assets/images/spasynth-hero.png` is the **closed/base** state (shows
  Oscillator A mid-"loading…", matching `~/spasynth/docs/spasynth-loading.png`).
- `assets/images/spasynth-hero-panel.png` is a **precise crop** (0,0 to
  312×900 px) of just the presets-panel region from the open-drawer
  screenshot (`~/spasynth/docs/spasynth-dark.png`), measured via pixel-diff
  against the closed image, not eyeballed.
- These are layered in `.hero-shot` in `index.html`: base `<img>` +
  `<img class="hero-shot-panel">`. CSS (`.hero-shot .hero-shot-panel` in
  `css/styles.css`) positions the panel at `width: 22.6087%` (= 312/1380,
  the source image width) with `height: auto` — this only works because
  both source images share the same 1380×900 dimensions and the panel crop
  starts at the image's top-left corner. If either source image is ever
  re-exported at different dimensions or the panel's on-screen position
  changes, this percentage and the crop need to be redone (see the
  pixel-diff approach used this session: crop a vertical strip from both
  images, diff to find the true edge, don't guess).
- Animates via `transform: translateX()` on a `@keyframes hero-panel-slide`
  loop (currently 9s: ~1.5s closed → 0.5s slide open → 5s held open → 0.5s
  slide closed → ~1.5s closed). Slides in from the **left**, matching the
  panel's actual dock side in the real plugin UI — Mike initially asked for
  "from the right" but that would sweep the panel across the whole frame
  to reach a left-docked resting position, which looks broken; explained
  this and got confirmation to do it correctly instead.
- **No drop-shadow on the panel overlay** — a `filter: drop-shadow(...)`
  was tried and removed because it wraps around all four edges of the
  cropped rectangle (including the top/bottom crop lines, which aren't
  real UI edges), producing a visible shadow smear mid-toolbar. If you
  want depth on the panel again, it needs to be a shadow only on the
  right edge (e.g. a pseudo-element gradient), not a `filter`.
- Retint showcase image (`assets/images/spasynth-accent.png`) and the hero
  images were all refreshed this session to the current v1.0.0 build
  (previous versions showed "v0.1" in the corner).

### Pricing (real numbers, from Mike directly — not from the marketing brief)

- Standard: $149 regular, **$99 intro** (badge makes the discount explicit).
- Pro: $702, discounted from **$1,264** (the Everything Bundle's list price
  on Shopify). $702 is what the bundle *already* sells for after its own
  discount — Pro is priced to **exactly match** that bundle sale price, not
  undercut it. The pitch is "SPASynth comes included at no extra cost," not
  "cheaper than the bundle." Got this wrong once (said "cheaper") and had
  to correct it — keep this distinction precise if the copy changes.
- Standard→Pro upgrade (library only, no synth): $603 intro, discounted
  from $1,115 regular. Shown in the dashed box under the edition cards,
  with the same price-badge visual treatment as the edition cards.
- All these numbers should stay in sync across `~/spasynth/docs/shopify-listings.md`,
  this file, and the Editions section in `index.html`.
- Pricing cards (Standard/Pro/Upgrade box) have a hover effect: a soft
  drifting orange/cyan "vapor" glow behind the card, built from a blurred
  `::before` pseudo-element. It's masked by an opaque `::after` layer
  sandwiched between the glow and the content so the vapor only shows
  *outside* the card border — an earlier version let it wash over the
  card interior and hurt text contrast. If extending this pattern to a
  new card, keep the three-layer structure (glow → mask → content).

## Section order (index.html)

Hero → Library-is-the-synth (signal diagram) → Randomize/Chaos (WILD knob +
lock chips + Organic Chaos scope) → Feature grid (8 cards) → Accent re-tint
showcase → Editions (Standard/Pro + upgrade box) → No-DRM statement (verbatim
blockquote from the brief) → Specs table → FAQ accordion → Footer.

Feature grid is a strict 4-column grid (2-col tablet, 1-col mobile) — an
"In-pack quick-swap" 9th card was added and then explicitly removed same
session (Mike: let users discover it organically). If a 9th feature card
ever gets added again, either accept the last-row grid gap or reintroduce
a full-width spotlight treatment (was called `.feature-card-wide`, fully
removed now — would need to be rebuilt, not just uncommented).

## Known placeholder / intentionally incomplete

- **Nav CTA button** currently reads "Coming soon" and links to `#editions`.
  This was "Get SPASynth" originally; changed because the Shopify store
  isn't live yet. **Swap the text and href to the real store URL once the
  Shopify listing goes live.**
- Footer logo and a "Silverplatter Audio" nav link both point to
  `https://www.silverplatteraudio.com` (opens in a new tab).
- FAQ has two items pulled from the Shopify shared FAQ that weren't on the
  site before: free v1 updates, and the Windows SmartScreen warning
  explainer. The Shopify doc has a few more FAQ entries (system
  requirements, sound/preset counts, usage rights) not yet mirrored here
  since they felt redundant with content elsewhere on the page; revisit if
  the FAQ section feels thin.
- Sound count is **11,474** (updated from an earlier 11,401 — more accurate
  count) everywhere it appears, qualified as "up to" except where the copy
  is explicitly about the complete/Pro library.

## Outstanding tasks (pick up here next session)

1. Once the Shopify store is live, update the nav CTA (text + href) and
   possibly add real "Buy" buttons/links inside the Editions cards.
2. Manual cross-browser check — so far only verified via headless Chrome
   (Playwright) screenshots at various widths, not a real device/browser
   pass (mobile nav toggle, canvas animation smoothness, hover states,
   the hero drawer animation on an actual phone).
3. Deployment/infra is done (HTTPS live and enforced). Everything else is
   content/polish, not blocking.

## Recent session summary (2026-07-17)

In rough order: added hero scroll parallax; linked footer logo + nav to
Silverplatter Audio's site; swapped hero screenshot to a newer build;
qualified sound-count claims as "up to" except where Pro-specific;
corrected the retint section's default-theme copy (single teal, not
split orange/cyan); added real Editions pricing with intro-price badges;
corrected the Pro pricing pitch (matches bundle price, doesn't undercut
it); tried and reverted a Montserrat font swap; added pricing-card hover
vapor glow (then fixed it leaking into card interiors); bumped sound
count 11,401 → 11,474; bolded/underlined the Everything Bundle bullet;
refreshed hero + retint screenshots to v1.0.0; added the animated
preset-drawer hero overlay (built, tuned timing per feedback, then
removed its drop-shadow per feedback); added and then removed an
"in-pack quick-swap" feature card per feedback.
