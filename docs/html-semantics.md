# HTML feature mapping

The goal is to carry layout intent into the web platform. The package uses
selectable content, CSS sizing, normal document flow, and decorative vector
strokes. It does not measure a PDF page or turn document content into a picture.
All mappings below apply only to HTML. Paged exports retain the native elements.

## Grid

| Native feature | HTML interpretation |
| --- | --- |
| `columns` count / scalar / array | CSS column tracks; an empty definition means one automatic column. |
| `rows` count / scalar / array | CSS row tracks, repeating the final definition to fit placed cells. |
| `auto` tracks | Browser intrinsic sizing. |
| Fractional tracks | `minmax(0, Nfr)`; available width is shared without forcing the intrinsic minimum width of long content. |
| Absolute, font-relative, percentage, mixed lengths | CSS `pt`, `em`, `%`, and `calc(...)`, preserving responsive sizing. |
| `gutter`, `column-gutter`, `row-gutter` | Uniform lengths use CSS gaps. Varying, automatic, or fractional gutters become explicit tracks between content tracks. Axis-specific settings take precedence. The last gutter repeats. |
| Children | Flow into logical cells in row-major order. Empty slots become styled cells. Nested supported layouts remain HTML. |
| `inset` | Cell padding; scalar or side dictionary, including `x`, `y`, and `rest` shorthands. |
| `align` | Text and CSS container alignment, independently on both axes. |
| `fill` | CSS backgrounds for solid colors and supported gradients. `none` is transparent. |
| `stroke` | Decorative vector edges painted by CSS; supports side dictionaries, thickness, caps, dashes, phase, and supported gradients. |
| Styling arrays / functions | Arrays cycle by column; callbacks receive the logical `(x, y)` coordinates. Empty arrays use the property's default. |
| Cell `x`, `y` | Explicit CSS placement after resolving occupied cells. A single fixed coordinate finds the first available position on its other axis. Overlaps are errors. |
| Cell `colspan`, `rowspan` | CSS track spans, including intervening gutters. |
| Cell `inset`, `align`, `fill`, `stroke` | Overrides of grid-wide styling, including partial side/axis overrides. Unspecified values inherit. Explicit `none` removes paint/strokes. |
| Cell `breakable` | CSS `break-inside: auto` or `avoid`, for print/fragmentation. `auto` follows whether its rows contain an intrinsic track. This is a browser hint, not a pagination engine. |
| `grid.hline`, `grid.vline` | Grid-positioned vector separators, including partial ranges and automatic indices. They can cross gutters. |
| Line `position` | Chooses the edge before or after its logical row/column. Start/end follow RTL; left/right remain physical. |
| Stroke precedence | Explicit separators override cell edges; cell edges override grid defaults. Later separators replace earlier ones. An explicit `none` erases the affected edge. Equal-priority cell edges use the thicker stroke. |
| `grid.header`, `grid.footer` | Ordered layout cells with group metadata, rendered once in the continuous document. These are generic layout groups, not semantic HTML table sections. |
| Header/footer `repeat`, header `level` | Preserved as `data-grid-repeat` and `data-grid-level`. There are no page boundaries on a screen, so repetition and hierarchical page-header replacement do not run. They are available to host CSS/scripts as metadata. |

The DOM is sorted by logical row and column, so reading order follows visual
placement. A grid does not acquire ARIA table/grid roles: Typst grids also carry
no table semantics. Use a table for tabular data. Header/footer repetition during
browser printing is not implemented; CSS Grid has no equivalent of repeating
`thead`/`tfoot` groups. Sticky positioning is left to the host site rather than
being imposed on every document header.

Native `set std.grid(...)` and set rules on its subelements supply defaults.
Adapters replace native layout show transformations within their local HTML
scope. Arbitrary custom show transformations of grid/line/align/cell elements
are not composed with the adapters; style the emitted classes or their body
content instead. The wrapper functions themselves cannot be used as native
set/show selectors; see the README's naming limitation.

## Align

