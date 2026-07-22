# SPASynth Landing Page — Project Progress

Last updated: 2026-07-21

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
     `~/spasynth/docs/spasynth-hardware.png`) with a heavy vertical dark
     gradient scrim over it. The scrim had to be tuned much darker than a
     typical hero overlay (up to ~0.97 opacity near the edges) because
     `background-size: cover` crops a *different* part of the image at
     different viewport aspect ratios, so contrast that works at one width
     can fail at another (a nav link nearly disappeared against a bright
     lamp in the photo before this was fixed) — don't lighten the scrim
     without re-checking contrast across several widths.
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
     the overflow instead of creating a horizontal scrollbar.
- Retint showcase image (`assets/images/spasynth-accent.png`) was refreshed
  to the current v1.0.3 build (previous versions showed "v0.1" in the
  corner).

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

- **Nav CTA button** reads "Get SPASynth" and links to `#editions` (its
  original text; was briefly "Coming soon" while the store wasn't live,
  reverted back once Buy buttons were added). It just scrolls to the
  Editions section, it's not a purchase link itself.
- **"Buy now" buttons** exist on all three products (Standard, Pro, and the
  Standard→Pro upgrade box) but all point to `href="#"` as a placeholder,
  each flagged with an inline `<!-- TODO -->` comment in `index.html`.
  **Swap all three for real Shopify product URLs once the store is live**
  (`target="_blank" rel="noopener"` is already set on all of them, so only
  the `href` needs to change). The upgrade button is `.upgrade-buy` inside
  `.upgrade-path`, simple fixed `margin-top`.

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

1. Once the Shopify store is live, swap the three placeholder "Buy now"
   `href="#"` links (Standard, Pro, upgrade) for real Shopify product URLs.
2. Manual cross-browser check — so far only verified via headless Chrome
   (Playwright) screenshots at various widths, not a real device/browser
   pass (mobile nav toggle, hover states, the new hero effects — background
   parallax and the title letter-spacing/blur scroll effect — on an actual
   phone/tablet).
3. Deployment/infra is done (HTTPS live and enforced). Everything else is
   content/polish, not blocking.
4. **Site content is behind the actual product (v1.0.3 shipped, confirmed
   by Mike against `~/spasynth`'s own git history).** Version number and
   the FX feature card are now fixed (see below), but still stale/missing:
   - "Built to play live" feature card only mentions 16-voice polyphony;
     doesn't mention the new **Voice modes** (Poly/Mono/Duo/Paraphonic/
     Unison), the **Panic button**, or **standalone tempo** (internal BPM +
     MIDI clock).
   - **Oversampling** (2x/4x/8x quality setting) isn't mentioned anywhere.
   - 1.0.2 features never made it onto the site either: the **on-screen
     keyboard** and the **settings menu** (Set Library Folder, Rescan,
     Accent Colors, Clear MIDI Learn).
   - Cross-check against `~/spasynth/docs/CHANGELOG.md` for the full,
     confirmed-accurate feature list next time this gets picked up.

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
