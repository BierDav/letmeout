# letmeout

Typst layouts for HTML. Import the package and keep calling `grid`, `line`, and
`align`. Add `#show: letmeout` to also bring `page` settings and `pagebreak` to
HTML, and use `html-page` or `show-target` where HTML should differ from print. Text, math, links, and images remain ordinary HTML content; the browser
controls layout. PDF, PNG, and SVG use Typst's native elements.

```typ
#import "lib.typ": *

#let plot-img(path, height: 4cm) = image(path, height: height)
#let items = (
  [
    $rect(t) dot cos(t)$
    #image("image.png", height: 4cm)
  ],
)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 15pt,
  ..items.enumerate().map(((i, item)) => {
    let formatted-label = numbering("a)", i + 1)
    block(breakable: false)[#formatted-label #item]
  }),
)
#line(length: 100%, stroke: (paint: blue, dash: "dashed"))
#align(center)[Centered text]
```

Use your own `image.png`, or run the included examples:

```sh
typst compile --root . --features html docs/grid.typ docs/grid.html
typst compile --root . --features html docs/features.typ docs/features.html
typst compile --root . docs/features.typ docs/features.pdf
typst compile --root . --features html docs/page.typ docs/page.html
```

Requires Typst 0.15 or newer. This is a local package; it has not been published
on Typst Universe. No external stylesheet or JavaScript is required. `grid`,
`line`, and `align` need no setup; only page support needs `#show: letmeout`. Import with `: *` or explicitly import the functions you
use. Bindings follow Typst's lexical scopes: import in each file that calls the
functions, before defining helper functions that use them.

## HTML behavior

- `grid` uses CSS Grid for tracks, gutters, spans, explicit placement, and cell
  alignment. Per-column arrays and coordinate-based styling functions work.
  Empty cells receive grid styling too. Native grid subelements are supported.
- `line` uses an SVG stroke mask painted by CSS. Endpoints, length, angle, solid
  and gradient paint, thickness, caps, arbitrary dashes, and dash phase work.
  Percentage coordinates respond to the available container width.
- `align` uses CSS Grid alignment and text alignment. Logical `start`/`end` follow
  text direction; physical `left`/`right` stay fixed. Vertical alignment uses free
  space from an enclosing container, such as a grid row, rather than a PDF page.
- With `#show: letmeout`, page settings become one continuous block, not a sheet of paper. Its width sets the
  maximum width of a centred sheet. Margins become padding that shrinks on
  narrow screens. The header becomes a `<header>` before the content and the
  footer a `<footer>` after it. `fill` paints the full width behind the sheet.
  `background` and `foreground` are layers behind and above the content.
  Columns become CSS columns that collapse on narrow screens.
- With `#show: letmeout`, `pagebreak` adds nothing on screen, so the content continues without a gap.
  It becomes a page break when the HTML is printed.

### Pages

Put `#show: letmeout` at the top of the document, before anything else, then use
Typst's own page APIs: `#set page(...)`, `#page(...)[...]`, `#show: page.with(...)`,
and `#pagebreak()`. A page call or a `set page` that changes the settings starts
a new block. Other set rules do not start blocks, so inline styles stay in
their paragraph. Paged output is unchanged.

```typ
#import "lib.typ": *
#show: letmeout
#set document(title: "Report")
#set page(
  paper: "a5", numbering: "1 / 1",
  header: grid(columns: (1fr, auto), [Report], [2026]),
)
= Introduction
...
#pagebreak()
= Results
```

Typst still prints "page set rule was ignored" for each page setting in HTML
export. Packages cannot silence that warning; the settings are applied anyway.

HTML export ignores `h(1fr)`, so use `grid` to spread a header across the
width, as above.

### Different settings for HTML

A screen often needs different settings than paper, for example smaller
margins. `html-page` takes the same named arguments as `page` and applies them
only in HTML export:

```typ
#import "lib.typ": *
#show: letmeout
#set page(paper: "a4", margin: 2.5cm)
#show: html-page(margin: (x: 1em, y: 2em))
```

The PDF keeps 2.5cm margins; the HTML page uses `1em` at the sides and `2em`
at the top and bottom. `#show: html-page(...)` behaves exactly like a
`#set page(...)` that only HTML sees:

