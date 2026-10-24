#import "../lib.typ": *
#set document(title: "Letmeout HTML layouts", date: none)

// Give this example a readable palette in both light and dark HTML hosts.
#context if target() == "html" {
  html.elem("style", ".letmeout-grid-cell { color: #18283b; } .letmeout-grid-cell-body { padding: 4px; }")
}

#grid(
  columns: (1fr, 1fr, 1fr), rows: (auto, 80pt),
  gutter: 8pt, inset: 6pt,
  fill: rgb("edf3fb"),
  letmeout-extras.grid-header(letmeout-extras.grid-cell(colspan: 3, fill: rgb("d0e2f8"))[
    *A CSS grid with selectable text, math, and links*
  ]),
  align(center + top)[Top  $cos(t)$],
  align(center + horizon)[Middle  #link("https://typst.app")[Typst]],
  align(center + bottom)[Bottom  $t^2$],
)
#line(length: 100%, stroke: (paint: gradient.linear(rgb("397ccc"), rgb("9061d1")), thickness: 3pt, cap: "round", dash: "dashed"))
#align(center)[The grid and line adapt to their HTML container.]
