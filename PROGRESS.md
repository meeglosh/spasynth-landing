# SPASynth Landing Page — Project Progress

Last updated: 2026-09-14

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

- `https://spasynth.com` — **fully live**, confirmed working end-to-end
  (2026-07-18): apex returns 200, `http://` redirects to `https://`, `www`
  redirects to the apex. Served through Cloudflare's proxy in front of
  GitHub Pages (see DNS section below — this is a real architecture change,
  not just a config detail).
- GitHub Pages: enabled, source = `main` branch, `/` root. (Had to be turned
  on manually in the GitHub web UI — the `gh` CLI token in this environment
  doesn't have Pages admin scope, `gh api repos/.../pages` POST returns 403.)

### DNS — now on Cloudflare, NOT GoDaddy (changed 2026-07-18)

**Read this before touching DNS again.** The domain's nameservers were
switched at the registrar level from GoDaddy to Cloudflare
(`amanda.ns.cloudflare.com` / `ignacio.ns.cloudflare.com`) at some point
before 2026-07-18, for reasons unknown (Mike didn't recall a deliberate
reason when asked; possibly set up for something else and forgotten).
**GoDaddy's own DNS panel is now inert** — whatever records live there
(including the old 4 A records pointing at GitHub Pages IPs) have zero
effect on real-world resolution, since GoDaddy isn't the authoritative
nameserver anymore. Only Cloudflare's DNS dashboard matters now.

- **What broke:** only `www.spasynth.com` (CNAME → `meeglosh.github.io`)
  had been carried over into Cloudflare's zone. The apex (`spasynth.com`,
  no `www`) had no record at all there, so it failed to resolve. Since
  GitHub Pages redirects `www` → apex, this took the whole site down even
  though `www`'s own DNS was technically fine.
- **The fix:** an apex record was added in Cloudflare's dashboard. It now
  resolves to a Cloudflare IP (`172.64.80.1` as of this writing, not a
  GitHub Pages IP directly) — confirms Cloudflare's proxy ("orange cloud")
  is turned ON for this record, so traffic flows browser → Cloudflare edge
  → GitHub Pages, not directly to GitHub. This is working correctly
  (verified HTTPS returns 200 with valid content), so no need to switch it
  to "DNS only" (grey cloud) unless something breaks later.
- **If DNS problems come up again:** check Cloudflare's dashboard first,
  not GoDaddy's. `dig spasynth.com NS` will show which nameservers are
  currently authoritative if there's ever doubt.