- It applies from that line to the end of the current scope.
- It changes only the settings it names. `margin: (x: 1em)` keeps the inherited
  top and bottom margins.
- A later `set page` or `page(...)[...]` still overrides it, also in HTML. Put
  `html-page` after the `set page` it should adjust, and repeat it after a later
  `set page` if needed.
- Like a redundant `set page`, an `html-page` that repeats the current settings
  fails with "page configuration is not allowed inside of containers". Remove it.

For anything else that should differ between targets, the package follows the
API of the [`bullseye`](https://typst.app/universe/package/bullseye) package:

```typ
// Content for one target; a missing target shows nothing.
#on-target(html: [Read the PDF version for print.], paged: [Printed 2026])

// A show rule for one target; a missing target leaves content unchanged.
#show: show-target(html: body => {
  set par(justify: false)
  show heading: set text(blue)
  body
})
```

`html-page` lists every parameter of `page`, with Typst's docs and what each
one does in HTML, in its doc comment in `src/target.typ`; editors show it on
hover. `grid`, `line`, and `align` carry the same kind of docs.

`html-page(margin: 1em)` is shorthand for
`show-target(html: body => { set page(margin: 1em); body })`.

Why not `#context if target() == "html" { ... }`? A set rule inside a context
block ends with that block, and `letmeout` cannot see page settings inside it.
`show-target` is built so that `#show: letmeout` can read the page settings in
its rules. Without `#show: letmeout`, both functions still work, but HTML page
settings have no effect, as in plain Typst.

## Native element APIs

Typst cannot copy an element function's associated definitions or set/show syntax
onto a wrapper function. Use the native names for those operations:

```typ
#import "lib.typ": *
#set std.grid(inset: 6pt)
#set std.line(stroke: 1pt + blue)
#set std.align(center)

#grid(columns: 2,
  std.grid.cell(colspan: 2)[Spanning cell],
  [Left], [Right],
)
```

For convenience, the package exports native aliases `grid-cell`, `grid-hline`,
`grid-vline`, `grid-header`, and `grid-footer`. They support `.with()` and native
set/show syntax. For example, `grid-cell(colspan: 2)[...]` works in both targets.

Existing uses of `grid.cell(...)`, `set grid(...)`, `set line(...)`, or
`set align(...)` need qualification with `std` after the import. Ordinary function
calls need only the import. This lexical limitation means the package cannot be
a completely transparent replacement for every use of the built-in element APIs.

For paged output, all original arguments and native styling are preserved. HTML
adapters are installed only in the HTML context, and check the target again at
nested boundaries such as `html.frame`. The regression suite compares PDF, PNG,
and SVG output against the native functions byte for byte.

## Development

The structure follows Solveng: `lib.typ` exports the public API, `src/` contains
implementation modules, `docs/` contains examples and design notes, and `tests/`
contains regression fixtures.

```sh
python3 tests/check.py
```

This checks the supplied image/math example, nesting, all functions,
inherited defaults, placement, styling, error handling, HTML frames, and native
paged equivalence. Generated files go in `tests/output/`. Open
`tests/output/features.html` in T3's browser and evaluate `tests/browser.js` for
browser assertions covering RTL, vertical alignment, resizing, and stroke removal.

`scripts/api-docs.py` writes the doc comments of `grid`, `line`, `align`, and
`html-page` from the latest Typst docs on typst.app. It copies Typst's summary,
parameters, types, and defaults, and adds the HTML notes from `scripts/api.toml`.
It stops if Typst adds or removes a parameter that `api.toml` doesn't cover yet,
so each new parameter gets a decision about what it does in HTML.

```sh
python3 scripts/api-docs.py           # update the doc comments
python3 scripts/api-docs.py --check   # fail if they are out of date
```

Releases run from the Actions tab (`.github/workflows/release.yml`), as in
Solveng. Pick a channel: `alpha` and `rc` publish a GitHub prerelease; `stable`
publishes a release and opens a pull request to Typst Universe. The workflow
installs the latest Typst, runs `scripts/api-docs.py`, runs the tests, and
commits the updated docs with the release. The version comes from the
Conventional Commits since the last stable release; enable the commit message
check once per clone with `git config core.hooksPath .githooks`.
