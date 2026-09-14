#!/usr/bin/env python3
"""Sync the landing page's library numbers from the SPAStation catalog.

Source of truth: ~/spastation/shared/catalog-releases.json (or $SPASTATION_CATALOG,
or a path/URL passed as argv[1]). Inclusion rule (Mike, 2026-09-13): count only
what is commercially available right now on the Silverplatter Audio store,
i.e. what the SPAStation catalog lists; legacy packs that are no longer sold
(e.g. Wood Impacts) are not counted even if older builds shipped them.
A "pack" is every entry with status "verified" that is not a bundle (no includedLibraryIds / archiveIncludes) and is
not a source archive whose contents are catalogued as their own packs.

  packs   = number of such entries
  sounds  = sum of each pack's `fileCount` (WAV count) PLUS the Vault's bonus
            recordings from ~/spastation/shared/vault-stats.json (written by
            `node scripts/vault-stats.mjs` there). Both ship to Pro / Everything
            Bundle owners, and Pro is the only edition that gets the full
            library, so "up to N sounds" is everything SPASynth can play. If any
            pack lacks fileCount the pack part falls back to
            scripts/library-stats.json -> soundTotalFallback with a warning.
  size    = catalog zip bytes + Vault bonus bytes, rounded to whole GB
  starter = 5 * packs (Standard's starter library: five sounds from every pack)
  presets = 3 * packs (factory presets: one each of Keys/Texture/Pulse per pack,
            confirmed in source/library/PresetManager.h)

Rewrites every <span data-stat="..."> in index.html plus the three description
<meta> tags. Run after every pack release; safe to run repeatedly.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PAGE = os.path.join(ROOT, 'index.html')
LOCAL = os.path.join(ROOT, 'scripts', 'library-stats.json')
DEFAULT_CATALOG = os.path.expanduser('~/spastation/shared/catalog-releases.json')
DEFAULT_VAULT = os.path.expanduser('~/spastation/shared/vault-stats.json')

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
    pack_sounds = sounds
    vault_src = os.environ.get('SPASTATION_VAULT_STATS', DEFAULT_VAULT)
    vault = load_catalog(vault_src) if (re.match(r'^https?://', vault_src) or os.path.exists(vault_src)) else {}
    bonus = int(vault.get('bonusSounds') or 0)
    if not bonus:
        print(f'warning: no Vault bonus count at {vault_src}; run `node scripts/vault-stats.mjs` in spastation. '
              'Sound total covers packs only.', file=sys.stderr)
    sounds += bonus
    size_bytes = sum(int(v.get('size') or 0) for v in packs) + int(vault.get('bonusBytes') or 0)
    size_gb = round(size_bytes / 1e9)
    n_packs, starter, presets = len(packs), 5 * len(packs), 3 * len(packs)
    fmt = lambda n: f'{n:,}'

    page = open(PAGE, encoding='utf-8').read()
    vals = {'packs': fmt(n_packs), 'sounds': fmt(sounds), 'starter': fmt(starter), 'size': f'{size_gb} GB', 'presets': fmt(presets)}
    def sub(m): return f'<span data-stat="{m.group(1)}">{vals[m.group(1)]}</span>'
    page, n = re.subn(r'<span data-stat="(packs|sounds|starter|size|presets)">[^<]*</span>', sub, page)

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

    local.update({'packs': n_packs, 'packSounds': pack_sounds, 'vaultBonusSounds': bonus, 'sounds': sounds, 'sizeGB': size_gb,
                  'starter': starter, 'presets': presets, 'soundsVerified': not missing and bool(bonus), 'catalog': src,
                  'vaultStats': vault_src, 'vaultCheckedAt': vault.get('checkedAt')})
    json.dump(local, open(LOCAL, 'w'), indent=2); open(LOCAL, 'a').write('\n')
    print(f'library stats: {n_packs} packs, {fmt(pack_sounds)} pack sounds{" (fallback)" if missing else ""} + {fmt(bonus)} Vault bonus '
          f'= up to {fmt(sounds)} sounds, {size_gb} GB, {starter}-sound starter, {presets} factory presets; {n} spans + 3 metas rewritten')

if __name__ == '__main__':
    main()
