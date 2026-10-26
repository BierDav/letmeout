// Generic reproductions: native APIs, styled text, a layout-based image, and
// rows of inline boxes. No résumé content or third-party packages are needed.
#set document(title: "Document adapters", date: none)
#set page(width: 360pt, height: auto, margin: 18pt)
#set text(size: 10pt)
#set par(leading: 0.8em)

#text(size: 36pt, weight: 300, style: "italic", tracking: -0.5pt)[Display title]

#grid(columns: (1fr, auto), gutter: 8pt,
  text(weight: 600)[An inline title with spaces], text(size: 8pt)[2025 – 2026],
)

#grid(columns: (1fr, 1fr, 1fr), rows: 70pt, stroke: gray,
  align(center + top)[Top], align(center + horizon)[Middle], align(center + bottom)[Bottom],
)

#align(center, layout(size => box(
  width: 80pt, height: 100pt, clip: true, radius: 8pt,
  image("../grid/image.png", width: 100%, height: 100%, fit: "cover", alt: "Fixture photo"),
)))

#let chip(body) = box(inset: (x: 5pt, y: 3pt), outset: (y: 0.7pt),
  radius: 3pt, fill: black, text(size: 8pt, fill: white, body))
#block(width: 120pt)[
  #par(leading: 0.9em,
    ("First chip", "Second chip", "Third chip", "Fourth chip", "Fifth chip").map(chip).join(h(3pt)),
  )
]

#link("https://example.com/plain")[Plain link]
#link("https://example.com/underlined")[#underline[Explicit underline]]

#block(fill: luma(98%))[
  #set par(spacing: 6pt)
  Paragraph one.

  Paragraph two.
]

// Overflowing native ink is a stand-in for a third-party image shadow. Keep
// the actual image clipped, but allow the surrounding decoration to paint.
#grid(columns: (1fr, 80pt), column-gutter: 10pt,
  [Decorated image],
  layout(size => box(width: 80pt, height: 100pt)[
    #place(top + left, dx: -20pt, dy: -20pt,
      rect(width: 120pt, height: 140pt, fill: blue.lighten(80%), stroke: none))
    #box(width: 80pt, height: 100pt, clip: true, radius: 8pt,
      image("../grid/image.png", width: 100%, height: 100%, fit: "cover"))
  ]),
)

// A tall shared row must not distribute spare height between a short card's
// heading, grid, vertical space, and paragraphs.
#grid(columns: (1fr, 1fr), rows: 220pt, gutter: 8pt,
  [
    #block(above: 0pt, below: 6pt)[Section label]
    #grid(columns: 1)[Company label]
    #v(3pt)
    #par[Project label]
    #v(2pt)
    #par[Project body.]
  ],
  [A neighbouring card sets the shared row height.],
)

#grid(columns: (1fr, auto), row-gutter: 5pt,
  text(size: 11.5pt)[Role label], pad(top: 4pt, text(size: 7pt)[Dates label]),
  [School label], [],
)

// Native text edges trim the line-box space around large stacked names.
#block(below: 0pt)[
  #set par(leading: 0pt, spacing: 0pt)
  #block(height: 40pt, text(size: 36pt, top-edge: "ascender")[Given name])
  #block(text(size: 48pt, top-edge: "cap-height", bottom-edge: "descender")[Family name])
]
#v(8pt)
#text(size: 8pt)[Display subtitle]

// Trimming must use the visible text's family, weight, and style. A parent
// strut in the document font can otherwise put ink outside the measured gap.
#block(below: 0pt)[
  #set par(leading: 0pt, spacing: 0pt)
  #block(text(font: "Arial", size: 48pt, weight: 800, style: "italic",
    top-edge: "cap-height", bottom-edge: "descender")[Display gyjq])
]
#v(8pt)
#text(font: "Courier New", size: 8pt, weight: 600, style: "italic")[Metric subtitle]

// Default block/grid spacing adds to strong vertical space. Explicit block
// edges override that default, including zero. Nested flow starts/ends flush.
#block(above: 0pt, below: 0pt)[
  #set par(spacing: 9pt)
  #block[Flow block A]
  #v(3pt)
  #block[Flow block B]
  #v(3pt)
  #grid(columns: 1)[Flow grid A]
  #v(3pt)
  #grid(columns: 1)[Flow grid B]
  #block(above: 2pt, below: 0pt)[Explicit edges]
  #par[After explicit zero]
]

// Mixed styles must retain leading when a narrow cell wraps, just like plain
// text. Compact metrics are appropriate for a box's inset, not a cell's lines.
#grid(columns: (75pt, 75pt), column-gutter: 8pt, row-gutter: 7pt,
  [Wrapped plain words that fill several lines],
  [Wrapped *bold words* that fill several lines],
  [Second row plain], [Second row *bold*],
)

// Fractional boxes share the remaining inline width, including lines used by
// heading show rules. These must remain inside the paragraph in parsed HTML.
#show heading: it => block(above: 8pt, below: 4pt)[
  #text(size: 16pt, it.body)#h(6pt)#box(width: 1fr, baseline: -0.3em, line(length: 100%, stroke: 0.5pt + gray))
]
= Flexible heading
#par[After flexible heading]
#par[Before #box(width: 1fr, line(length: 100%)) between #box(width: 2fr, line(length: 100%)) after]

#block(above: 0pt, below: 0pt)[
  #par(spacing: 12pt)[Weak first]
  #v(3pt, weak: true)
  #par(spacing: 4pt)[Weak second]
]
#block(spacing: 5pt)[Spacing shorthand]
#block(above: 2%, below: 1em)[Relative spacing]

// Native frame SVG uses em sizes. Font scopes must survive even when the
// frame has no selectable text; shrinking it must preserve the aspect ratio.
#grid(columns: (90pt, 40pt), column-gutter: 10pt,
  [
    #set text(size: 7pt)
    #align(center, layout(_ => box(width: 80pt, height: 100pt,
      image("../grid/image.png", width: 100%, height: 100%, fit: "cover"))))
    #block(above: 9pt, below: 0pt)[Small frame follower]
  ],
  [
    #set text(size: 13pt)
    #align(center, layout(_ => box(width: 80pt, height: 100pt,
      image("../grid/image.png", width: 100%, height: 100%, fit: "cover"))))
    #block(above: 9pt, below: 0pt)[Narrow frame follower]
  ],
)
