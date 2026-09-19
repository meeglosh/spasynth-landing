# SPASynth landing page handoff

Current-state snapshot for picking the work back up. `PROGRESS.md` is the long
chronological log (DNS history, design decisions, every past session); this file
is just what is true right now and what to do next.

- Repo `github.com/meeglosh/spasynth-landing`, branch `main`, local
  `~/spasynth-landing`. Static one-page site, no build step, GitHub Pages behind
  Cloudflare at **spasynth.com**.
- As of 2026-09-15 `main` is clean and fully pushed; the live site matches it.
- The Vault refill is visibly progressing: bonus recordings went
  7,632 -> 25 -> 98 -> 199 over 2026-09-14/15. Expect this number to keep
  climbing toward roughly 2,000; the job publishes each move on its own.

## The auto-refresh is live

Mike loaded the LaunchAgent on 2026-09-14, so the Vault count now updates
itself. Nothing is waiting on a human.

Its **first scheduled run failed** (2026-09-15 10:00 local) and has been fixed.
Wrangler's own log showed the cause: it refreshed the expired OAuth access
token and then the very next D1 call came back 7403, because a just-refreshed
token is briefly not yet valid for the D1 API. Manual re-runs always worked,
the same fail-once-then-succeed pattern seen earlier in the isolated store. The
query now retries 3 times with backoff, which rides that window out; exhausting
the retries still raises, so a genuine outage publishes nothing rather than a
wrong number.

Check on it:

    tail ~/Library/Logs/spasynth-vault-refresh.log
    launchctl list | grep spasynth      # second column is last exit status

Note: three `query attempt N/3 failed` lines timestamped 2026-09-15T20:00:38 in
that log are **unit-test output**, not a real outage. Left in place rather than
rewriting the log.

## What the page says right now

Everything below is generated, not typed. Do not hand-edit these numbers in
`index.html`; they live in `<span data-stat>` tags and the three description
`<meta>` tags, and the next script run will overwrite anything typed by hand.

| Stat | Value | Where it comes from |
|---|---|---|
| Packs | 90 | SPAStation catalog, verified non-bundle entries |
| Sounds ("up to") | 11,678 | 11,479 pack sounds + 199 Vault bonus |
| Library size | 75 GB | catalog zip bytes + Vault bonus bytes |
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

## Demo tracks (the listening room)

Six tracks, in this order: SPA, Dark, The Onus is on You, City of Cones,
Barnicle, Homebound. All are Ruger Seeds except Dark, which is add.remove and
sits second at Mike's request (2026-09-17). More are expected; a new track
lands at the bottom unless Mike says otherwise.

**This list and the flat7.design case study's have deliberately diverged as of
2026-09-17.** The case study (`~/flat7-design-spasynth/public/spasynth/`) keeps
the five Ruger Seeds tracks with no artist bylines; Dark is landing-page
only, at Mike's request. Do not re-sync the two without asking.

Adding a track is a manual job with settled conventions:

- Convert Mike's AIFF master to **320 kbps MP3, 44.1 kHz stereo, no
  normalization, trimming or effects**, and leave the original untouched:
  `ffmpeg -i master.aif -codec:a libmp3lame -b:a 320k -ar 44100 -ac 2 -map_metadata -1 out.mp3`
- **If Mike supplies an MP3 rather than an AIFF and it is already 320 kbps
  stereo, copy it, don't re-encode** — re-encoding only adds a second lossy
  generation, and a 48 kHz sample rate is not worth fixing at that cost. This
  came up once, for a first cut of Dark, and was superseded hours later by a
  proper AIFF master. Ask for the AIFF if there is any doubt.
- **Filename keeps the working version number, the displayed title drops it**
  (`the-onus-is-on-you-v1.0.mp3` renders as "The Onus is on You"). Filenames are
  kebab-case, and a track with no version number in its name keeps none
  (`Dark.aif` became `dark.mp3`, displayed "Dark", like `city-of-cones.mp3`).
- **Every track carries an artist byline** in `<p class="track-artist">`, under
  the title, and names the artist in the player's `aria-label` ("Play <title> by
  <artist>, made entirely with SPASynth"). Ruger Seeds and add.remove are the
  artists so far.
- The "N tracks made entirely with SPASynth" sentence counts the players on the
  page in `js/page.js`, so it updates itself. Set the static `data-track-count`
  fallback to match for the pre-JS and no-JS cases. Never hardcode the number
  anywhere else.