- GoDaddy's stray parking-forwarding A records (documented in earlier
  versions of this file) are now moot, since GoDaddy DNS isn't in the
  resolution path at all anymore.

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
- **Hero is a full-screen photographic background** (as of 2026-07-21,
  merged from the `experiment/fullscreen-hero-bg` branch — this replaced an
  earlier version built around a canvas oscilloscope + framed plugin
  screenshot + animated preset-drawer overlay; that whole approach, its
  CSS, and its image assets were removed in the merge, so ignore any old
  references to `.hero-scope`, `.hero-shot`, `#hero-scope`, or
  `spasynth-hero-panel.png` if they turn up in old notes or git history).
  Current implementation, all respecting `prefers-reduced-motion`:
  1. `.hero-bg-image` (in `index.html`, styled in `css/styles.css`) is a
     full-bleed `background-image` div behind the copy: a stylized "SPASynth
     as hardware" render (`assets/images/spasynth-hero-bg.jpg`, sourced from
     `~/spasynth/docs/spasynth-hardware.png`, later swapped for a zoomed-out
     crop Mike provided) with **two** dark gradient layers over it, not one.
     Hero content (title/subtitle/CTAs) is **left-aligned**, not centered
     (`.hero-bg .hero-inner{text-align:left}` plus overrides on `.hero-bg
     h1`/`.hero-bg .hero-sub`'s `margin:0 auto` and `.hero-cta`'s
     `justify-content`, all scoped to `.hero-bg` so the shared `.hero`/
     `.hero-sub`/`.hero-cta` rules used elsewhere aren't touched) — this was
     a deliberate change so the right two-thirds of the image reads clearly
     instead of being evenly darkened for centered text. The two gradients:
     a horizontal one (dark on the left under the text, fading to
     transparent by ~78% width) layered with a vertical one (kept dark at
     the very top for nav legibility and at the very bottom for a clean
     section handoff, but much lighter through the middle band than before,
     since the horizontal gradient now carries the legibility burden on the
     left while the right is meant to stay visible). `background-size:
     cover` crops a *different* part of the image at different viewport
     aspect ratios, so contrast that works at one width can fail at another
     (a nav link nearly disappeared against a bright lamp in the photo
     before this was first fixed, pre-left-align) — re-check contrast at
     1440/1920/mobile if either gradient's stops change.
  2. Scroll-linked parallax (`js/main.js`, the "hero parallax" block):
     `#hero-copy` (title/subtitle) drifts up faster than scroll
     (`translateY(scrolled * -0.18)`), `.hero-bg-image` lags behind
     (`translateY(scrolled * 0.4)`). The background image has an
     oversized box (`top: -45%; height: 150%`) so this shift never reveals
     a gap at the section edge — if either multiplier is increased, this
     buffer needs to grow to match (worked example of the math is in the
     merged commit history on the experiment branch).
  3. `#hero-title` also widens (`letter-spacing`, -0.01em resting up to
     +0.3em) and blurs (`filter: blur()`, 0 to 10px) as the user scrolls,
     scaled to roughly the point the title exits the viewport (not the
     full hero height) so the effect completes while it's still visible.
     `white-space: nowrap` keeps it from wrapping to a second line as it
     widens; relies on `body{overflow-x:hidden}` (already present) to clip
     the overflow instead of creating a horizontal scrollbar. Since the
     hero is left-aligned, the growing letter-spacing now bleeds off the
     **right** edge only (the left edge stays anchored at the margin) —
     reads as the text dissolving into the revealed image detail, which is
     the intended effect, not a bug.
     **Gotcha found on mobile:** `.hero.hero-bg` is `display:flex` (for
     vertical centering), which makes `.hero-inner` a flex item. The
     shared `.wrap` class's `margin: 0 auto`, inherited by `.hero-inner`,
     triggers flexbox's auto-margin behavior (absorbs free space instead
     of stretching), so a flex item with auto margins sizes to its
     content instead of filling the container. Normally invisible, but
     once the title's nowrap content grew wide enough from the
     letter-spacing effect, `.hero-inner` itself grew to match — dragging
     the subtitle and CTA buttons wider too, even though they have no
     letter-spacing of their own. Fixed with
     `.hero-bg .hero-inner{ width:100%; margin-left:0; margin-right:0; }`,
     scoped narrowly so the shared `.wrap` class elsewhere is untouched.
     If `.hero-bg` or `.wrap` ever change, re-check this interaction
     (measure `.hero-inner`'s `getBoundingClientRect().width` at a
     scrolled position on a narrow viewport — it should equal the
     viewport width, not grow past it).
- Retint showcase image (`assets/images/spasynth-accent.png`) was refreshed
  to the current v1.0.3 build (previous versions showed "v0.1" in the
  corner), swapped again later same-session for a further-updated capture.
  It also **continuously animates through different accent-color pairs**:
  `.retint-shot img` has a 24s linear `filter: hue-rotate()` loop (0deg to
  360deg, `@keyframes retint-hue-cycle`). This works cleanly because
  hue-rotate only visibly shifts saturated pixels — the two accent colors
  (violet/lime in the source screenshot) — while the mostly-neutral dark
  UI chrome stays put, confirmed by sampling several rotation angles.
  Disabled under `prefers-reduced-motion`. If the source screenshot is
  ever replaced with one whose background isn't sufficiently neutral/dark,
  re-check that the background doesn't visibly shift too.

### Hero demo shot (non-obvious, read before touching)

A separate section (`.hero-demo`, not part of `.hero`) sits directly under
the hero, before `#library`. A static base screenshot
(`spasynth-hero-anim-base.jpg`, from `~/spasynth/docs/spasynth-loading.png`,
the "loading…" closed state) with the preset browser (`.hero-demo-panel`,
cropped from `~/spasynth/docs/spasynth-dark.png`, same left-docked-strip
technique as the old hero drawer) sliding in from the left, holding, then
sliding back out, on a 9s loop (`demo-panel-slide` keyframes: ~1.5s
closed → 0.5s slide open → 5s held → 0.5s slide closed → ~1.5s closed).

