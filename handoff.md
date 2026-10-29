# SPASynth landing page handoff

Current-state snapshot for picking the work back up. `PROGRESS.md` is the long
chronological log (DNS history, design decisions, every past session); this file
is just what is true right now and what to do next.

- Repo `github.com/meeglosh/spasynth-landing`, branch `main`, local
  `~/spasynth-landing`. Static one-page site, no build step, GitHub Pages behind
  Cloudflare at **spasynth.com**.
- As of 2026-10-27 `main` is clean and fully pushed (head: the video-demos
  commit `4957757` plus this handoff update); the live site matches it.
- The Vault refill is visibly progressing: bonus recordings went
  7,632 -> 25 -> 98 -> 199 -> 509 -> 733 -> 826 (published 2026-10-23,
  unchanged at the 2026-10-26 poll). Expect this
  number to keep climbing toward roughly 2,000; the job publishes each move on
  its own.

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

## Pricing and editions (current as of 2026-10-14)

Pro and the "Standard to Pro upgrade" are gone. "SPASynth Standard" was renamed
to just **SPASynth** (2026-10-13); do not reintroduce "Standard" in copy.
Editions shows two cards, both with "Intro price" badges and no end date:

- **SPASynth**: intro $99, regular $149, 450-sound 24/48 starter library.
  A **single purchase**, not seat-based: buy as many copies as needed, each
  with its own serial. Note under the card: "Buy 3 or more of our apps and save
  20%." (the 20% applies across Silverplatter apps, not just SPASynth).
- **Everything Bundle**: intro $499, regular $699; SPASynth plus the full
  library and free updates for life. **The only seat-based product**: first
  seat full price, each extra seat half, 1 to 10 seats online, contact us above
  10. Card note: two seats are $748.50 intro / $1,048.50 regular.

Every seat and every copy gets its own serial; each serial activates up to 3
computers. **Upgrade:** pay the bundle price for the same number of seats as
SPASynth copies owned, minus what was paid for SPASynth, via a personal upgrade
code. The "Seats and upgrades" box below the cards and three FAQ entries
(SPASynth vs bundle, upgrading, "Can I buy more than one copy or seat?") all
state these rules; keep them in sync if pricing changes again. Both buy
buttons still say "Coming soon". Also fixed in that pass: 21 mod sources, eight
engines.

## SEO / AEO (audited 2026-10-17)

Audited against AgriciDaniel/claude-seo (the top-starred SEO/GEO skills repo,
~19k stars; read only, its scripts were never run) and shipped in `92b5cd9`:

- **Title** "SPASynth: Sound-Effects Synth Plugin (VST3, AU) | Silverplatter
  Audio" (also og/twitter titles). Hero eyebrow is now "Hybrid synth plugin by
  Silverplatter Audio". Mike approved title/meta/eyebrow changes but **not** the
  H1; leave "Your sound library is the synth." alone.
- **Meta descriptions** are still generated: the wording lives in the `desc` /
  `social` templates in `scripts/update-library-stats.py`. Edit there, never in
  the page.
- **Head**: canonical `https://spasynth.com/`, robots meta
  (`max-image-preview:large`), og:site_name, og:image width/height/alt.
- **JSON-LD** `@graph` in the head: Organization (Silverplatter Audio), WebSite,
  SoftwareApplication. Deliberately has **no offers** (Mike: no prices until
  it's purchasable), **no counts** (would go stale; the stats script doesn't
  touch it) and **no version string** (`prepare-release.py` demands the version
  in exactly five places outside the changelog block; a sixth makes it refuse).
  No FAQPage: Google retired FAQ rich results 2026-05-07, and the FAQ is already
  plain server-rendered HTML that AI crawlers read.
- **New files**: `robots.txt` (allow all + Sitemap line; Mike chose to allow
  every AI bot, training included), `sitemap.xml` (single URL; bump `lastmod`
  on meaningful content changes), `llms.txt` (no live numbers by design; Google
  ignores it, other AI tools may not), `404.html` (noindex, branded).
- Already fine, no change needed: all content is in raw HTML (no JS
  dependency), clean H1/H2/H3, images have alt and dimensions, AI *search*
  bots (OAI-SearchBot, Claude-SearchBot, PerplexityBot) were already allowed.

**Cloudflare currently prepends its managed block to our robots.txt.** The live
file is Cloudflare's rules (Disallow for Google-Extended, GPTBot, ClaudeBot,
CCBot, Applebot-Extended, etc.) followed by ours; the bot-specific Disallows win.
Verify with `curl -s https://spasynth.com/robots.txt | head`; it is fixed when
"BEGIN Cloudflare Managed content" is gone.

## What the page says right now

Everything below is generated, not typed. Do not hand-edit these numbers in
`index.html`; they live in `<span data-stat>` tags and the three description
`<meta>` tags, and the next script run will overwrite anything typed by hand.