- Starting one track pauses the others; that is also handled in `js/page.js`.
- **Bump the `?v=` on `css/styles.css` in `index.html` whenever the stylesheet
  changes**, and do the same for any JS file you edit. Cloudflare caches CSS and
  JS for four hours (`max-age=14400`, `cf-cache-status: HIT`) while the HTML is
  not edge-cached at all (`DYNAMIC`, `max-age=600`). Without the bump, visitors
  get new markup against a stale stylesheet for up to four hours — which is
  exactly what happened when the artist bylines shipped on 2026-09-17. Check a
  deploy with `curl -sI https://spasynth.com/css/styles.css | grep -i age`.

## Shipping a new SPASynth version

**This is automated now, and it deliberately stops one step short of publishing.**
`scripts/prepare-release.py` notices when `~/spasynth` ships a version newer than
the site advertises, regenerates the changelog accordion, bumps the version
string in its five places (hero strip, demo caption alt text, demo figcaption,
specs note, footer), commits locally, and posts a macOS notification. **It never
pushes.** Mike does that when the build is actually downloadable.

That gap is the whole point. The product changelog is written at *build* time —
the 1.0.17 commit says "built + staged" — which can be days before customers can
download anything. Publishing on that signal would put "Current release: v1.0.17"
on the marketing site while the release was still staged.

- Scheduled by `scripts/launchd/com.spasynth.release-prepare.plist`: fires on
  every commit in `~/spasynth` (via `.git/logs/HEAD`) plus daily at 11:00 as a
  backstop. Running on every product commit is fine — with the version unmoved
  it exits in milliseconds. Log: `~/Library/Logs/spasynth-release-prepare.log`.
- Version of record is `project(SPASynth VERSION x.y.z)` in
  `~/spasynth/CMakeLists.txt`; notes come from `~/spasynth/docs/CHANGELOG.md`.
  They must agree, or it refuses and says so rather than publish a version with
  no release notes.
- It reads **committed** state only, so a half-written changelog is invisible to
  it. Save as much as you like; only a commit in the product repo counts.
- It bails instead of guessing if the old version string stops appearing in
  exactly five places outside the generated block — i.e. if someone restructures
  the page. Reverts cleanly and commits nothing.
- **A prepared release that is superseded before it is pushed gets replaced, not
  stacked behind.** If the version moves again while an earlier prep sits
  unpushed, the script drops its own obsolete commit and prepares the current
  version instead, so the pending commit always reflects the newest release and
  its message measures from what is actually published. Recognised by the exact
  subject `Changelog and version: vX.Y.Z` *and* touching `index.html` alone;
  anything else counts as a human's work and still stops the run cold. Discarded
  hashes are logged and remain in the reflog.
  (Added 2026-09-19: without it the site sat three versions behind, because
  1.0.20 was prepared but never pushed and 1.0.21 queued silently behind it.)
- Run it by hand any time: `python3 scripts/prepare-release.py [--dry-run]`.
  `--force` overrides the up-to-date and don't-roll-backwards checks.
- To publish what it prepared: `git -C ~/spasynth-landing push origin main`.

`scripts/build-changelog.py` still exists and does the accordion on its own;
prepare-release.py calls it rather than duplicating it.

**A pending release still pauses the Vault job, so push promptly.** The site
falling behind is not the only cost of leaving one unpushed: the sound-count
refresh stands down for as long as it sits there.

**Both cron jobs refuse to run on unpushed commits they did not write.** The Vault refresh pushes
`main`, so before 2026-09-18 it would have published any unpushed local commit
as a side effect of a sound-count update — including a release being held back
on purpose. Both scripts now stand down when the repo is ahead of origin. If a
job logs `SKIP: N unpushed commit(s)`, something is waiting for a human; look
before you clear it.

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

- A one-off `7403 Unauthorized` from wrangler is **not** a broken credential.
  It happens when an expired OAuth access token has just been refreshed and the
  new one has not propagated to the D1 API yet. Re-running works, and the
  auto-refresh script retries for exactly this reason. Only a persistent 7403
  across retries means a real re-login is needed.
- The design is the flat7.design SPASynth case-study grammar (scroll-craft
  engine in `js/scrollcraft.js` + `css/scrollcraft.css`). **Never edit the
  engine files**; bespoke behaviour is driven from `--sc-p` in page CSS/JS.
- The 3D hero/teardown renders model the pre-1.0.11 faceplate. They read as a
  stylized study model rather than a screenshot, so they were left as-is.
- `scripts/.vault-poll-state.json` is gitignored local-only cadence state.
  Deleting it just restarts the clock at daily.
- **Audio will not decode in the Claude-in-Chrome tab.** Media loading is
  throttled there, so `loadedmetadata` times out even for tracks that have been
  live for days. Verify audio with `ffprobe` plus an HTTP fetch, or on the real
  site; a timeout in that tab proves nothing.