- This originally also had an on-screen-keyboard overlay alternating with
  the panel on a shared 14s timeline, plus an edge-shadow div on the
  panel. **Both were removed same-session per Mike's feedback** ("remove
  the drop shadow," "remove the keyboard part entirely, I don't like
  it") — don't re-add either without being asked again. If the keyboard
  idea comes back, the crop was `~/spasynth/docs/spasynth-keyboard.png`,
  y 882–967 of a 1380×996 source (re-derive via pixel-diff against the
  base image, don't assume those numbers still hold if the screenshot
  changes), and it necessarily covered real content (the FX tab row and
  bottom of the Distortion panel) since a fixed-aspect container can't
  grow the way the real app's window does when the keyboard appears.
- The panel overlay is still a **wrapper `<div>`, not the `<img>` itself**
  — kept that way even after removing the edge-shadow sibling div it was
  originally there to support, since replaced elements like `<img>` don't
  reliably render `::before`/`::after` if a shadow or other pseudo-element
  effect gets added back later.
- **Watch the CSS cascade if editing `.hero-demo`'s padding**: it needs
  `padding-top: 0` to sit close under the hero, but the general
  `.section{padding:120px 0}` rule comes later in the stylesheet and has
  equal specificity as a single-class selector, so it silently wins ties.
  Fixed with a `.section.hero-demo` compound selector; don't revert to a
  plain `.hero-demo{...}` override without re-checking computed style.

### Pricing (real numbers, from Mike directly — not from the marketing brief)

**All prices are USD.** An earlier session priced Pro/Upgrade using numbers
that turned out to be CAD, not USD — those were wrong and got corrected this
session. If a pricing update ever comes in without an explicit currency,
confirm USD before touching the copy.

- Standard: $149 regular, **$99 intro** (badge makes the discount explicit).
- Pro: $499, discounted from **$899** (the Everything Bundle's list price
  on Shopify, in USD). $499 is what the bundle *already* sells for after its
  own discount — Pro is priced to **exactly match** that bundle sale price,
  not undercut it. The pitch is "SPASynth comes included at no extra cost,"
  not "cheaper than the bundle." Got this wrong once before (said "cheaper")
  and had to correct it — keep this distinction precise if the copy changes.
- Standard→Pro upgrade (library only, no synth): $400 intro, discounted
  from $750 regular (the difference at each tier: 499−99=400, 899−149=750).
  Shown in the dashed box under the edition cards, with the same price-badge
  visual treatment as the edition cards.
- All these numbers should stay in sync across `~/spasynth/docs/shopify-listings.md`
  (source of truth, already correct in USD as of this session), this file,
  and the Editions section in `index.html`.
- Pricing cards (Standard/Pro/Upgrade box) have a hover effect: a soft
  drifting orange/cyan "vapor" glow behind the card, built from a blurred
  `::before` pseudo-element. It's masked by an opaque `::after` layer
  sandwiched between the glow and the content so the vapor only shows
  *outside* the card border — an earlier version let it wash over the
  card interior and hurt text contrast. If extending this pattern to a
  new card, keep the three-layer structure (glow → mask → content).

## Section order (index.html)

Hero → Hero demo shot → Library-is-the-synth (signal diagram) →
Randomize/Chaos (WILD knob + lock chips + Organic Chaos scope) → Feature grid
(8 cards) → Accent re-tint showcase (now with the hue-cycle animation, see
Design decisions) → Editions (Standard/Pro + upgrade box) → No-DRM statement
(verbatim blockquote from the brief) → Specs table → FAQ accordion → Footer.

The Library-is-the-synth **signal diagram is 4 nodes, not 3**: Oscillator,
Granular Fuel, Modulation Source, and (added 2026-07-22) **Convolution
Impulse** — a sound loaded into SPASynth can now also become a convolution
reverb impulse (the shipped 1.0.3 Convolve module), so the diagram, hero
subtitle, meta descriptions, and the Library section lede were all updated
together to describe 4 uses instead of 3. The SVG connector lines
(`.signal-lines`) are evenly spaced at y = 12.5/37.5/62.5/87.5 in a 0–100
viewBox; if a 5th use ever gets added, recompute all the y-positions rather
than just appending one (they need to stay evenly spaced across the new
total). Convolution Impulse is tagged cyan (`tag-cyan`), grouped with
Modulation Source as a "shaping" category rather than orange "generation"
like Oscillator/Granular Fuel.

