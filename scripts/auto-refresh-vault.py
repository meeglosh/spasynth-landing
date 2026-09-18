#!/usr/bin/env python3
"""Daily unattended refresh of the Vault sound count on spasynth.com.

Queries the live SPAStation D1 database for the Vault's current sound counts,
writes them to the shared stats file, regenerates the landing page's numbers,
and commits + pushes only if a published number actually changed.

Scheduled by ~/Library/LaunchAgents/com.spasynth.vault-refresh.plist (daily).

ADAPTIVE CADENCE (Mike, 2026-09-14): polls daily while the count is moving.
Once the bonus count has held steady for 90 days, the script self-throttles to
roughly monthly (it still wakes daily but returns early unless 30 days have
passed since the last real poll). Any change to the count resets it to daily.
State lives in scripts/.vault-poll-state.json (gitignored, local only); losing
it just restarts the clock at daily, which is a safe default.

SAFETY RAILS, because this pushes to a live site with nobody watching:
  - Skips entirely if the repo has staged changes or is behind origin, so it
    can never sweep up someone's work-in-progress or fight a human's push.
  - Stages only index.html and scripts/library-stats.json, never `git add -A`.
  - Publishes nothing if the query fails or returns a structurally bad result
    (no rows, or zero pack sounds, which would mean a broken read).
  - A falling count is NOT treated as an error: the 2026-09-14 cull was real.
    Only an unusable query result blocks publishing.

Run by hand any time: python3 scripts/auto-refresh-vault.py [--force] [--dry-run]
"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'scripts', '.vault-poll-state.json')
LOCAL_STATS = os.path.join(ROOT, 'scripts', 'library-stats.json')
SPASTATION = os.path.expanduser('~/spastation')
VAULT_STATS = os.path.join(SPASTATION, 'shared', 'vault-stats.json')
LOG = os.path.expanduser('~/Library/Logs/spasynth-vault-refresh.log')

STEADY_DAYS = 90     # unchanged this long -> back off from daily
BACKOFF_DAYS = 30    # ...to roughly monthly

SQL = ("SELECT source_kind,count(*) AS n,sum(size) AS bytes FROM vault_catalog "
       "WHERE run=(SELECT active_run FROM vault_sync_state WHERE id=1) GROUP BY source_kind")

ENV = {**os.environ, 'PATH': '/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'}


def log(msg):
    line = f'{datetime.now(timezone.utc).isoformat(timespec="seconds")}  {msg}'
    # Only echo when a human is watching. Under launchd there is no TTY and its
    # StandardOutPath points at this same file, which would double every line.
    if sys.stdout.isatty():
        print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


def run(cmd, cwd=ROOT, check=True):
    return subprocess.run(cmd, cwd=cwd, env=ENV, check=check,
                          capture_output=True, text=True, timeout=300)


def wrangler_error(proc_output):
    """Pull the human-readable message out of wrangler's JSON error envelope."""
    blob = proc_output or ''
    m = re.search(r'\{.*\}', blob, re.S)
    if m:
        try:
            err = json.loads(m.group(0)).get('error', {})
            text = err.get('text') or err.get('name') or ''
            notes = ' '.join(n.get('text', '') for n in err.get('notes', []) if isinstance(n, dict))
            joined = ' '.join(x for x in (text, notes) if x).strip()
            if joined:
                return joined
        except ValueError:
            pass
    lines = [ln for ln in blob.strip().splitlines() if ln.strip() not in ('{', '}', '')]
    return lines[-1].strip() if lines else 'no error detail'


