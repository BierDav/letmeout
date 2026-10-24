// The runner prepends either the package import or the native grid binding.
#set document(title: "Letmeout grid regression", date: none)

#let plot-img(path, height: 4cm) = image(path, height: height)
#let items = (
  [
    $rect(t) dot cos(t)$
    #image("/tests/grid/image.png", height: 4cm)
  ],
)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 15pt,
  ..items
    .enumerate()
    .map(((i, item)) => {
      let formatted-label = numbering("a)", i + 1)
      block(breakable: false)[
        #formatted-label #item
      ]
    })
)

// Exercise multiple rows, nested grids, and a helper that loads an image.
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 15pt,
  ..range(7).map(i => block(breakable: false)[
    #numbering("a)", i + 1) $cos(#i)$
    #plot-img("/tests/grid/image.png")
  ]),
)
#grid(columns: 2, column-gutter: 2em, row-gutter: 5pt,
  [outer], grid(columns: (1fr, 2fr), [inner one], [inner two]),
  [third], [fourth],
)
#grid(columns: (30%, auto, 1fr), rows: (20pt, auto), gutter: (3pt,),
  [percent], [automatic], [fraction], [next row],
)
#grid(columns: (1em + 10pt, 1fr), [mixed units], [fraction])
#grid()[single column]
#grid()