Feature grid is a strict 4-column grid (2-col tablet, 1-col mobile) — an
"In-pack quick-swap" 9th card was added and then explicitly removed same
session (Mike: let users discover it organically). If a 9th feature card
ever gets added again, either accept the last-row grid gap or reintroduce
a full-width spotlight treatment (was called `.feature-card-wide`, fully
removed now — would need to be rebuilt, not just uncommented).

## Known placeholder / intentionally incomplete

- **Nav CTA button** reads "Get SPASynth" and links to `#editions` (its
  original text; was briefly "Coming soon" while the store wasn't live,
  reverted back once Buy buttons were added). It just scrolls to the
  Editions section, it's not a purchase link itself.
- **Pricing card CTA buttons** exist on all three products (Standard, Pro,
  and the Standard→Pro upgrade box) but currently read "Coming soon" (was
  briefly "Buy now," reverted per Mike). All point to `href="#"` as a
  placeholder, each flagged with an inline `<!-- TODO -->` comment in
  `index.html`. **Swap all three for real Shopify product URLs (and
  probably the label back to "Buy now") once the store is live**
  (`target="_blank" rel="noopener"` is already set on all of them, so only
  the `href`/label need to change). The upgrade button is `.upgrade-buy`
  inside `.upgrade-path`, simple fixed `margin-top`.

  Standard/Pro buttons (`.edition-buy`) are trickier: `.edition-card` is a
  flex column, and each card has an `.edition-spacer` div (`flex: 1 0 0`)
  right before the button, plus the button itself has a fixed
  `margin-top: 20px`. **Don't simplify this back to `margin-top: auto` on
  just the button** — Pro is the taller card (defines the grid row height
  via stretch), so it structurally has zero leftover space relative to
  itself, meaning a lone `margin-top: auto` always resolves to 0 for Pro
  specifically, no matter how much you trim elsewhere. The spacer+fixed-
  margin combo is what makes Pro get a real minimum gap while Standard
  (which does have leftover space) still bottom-pins correctly, and titles
  stay top-aligned across both cards. If touching this again, don't use
  `justify-content: flex-end` either — that pushes each card's *entire*
  content block to the bottom, breaking title alignment between the cards.
- Footer logo and a "Silverplatter Audio" nav link both point to
  `https://www.silverplatteraudio.com` (opens in a new tab).
