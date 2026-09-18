#!/usr/bin/env python3
"""Prepare (but never publish) a new SPASynth version on spasynth.com.

Watches the product repo. When it ships a version newer than the one the
landing page advertises, this regenerates the changelog accordion, bumps the
hand-typed version strings, commits locally, and tells Mike. It does NOT push:
the changelog is written at BUILD time ("1.0.17 built + staged"), which can be
days before customers can download anything, and the site must not announce a
release that is not out yet. Mike pushes when the build is actually live.

Scheduled by ~/Library/LaunchAgents/com.spasynth.release-prepare.plist, which
fires on every commit in ~/spasynth plus once daily as a backstop. Running on
every product commit is fine: when the version has not moved this exits in
milliseconds without touching anything.

WHY IT READS COMMITTED STATE ONLY: a half-written changelog must never reach
the site. The script refuses to act while CHANGELOG.md or CMakeLists.txt have
uncommitted edits in the product repo, so a mid-edit save is invisible to it
and only a deliberate commit counts.

SAFETY RAILS, because this writes to the repo unattended:
  - Refuses if the landing repo has staged changes, unexpected dirty files, is
    behind origin, or already has unpushed commits.
  - Version and changelog must agree; a build whose notes are missing is an
    error, not something to publish silently.
  - The old version string must appear exactly VERSION_SPOTS times outside the
    generated changelog block. Anything else means the page moved around and a
    human should look, so it bails rather than guess.
  - Stages only index.html. Never `git add -A`. Never pushes.

Run by hand any time: python3 scripts/prepare-release.py [--dry-run] [--force]
"""
import json, os, re, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'index.html')
PRODUCT = os.path.expanduser('~/spasynth')
CMAKE = os.path.join(PRODUCT, 'CMakeLists.txt')
CHANGELOG = os.path.join(PRODUCT, 'docs', 'CHANGELOG.md')
LOG = os.path.expanduser('~/Library/Logs/spasynth-release-prepare.log')

START, END = '<!-- CHANGELOG:START -->', '<!-- CHANGELOG:END -->'
VERSION_SPOTS = 5  # hero strip, demo alt text, demo figcaption, specs note, footer

ENV = {**os.environ, 'PATH': '/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'}


def log(msg):
    line = f'{datetime.now(timezone.utc).isoformat(timespec="seconds")}  {msg}'
    # Only echo when a human is watching; under launchd StandardOutPath is this
    # same file and every line would be written twice.
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
                          capture_output=True, text=True)