| Native feature | HTML interpretation |
| --- | --- |
| `left`, `center`, `right` | Physical text alignment and CSS `justify-items`. |
| `start`, `end` | Logical alignment with an explicit `dir` and language on the wrapper. |
| `top`, `horizon`, `bottom` | CSS `align-content: start / center / end`. |
| Combined axes | Both mappings apply to the same block container. |
| A single axis | The specified axis changes; unspecified axes fold with the native outer alignment default. |
| Nested alignment | Nested containers allow the group position and its inner text alignment to differ. |
| Default / native set rules | Resolved from `std.align` by the HTML show adapter. |
| Paragraph boundaries | A block element, matching the function's block-level intent. |
| Vertical page space | No artificial page or viewport height. Alignment has a visible vertical effect when an enclosing layout supplies free space. |

The wrappers preserve the browser's content flow and links. They do not
automatically center the entire document in the viewport.

## Line

| Native feature | HTML interpretation |
| --- | --- |
| `start` | Physical `(x, y)` offset into a container spanning the available inline width. |
| `end` | Explicit endpoint; takes precedence over `length` and `angle`. |
| `length` | A responsive length, defaulting to the native 30pt. |
| `angle` | Clockwise geometric direction, including vertical and reversed lines. |
| Relative coordinates | Percentages on **both axes** use the container's inline width. This gives a stable geometric reference in an intrinsically tall web document. It deliberately does not use page height or viewport height. |
| Absolute / `em` / mixed coordinates | CSS lengths and arithmetic, retaining their responsive components. |
| `stroke.paint` | CSS solid or gradient paint through an SVG mask. |
| `stroke.thickness` | The geometric stroke width, resolved with the current font size. |
| `stroke.cap` | SVG butt, round, or square caps; the mask allows a half-stroke outside each endpoint. |
| `stroke.dash` | Native named patterns, arbitrary arrays, `dot`, and dictionary `array`/`phase`. |
| `stroke.join`, `miter-limit` | Retained in the SVG mask. A straight segment has no corner for these to change. |
| Set rules | Resolved from `std.line`. |

A line is a decorative block in normal HTML flow, hidden from assistive
technology. It is not automatically an `hr`: a geometric stroke does not imply
a thematic break. Positive vertical extent reserves space in the flow; negative
coordinates can overflow its box. The line itself follows physical coordinates,
independent of text direction.

## Paint, CSS, and deliberate limits

Solid colors convert to sRGB. Linear, conic, and concentric radial gradients
become CSS gradients. Additional stops sampled in Typst's chosen interpolation
space approximate spaces the browser cannot represent; original stops and hard
transitions are retained. Browser gradient geometry follows CSS conventions.
Parent-relative gradients and off-center radial focal circles currently produce
an explicit diagnostic. Arbitrary Typst tilings also produce a diagnostic: their
layout-bearing content is not exposed as a reusable CSS image by Typst. Use a
host background image for that case. These limits apply equally to fills and
stroke paints; nothing is silently replaced with a solid color.

The generated CSS needs a browser with CSS Grid, container query length units,
CSS masks, and CSS math functions `hypot()` and `atan2()`. It does not require
JavaScript or a runtime library. Host styles can customize `.letmeout-grid`,
`.letmeout-grid-cell`, `.letmeout-align`, `.letmeout-line`, and
`.letmeout-stroke-paint`.

