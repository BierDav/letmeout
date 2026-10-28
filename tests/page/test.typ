// The runner prepends the package import, or a no-op `letmeout` for native Typst.
#show: letmeout
#set document(title: "Page coverage", date: none)
#set text(lang: "de")
#show: page.with(
  paper: "a5", numbering: "1 / 1", margin: (x: 2cm, top: 3cm),
  header: grid(columns: (1fr, auto), [Running header], [Letmeout]),
  fill: rgb("fbf8f1"),
  background: [DRAFT],
)
#set heading(numbering: "1.")
= Introduction
#lorem(40) Inline #text(red)[styles] stay in the paragraph.

#pagebreak()
= Continued
Content after a pagebreak continues in the same block.
#page(fill: rgb("1d2b3a"), header: none, numbering: none, margin: 0pt)[
  #align(center)[Title page]
]
= After a nested page
#pagebreak(weak: true)
#pagebreak(to: "odd")
Still the same page.
#page(columns: 2, flipped: true, margin: (inside: 1cm, outside: 3cm), binding: right,
  number-align: right + top, foreground: [Foreground])[
  #lorem(30)
]
#page(width: auto, height: auto, margin: 10%, footer: [
  Custom footer

  Second footer paragraph

  #stack(spacing: 3pt, [First footer item], [Second footer item])
], header: none)[
  Automatic size.
]
#set page(fill: rgb("eef"))
= Set rule
A later `set page` starts a new block.
