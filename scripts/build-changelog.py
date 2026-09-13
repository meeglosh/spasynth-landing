#!/usr/bin/env python3
"""Regenerate the Changelog accordion in index.html from the product changelog.

Reads ~/spasynth/docs/CHANGELOG.md (newest version first, as written) and
replaces everything between <!-- CHANGELOG:START --> and <!-- CHANGELOG:END -->
in index.html. Run it whenever a new SPASynth version ships.
"""
import html, os, re, sys

SRC = os.path.expanduser('~/spasynth/docs/CHANGELOG.md')
DST = os.path.join(os.path.dirname(__file__), '..', 'index.html')

def clean(text):
    text = re.sub(r'\s*--\s*', ', ', text)           # no em/double dashes in visible copy
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def parse(md):
    versions, cur = [], None
    for line in md.splitlines():
        m = re.match(r'^## (\S+)', line)
        if m:
            cur = {'v': m.group(1), 'blocks': []}
            versions.append(cur); continue
        if cur is None: continue
        cur['blocks'].append(line)
    return versions

def render_blocks(lines):
    out, para, items, item = [], [], [], None
    def flush_para():
        nonlocal para
        if para:
            text = ' '.join(s.strip() for s in para)
            if re.fullmatch(r'\*\*.+\*\*', text):
                out.append('<h4>%s</h4>' % clean(text.strip('*')))
            else:
                out.append('<p>%s</p>' % clean(text))
            para = []
    def flush_items():
        nonlocal items, item
        if item is not None: items.append(' '.join(item)); item = None
        if items:
            out.append('<ul>' + ''.join('<li>%s</li>' % clean(i) for i in items) + '</ul>')
            items = []
    for line in lines:
        if not line.strip():
            flush_para(); flush_items(); continue
        if line.startswith('- '):
            flush_para()
            if item is not None: items.append(' '.join(item))
            item = [line[2:].strip()]
        elif line.startswith('  ') and item is not None:
            item.append(line.strip())
        else:
            flush_items(); para.append(line)
    flush_para(); flush_items()
    return '\n'.join(out)

def main():
    md = open(SRC, encoding='utf-8').read()
    versions = parse(md)
    parts = []
    for i, v in enumerate(versions):
        # First paragraph is the release summary; surface it in the summary row.
        body = render_blocks(v['blocks'])
        parts.append(
            '<details class="log-item"%s>\n<summary><span class="log-version">v%s</span>%s</summary>\n<div class="log-body">\n%s\n</div>\n</details>'
            % ('', html.escape(v['v']),
               ' <span class="log-latest">Latest</span>' if i == 0 else '', body))
    fragment = '\n'.join(parts)
    page = open(DST, encoding='utf-8').read()
    start, end = '<!-- CHANGELOG:START -->', '<!-- CHANGELOG:END -->'
    a, b = page.index(start) + len(start), page.index(end)
    open(DST, 'w', encoding='utf-8').write(page[:a] + '\n' + fragment + '\n' + page[b:])
    print('changelog: %d versions written (%s .. %s)' % (len(versions), versions[0]['v'], versions[-1]['v']))

if __name__ == '__main__':
    main()