| Stat | Value | Where it comes from |
|---|---|---|
| Packs | 90 | SPAStation catalog, verified non-bundle entries |
| Sounds ("up to") | 12,305 | 11,479 pack sounds + 826 Vault bonus |
| Library size | 87 GB | catalog zip bytes + Vault bonus bytes |
| Starter library | 450 | 5 x packs |
| Factory presets | 370 | 3 x packs (Keys/Texture/Pulse per pack) + 100 synth bank |
| Version | v1.0.36 | automated, see "Shipping a new SPASynth version" |

The sounds/size rows move on their own (the Vault refresh job) and the version
row now does too, so treat all three as snapshots — `scripts/library-stats.json`
and the page itself are the truth.

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

Seven tracks, in this order: SPA, Dark, The Onus is on You, City of Cones,
Barnicle, Homebound, Breath. All are Ruger Seeds except Dark, which is add.remove and
sits second at Mike's request (2026-09-17). Breath is by Philharmonic (added
2026-10-28 from a 24-bit/48 kHz WAV master, converted with the command below). More are expected; a new track
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
- **The tracks play through one playlist player** (since 2026-10-28, when the
  list reached seven): a deck with previous / play / next, a seek bar and the
  current title, over a numbered track list. Each track is one `<li
  class="audio-track">` in `index.html`: a `.track-play` link to the MP3 (it
  covers the whole row; without JavaScript it simply opens the file), the
  title `<h3>`, the artist `<p class="track-artist">` and a `.track-time`
  length (m:ss, from `ffprobe`). Copy an existing row for a new track. Playback
  runs straight down the list and stops back on track 1 after the last.
- **Every track carries an artist byline** in `<p class="track-artist">`, under
  the title, and names the artist in the link's `aria-label` ("Play <title> by
  <artist>, made entirely with SPASynth"). Ruger Seeds, add.remove and
  Philharmonic are the artists so far.
- **Also add the track to the `MusicPlaylist` node in the JSON-LD** at the top of
  `index.html` (name, artist, ISO duration, MP3 URL) and bump its `numTracks`.
- The "N tracks made entirely with SPASynth" sentence counts the playlist rows in
  `js/page.js`, so it updates itself. Set the static `data-track-count`
  fallback to match for the pre-JS and no-JS cases. Never hardcode the number
  anywhere else.
- The playlist and the videos share "one sound at a time"; also in `js/page.js`.
- **Bump the `?v=` on `css/styles.css` in `index.html` whenever the stylesheet
  changes**, and do the same for any JS file you edit. Cloudflare caches CSS and
  JS for four hours (`max-age=14400`, `cf-cache-status: HIT`) while the HTML is
  not edge-cached at all (`DYNAMIC`, `max-age=600`). Without the bump, visitors
  get new markup against a stale stylesheet for up to four hours — which is
  exactly what happened when the artist bylines shipped on 2026-09-17. Check a
  deploy with `curl -sI https://spasynth.com/css/styles.css | grep -i age`.

## Video demos ("See it play", added 2026-10-27)

Two screen recordings sit in their own section just before the listening
room, Haunted Forest first and Sample Pool second (swapped at Mike's request
2026-10-28), click to play with sound (one player at a time, shared with the audio
tracks in `js/page.js`):

- **Sample Pool: a new laugh on every note** (preset SFX Crowd Laughter). All
  three oscillators are in Sample Pool mode, Random, holding 4 + 5 + 4 = 13
  laughter takes. Mike wanted this one clearly labelled as the Sample Pool
  demo; keep that framing.
- **Haunted Forest** (preset SC Haunted Forest): three Sample oscillators
  layering air ambience, crickets and a tonal drone.

Mike's `.mov` masters stay in `assets/videos/` but are gitignored. The page uses
web encodes made from them (1080p30 H.264, CRF 24, AAC 192k, faststart, about
3.5 MB each) plus poster JPGs from mid-video, since both recordings open on
black:
`ffmpeg -i in.mov -map 0:v:0 -map 0:a:0 -vf "fps=30,scale=1920:-2" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -map_metadata -1 out.mp4`