- FAQ has grown organically, item by item, rather than as one pass: free v1
  updates and the Windows SmartScreen warning (from the Shopify shared FAQ),
  iZotope RX9 compatibility (won't load, by design), using SPASynth for
  film/TV/game SFX (Keys preset workflow), and where Pro purchasers find
  their library download links (the included "SPASynth Pro Library -
  Downloads.html" file). The Shopify doc has a few more entries (system
  requirements, sound/preset counts, usage rights) not yet mirrored here
  since they felt redundant with content elsewhere on the page; revisit if
  the FAQ section feels thin.
- **"Will I get updates?"** already exists as a FAQ item ("Yes. Updates
  across the v1 line are free...") — Mike asked for a FAQ confirming free
  updates late in a session and this was pointed out as already covering
  it. He hadn't replied to confirm whether that existing entry satisfies
  the ask, or whether he wanted something different (different phrasing,
  more detail, a separate question), by the time this got written down —
  **check with him first thing next session** rather than assuming either
  answer.
- Sound count is **11,474** (updated from an earlier 11,401 — more accurate
  count) everywhere it appears, qualified as "up to" except where the copy
  is explicitly about the complete/Pro library.

## Outstanding tasks (pick up here next session)

1. **Ask Mike first:** does the existing "Will I get updates?" FAQ item
   satisfy his request for "a FAQ answer confirming updates are free," or
   did he want something different? He asked this near the end of a
   session and never replied to the clarifying question — don't assume,
   just ask.
2. **Library numbers are generated, not typed.** Pack count, sound total and
   the starter-library size live in `<span data-stat>` spans (and the three
   description metas) and are written by `scripts/update-library-stats.py`
   from the SPAStation catalog (`~/spastation/shared/catalog-releases.json`,
   the release source of truth: verified, non-bundle, non-source-archive
   entries, summing each pack's `fileCount`) **plus the Vault's bonus
   recordings** from `~/spastation/shared/vault-stats.json`. Mike's decision
   2026-09-13: the "up to N sounds" figure is everything SPASynth can play,
   packs + Vault, because only Pro / Everything Bundle owners get the full
   library either way. The `size` stat (Pro card, specs note) is catalog zip
   bytes + Vault bonus bytes in GB. **After every pack release or Vault
   sync, in the spastation repo:** `python3 scripts/count-pack-sounds.py`
   (reads each zip's central directory over Range requests, no full
   downloads), `node scripts/build-release-registry.mjs`, and
   `node scripts/vault-stats.mjs` (one read-only D1 aggregate query);
   **then here:** `python3 scripts/update-library-stats.py` and commit. The
   `soundTotalFallback` in `scripts/library-stats.json` is only used if any
   pack lacks a fileCount (the script warns). Done 2026-09-13: 90 packs,
   11,479 pack sounds + 7,632 Vault bonus = up to 19,111 sounds, 190 GB,
   450-sound starter. Inclusion rule from Mike: count only packs, micro-packs and bundles
   currently sold on the store (= the SPAStation catalog); legacy packs such
   as Wood Impacts (101 sounds, in the old built library, not on Shopify)
   are out. Download copy rewritten 2026-09-13: Pro = original 24/96 packs
   via Everything Bundle links in Shopify order emails or SPAStation;
   Standard = 24/48 starter via Shopify links or SPAStation. TODO: link
   "SPAStation" in that FAQ once its public download page exists. Reconciled against the old 11,474:
   + Seagulls 26, New York 23, Flashback 21, Fire Burning +35, Countryside
   +1, minus Wood Impacts 101 (in the old built library, absent from the
   SPAStation catalog; ask Mike whether it is retired). **Also generated
   2026-09-14: a `presets` stat (3 * packs = 270), replacing the hardcoded
   "264" in two places** (see the 2026-09-14 session summary).
   **Vault bonus count is deliberately low right now (2026-09-14, confirmed
   real by Mike, not a bug):** it dropped from 7,632 to 25 because
   throwaway/generic Vault recordings are being culled and replaced with
   deliberately-added sounds; Mike expects it to climb back toward ~2,000
   over time. The site's numbers now use the live figure as-is (11,504
   total sounds, 72 GB), no longer pinned to the old 7,632. **Re-run
   `update-library-stats.py` periodically as the Vault refill progresses**;
   see the 2026-09-14 session summary for the full story, including the
   false-alarm first pass.
3. Once the Shopify store is live, swap the three placeholder "Coming soon"
   `href="#"` links (Standard, Pro, upgrade) for real Shopify product URLs
   (and likely change the label back to "Buy now").
4. Manual cross-browser check — so far only verified via headless Chrome
   (Playwright) screenshots at various widths, not a real device/browser
   pass (mobile nav toggle, hover states, the hero effects — background
   parallax, the title letter-spacing/blur scroll effect, the left-aligned
   layout, the retint hue-cycle animation — on an actual phone/tablet).
5. Deployment/infra is done (HTTPS live and enforced). Everything else is
   content/polish, not blocking.
6. **Site content vs. actual product — re-audited 2026-09-12, spec-checked
   against plugin source 2026-09-14.** Version is now v1.0.16 (specs note,
   footer, hero strip, demo caption; bumped 2026-09-14). All landing-worthy
   1.0.8–1.0.16 items are folded into existing feature cards (see the
   2026-09-12 and 2026-09-14 summaries); the 2026-09-14 pass also verified
   engine/filter/matrix/FX counts directly against `~/spasynth/source/`,
   not just changelog prose, and fixed the preset count and arp mode list
   (see above and the 2026-09-14 summary). Still unconfirmed: the Filters
   card's "±4 octave envelope depth" and the exact mod-matrix destination
   count (currently "90+", matches Shopify's own wording, not independently
   recounted).
   Standalone tempo (1.0.3) finally landed in the PLAY card. Still open:
   - Screenshots refreshed to v1.0.15 on 2026-09-12 (UI demo, retint). The
     3D render (hero, teardown, studio photo) still models the pre-1.0.11
     faceplate; it reads as a stylized study model, re-render only if asked.
   - Intentionally excluded as internal fixes/polish: 1.0.7–1.0.10 bug
     fixes, 1.0.9 CPU work, 1.0.13/1.0.14 crash fixes, greyed-out
     inapplicable controls, factory preset re-voicing.
   - Re-run this audit against `~/spasynth/docs/CHANGELOG.md` next time a
     new version ships.

## Recent session summary (2026-09-14, drift audit against source)

Mike asked whether the site's specs still matched the shipped product,
since the changelog is not the only ground truth, the C++ plugin source at
`~/spasynth/source/` is. Grepped the parameter registry, DSP headers, and
preset manager directly rather than trusting copy alone. Confirmed against
source: 7 engines/3 slots, 8 filter types with drive/keytracking, 16 matrix
routes, 20 mod sources (3 env, 3 LFO, 4 macros, velocity, mod wheel,
aftertouch, chaos, 6 SFX followers), 64-sample mod block, 9 FX modules, 8 EQ
bands with the listed shapes, Crush distortion, 5 reverb characters, 8
built-in wavetables, white/pink/brown noise, 5 voice modes, unison
detune/width, glide, CHANCE/STUTTER/JUMP/HUMAN, Panic, MIDI clock sync,
2x/4x/8x oversampling, resizable window, portable preset paths. Found and
fixed three real drifts:

1. **v1.0.16 had shipped** (library self-refreshes when packs are
   added/removed, no rescan needed, plus a VOICE-panel crash fix) and the
   site was still on v1.0.15 everywhere (hero, demo caption, specs note,
   footer) with the changelog accordion one entry short. Bumped all five
   version strings by hand (no generator exists for the version number
   itself, only the changelog body) and re-ran `build-changelog.py`.
2. **"264 factory presets" was hardcoded and already wrong** at 90 packs
   (should be 270): confirmed in `source/library/PresetManager.h` that the
   plugin generates exactly 3 presets per pack (Keys/Texture/Pulse), not a
   fixed 264. Added a `presets` stat (3 × packs) to
   `scripts/update-library-stats.py` alongside the existing packs/sounds/
   starter/size stats, wrapped both hardcoded "264" spots (Library feature
   card, Pro edition bullet) in `<span data-stat="presets">`, and added a
   line to the Library card that the library now self-refreshes (from the
   1.0.16 fix above).
3. **Arpeggiator mode list was incomplete.** `enum class ArpMode` in
   `ParameterRegistry.h` has exactly 12 modes; the card named 8 and was
   missing down/up, up/down-inclusive, as-played, and random. Card copy now
   lists all 12.

**Not fixed, flagged instead, not asked for:** the Filters card's "±4 octave
envelope depth" claim could not be confirmed against a specific constant in
source; the "90+ destinations" mod-matrix figure is built at runtime from
parameter flags (`maxModDests = 96` cap) and could not be counted without
building the plugin, matches Silverplatter's own Shopify listing wording
("more than 90") so left as-is.

**Vault data integrity flag for Mike, found while re-running the stats
scripts, not part of what was asked:** `~/spastation/shared/vault-stats.json`
was re-generated on disk (uncommitted) between the last session and this
one, and its `bonusSounds` count collapsed from 7,632 to 25 while
`packSounds` stayed at 11,493, a same-day, nearly-total drop that reads as a
broken Vault sync run rather than 7,600 sounds actually leaving the store.
Did not publish that number: pinned the landing page's sound/size stats to
the last known-good, git-committed spastation value (7,632 bonus / 19,111
total / 190 GB, commit `1dbffc8`) via a one-off `SPASTATION_VAULT_STATS`
override, documented in `scripts/library-stats.json`'s `vaultStats` note.
**Correction, same day, minutes later: Mike confirmed the drop was real
and deliberate**, not a bug. Silverplatter is culling throwaway/generic
Vault recordings and replacing them with deliberately-added sounds; the
bonus count is genuinely ~25 right now and expected to climb back toward
~2,000 over time as re-additions land, not snap back to 7,632. Re-ran
`update-library-stats.py` against the live (unpinned) Vault file and
published the real current numbers: 90 packs, 11,479 pack sounds + 25
Vault bonus = 11,504 sounds, 72 GB. Removed the pin and the "flag as bug"
framing from `scripts/library-stats.json`'s `vaultStats` note, replaced
with a note that a low bonus count is expected during the refill and
should just be taken as-is on each run, not treated as a signal to
re-pin. **No action needed unless the number looks wrong in some new way**
(e.g. it should only ever move up from here as sounds are re-added, so a
further drop would be worth asking about; a rise toward ~2,000 over
coming weeks/months is the expected, healthy trend).

## Recent session summary (2026-09-12, later: case-study redesign shipped)

Rebuilt the whole landing page in the grammar of the flat7.design SPASynth
case study (`/Users/mikejerugim/flat7-design-spasynth/public/spasynth/`) and
merged it to `main`. Every piece of landing copy survived (all 8 feature
cards, both edition cards, upgrade path, all 15 FAQ items, specs, no-DRM
quote); only connective tissue is new. Stack: the scroll-craft engine
(`css/scrollcraft.css`, `js/scrollcraft.js`, copied verbatim, never edit),
Barlow / Barlow Condensed, teal `#6dd6c2` on charcoal with sage interludes.
Page order: masthead (sticky, section nav + CTA) → hero with the assembled
3D render → **UI demo**: a pinned scroll-craft act (`data-sc-act="pin"`,
span 2.2) where the v1.0.15 synth sits centred, then the preset browser
panel slides out from behind its left edge as you scroll while the synth
nudges right so the pair stays centred, flush like the real window; no
copy, driven purely by `--sc-p` in CSS → The Hook + studio photo → sage
bench intro → **3D teardown** (`js/scene.js`, 181-frame WebP sequences in
`assets/scene/`, three module stops remapped to Sample engine / Organic
Chaos / Mod matrix notes, then Randomize + reassembly) → features grid on
sage + case-study interface figure → retint (new v1.0.15 purple/green
capture with the 24s hue cycle) → listening room (3 MP3s in
`assets/audio/`) → editions → no-DRM teal band → specs → FAQ →
**Changelog accordion** (all 13 releases newest first, collapsed; regenerate
with `python3 scripts/build-changelog.py` whenever a version ships) → close.
Removed the old CSS/JS/hero assets. Verified in headless real Chrome
(Playwright from the flat7 checkout) at 1440 and 390 wide, plus the pin at
p=.1/.5/.9 and the teardown at its stops. Mike's new v1.0.15 captures live
in `~/spasynth/docs/` (accent, chaos, dark/browser, keyboard, loading,
marketing); the demo uses marketing + a 320px crop of dark.

## Recent session summary (2026-09-12)

Re-ran the missing-features audit against `~/spasynth/docs/CHANGELOG.md`,
which had moved from 1.0.7 to 1.0.15 since August. Bumped the version
(specs note + footer). Folded new features into existing cards rather than
adding cards, to keep the 2x4 grid: ENGINES now mentions the 8 built-in
wavetables, tempo-synced beat-locked sample loops with a zoomable waveform,
and the analog SUB oscillator; MODULATION adds ASSIGN mode and the live
modulation indicator on knobs; PLAY adds the standalone tempo bar (BPM, tap
tempo, time signature, MIDI clock sync), closing the long-standing tempo
gap; FX adds the Crush bit crusher, the new plate-derived reverb engine,
and the switchable EQ band types; LIBRARY adds user preset banks; INTERFACE
adds the side-opening preset browser. Verified the grid still lays out
cleanly at 1400px via headless Chromium (Playwright). Flagged that every
screenshot on the site predates the 1.0.11 faceplate redesign.

## Recent session summary (2026-08-10)

Ran a missing-features audit against `~/spasynth/docs/CHANGELOG.md` (see
Outstanding tasks above for the full breakdown). Fixed the stale version
number (v1.0.3 → v1.0.7, specs note + footer). Rewrote the "Built to play
live" PLAY feature card to cover 1.0.3's Voice modes (Poly/Mono/Duo/
Paraphonic/Unison) and the Panic button, dropping the old MIDI-Learn
explanation to keep the card tight. Rewrote the INTERFACE feature card to
add the on-screen keyboard, settings menu, and oversampling (2x/4x/8x),
folded in alongside the existing accent re-tint mention rather than as a
new card. Added 60px of left padding to the hero content on large/XL
viewports only (`min-width: 901px`, matching the existing tablet
breakpoint) per Mike's request to push it further from the screen edge —
applied at the `.hero-copy` and `.hero-cta` container level so the
eyebrow, title, subtitle, and CTA buttons all shift together; tablet/phone
layout untouched. Committed and pushed to `main` (`3f5706a`, `cee8d26`).
Standalone tempo (1.0.3) is the one remaining audited gap — no card fits it
naturally yet.

## Recent session summary (2026-07-22 to 2026-07-23)

Fixed a real mobile layout bug: the hero title's scroll-driven letter-spacing
widening was dragging the subtitle and CTA buttons wider too, root-caused to
a flexbox auto-margin interaction (see Design decisions, hero section, the
"Gotcha found on mobile" note) rather than anything specific to the title
itself. Added convolution impulse as a 4th documented use for library sounds
(shipped in 1.0.3 as the Convolve FX module) across the hero subtitle, meta
descriptions, the Library section lede, and expanded the signal diagram from
3 nodes to 4. Left-aligned the hero title/subtitle/CTAs (were centered) and
added a second, horizontal gradient layer so the right two-thirds of the
background photo reads clearly instead of being evenly darkened — verified
contrast at 1440/1920/mobile again since this touches the same
scroll-and-viewport-sensitive area as earlier hero work. Reverted the
pricing card CTAs from "Buy now" back to "Coming soon" per Mike. Added a FAQ
entry for where Pro purchasers find their library download links (the
included "SPASynth Pro Library - Downloads.html" file). Swapped the retint
showcase image for Mike's latest capture and added a 24s hue-rotate
animation so the two accent colors continuously cycle through different
complementary pairs while demoing the feature, instead of sitting static.
Cleaned up stray macOS `.DS_Store` files and added a `.gitignore`. Confirmed
the local `experiment/fullscreen-hero-bg` branch is fully merged into `main`
(never pushed to origin) — safe to ignore or delete, left as-is since
deleting branches wasn't asked for.

## Recent session summary (2026-07-21)

Added FAQ entries for iZotope RX9 (won't load, by design) and using
SPASynth for film/TV/game SFX (Keys preset workflow). Diagnosed and fixed
a real production outage: spasynth.com's nameservers had moved to
Cloudflare and the apex domain had no record in Cloudflare's zone (see
the DNS section above). Checked `~/spasynth/docs/CHANGELOG.md` against
`~/spasynth/docs/next-release-plan.md` and found what looked like a
premature/aspirational changelog entry, listing planned-but-maybe-not-built
features as shipped; Mike confirmed 1.0.3 genuinely shipped with all of it
(verified independently against `~/spasynth`'s own git log). Added a
"Notes for this build" section to the 1.0.3 changelog entry (it only
existed for 1.0.2 before). Confirmed the landing site itself is behind
that shipped 1.0.3 state and fixed the two most obviously wrong things
(stale v1.0.0 version number, stale 5-effect FX feature card) per Mike's
explicit request to scope down to just those two for now (see Outstanding
tasks above for the rest). Built a full-screen photographic hero
background on `experiment/fullscreen-hero-bg` (replacing the oscilloscope
canvas + framed screenshot + preset-drawer overlay), iterated on it per
feedback (stronger parallax, title letter-spacing/blur on scroll, no
line-wrap), then merged it to `main` and deleted the now-dead CSS/image
assets the old hero left behind (see Design decisions above for how the
new hero actually works). Swapped the hero background photo for a
zoomed-out version Mike provided (reads even better across viewport
widths than the original crop). Brought back a screenshot demo under the
hero (removed when the hero went full-bleed photographic) as its own new
section before Library, rebuilt against fresh v1.0.3 screenshots, now
alternating two overlay animations (preset browser, on-screen keyboard)
instead of just the one drawer the old hero had, then simplified back
down to just the preset browser (dropped the keyboard overlay and the
panel's edge shadow) per Mike's immediate follow-up feedback (see Hero
demo shot above for the implementation details).

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
