#!/usr/bin/env python3
"""Package a checked Sphinx build without changing source, DNS, or Pages settings."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

SOURCE_COMMIT = 'aac9a7f88348df9e149447a2ad2916dbf8125d1e'
SOURCE_REPOSITORY = 'sonyyt/EdgeComputingBook'
PORTABLE_CSS = r'''
/* Static edition: use system characters instead of bundled icon fonts. */
.fa::before, .icon::before, .toctree-expand::before,
.rst-content .headerlink::before,
.rst-content .admonition-title::before {font-family: Arial, sans-serif !important;}
.icon-home::before, .fa-home::before {content: "\2302" !important;}
.fa-bars::before {content: "\2630" !important;}
.fa-github::before {content: "\2197" !important;}
.fa-arrow-circle-left::before {content: "\2190" !important;}
.fa-arrow-circle-right::before {content: "\2192" !important;}
.wy-menu-vertical li button.toctree-expand::before {content: "+" !important; font-family: Arial, sans-serif !important;}
.wy-menu-vertical li.current > a button.toctree-expand::before {content: "\2212" !important;}
.rst-content .headerlink::before {content: "\00b6" !important;}
.rst-content .admonition-title::before {content: "\2139" !important;}
'''
README = '''# EdgeComputingBook-HTML

Compiled static HTML edition of **Edge Computing Systems**, English v0.4.2.

## Read or publish

The complete 14 chapters, Appendices A-E (including selected solutions), 211 references,
156 numbered figures using 159 original images, tables, equations, styles, and search
index are included. `index.html` is at the repository root, not inside a ZIP or an
extra enclosing folder. No Python or Sphinx installation is required to serve these files.

For GitHub Pages, select **Settings > Pages > Deploy from a branch > main > /(root)**.
The `.nojekyll` file preserves underscore-prefixed asset directories.
Pages activation and custom-domain settings are separate; this upload changes neither.

A downloadable snapshot is at `downloads/EdgeComputingBook-HTML-v0.4.2.zip`.
Extract the whole archive together before opening `index.html`.
Mathematical typesetting uses the existing external MathJax script. Test interactive
search and CDN loading after serving the site over HTTP.

## Source and regeneration

Editable source: https://github.com/sonyyt/EdgeComputingBook
Source commit: `aac9a7f88348df9e149447a2ad2916dbf8125d1e`.

The workflow **Populate compiled textbook** rebuilds this exact source snapshot,
checks manuscript preservation, and stores generated files in this repository.
It does not edit the source repository or configure DNS/Pages. It can also be run
manually; it is not automatic synchronization with future source changes.

See `BUILD_REPORT.json` for the preservation checks and `FILES_SHA256.json` for
checksums of the published files. Bundled font binaries and build caches are omitted;
text and navigation use system fonts and ordinary Unicode characters.

## License and image credits

The MIT `LICENSE` initially selected by the repository owner is preserved unchanged.
The source repository's original GPL-3.0 license text is preserved separately in
`LICENSE-SOURCE`. Importing the book does not relicense the imported material under MIT.
Original third-party credits, licenses, and publication-permission caveats remain in
`references.html` and `publication.html`. Compilation is not rights clearance.
The separate laboratory companion archive is not part of this static edition.
'''

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('site', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    source, site, target = (p.resolve() for p in (args.source, args.site, args.target))
    actual_commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual_commit != SOURCE_COMMIT:
        raise SystemExit('Unexpected source commit; no files copied.')
    if not (target / '.git').is_dir() or site == target or source == target:
        raise SystemExit('Invalid source/build/target separation.')
    # Remove build-only files and font payloads before any copy or archive upload.
    for name in ('.doctrees', '_sources'):
        shutil.rmtree(site / name, ignore_errors=True)
    (site / '.buildinfo').unlink(missing_ok=True)
    for directory in sorted(site.rglob('fonts'), key=lambda p: len(p.parts), reverse=True):
        if directory.is_dir():
            shutil.rmtree(directory)
    for path in list(site.rglob('*')):
        if path.is_file() and path.suffix.lower() in {'.ttf', '.otf', '.woff', '.woff2', '.eot'}:
            path.unlink()
    for path in site.rglob('*.css'):
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'@font-face\s*\{[^}]*\}', '', text, flags=re.I | re.S)
        path.write_text(text, encoding='utf-8')
    css = site / '_static/book.css'
    css.write_text(css.read_text(encoding='utf-8') + PORTABLE_CSS, encoding='utf-8')
    (site / '.nojekyll').touch()
    if (site / 'CNAME').exists():
        raise SystemExit('Unexpected domain-binding file in build.')
    report_file = site / 'BUILD_REPORT.json'
    subprocess.run([
        'python', str(source / 'tools/check_site.py'), str(site), '--report', str(report_file)
    ], check=True, cwd=source)
    report = json.loads(report_file.read_text())
    manifest = json.loads((source / 'SOURCE_MANIFEST.json').read_text())
    for image in manifest['images']:
        path = site / '_images' / image['file']
        if not path.is_file() or digest(path) != image['sha256']:
            raise SystemExit('Compiled image is missing or differs: ' + image['file'])
    css_assets = 0
    for path in site.rglob('*.css'):
        for raw in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', path.read_text()):
            url = urlsplit(raw.strip())
            if url.scheme or url.netloc or not url.path:
                continue
            css_assets += 1
            if not (path.parent / unquote(url.path)).resolve().is_file():
                raise SystemExit('Missing CSS asset: ' + raw)
    chapters = len(list((site / 'chapters').glob('ch*.html')))
    appendices = len(list((site / 'appendices').glob('*.html')))
    if chapters != 14 or appendices != 5 or report['html_pages'] != 25:
        raise SystemExit('Incomplete book output.')
    report.update({
        'source_repository': SOURCE_REPOSITORY,
        'source_commit': SOURCE_COMMIT,
        'target_repository': 'sonyyt/EdgeComputingBook-HTML',
        'packaging_checks': {
            'compiled_image_sha256_checks': len(manifest['images']),
            'css_local_asset_checks': css_assets,
            'chapter_pages': chapters, 'appendix_pages': appendices,
            'font_binaries_bundled': 0, 'nojekyll_present': True, 'errors': []
        },
        'publication_scope': 'Generated files and ZIP only; no source-repository, domain, or Pages-setting changes.',
        'license_handling': 'Target LICENSE retained; original source license copied to LICENSE-SOURCE.',
        'browser_validation': 'This workflow checks content and local resources, not live browser search or external CDN availability.'
    })
    report_file.write_text(json.dumps(report, indent=2) + '\n')
    # Only generated website paths are copied. Existing Git metadata, workflows,
    # owner-selected LICENSE, and any CNAME are left untouched.
    copied = []
    for path in sorted(site.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(site)
        if relative.parts[0] in {'.git', '.github', 'tools'} or relative.name in {'LICENSE', 'CNAME'}:
            raise SystemExit('Unexpected protected path in build: ' + str(relative))
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        copied.append(relative.as_posix())
    (target / 'README.md').write_text(README, encoding='utf-8')
    shutil.copyfile(source / 'LICENSE', target / 'LICENSE-SOURCE')
    copied += ['README.md', 'LICENSE-SOURCE']
    if (target / 'LICENSE').is_file():
        copied.append('LICENSE')
    copied = sorted(set(copied))
    file_hashes = {name: digest(target / name) for name in copied}
    (target / 'FILES_SHA256.json').write_text(json.dumps(file_hashes, indent=2) + '\n')
    copied.append('FILES_SHA256.json')
    archive = target / 'downloads/EdgeComputingBook-HTML-v0.4.2.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for name in sorted(copied):
            output.write(target / name, arcname=name)
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None:
            raise SystemExit('ZIP integrity verification failed.')
    print(json.dumps({
        'status': 'ready_to_commit', 'site_files': len(copied),
        'html_pages': report['html_pages'], 'chapters': chapters,
        'appendices': appendices, 'images': len(manifest['images']),
        'zip_bytes': archive.stat().st_size, 'zip_sha256': digest(archive)
    }, indent=2))

if __name__ == '__main__':
    main()
