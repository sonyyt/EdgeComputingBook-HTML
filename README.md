# EdgeComputingBook-HTML

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