def load_state():
    try:
        return json.load(open(STATE, encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def save_state(state):
    json.dump(state, open(STATE, 'w', encoding='utf-8'), indent=2)
    open(STATE, 'a', encoding='utf-8').write('\n')


def days_since(iso):
    if not iso:
        return None
    try:
        then = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - then).total_seconds() / 86400


def query_vault(attempts=3, backoff=8):
    """Ask the live D1 database for the active run's sound counts.

    Retries on failure. When the OAuth access token has expired, wrangler
    refreshes it and then the very next API call can still come back 7403
    because the new token has not propagated yet; the retry rides that out.
    This is what broke the first scheduled run (2026-09-15 10:00 local).
    """
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return _query_once()
        except subprocess.CalledProcessError as e:
            last = e
            detail = wrangler_error(e.stdout or e.stderr)
            if attempt < attempts:
                log(f'query attempt {attempt}/{attempts} failed ({detail}); retrying in {backoff}s')
                time.sleep(backoff)
            else:
                log(f'query failed after {attempts} attempts: {detail}')
    raise last


def _query_once():
    out = run(['npx', 'wrangler', 'd1', 'execute', 'spastation-staging', '--remote',
               '--command', SQL, '--json', '--config', 'server/cloudflare/wrangler.jsonc'],
              cwd=SPASTATION)
    # wrangler prints a banner before the JSON payload; take the first JSON array.
    m = re.search(r'^\[', out.stdout, re.M)
    if not m:
        raise ValueError('no JSON in wrangler output')
    rows = json.loads(out.stdout[m.start():])[0]['results']
    by = {r['source_kind']: r for r in rows}
    pack = int(by.get('pack', {}).get('n') or 0)
    bonus = int(by.get('bonus', {}).get('n') or 0)
    if not rows or pack <= 0:
        raise ValueError(f'implausible result (pack={pack}, rows={len(rows)})')
    return {
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        'packSounds': pack,
        'bonusSounds': bonus,
        'bonusBytes': int(by.get('bonus', {}).get('bytes') or 0),
        'totalSounds': pack + bonus,
        'note': ('Active Vault run only: names failing the descriptive-name policy are never '
                 'indexed, so these are downloadable counts. packSounds mirrors the catalog packs '
                 'and is NOT added to the pack total by the landing site; bonusSounds is.'),
    }


def repo_is_safe():
    """Never run over staged work, a dirty page, or a repo that is behind origin."""
    if run(['git', 'diff', '--cached', '--name-only']).stdout.strip():
        log('SKIP: changes are already staged in the repo; leaving them alone.')
        return False
    dirty = run(['git', 'diff', '--name-only']).stdout.split()
    stray = [f for f in dirty if f not in ('index.html', 'scripts/library-stats.json')]
    if stray:
        log(f'SKIP: unexpected local modifications ({", ".join(stray)}); not touching this tree.')
        return False
    try:
        run(['git', 'fetch', '--quiet', 'origin', 'main'])
    except subprocess.CalledProcessError as e:
        log(f'SKIP: git fetch failed: {e.stderr.strip()}')
        return False
    behind = run(['git', 'rev-list', '--count', 'HEAD..origin/main']).stdout.strip()
    if behind != '0':
        log(f'SKIP: local main is {behind} commit(s) behind origin; a human should reconcile first.')
        return False
    # An unpushed commit is somebody's held-back work -- most often a release
    # prepared by scripts/prepare-release.py and deliberately NOT published yet.
    # This job pushes main, so committing on top would publish that too, under a
    # message about sound counts. Stand down until a human has dealt with it.
    ahead = run(['git', 'rev-list', '--count', 'origin/main..HEAD']).stdout.strip()
    if ahead != '0':
        log(f'SKIP: {ahead} unpushed commit(s) on main; pushing now would publish '
            f'them too. Leaving them for a human.')
        return False
    return True


def main():
    force = '--force' in sys.argv
    dry = '--dry-run' in sys.argv
    state = load_state()
    prev_bonus = state.get('bonusSounds')
    if prev_bonus is None:
        try:
            prev_bonus = json.load(open(LOCAL_STATS, encoding='utf-8')).get('vaultBonusSounds')
        except (OSError, ValueError):
            prev_bonus = None

    # Adaptive cadence: back off to monthly once the count has been steady a while.
    steady = days_since(state.get('lastChangedAt'))
    since_poll = days_since(state.get('lastPolledAt'))
    if not force and steady is not None and since_poll is not None:
        if steady >= STEADY_DAYS and since_poll < BACKOFF_DAYS:
            log(f'throttled: count steady {steady:.0f}d, last polled {since_poll:.1f}d ago '
                f'(monthly cadence; next poll in {BACKOFF_DAYS - since_poll:.1f}d)')
            return 0

    if not (dry or repo_is_safe()):
        return 0

    try:
        stats = query_vault()
    except subprocess.CalledProcessError as e:
        log(f'ERROR: Vault query failed: {wrangler_error(e.stdout or e.stderr)}')
        log('       A lone 7403 here is usually a just-refreshed token that has not')
        log('       propagated yet; the retries cover it. Persistent 7403 means re-login.')
        return 1
    except Exception as e:  # noqa: BLE001 - want any parse/shape failure logged, not published
        log(f'ERROR: Vault query unusable: {e}')
        return 1

    bonus = stats['bonusSounds']
    changed = prev_bonus is None or bonus != prev_bonus
    log(f'polled: {bonus} bonus sounds (was {prev_bonus}), {stats["packSounds"]} pack sounds')

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    state['lastPolledAt'] = now
    state['bonusSounds'] = bonus
    if changed or not state.get('lastChangedAt'):
        state['lastChangedAt'] = now

    if dry:
        log('dry run: not writing files or committing')
        return 0

    if not changed:
        log('unchanged; nothing to publish')
        save_state(state)
        return 0

    json.dump(stats, open(VAULT_STATS, 'w', encoding='utf-8'), indent=2)
    open(VAULT_STATS, 'a', encoding='utf-8').write('\n')
    out = run(['python3', 'scripts/update-library-stats.py'])
    log(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else 'stats script produced no output')

    touched = run(['git', 'diff', '--name-only', '--', 'index.html', 'scripts/library-stats.json']).stdout.split()
    if not touched:
        log('published numbers did not move; no commit needed')
        save_state(state)
        return 0

    run(['git', 'add', '--', 'index.html', 'scripts/library-stats.json'])
    msg = (f'Auto-refresh Vault sound count: {bonus} bonus sounds\n\n'
           f'Polled the live SPAStation Vault; bonus recordings moved '
           f'{prev_bonus} -> {bonus}. Regenerated the landing page numbers.\n\n'
           f'Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n'
           f'Claude-Session: https://claude.ai/code/session_01BGBUbwrpKLsmEhbEceEQjR')
    run(['git', 'commit', '-m', msg])
    try:
        run(['git', 'push', 'origin', 'main'])
        log(f'committed and pushed ({prev_bonus} -> {bonus})')
    except subprocess.CalledProcessError as e:
        log(f'WARNING: committed locally but push failed: {(e.stderr or "").strip()}')
    save_state(state)
    return 0


if __name__ == '__main__':
    sys.exit(main())