The same two videos (same posters as covers, alt text starting "Sample Pool
demo:" / "Soundscape demo:") are on the draft SPASynth Shopify product,
after the five images. Shopify's gallery shows no captions, so alt text is the
only label there. Mike was offered a visible "Watch it play" block in the
product description and has not asked for it; don't add it unprompted.

## The SPASynth Shopify listing (draft)

SPASynth **does** have a Shopify product now, as a **Draft**:
`https://admin.shopify.com/store/silverplatter-audio/products/10425859899671`
(Mike's admin, reached through Claude in Chrome). Drafts are not in the public
`products.json`, which is why `prepare-release.py` still sees "no listing" and
keeps auto-publishing. **Setting this product to Active is the launch trigger**
that switches release auto-publishing off (see the next section).

- Price $99, compare-at $149, theme template `spasynth`, collections "Apps (3+
  discount)" and "Software". Media: five promo images plus the two demo videos.
- **The `spasynth` theme template, not the product description, drives the
  page.** `templates/product.spasynth.json` (live theme "Updated copy of
  Streamline", #170150887703) has the description block and full-width
  description section *disabled*; all copy is hardcoded in its sections.
  Anything meant to appear on the page goes in the template. Edit with the
  Shopify CLI (already logged in): `shopify theme pull --store
  silverplatter-audio.myshopify.com --theme 170150887703 --only
  templates/product.spasynth.json`, edit, then `shopify theme push ... --only
  <same> --allow-live --nodelete`. Check a draft in the theme customizer
  (`/themes/<id>/editor?previewPath=/products/spasynth`); `?view=spasynth` on
  any live product renders the template for a quick curl check.
- 2026-10-27: added "See it play" (custom-liquid section looping the product's
  video media with the site's captions) after the intro text, and "Hear it:
  100% SPASynth" after "Inside the synth". MP3s live in Content -> Files, same
  names as `assets/audio/`.
- 2026-10-28: the per-track `spa-audio-preview` sections were replaced by one
  playlist in the `spasynth_listen` section (custom liquid, same accent
  #e8553d as the store's other players). A new track is one more `<li
  class="spa-pl__row">` in that section's code (copy a row; CDN URL, title,
  artist, m:ss length); the "Seven tracks" count is filled in by its script.
  The track rows start as links and the script swaps them for buttons, because
  the theme's own link handling otherwise opens the MP3 instead of playing it.
  Text in the rows uses `<span>`s, not `<p>`, to dodge the theme's paragraph
  margins. "See it play" shows Haunted Forest first regardless of the
  product's media order. The product description still carries seven plain
  players (harmless, not rendered).
  SEO title is now "SPASynth: Sound-Effects Synth Plugin (VST3, AU)" (theme
  appends " – Silverplatter Audio"), meta description mentions VST3/AU.
- 2026-10-27: the description's leftover "Standard is the complete
  synthesizer" became "SPASynth is …", and the placeholder "[UPGRADE OFFER FOR
  STANDARD OWNERS: …]" was replaced with the site's upgrade wording (pay the
  bundle price for the same number of seats, minus what you paid, personal
  upgrade code). Keep it in sync with the site's "Seats and upgrades" box if
  pricing changes.
- The description is a TinyMCE editor (`tinymce.get('product-description-ro')`).
  Exact-string replacements on `getContent()`, then `setContent()` plus
  `fire('change')`, register as unsaved changes; then click Save. Verify after
  a reload.
- **Uploading media through Claude in Chrome needs a workaround.** The real file
  input is inside a shadow DOM and the upload tool cannot target it, and
  fetching from localhost is blocked by Shopify's CSP. What worked: inject a
  temporary `<input type=file>` into the page, fill it with the upload tool, copy
  its `files` onto Shopify's input with a DataTransfer, and dispatch **one
  non-bubbling** `change` (a bubbling/composed one uploads everything twice).
  **Wait until every thumbnail has finished "Processing…" before clicking
  Save**, or the videos are silently dropped. Cover images upload through the
  media viewer's "Upload image" input, and doing so clears any unsaved alt
  text, so set the cover first, then the alt text, then Save.
- Deleting Shopify files is permanent, so Claude does not do it; Mike deletes
  them himself (Content -> Files, keep the copy with alt text and "1 product"
  under References). The stray uploads from 2026-10-27 are already deleted.

## Shipping a new SPASynth version

**This is fully automated while SPASynth is pre-launch.**
`scripts/prepare-release.py` notices when `~/spasynth` ships a version newer than
the site advertises, regenerates the changelog accordion, bumps the version
string in its five places (hero strip, demo caption alt text, demo figcaption,
specs note, footer), commits, pushes, and posts a macOS notification. Nobody
needs to be involved.

**It stops publishing by itself the day SPASynth goes on sale, and that is
deliberate.** The original worry was announcing a version before customers could
download it: the product changelog is written at *build* time (the 1.0.17 commit
says "built + staged"), potentially days before a release is out. But SPASynth is
not purchasable yet — the public Shopify catalogue has no SPASynth (the listing
exists only as a Draft, see above),
and the page's own edition buttons say "Coming soon" — so nobody can be out of
step with what the page claims, and publishing unattended costs nothing.

That changes at launch. Before each push the script reads Shopify's public
catalogue (`silverplatteraudio.com/products.json`, no auth needed) and looks for
a SPASynth listing:

- **No listing** → pre-launch → commits and pushes on its own.
- **Listing found** → commits, does *not* push, and notifies. The judgement of
  when the site should announce a version is a human's again.
- **Cannot get a trustworthy answer** (network down, or a suspiciously empty
  catalogue, which means a broken read rather than an empty shop) → also holds
  back. Every failure mode fails toward *not* publishing.

So launch day needs nobody to remember to re-tighten this; it re-tightens itself.
When that notification first appears, decide the real post-launch process and
write it down here. `--no-publish` forces hold-back whatever the storefront says.

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
- Run it by hand any time:
  `python3 scripts/prepare-release.py [--dry-run] [--force] [--no-publish]`.
  `--force` overrides the up-to-date and don't-roll-backwards checks;
  `--no-publish` commits but leaves the push to you, whatever the storefront
  says. Set `SPASYNTH_STOREFRONT_URL` to a fixture to exercise the post-launch
  path without waiting for launch day.
- To publish something it held back: `git -C ~/spasynth-landing push origin main`.

`scripts/build-changelog.py` still exists and does the accordion on its own;
prepare-release.py calls it rather than duplicating it.

**A held-back release pauses the Vault job, so clear one promptly.** The
sound-count refresh stands down while any unpushed commit sits on `main`. This
only arises post-launch, or when the storefront check fails, since a pre-launch
run leaves nothing pending.

**Both cron jobs refuse to run on unpushed commits they did not write.** The Vault refresh pushes
`main`, so before 2026-09-18 it would have published any unpushed local commit
as a side effect of a sound-count update — including a release being held back
on purpose. Both scripts now stand down when the repo is ahead of origin. If a
job logs `SKIP: N unpushed commit(s)`, something is waiting for a human; look
before you clear it.

## Decisions worth not relitigating

- **"Up to N sounds" = packs + Vault bonus.** Mike's call 2026-09-14: only
  Everything Bundle owners get the full library either way, so the ceiling
  is everything SPASynth can play. Vault bonus is added; the Vault's own pack
  mirror (11,493) is not, the catalog is authoritative for packs.
- **Count only what is currently sold.** The SPAStation catalog is the
  inclusion rule. Legacy packs no longer on Shopify (e.g. Wood Impacts, 101
  sounds, still in the old built library) are excluded.
- **A falling Vault count is not a bug.** Throwaway/generic recordings were
  culled 2026-09-14 and are being replaced with deliberate additions; expect it
  to climb back toward ~2,000 over time. It went 7,632 -> 25 -> 98. Do not
  "fix" a drop by pinning to an older figure; publish what the database says.
- **The Everything Bundle is 24/96, SPASynth's starter is 24/48**, delivered
  via Everything Bundle links in Shopify order emails or directly in SPAStation.
- No em dashes in visible copy.

## Open items

1. **Ask Mike:** does the existing "Will I get updates?" FAQ satisfy his older
   request for "a FAQ answer confirming updates are free"? Never answered.
2. **Shopify links.** The two edition buttons (SPASynth, Everything Bundle) are
   still `href="#"` placeholders labelled "Coming soon". Swap for real product URLs at
   launch and likely relabel to "Buy now". The SPASynth product exists as a Draft
   (see "The SPASynth Shopify listing"); its storefront URL is known once it is
   Active. **Activating it is also
   what switches release auto-publishing off** (see "Shipping a new SPASynth
   version"), so expect that notification around the same time and settle the
   post-launch release process then.
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
7. **SEO/AEO follow-ups (2026-10-17 audit).** (a) **Mike:** Cloudflare dashboard, Security -> Bots,
   turn off managed robots.txt / "Block AI bots" (see the SEO / AEO section). (b) **Mike:** `https://www.spasynth.com` fails TLS (curl
   verify error 10; `www` is DNS-only to GitHub Pages; `http://www` redirects
   fine). Proxy the `www` record or add a redirect rule to the apex. (c) **Mike:** submit `sitemap.xml` to Google Search Console and Bing
   Webmaster Tools (Bing feeds ChatGPT search and Copilot).
   (d) At launch, add `offers` (prices, Shopify URLs) to the SoftwareApplication
   JSON-LD in the head. Keep counts and the version string out of the JSON-LD:
   counts would go stale, and `prepare-release.py` requires the version in
   exactly five places. (e) Off-site entity signals matter most for AI
   answers: YouTube walkthrough, Reddit threads, KVR listing, links from
   silverplatteraudio.com. (f) Mobile hero not checked on a real phone.

8. **Video demos follow-ups (2026-10-27).** (a) No "Watch" link in the masthead
   nav (it already has eight); add one if Mike wants it. (b) Haunted Forest's
   audio is quiet (peaks about -18.5 dBFS against -8.5 for the laughter demo);
   left as recorded, mention it if Mike re-records. (c) Not yet played back on a
   real phone. (d) New demo videos: same encode, poster and labelling pattern
   as in "Video demos"; name what the video shows off (feature, preset).

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
