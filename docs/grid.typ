#import "../lib.typ": *
#show: letmeout
#set document(title: "Letmeout grid example", date: none)

= Letmeout

A native HTML grid containing Typst math and images.

#let plot-img(path, height: 4cm) = image(path, height: height)
#let items = (
  [$rect(t) dot cos(t)$ #plot-img("../tests/grid/image.png")],
  [$sin(t)$ #plot-img("../tests/grid/image.png")],
  [$cos(t)$ #plot-img("../tests/grid/image.png")],
  [$t^2$ #plot-img("../tests/grid/image.png")],
)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 15pt,
  ..items.enumerate().map(((i, item)) => {
    let formatted-label = numbering("a)", i + 1)
    block(breakable: false)[#formatted-label #item]
  }),
)