def notify(title, message):
    """Best-effort macOS banner. Never let a failed notification fail the run."""
    try:
        subprocess.run(
            ['osascript', '-e',
             f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
            env=ENV, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        pass


def product_version():
    """The authoritative version: project(SPASynth VERSION X.Y.Z ...)."""
    text = open(CMAKE, encoding='utf-8').read()
    m = re.search(r'project\s*\(\s*SPASynth\s+VERSION\s+(\d+\.\d+\.\d+)', text)
    if not m:
        raise ValueError('no project(SPASynth VERSION ...) line in CMakeLists.txt')
    return m.group(1)


def changelog_top_version():
    """Newest version heading in the product changelog."""
    for line in open(CHANGELOG, encoding='utf-8'):
        m = re.match(r'^## (\d+\.\d+\.\d+)\s*$', line)
        if m:
            return m.group(1)
    raise ValueError('no version headings in CHANGELOG.md')


def site_version():
    """What the page currently advertises as the current release."""
    text = open(PAGE, encoding='utf-8').read()
    m = re.search(r'Current release: v(\d+\.\d+\.\d+)', text)
    if not m:
        raise ValueError('no "Current release: vX.Y.Z" in index.html')
    return m.group(1)


def as_tuple(v):
    return tuple(int(p) for p in v.split('.'))


def product_is_committed():
    """Refuse to read a changelog or version that is still being edited."""
    dirty = run(['git', 'status', '--porcelain', '--',
                 'docs/CHANGELOG.md', 'CMakeLists.txt'], cwd=PRODUCT).stdout.strip()
    if dirty:
        log('SKIP: the product repo has uncommitted changelog/version edits; '
            'waiting for a deliberate commit.')
        return False
    return True


def repo_is_safe():
    """Never run over work in progress, and never build on an unpushed commit."""
    if run(['git', 'diff', '--cached', '--name-only']).stdout.strip():
        log('SKIP: changes are already staged in the landing repo; leaving them alone.')
        return False
    dirty = [f for f in run(['git', 'diff', '--name-only']).stdout.split()
             if f != 'index.html']
    if dirty:
        log(f'SKIP: unexpected local modifications ({", ".join(dirty)}); not touching this tree.')
        return False
    try:
        run(['git', 'fetch', '--quiet', 'origin', 'main'])
    except subprocess.CalledProcessError as e:
        log(f'SKIP: git fetch failed: {(e.stderr or "").strip()}')
        return False
    behind = run(['git', 'rev-list', '--count', 'HEAD..origin/main']).stdout.strip()
    if behind != '0':
        log(f'SKIP: local main is {behind} commit(s) behind origin; a human should reconcile first.')
        return False
    ahead = run(['git', 'rev-list', '--count', 'origin/main..HEAD']).stdout.strip()
    if ahead != '0':
        log(f'SKIP: {ahead} unpushed commit(s) on main already — most likely a release '
            f'waiting to be pushed. Not stacking another on top.')
        return False
    return True


def bump_version_strings(old, new):
    """Swap the hand-typed version outside the generated changelog block.

    The accordion is regenerated from source, so its historical entries must
    keep saying 1.0.16 forever. Only the surrounding page copy moves.
    """
    text = open(PAGE, encoding='utf-8').read()
    a, b = text.index(START), text.index(END)
    head, body, tail = text[:a], text[a:b], text[b:]
    found = head.count(old) + tail.count(old)
    if found != VERSION_SPOTS:
        raise ValueError(
            f'expected v{old} in {VERSION_SPOTS} places outside the changelog block, '
            f'found {found}. The page layout changed; a human should look before '
            f'this script edits it again.')
    open(PAGE, 'w', encoding='utf-8').write(
        head.replace(old, new) + body + tail.replace(old, new))
    return found


def main():
    dry = '--dry-run' in sys.argv
    force = '--force' in sys.argv

    try:
        pv, cv, sv = product_version(), changelog_top_version(), site_version()
    except (OSError, ValueError) as e:
        log(f'ERROR: could not read versions: {e}')
        return 1

    if pv == sv and not force:
        log(f'up to date: product and site are both v{sv}')
        return 0

    if as_tuple(pv) < as_tuple(sv) and not force:
        log(f'SKIP: product v{pv} is older than the published v{sv}; refusing to '
            f'roll the site backwards. Use --force if this is deliberate.')
        return 0

    if cv != pv:
        log(f'ERROR: product is v{pv} but the newest changelog entry is v{cv}. '
            f'Publishing a version with no release notes would leave the accordion '
            f'wrong, so nothing was changed. Write the v{pv} notes first.')
        notify('SPASynth release not prepared',
               f'v{pv} has no changelog entry yet (newest is v{cv}).')
        return 1

    if not product_is_committed():
        return 0

    if not (dry or repo_is_safe()):
        return 0

    log(f'new version: site v{sv} -> product v{pv}')
    if dry:
        log('dry run: not writing files or committing')
        return 0

    try:
        out = run(['python3', 'scripts/build-changelog.py'])
        log(out.stdout.strip() or 'build-changelog.py produced no output')
        spots = bump_version_strings(sv, pv)
    except (subprocess.CalledProcessError, OSError, ValueError) as e:
        detail = (getattr(e, 'stderr', '') or str(e)).strip()
        log(f'ERROR: could not rewrite the page: {detail}')
        run(['git', 'checkout', '--', 'index.html'], check=False)
        log('       reverted index.html; nothing was committed.')
        notify('SPASynth release not prepared', f'v{pv} failed: {detail[:120]}')
        return 1

    if not run(['git', 'diff', '--name-only', '--', 'index.html']).stdout.strip():
        log('nothing actually changed in the page; no commit made')
        return 0

    items = len(re.findall(
        r'<li>', open(PAGE, encoding='utf-8').read().split(START, 1)[1].split('</details>', 1)[0]))

    run(['git', 'add', '--', 'index.html'])
    msg = (f'Changelog and version: v{pv}\n\n'
           f'Regenerated the changelog accordion from the product changelog and '
           f'moved the advertised release from v{sv} to v{pv} in {spots} places.\n\n'
           f'Prepared automatically; held back from origin so the site does not '
           f'announce v{pv} before the build is downloadable.\n\n'
           f'Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>')
    run(['git', 'commit', '-m', msg])
    log(f'PREPARED v{pv} ({items} changelog items, {spots} version spots) — '
        f'committed locally, NOT pushed.')
    log('       Review with: git -C ~/spasynth-landing show')
    log('       Publish with: git -C ~/spasynth-landing push origin main')
    notify(f'SPASynth v{pv} ready to publish',
           f'{items} changelog items staged on spasynth.com. '
           f'Review and push when the build is live.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
