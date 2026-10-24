# letmeout

Typst layouts for HTML. Import the package and keep calling `grid`, `line`, and
`align`. Add `#show: letmeout` to also bring `page` settings, `pagebreak`, shapes,
styled boxes and blocks, spacing, transforms, stacks, columns, and placement to
HTML, and use `letmeout-extras.by-target` where HTML should differ from print. Text, math, links, and images remain ordinary HTML content; the browser
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

A wildcard import adds only `grid`, `line`, `align`, `letmeout`, and the `letmeout-extras`
namespace. All optional helpers, color-scheme functions, and native grid aliases
live inside `letmeout-extras`:

```typ
#import "lib.typ": *
#show: letmeout
#show: letmeout-extras.html-only(page.with(width: auto, margin: 1em))
```

Import individual helpers explicitly when you prefer unqualified names:

```typ
#import "lib.typ": grid, letmeout, letmeout-extras
#import letmeout-extras: html-only, grid-cell
#show: letmeout
#show: html-only(page.with(width: auto, margin: 1em))
#grid(grid-cell[Content])
```

## HTML behavior

See the [complete HTML field reference](docs/html-semantics.md) for every
parameter of the overridden functions, native grid subelements, page settings,
and page breaks, including defaults, inheritance, stroke fields, and print-only
behavior. The `grid`, `line`, and `align` doc comments also describe each
parameter's HTML behavior.

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
- With `#show: letmeout`, the page has no browser margin around it, and it
  follows the reader's light or dark mode. See [Dark mode](#dark-mode).
- With `#show: letmeout`, fonts and text colors carry over. The document's font
  and color go on the body, and text in another font or color gets a `<span>`.
  Typst's HTML export drops both otherwise. `<script>`, `<style>`, `<title>`, and `<textarea>`
  keep plain text. Math keeps Typst’s native MathML without text spans.
- With `#show: letmeout`, `pagebreak` adds nothing on screen, so the content continues without a gap.
  It becomes a page break when the HTML is printed.
