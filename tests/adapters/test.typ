#set document(title: "Adapters", date: none)
#set page(width: 16cm, height: auto, margin: 12pt)
Spacing: a#h(1cm)b #h(-2pt) c
#v(0.5cm)
#v(1em, weak: true)
#pad(left: 1cm, top: -2pt)[Padded by 1cm.]
#hide[hidden] visible
#hide[#block[hidden block]]
#stack(dir: ltr, spacing: 8pt,
  rect[plain rect],
  rect(fill: yellow, radius: 50%, stroke: (top: 2pt + red, left: blue))[sides],
  square(size: 1cm, fill: aqua),
  circle(radius: 0.6cm, stroke: 2pt + green)[c],
  ellipse(width: 2cm, height: 1cm, stroke: (dash: "dashed", paint: blue)),
  rect(stroke: gradient.linear(red, blue) + 3pt, radius: 4pt)[gradient],
  rect(stroke: (dash: "dash-dotted"), radius: 4pt)[dashed],
  rect(width: 1cm, height: 1cm, outset: 3pt, fill: gray),
)
#stack(dir: ttb, [one], 1fr, [two])
#stack(dir: rtl, [right], [left])
#stack(dir: ltr, spacing: 20pt, rotate(30deg)[rotated], scale(x: 150%)[scaled],
  scale(150%, reflow: true)[zoomed], skew(ax: -12deg)[skewed], move(dx: 5pt, dy: 5pt)[moved],
  polygon(fill: orange, (0pt, 0pt), (20pt, 0pt), (10pt, 15pt)),
  curve(curve.move((0pt, 0pt)), curve.line((10pt, 10pt))))
Inline #box(fill: red.lighten(60%), inset: 3pt, radius: 3pt, stroke: red)[box],
#box(baseline: 2pt)[shifted], #box[plain box],
#underline(stroke: red + 1.5pt, offset: 2pt)[underline] #underline[native]
#overline(stroke: (dash: "dotted"))[overline] #highlight(fill: aqua)[highlight]
#strike(stroke: blue + 1pt)[strike].
#block(fill: luma(230), inset: 8pt, radius: 4pt, width: 60%, outset: 2pt, breakable: false)[A styled block.]
#block[A plain block.]
#block(clip: true, radius: 6pt, height: 1cm, fill: aqua)[Clipped]
#columns(2)[First column. #colbreak() Second column.]
#rect(width: 100%, height: 2cm)[
  #place(bottom + right)[bottom right]
  #place(center + horizon, dx: 5pt)[centre]
]
#place(top, float: true, clearance: 1em)[floated]
