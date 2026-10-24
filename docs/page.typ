#import "../lib.typ": *
#show: letmeout
#set document(title: "Letmeout pages", date: none)
#set page(
  paper: "a5", numbering: "1 / 1", fill: rgb("fbf8f1"),
  header: grid(columns: (1fr, auto), [Letmeout], [Pages]),
  background: [DRAFT],
)
// Smaller side margins on screens. The PDF keeps the A5 defaults.
#show: html-page(margin: (x: 1.5cm))

#page(fill: rgb("dce7f5"), header: none, numbering: none, background: none)[
  #align(center)[Title page]
]

= Introduction
#on-target(html: [You are reading the web version.], paged: [You are reading the PDF.])

The page width becomes the width of a centred sheet, and its margins shrink on
narrow screens. The header comes before the content and the footer after it.

#pagebreak()
= Continuous content
A pagebreak adds nothing on screen. The content continues, and a printer starts
a new sheet here.

#set page(columns: 2)
= Columns
A changed `set page` starts a new block. #lorem(80)