- With `#show: letmeout`, elements that Typst's HTML export ignores or strips
  become HTML too. See [More elements](#more-elements).

### Pages

Put `#show: letmeout` at the top of the document, before anything else, then use
Typst's own page APIs: `#show: page.with(...)`, `#page(...)[...]`, `#set page(...)`,
and `#pagebreak()`. We recommend `#show: page.with(...)` over `#set page(...)`.
A page call or a `set page` that changes the settings starts
a new block. Other set rules do not start blocks, so inline styles stay in
their paragraph. Paged output is unchanged.

```typ
#import "lib.typ": *
#show: letmeout
#set document(title: "Report")
#show: page.with(
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

HTML has no free space to share, so `h(1fr)` stays ignored; use `grid` to
spread a header across the width, as above.

`letmeout-extras.page` is Typst's `page` with a note on every parameter about what it does
in HTML, which editors show on hover. It passes on exactly the arguments you
give, so `#show: letmeout-extras.page.with(...)` and `#letmeout-extras.page(...)[...]` behave like
`page` in every output. Typst allows set rules only on its own elements, so
`#import letmeout-extras: *` shadows `page` and `#set page(...)` then fails with "only
element functions can be used in set rules". Packages cannot replace that
message. Use `#show: page.with(...)`, or `#set std.page(...)`.

### More elements

With `#show: letmeout`, these elements also become HTML. Typst's HTML export
otherwise ignores them, or drops their styling:

| Element | HTML |
| --- | --- |
| `rect`, `square`, `circle`, `ellipse` | A box with the content. Fill and stroke are layers behind it, so stroke and `outset` take no space, as in Typst. Per-side strokes, per-corner radii, gradients, and exact dash patterns work. |
| `box`, `block` | Fill, stroke, radius, inset, outset, width, height, and clip. `block` also maps `breakable: false`, `above`, and `below`; `box` maps a length `baseline`. Without styling they stay Typst's native `<span>` and `<div>`. |
| `polygon`, `curve` | Native SVG, through `html.frame`. |
| `h`, `v` | Spacing. A weak `v` collapses with its neighbours' margins, as weak spacing collapses in Typst. |
| `pad` | Padding; negative sides become negative margins. |
| `hide` | `visibility: hidden`, so the content keeps its space. |
| `move`, `rotate`, `scale`, `skew` | CSS offsets and transforms around `origin`. `scale(reflow: true)` with one factor uses CSS `zoom`. |
| `stack` | A flex box in the stack's direction, with `spacing`, lengths, and fractions between items. |
| `columns`, `colbreak` | CSS columns, at least `12em` wide, so they collapse on narrow screens. |
| `place` | Floating content stays in the flow; HTML has no page to float to. Other content is placed in the nearest page body, shape, or styled box or block. |
| `underline`, `overline`, `strike`, `highlight` | Their stroke color, thickness, dash, and offset, and the highlight's fill and radius. |

Colors follow the reader's light or dark mode, as elsewhere. When CSS cannot
express something, the element keeps Typst's native output, including its
"was ignored" warning: `h(1fr)` and `v(1fr)`, `scale` to a length, tilings, and
paints CSS cannot draw. `repeat` and `layout` need the page geometry and are
not adapted. `rotate(reflow: true)` and `skew(reflow: true)` draw the transform
without reflowing. Round shapes inset their content approximately, and dashes
on mixed per-side strokes become CSS `dashed` or `dotted`. Paged output is
unchanged.

### Different settings for HTML

Use `letmeout-extras.html-only` or `letmeout-extras.paged-only` with a native `.with()` function as a show rule
to apply a wrapper for one export target:

```typ
#import "lib.typ": *
#show: letmeout
#show: page.with(paper: "a4", margin: 2.5cm)
#show: letmeout-extras.html-only(page.with(width: auto, margin: (x: 1em, y: 2em)))
```

The PDF keeps its A4 page and 2.5cm margins. HTML fills the available width,
with `1em` at the sides and `2em` at the top and bottom. Use `margin: 0pt`
for edge-to-edge content. No separate page-settings API is needed. For notes
on what each setting does in HTML, hover over `letmeout-extras.page`, which behaves
exactly like `page`.

`letmeout-extras.paged-only` selects PDF, PNG, and SVG output. Typst exposes these as one
`"paged"` target, so it cannot distinguish PDF from the other paged formats.
Both shortcuts also accept content:

```typ
#letmeout-extras.html-only[Read the PDF version for print.]
#letmeout-extras.paged-only[Printed 2026]
```

Use `letmeout-extras.by-target(html:, paged:)` when you want both branches in one place.
Content branches select content; function branches return a show rule. A missing
content branch is empty; a missing function branch leaves the body unchanged.

For several set/show rules at once, use a function. It receives the rest of the
scope as `body`; return it after applying your rules:

```typ
#show: letmeout-extras.html-only(body => {
  set page(width: auto, margin: 1em)
  set par(justify: false)
  show heading: set text(blue)
  body
})
```

The `.with()` shorthand has native wrapper semantics (`page(...)` in the page
example). Place `set document(...)` before the page wrapper, as with native
`#show: page.with(...)`. The function form can use native set rules instead.

- Rules apply from that line to the end of the current scope.
- Page settings change only the fields they name. `margin: (x: 1em)` keeps
  the inherited top and bottom margins.
- A later `set page` or `page(...)[...]` still overrides those settings.
- A redundant page set rule that repeats the current settings can fail with
  "page configuration is not allowed inside of containers"; remove it.

Pass content instead of functions to select target-specific content:

```typ
#letmeout-extras.by-target(html: [Read the PDF version for print.], paged: [Printed 2026])
```

Use either content branches or function branches in each call; mixing the two
is an error. The previous `for-*`, `on-target`, `show-target`, and `on-scheme`
names remain available for compatibility. `letmeout-extras.by-color-scheme(light:, dark:)` selects content by color
scheme; `letmeout-extras.theme(...)` controls scoped colors and frame rendering.

Why not `#context if target() == "html" { ... }`? A set rule inside a context
block ends with that block, and `letmeout` cannot see page settings inside it.
The function form of `letmeout-extras.by-target` lets `#show: letmeout` read those settings.
Without `#show: letmeout`, target selection still works, but HTML page settings
have no effect, as in plain Typst.

## Dark mode

With `#show: letmeout`, the page follows the reader's light or dark mode, and
most documents need nothing more:

- The background and the default text color switch with the scheme.
- Every color letmeout writes (text, fills, strokes, gradients, page fills, and
  Typst's default code highlighting) gets a dark variant. It keeps the hue and
  mirrors the lightness: dark ink becomes light, light fills become dark, mid
  tones stay. White fills match the dark background, as they match the light one.
- Frames (`html.frame`) are inverted.

Everything can be tuned:

```typ
#show: letmeout.with(
  color-scheme: "light dark",   // "light", "dark", or none to leave it to the browser
  dark-colors: (                // the dark variant of a color, everywhere
    (rgb("fbf8f1"), rgb("23211c")),
    (black, rgb("d0d0d0")),
  ),
  dark-frames: "invert",        // or none to keep frames as drawn
  css: "@media (prefers-color-scheme: dark) { img { opacity: 0.9 } }",
)

// Alternative content for each color scheme, such as a logo.
#letmeout-extras.by-color-scheme(light: image("logo.svg"), dark: image("logo-dark.svg"))

// Content visible in just one color scheme.
#letmeout-extras.light-only[This note is visible in light mode.]
#letmeout-extras.dark-only[This note is visible in dark mode.]

// The same settings for one scope: text, fills, strokes, and gradients.
#letmeout-extras.theme(
  dark-colors: ((black, rgb("ffd479")), (white, rgb("242424"))),
  dark-frames: none,
)[
  Text and #grid(fill: white, stroke: black)[a cell].
  #html.frame(plot)
]
```

`letmeout-extras.by-color-scheme`, `letmeout-extras.light-only`, and `letmeout-extras.dark-only` select content. Their HTML
visibility follows the document’s allowed color schemes and the reader’s
preference. Paged output uses the light branch: `letmeout-extras.light-only` is included and
`letmeout-extras.dark-only` is omitted. Use `letmeout-extras.theme` for scoped color and frame settings.

Nested themes inherit mappings and replace only the colors they name.
`dark-frames: auto` (the default) inherits the surrounding frame policy;
`none` preserves SVG colors and `"invert"` enables inversion in dark mode.
Frames are rendered SVG, so their internal colors do not use `dark-colors`.

Paged output, and HTML without a dark scheme, use the light side. Colors are
written as `light-dark(light, var(--letmeout-dark-<hex>, auto-variant))`, so
`dark-colors` only sets those properties, and your own CSS can too. Raw blocks
with a custom `theme` keep its colors; adjust them with `css`.

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

For convenience, `letmeout-extras` exports native aliases `letmeout-extras.grid-cell`, `letmeout-extras.grid-hline`,
`letmeout-extras.grid-vline`, `letmeout-extras.grid-header`, and `letmeout-extras.grid-footer`. They support `.with()` and native
set/show syntax. For example, `letmeout-extras.grid-cell(colspan: 2)[...]` works in both targets.

Existing uses of `grid.cell(...)`, `set grid(...)`, `set line(...)`, or
`set align(...)` need qualification with `std` after the import. Ordinary function
calls need only the import. This lexical limitation means the package cannot be
a completely transparent replacement for every use of the built-in element APIs.

For paged output, all original arguments and native styling are preserved. HTML
adapters are installed only in the HTML context, and check the target again at
nested boundaries such as `html.frame`. The regression suite compares PDF, PNG,
and SVG output against the native functions byte for byte.

## Development

The structure follows Solveng: `lib.typ` exports the core API, `letmeout-extras.typ` groups optional helpers, `src/` contains
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

`scripts/api-docs.py` writes the doc comments of `grid`, `line`, and `align`
from the latest Typst docs on typst.app. It copies Typst's summary,
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
