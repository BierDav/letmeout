#set document(title: "HTML feature coverage", date: none)

= Alignment
#align(center)[Centered text with a #link("https://typst.app")[link].]
#align(right)[Right aligned.]
#align(left)[Left aligned.]
#align(center + bottom)[Combined axes in a flowing document.]
#align(center)[#align(left)[Nested left alignment.]]
#grid(columns: (1fr, 1fr, 1fr), rows: 90pt, stroke: 1pt + gray,
  align(center + top)[Top],
  align(center + horizon)[Middle],
  align(center + bottom)[Bottom],
)
#text(dir: rtl, lang: "ar")[
  #align(start)[بداية]
  #align(end)[نهاية]
  #align(left)[يسار]
  #align(right)[يمين]
]

= Lines
#line()
#line(length: 100%, stroke: 2pt + blue)
#line(start: (10%, 5pt), end: (80%, 20pt), stroke: (paint: red, thickness: 3pt, cap: "round"))
#line(length: 60pt, angle: 90deg, stroke: (paint: green, thickness: 4pt, cap: "square"))
#line(length: 50%, angle: 20deg, stroke: (paint: blue, thickness: 2pt, dash: (array: (4pt, 2pt, "dot", 2pt), phase: 1pt)))
#line(start: (80%, 20pt), end: (20%, 5pt), stroke: (paint: purple, dash: "dashed"))
#line(length: 100%, stroke: 4pt + gradient.linear(red, blue))
#line(length: 100%, stroke: 4pt + gradient.conic(red, blue))
#line(length: 100%, stroke: 4pt + gradient.radial(red, blue))
#line(end: (50pt, 5pt), length: 300pt, angle: 90deg)

= Grid placement and styles
#grid(
  columns: (1fr, 2fr, 1fr), rows: (35pt, auto),
  column-gutter: (4pt, 10pt), row-gutter: (2pt, 7pt),
  fill: (x, y) => if calc.even(x + y) { rgb("e7f0fa") } else { rgb("f5f5f5") },
  inset: (left: 7pt, rest: 4pt), align: center + horizon,
  stroke: (bottom: 1pt + gray),
  grid-header(grid-cell(colspan: 3, fill: rgb("b8d8fa"))[*Header*]),
  grid-cell(x: 1, y: 1, colspan: 2, fill: yellow)[Spanning columns],
  grid-cell(rowspan: 2)[Spanning rows],
  [Body A], [Body B],
  grid-hline(y: 1, stroke: 2pt + blue),
  grid-vline(x: 1, start: 1, stroke: (paint: red, dash: "dotted")),
  grid-footer(grid-cell(colspan: 3, breakable: false)[Footer]),
)
#grid(columns: 3, gutter: (1fr, 2fr), inset: (2pt, 5pt),
  fill: (rgb("eef"), rgb("fee")),
  stroke: (left: red, right: 2pt + blue),
  [one], grid-cell(stroke: (bottom: 3pt + green), inset: (left: 8pt))[two], [three],
)
#grid(columns: 2, rows: (30pt, 60pt), fill: gradient.linear(red, blue),
  [linear], [fill], grid-cell(fill: gradient.conic(red, blue))[conic],
  grid-cell(fill: gradient.radial(red, blue))[radial],
)

= Inherited defaults
#set std.grid(columns: 2, inset: 5pt, fill: rgb("eee"))
#set std.line(length: 75%, stroke: 2pt + purple)
#set std.align(center)
#grid[Inherited][Defaults]
#line()
#align[Inherited alignment]

= Cell defaults and overrides
#{
set std.grid.cell(inset: 4pt, stroke: blue, align: right + horizon)
grid(columns: 2, rows: 45pt,
  grid-cell(inset: (left: 8pt), stroke: (bottom: 2pt), align: left)[Partial overrides],
  [Inherited cell styles],
)
}
#grid(columns: 2, stroke: 2pt + gradient.linear(red, blue),
  grid-hline(y: 0, stroke: none), [No top border], [Gradient edges],
)
#grid(columns: 2, fill: (rgb("eef"), rgb("fee")),
  grid-cell(x: 1)[Explicit column], grid-cell(y: 1)[Explicit row], [Auto],
)
