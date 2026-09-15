# SPASynth landing page handoff

Current-state snapshot for picking the work back up. `PROGRESS.md` is the long
chronological log (DNS history, design decisions, every past session); this file
is just what is true right now and what to do next.

- Repo `github.com/meeglosh/spasynth-landing`, branch `main`, local
  `~/spasynth-landing`. Static one-page site, no build step, GitHub Pages behind
  Cloudflare at **spasynth.com**.
- As of 2026-09-15 `main` is clean and fully pushed; the live site matches it.

## One thing is waiting on you

The daily Vault auto-refresh is **built and committed but not switched on**. It
needs a one-time install, deliberately left to a human because the job pushes to
the live site unattended:

    cp scripts/launchd/com.spasynth.vault-refresh.plist ~/Library/LaunchAgents/
    launchctl load ~/Library/LaunchAgents/com.spasynth.vault-refresh.plist

Until that runs, the sound count only updates when someone runs the scripts by
hand. Nothing else is blocked.

## What the page says right now

Everything below is generated, not typed. Do not hand-edit these numbers in
`index.html`; they live in `<span data-stat>` tags and the three description
`<meta>` tags, and the next script run will overwrite anything typed by hand.

| Stat | Value | Where it comes from |
|---|---|---|
| Packs | 90 | SPAStation catalog, verified non-bundle entries |
| Sounds ("up to") | 11,577 | 11,479 pack sounds + 98 Vault bonus |
| Library size | 73 GB | catalog zip bytes + Vault bonus bytes |
| Starter library | 450 | 5 x packs |
| Factory presets | 270 | 3 x packs (Keys/Texture/Pulse per pack) |
| Version | v1.0.16 | hand-bumped, see below |

## The generator pipeline

Three scripts, run in this order after a pack release or Vault change:

1. **spastation** `python3 scripts/count-pack-sounds.py` reads each pack zip's
   central directory over HTTP Range requests (no full downloads) and records a
   `soundCount` per pack. Ignores macOS `._` resource forks; the older
   `audioEntries` field double-counts those and must not be used for marketing.
2. **spastation** `node scripts/build-release-registry.mjs` copies those into
   `shared/catalog-releases.json` as `fileCount`.
3. **spastation** `node scripts/vault-stats.mjs` writes `shared/vault-stats.json`
   (one read-only D1 aggregate of the active Vault run).
4. **here** `python3 scripts/update-library-stats.py` sums it all and rewrites
   the page. Safe to re-run; prints what it changed.

`scripts/auto-refresh-vault.py` automates steps 3 and 4 daily once the
LaunchAgent above is loaded. It commits and pushes **only** when a published
number actually moves, skips itself if this repo has staged changes/unexpected
edits/is behind origin, stages only `index.html` and `scripts/library-stats.json`,
and publishes nothing if the query fails or returns a structurally bad result.
Cadence is daily while the count moves, self-throttling to ~monthly after 90
steady days, snapping back to daily on any change. Log:
`~/Library/Logs/spasynth-vault-refresh.log`.

**The version number is the one thing still hand-typed.** `v1.0.16` appears in
five places (hero strip, demo caption alt text, demo figcaption, specs note,
footer). The changelog accordion body is generated separately by
`python3 scripts/build-changelog.py` from `~/spasynth/docs/CHANGELOG.md`.

## Decisions worth not relitigating

- **"Up to N sounds" = packs + Vault bonus.** Mike's call 2026-09-14: only
  Pro/Everything Bundle owners get the full library either way, so the ceiling
  is everything SPASynth can play. Vault bonus is added; the Vault's own pack
  mirror (11,493) is not, the catalog is authoritative for packs.
- **Count only what is currently sold.** The SPAStation catalog is the
  inclusion rule. Legacy packs no longer on Shopify (e.g. Wood Impacts, 101
  sounds, still in the old built library) are excluded.
- **A falling Vault count is not a bug.** Throwaway/generic recordings were
  culled 2026-09-14 and are being replaced with deliberate additions; expect it
  to climb back toward ~2,000 over time. It went 7,632 -> 25 -> 98. Do not
  "fix" a drop by pinning to an older figure; publish what the database says.
- **Pro is 24/96, Standard's starter is 24/48**, delivered via Everything
  Bundle links in Shopify order emails or directly in SPAStation.
- No em dashes in visible copy.

## Open items

1. **Ask Mike:** does the existing "Will I get updates?" FAQ satisfy his older
   request for "a FAQ answer confirming updates are free"? Never answered.
2. **Shopify links.** Three CTAs (Standard, Pro, upgrade) are still
   `href="#"` placeholders labelled "Coming soon". Swap for real product URLs at
   launch and likely relabel to "Buy now".
3. **Link "SPAStation"** in the download FAQ once its public download page exists.
4. **Real-device pass.** Verified only via headless Chrome and one in-browser
   check; no actual phone/tablet run of the mobile nav, hover states, the pinned
   preset-browser demo, or the retint hue cycle.
5. **Two unverified claims** in the Filters and Modulation cards: "±4 octave
   envelope depth" could not be confirmed against a constant in
   `~/spasynth/source/`, and "90+ destinations" is built at runtime (cap
   `maxModDests = 96`) so it could not be counted without building the plugin.
   It matches Silverplatter's own Shopify wording, so it was left alone.
6. **Re-audit on each release.** Check `~/spasynth/docs/CHANGELOG.md` against the
   page, and prefer verifying spec numbers against `~/spasynth/source/` directly
   rather than changelog prose; that is how the stale 264-preset count and the
   incomplete arpeggiator list were caught.

## Gotchas

- An occasional one-off `7403 Unauthorized` from wrangler after a long idle gap
  is just an expired OAuth access token. The failing call itself triggers the
  refresh; re-run and it works. Not a broken credential.
- The design is the flat7.design SPASynth case-study grammar (scroll-craft
  engine in `js/scrollcraft.js` + `css/scrollcraft.css`). **Never edit the
  engine files**; bespoke behaviour is driven from `--sc-p` in page CSS/JS.
- The 3D hero/teardown renders model the pre-1.0.11 faceplate. They read as a
  stylized study model rather than a screenshot, so they were left as-is.
- `scripts/.vault-poll-state.json` is gitignored local-only cadence state.
  Deleting it just restarts the clock at daily.
