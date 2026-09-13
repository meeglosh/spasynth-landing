#!/usr/bin/env python3
"""Sync the landing page's library numbers from the SPAStation catalog.

Source of truth: ~/spastation/shared/catalog-releases.json (or $SPASTATION_CATALOG,
or a path/URL passed as argv[1]). A "pack" is every entry with status
"verified" that is not a bundle (no includedLibraryIds / archiveIncludes) and is
not a source archive whose contents are catalogued as their own packs.

  packs   = number of such entries
  sounds  = sum of each pack's `fileCount` (WAV count) once the catalog carries
            it. Until every pack has one, the total falls back to
            scripts/library-stats.json -> soundTotalFallback and the script
            warns which packs are missing a count, so the page never claims a
            number nobody has verified.
  starter = 5 * packs (Standard's starter library: five sounds from every pack)

Rewrites every <span data-stat="..."> in index.html plus the three description
<meta> tags. Run after every pack release; safe to run repeatedly.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PAGE = os.path.join(ROOT, 'index.html')
LOCAL = os.path.join(ROOT, 'scripts', 'library-stats.json')
DEFAULT_CATALOG = os.path.expanduser('~/spastation/shared/catalog-releases.json')

def load_catalog(src):
    if re.match(r'^https?://', src):
        with urllib.request.urlopen(src, timeout=30) as r: return json.load(r)
    with open(src, encoding='utf-8') as f: return json.load(f)

def is_pack(v, sources):
    """A sellable single pack: verified, not a bundle, and not an archive that
    only exists to carry other listed packs (e.g. glitch-bundle.zip, whose
    contents are catalogued as their own packs via sourceCatalogId)."""
    return (v.get('status') == 'verified'
            and not (v.get('includedLibraryIds') or v.get('archiveIncludes'))
            and v['id'] not in sources)

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('SPASTATION_CATALOG', DEFAULT_CATALOG)
    catalog = load_catalog(src)
    local = json.load(open(LOCAL)) if os.path.exists(LOCAL) else {}
    sources = {v.get('sourceCatalogId') for v in catalog.values() if v.get('sourceCatalogId')}
    packs = [v for v in catalog.values() if is_pack(v, sources)]
    counts = {v['id']: v.get('fileCount') for v in packs}
    missing = sorted(i for i, c in counts.items() if not isinstance(c, int))
    if missing:
        sounds = int(local.get('soundTotalFallback', 0))
        print(f'warning: {len(missing)} of {len(packs)} packs have no fileCount in the catalog; '
              f'using soundTotalFallback={sounds:,} from scripts/library-stats.json', file=sys.stderr)
        print('  missing:', ', '.join(missing), file=sys.stderr)
    else:
        sounds = sum(counts.values())
    n_packs, starter = len(packs), 5 * len(packs)
    fmt = lambda n: f'{n:,}'

    page = open(PAGE, encoding='utf-8').read()
    vals = {'packs': fmt(n_packs), 'sounds': fmt(sounds), 'starter': fmt(starter)}
    def sub(m): return f'<span data-stat="{m.group(1)}">{vals[m.group(1)]}</span>'
    page, n = re.subn(r'<span data-stat="(packs|sounds|starter)">[^<]*</span>', sub, page)

    desc = (f'SPASynth is a hybrid synthesizer built around the entire Silverplatter Audio sound-effects library '
            f'({vals["packs"]} packs, up to {vals["sounds"]} sounds), playable as oscillators, granular fuel, '
            f'modulation sources, and convolution impulses. No DRM, ever.')
    social = (f'A hybrid synthesizer built around the entire Silverplatter Audio sound-effects library, up to '
              f'{vals["sounds"]} sounds playable as oscillators, granular fuel, modulation sources, and convolution '
              f'impulses. No DRM, ever.')
    page = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), page)
    page = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+social+m.group(2), page)
    page = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1)+social+m.group(2), page)
    open(PAGE, 'w', encoding='utf-8').write(page)

    local.update({'packs': n_packs, 'sounds': sounds, 'starter': starter, 'soundsVerified': not missing, 'catalog': src})
    json.dump(local, open(LOCAL, 'w'), indent=2); open(LOCAL, 'a').write('\n')
    print(f'library stats: {n_packs} packs, {fmt(sounds)} sounds{" (fallback)" if missing else ""}, '
          f'{starter}-sound starter; {n} spans + 3 metas rewritten')

if __name__ == '__main__':
    main()