The native parameter contracts were checked against Typst's documentation for
[grid](https://typst.app/docs/reference/layout/grid/),
[align](https://typst.app/docs/reference/layout/align/),
[line](https://typst.app/docs/reference/visualize/line/),
[stroke](https://typst.app/docs/reference/visualize/stroke/), and
[target](https://typst.app/docs/reference/foundations/target/).

## Page

Page support needs `#show: letmeout` at the top of the document. HTML is one
continuous document, so page settings become one block rather than a series of
sheets. Content never moves to another page, and the package adds no
screen-sized pages. A new block starts only where the page settings change:
at a `set page`, `page(...)[...]`, or `show: page.with(...)` with different
values. Each block has this structure:

```
section.letmeout-page                full width; fill
└ div.letmeout-page-sheet           centred; max-width = page width
  ├ div.letmeout-page-background    layer behind the content
  ├ header.letmeout-page-header     top margin, before the content
  ├ div.letmeout-page-body          the content
  ├ footer.letmeout-page-footer     bottom margin, after the content
  └ div.letmeout-page-foreground    layer above the content
```

| Native feature | HTML interpretation |
| --- | --- |
| `paper`, `width` | The maximum width of the centred sheet. On narrower screens the sheet fills the available width. `auto` means full width. |
| `height` | No effect. HTML has no page height; the block fits its content. |
| `flipped` | Swaps width and height, so it changes the sheet width. |
| `margin` | Padding on the sheet, with Typst's defaults (2.5/21 of the shorter side), folding, `x`/`y`/`rest`, and ratios. With a fixed width, every margin is a fraction of the sheet width (`cqi`). It equals the declared length at full width and shrinks on narrower screens. |
| `binding`, `inside`/`outside` | There are no facing pages, so the first page's layout applies. With a left binding, the inside margin is on the left. |
| `fill` | Background of the full-width block. `auto` is transparent, so host colours and dark mode are not overridden; set a fill for a paper colour. |
| `header`, `footer` | A `<header>` at the start of the block and a `<footer>` at its end, each shown once and placed inside the margins. The header is bottom-aligned with `header-ascent` spacing; the footer is top-aligned with `footer-descent` spacing. Taller content grows the margin instead of overlapping. |
| `numbering`, `number-align` | Automatic header or footer with `counter(page).display`, including totals such as `"1 / 1"`. The page counter does not advance, because the document is one page. `counter(page).update` works. |
| `background`, `foreground` | Layers covering the sheet, centred like Typst's, hidden from assistive technology (Typst marks them as artifacts). The foreground does not intercept clicks. |
| `columns` | CSS columns with the `columns.gutter` gap. Columns are at least `12em` wide, so they collapse on narrow screens. |
| `page(...)[...]` | Its own block with its own settings, inheriting the surrounding settings. Content before and after it forms separate blocks, each with its header and footer. |
| `bleed`, `supplement` | No effect on screen. Fills already extend to the screen edges. |

### How `set page` is read

A set rule runs no code, and its styles cannot be inspected or separated from
other set rules, so the package cannot intercept it. Instead, `letmeout` places
an invisible probe under every style node, and the probe records the page
settings in effect there. Typst's introspection reads the probes back, and the
document is split only at style nodes whose page settings differ. Inline
styles such as `text(red)[...]` therefore stay inside their paragraph.

Two Typst rules shape the result:

- Page styles are not allowed inside an HTML element. A style node that
  changes the page settings therefore wraps its blocks instead of sitting
  inside one. A `set page` that repeats the current values exactly is not
  detected and fails with "page configuration is not allowed inside of
  containers"; remove the redundant rule.
- `set document` must come before any content. Set rules at the start of the
  document therefore stay outside all blocks, and `#show: letmeout` must come
  first.

Typst prints "page set rule was ignored" for page styles in HTML export.
Packages cannot silence warnings, but the settings are applied.

A block sets `break-before: page` and `break-after: page`, so each block starts
on a new sheet when the HTML is printed.

## Target-specific settings

`on-target(html:, paged:)` is a context block that shows one of two contents.
`show-target(html:, paged:)` returns a function for `#show:`. Both choose by
`target()` and do nothing else, so paged output equals the paged branch alone.

`html-page(..)` is `show-target` with a `set page` in its HTML branch. It is
needed because a context block hides its set rules: they end with the block,
and the probes described above cannot see into a context block that has not
run. So `show-target` returns two things: an invisible `metadata` marker that
holds the HTML rule and the body, followed by the context block as the
fallback. `#show: letmeout` runs in HTML, finds markers at the document level
(in sequences and style nodes), applies the HTML rule directly, and drops the
fallback. The page settings in the rule then become ordinary style nodes, and
blocks split as for `set page`. Markers nested inside other elements, or a
document without `#show: letmeout`, use the context fallback.

## Pagebreak

With `#show: letmeout`, a native `pagebreak` adds nothing on screen: the content
continues in the same block, with no gap, repeated header, or new page number.
A strong break renders an empty, hidden `div.letmeout-pagebreak` with
`break-before: page`, so a printer breaks there. `to: "odd"` / `"even"` become
`recto` / `verso`. Weak breaks, including the ones a `page` call adds around
its body, render nothing: a block already starts on a new printed sheet.
