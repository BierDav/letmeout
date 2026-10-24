#!/usr/bin/env python3
"""Compile real fixtures, inspect HTML, and compare paged exports to native Typst."""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/output"
OUTPUT.mkdir(exist_ok=True)


# Typst reports every `set page` in HTML, and packages cannot silence it.
PAGE_WARNING = "page set rule was ignored"


def compile_source(source, name, fmt, success=True, page_rules=False, ignored=()):
    output = OUTPUT / f"{name}.{fmt}"
    result = subprocess.run(
        ["typst", "compile", "--root", str(ROOT), "--features", "html",
         "--creation-timestamp", "0", "--format", fmt,
         *(["--pages", "1"] if fmt in ("svg", "png") else []), "-", str(output)],
        input=source, text=True, capture_output=True,
    )
    if success:
        assert result.returncode == 0, result.stderr
        stderr = result.stderr
        if page_rules:
            stderr = "\n".join(line for line in stderr.splitlines() if PAGE_WARNING not in line)
        for element in ignored:
            stderr = "\n".join(line for line in stderr.splitlines() if f"{element} was ignored" not in line)
        assert "was ignored" not in stderr, result.stderr
    else:
        assert result.returncode != 0, f"{name} unexpectedly succeeded"
    return output, result.stderr


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.grids = []
        self.images = []
        self.math = 0
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("class") == "letmeout-grid":
            self.grids.append(attrs["style"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "math":
            self.math += 1

    def handle_data(self, data):
        self.labels.append(data)


# A wildcard import exposes only the layout overrides, letmeout, and letmeout-extras.
# Existing helper names must survive that import without being overwritten.
helper_names = ("theme", "by-target", "html-only", "paged-only", "by-color-scheme",
                "light-only", "dark-only", "grid-cell", "grid-header", "grid-hline",
                "grid-vline", "grid-footer", "for-target", "for-html", "for-paged",
                "for-scheme", "on-target", "show-target", "on-scheme")
# Every helper except `letmeout-extras.page`: a wildcard import of letmeout-extras would shadow
# `page`, and the fixtures use `set page`.
IMPORT = '#import "/lib.typ": *\n#import letmeout-extras: ' + ", ".join(helper_names) + '\n'
namespace_probe = "".join(f"#let {name} = 42\n" for name in helper_names)
namespace_probe += '#import "/lib.typ": *\n'
namespace_probe += "".join(f"#assert({name} == 42)\n" for name in helper_names)
namespace_probe += '#show: letmeout\n#show: letmeout-extras.html-only(page.with(width: auto, margin: 1em))\n'
namespace_probe += '#grid(columns: 1, letmeout-extras.grid-cell[scoped cell])\n#line()\n#align(center)[scoped alignment]'
namespace_html, _ = compile_source(namespace_probe, "extras-namespace", "html", page_rules=True)
assert not re.search(r'class="letmeout-page-sheet"[^>]*max-width:', namespace_html.read_text())
assert 'scoped cell' in namespace_html.read_text()
# Individual imports can come from the namespace, including native set syntax.
selective_source = ('#import "/lib.typ": *\n#import letmeout-extras: html-only, grid-cell\n'
                    '#show: letmeout\n#show: html-only(page.with(width: auto))\n'
                    '#set grid-cell(inset: 3pt)\n#grid(grid-cell[selected helper])')
selective_html, _ = compile_source(selective_source, "extras-selective", "html", page_rules=True)
assert 'selected helper' in selective_html.read_text() and 'padding-left: 3pt' in selective_html.read_text()

fixture = (ROOT / "tests/grid/test.typ").read_text()
html, _ = compile_source(IMPORT + fixture, "grid", "html")
elements = Elements()
elements.feed(html.read_text())
assert len(elements.grids) == 8, elements.grids
assert "grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)" in elements.grids[0]
assert "column-gap: 15pt; row-gap: 15pt" in elements.grids[0]
assert "column-gap: 2em; row-gap: 5pt" in elements.grids[2]
assert "grid-template-columns: 30% auto minmax(0, 1fr)" in elements.grids[4]
assert "grid-auto-rows: auto" in elements.grids[4]
assert "calc(10pt + 1em) minmax(0, 1fr)" in elements.grids[5]
assert len(elements.images) == 8, len(elements.images)
assert elements.math == 8, elements.math
assert "a)" in "".join(elements.labels) and "g)" in "".join(elements.labels)
assert all("data:image/png;base64," in img["src"] for img in elements.images)

# Images keep their aspect ratio like in PDF: the side left `auto` must not
# keep the pixel size from Typst's width/height attributes.
image_source = (IMPORT + '#show: letmeout\n'
                '#image("/tests/grid/image.png", height: 4cm)\n#image("/tests/grid/image.png", width: 50%)\n'
                '#image("/tests/grid/image.png")\n#image("/tests/grid/image.png", width: 3cm, height: 4cm, fit: "contain")\n')
image_html, _ = compile_source(image_source, "images", "html")
image_text = image_html.read_text()
for size in ("height", "width", "auto"):
    assert f'<letmeout-image data-size="{size}"><img' in image_text, size
assert '<letmeout-image data-size="both" data-fit="contain"><img' in image_text
assert 'letmeout-image[data-size="height"] > img { width: auto;' in image_text
assert 'letmeout-image[data-size="width"] > img { height: auto;' in image_text

for fmt in ("pdf", "svg"):
    # Use a small single-page document for SVG comparison.
    source = fixture if fmt == "pdf" else fixture.split("// Exercise")[0]
    native, _ = compile_source(source, "native", fmt)
    patched, _ = compile_source(IMPORT + source, "patched", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"{fmt} output changed"

# All native options remain usable in paged output, even outside the HTML subset.
pdf_only = '''
#set document(date: none)
#set std.grid(inset: 4pt, fill: yellow)
#show std.grid: it => block(stroke: red, it)
#grid(columns: 2, stroke: blue,
  std.grid.cell(colspan: 2)[wide], [left], [right],
  std.grid.hline(), [last], [row])
'''
native, _ = compile_source(pdf_only, "native-options", "pdf")
patched, _ = compile_source(IMPORT + pdf_only, "patched-options", "pdf")
assert native.read_bytes() == patched.read_bytes(), "paged styling changed"

for name, body, message in (
    ("invalid-option", '#grid(unknown: true)[cell]', "unexpected argument"),
    ("overlapping-cells", '#grid(columns: 2, grid-cell(x: 0, y: 0)[a], grid-cell(x: 0, y: 0)[b])', "second cell"),
    ("invalid-span", '#grid(columns: 2, grid-cell(colspan: 3)[a])', "span"),
    ("invalid-grid-line", '#grid(columns: 2, [a], grid-hline(y: 5))', "invalid row"),
):
    _, error = compile_source(IMPORT + body, name, "html", success=False)
    assert message in error, error

# The same fixture exercises all three adapters in HTML and paged output.
features = (ROOT / "tests/features/test.typ").read_text()
feature_html, _ = compile_source(IMPORT + features, "features", "html")
feature_text = feature_html.read_text()
for expected in (
    'class="letmeout-align"', 'text-align: center', 'text-align: left',
    'justify-items: right', 'align-content: end', 'class="letmeout-line"',
    'mask-image:', 'stroke-dashoffset=', 'linear-gradient(', 'conic-gradient(',
    'radial-gradient(', 'data-grid-group="header"', 'data-grid-group="footer"',
    'data-grid-repeat="true"', 'class="letmeout-grid-hline"',
    'class="letmeout-grid-vline"', 'span 3', 'break-inside: avoid',
):
    assert expected in feature_text, expected
aliases = '\n'.join(f'#let grid-{name} = std.grid.{name}'
                    for name in ('cell', 'hline', 'vline', 'header', 'footer')) + '\n'
for fmt in ("pdf", "png"):
    native, _ = compile_source(aliases + features, "native-features", fmt)
    patched, _ = compile_source(IMPORT + features, "patched-features", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"{fmt} feature output changed"

single_axis, _ = compile_source(IMPORT + '#set std.align(right)\n#align(horizon)[inherited axis]',
                                "single-axis", "html")
assert "text-align: right" in single_axis.read_text()
assert "align-content: center" in single_axis.read_text()

# Paints without an implemented web mapping must fail visibly.
for name, body, message in (
    ("tiling-paint", '#grid(fill: tiling(size: (5pt, 5pt), rect(width: 5pt, height: 5pt)))[cell]', "tiling"),
    ("parent-paint", '#line(stroke: gradient.linear(red, blue, relative: "parent"))', "parent-relative"),
    ("focal-paint", '#grid(fill: gradient.radial(red, blue, focal-center: (20%, 20%)))[cell]', "focal"),
):
    _, error = compile_source(IMPORT + body, name, "html", success=False)
    assert message in error, error

# All named dash families and a zero-length round-cap line remain valid.
patterns = ("solid", "dotted", "densely-dotted", "loosely-dotted", "dashed",
            "densely-dashed", "loosely-dashed", "dash-dotted", "densely-dash-dotted",
            "loosely-dash-dotted")
compile_source(IMPORT + "\n".join(
    f'#line(length: 100%, stroke: (dash: "{pattern}"))' for pattern in patterns
) + '\n#line(length: 0pt, stroke: (cap: "round", thickness: 4pt))', "dash-families", "html")

# A scoped HTML adapter must not leak across an html.frame target boundary.
compile_source(IMPORT + '#grid(columns: 2, [HTML], html.frame(grid(columns: 2, [native], [frame])))',
               "frame", "html")
compile_source(IMPORT + '#grid(inset: (), fill: (), stroke: (), align: ())[empty styles]',
               "empty-styles", "html")

# Positional values accepted by Typst must retain its content coercion.
compile_source(IMPORT + '#grid("text", none)', "coercion", "html")
compile_source(IMPORT + '#grid(columns: (20% + 2em, 1fr))[relative]', "relative", "html")

# `show: letmeout` turns native page settings into continuous blocks.
page_fixture = (ROOT / "tests/page/test.typ").read_text()
page_html, page_stderr = compile_source(IMPORT + page_fixture, "page", "html", page_rules=True)
page_text = page_html.read_text()
assert "<title>Page coverage</title>" in page_text, "set document after show: letmeout"
parts = page_text.split('<section class="letmeout-page"')[1:]
assert len(parts) == 6, len(parts)
for expected in (
    'max-width: 419.5275590551181pt', 'max-width: 595.2755905511812pt',
    'background: light-dark(#fbf8f1', 'background: light-dark(#1d2b3a', 'background: light-dark(#eeeeff',
    'padding-left: 13.5135cqi', 'min-height: 20.2703cqi', 'padding-bottom: 6.0811cqi',
    'class="letmeout-page-background"', 'class="letmeout-page-foreground"', 'z-index: -1',
    'column-count: 2', 'column-gap: 4%', 'padding-left: 10cqi', 'Custom footer',
    'break-before: recto', 'lang="de"',
):
    assert expected in page_text, expected
assert "100svh" not in page_text and "100vh" not in page_text, "no screen-sized pages"
# Strong breaks are print hints in the flow; weak ones render nothing.
assert page_text.count('class="letmeout-pagebreak"') == 2
assert "2. Continued" in parts[0] and "letmeout-pagebreak" in parts[0]
assert re.search(r"<p>(?:(?!</p>).)*Inline(?:(?!</p>).)*stay in the paragraph", parts[0]), "inline styles split a paragraph"
assert '<header class="letmeout-page-header"' in parts[0] and "1 / 1" in parts[0]
assert "Title page" in parts[1] and "<header" not in parts[1] and "<footer" not in parts[1]
assert "Still the same page" in parts[2] and "3. After a nested page" in parts[2]
flipped = parts[3]
assert "max-width: 595.2755905511812pt" in flipped
assert "padding-left: 14.2857cqi" in flipped and "padding-right: 4.7619cqi" in flipped
# Numbers at the top replace only the automatic header, so no footer remains.
assert '<header class="letmeout-page-header"' in flipped and "<footer" not in flipped
assert "4. Set rule" in parts[5] and "background: light-dark(#eeeeff" in parts[5]

# The page needs no browser margin, follows light and dark mode, and keeps the fonts.
screen, _ = compile_source(IMPORT + '#show: letmeout\n#set document(title: "Screen")\n#set text(font: "Georgia")\n'
                           'Body #text(font: "Menlo")[mono]\n\n#html.frame[#rect()]\n\nA #box(html.frame[#circle(radius: 2pt)]) B\n'
                           '#html.elem("script")[let x = 1;]\n#html.elem("style")[p { color: red }]',
                           "screen", "html")
screen_text = screen.read_text()
for expected in (
    'body { margin: 0; font-family: "georgia"; color: light-dark(#000000', ':root { color-scheme: light dark; background: Canvas; }',
    'letmeout-frame > svg { filter: var(--letmeout-dark-frame-filter)', '<span style="font-family: &quot;menlo&quot;">mono</span>',
    '<script>let x = 1;</script>', '<style>p { color: red }</style>', '<title>Screen</title>',
):
    assert expected in screen_text, expected
assert screen_text.count('<span style="font-family') == 1, "only text in another font gets a span"
# Frames stay where Typst puts them: standalone ones outside paragraphs, boxed ones inline.
assert re.search(r"</p><letmeout-frame><svg", screen_text) and re.search(r"<p>A <letmeout-frame><svg", screen_text)
# Dark mode: every color gets a dark variant, which `dark-colors` replaces; text colors come back.
dark, _ = compile_source(IMPORT + '#show: letmeout.with(dark-colors: ((rgb("fbf8f1"), rgb("23211c")),))\n'
                         '#set page(fill: rgb("fbf8f1"))\nA #text(fill: rgb("1d3a8f"))[navy] #text(fill: red)[red]\n'
                         '#grid(fill: white, stroke: black)[cell]\n```rust\nlet s = 1;\n```\n'
                         '#by-color-scheme(light: [for-light], dark: [for-dark])\n'
                         '#theme(dark-colors: ((black, yellow),), dark-frames: none)[region #html.frame[#rect()]]',
                         "dark", "html", page_rules=True)
dark_text = dark.read_text()
for expected in (
    ':root { --letmeout-dark-fbf8f1: #23211c; }', 'background: light-dark(#fbf8f1, var(--letmeout-dark-fbf8f1, ',
    # Dark ink turns light, light fills turn dark, mid tones stay.
    'color: light-dark(#1d3a8f, var(--letmeout-dark-1d3a8f, #567bd6))',
    'color: light-dark(#ff4136, var(--letmeout-dark-ff4136, #ff4136))',
    'background: light-dark(#ffffff, var(--letmeout-dark-ffffff, #1e1e1e))',
    'background: light-dark(#000000, var(--letmeout-dark-000000, #e4e4e4))',
    'code [style="color: #d73948"] { color: light-dark(#d73948',
    '<letmeout-light style="display: contents">for-light</letmeout-light>',
    '<letmeout-dark style="display: none">for-dark</letmeout-dark>',
    'letmeout-dark { display: contents !important; }',
    '--letmeout-dark-000000: #ffdc00; color: light-dark(#000000, var(--letmeout-dark-000000, #e4e4e4)); --letmeout-dark-frame-filter: none',
):
    assert expected in dark_text, expected
extra, _ = compile_source(IMPORT + '#show: letmeout.with(dark-frames: none, css: "p { hyphens: auto }")\nA',
                          "dark-options", "html")
assert "p { hyphens: auto }" in extra.read_text() and ":root { --letmeout-dark-frame-filter: none; }" in extra.read_text()
only_light, _ = compile_source(IMPORT + '#by-color-scheme(light: [L], dark: [D])\n#theme(dark-colors: ((black, white),))[x]', "scheme-paged", "pdf")
light, _ = compile_source(IMPORT + '#show: letmeout.with(color-scheme: "light")\nA', "screen-light", "html")
assert "color-scheme: light;" in light.read_text() and "@media" not in light.read_text()
plain_scheme, _ = compile_source(IMPORT + '#show: letmeout.with(color-scheme: none)\nA', "screen-none", "html")
assert "color-scheme" not in plain_scheme.read_text()

# Color-scheme shortcuts select content; paged output always uses light.
color_scheme_source = ('#light-only[light-note]\n\n#dark-only[dark-note]\n\n'
                       '#by-color-scheme(light: [light-choice], dark: [dark-choice])')
for scheme in ('light', 'dark', 'light dark'):
    selected, _ = compile_source(IMPORT + '#show: letmeout.with(color-scheme: "' + scheme + '")\n'
                                 + color_scheme_source, "color-scheme-" + scheme.replace(' ', '-'), "html")
    selected_text = selected.read_text()
    assert '<letmeout-light style="display: contents">light-note</letmeout-light>' in selected_text
    assert '<letmeout-dark style="display: none">dark-note</letmeout-dark>' in selected_text
    assert 'light-choice' in selected_text and 'dark-choice' in selected_text
    assert ('letmeout-dark { display: contents !important; }' in selected_text) == ('dark' in scheme)
    assert ('@media (prefers-color-scheme: dark)' in selected_text) == (scheme == 'light dark')
for fmt in ('pdf', 'png', 'svg'):
    selected, _ = compile_source(IMPORT + color_scheme_source, "color-scheme-paged", fmt)
    native, _ = compile_source('#context [light-note]\n\n#context none\n\n#context [light-choice]', "color-scheme-native", fmt)
    assert selected.read_bytes() == native.read_bytes(), f"color-scheme content changed native {fmt}"

# Math must keep native MathML, including token types and script structure.
math_fixture = r'''Inline $x_i^2$ and $a_1$.
$ f(x) = cases(x^2 & "if" x >= 0, -x & "otherwise") $
$ sum_(i=1)^n i + frac(1, 2) + sqrt(x) $
$ mat(1, 2; 3, 4) $
$ hat(x) + vec(a, b) $
After math #text(font: "Menlo", fill: red)[styled text].
'''
native_math, _ = compile_source(math_fixture, "math-native", "html")
patched_math, _ = compile_source(IMPORT + '#show: letmeout\n' + math_fixture, "math-patched", "html")
math_blocks = lambda path: re.findall(r"<math\b.*?</math>", path.read_text(), re.S)
assert len(math_blocks(native_math)) == 6
def math_structure(source):
    # Contextual show rules can add an inert mrow around a single token.
    def tree(node):
        children = tuple(tree(child) for child in node)
        if node.tag == "mrow" and not node.attrib and len(children) == 1:
            return children[0]
        return (node.tag, tuple(sorted(node.attrib.items())), node.text or "", children)
    return tree(ET.fromstring(source))

assert [math_structure(m) for m in math_blocks(native_math)] == [math_structure(m) for m in math_blocks(patched_math)], "text styling changed MathML tokens"
assert "<span" not in "".join(math_blocks(patched_math)), "HTML spans inside MathML"
assert re.search(r'<span style="font-family: &quot;menlo&quot;; color: [^"]+">styled text</span>', patched_math.read_text()), "text styling did not resume after math"
# Marking math must not need extra layout passes, nor change what references to an equation say.
numbered, numbered_err = compile_source(IMPORT + '#show: letmeout\n#set math.equation(numbering: "(1)")\n' + math_fixture + '$ y = 2 $ <eq>\nSee @eq.\n', "math-numbered", "html")
assert "did not converge" not in numbered_err, numbered_err
assert re.search(r'<a href="#eq">Equation\s5</a>', numbered.read_text()), "equation references lost their supplement"
for fmt in ("pdf", "svg"):
    native, _ = compile_source(math_fixture, "math-native", fmt)
    patched, _ = compile_source(IMPORT + '#show: letmeout\n' + math_fixture, "math-patched", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"math {fmt} changed"

# Fluid HTML pages drop the width cap; print settings still apply in PDF.
fluid_source = ('#set page(width: 400pt, margin: 20pt)\n'
                '#show: by-target(html: body => { set page(width: auto, margin: 1em); body })\nFluid')
fluid, _ = compile_source(IMPORT + '#show: letmeout\n' + fluid_source, "fluid", "html", page_rules=True)
assert not re.search(r'class="letmeout-page-sheet"[^>]*max-width:', fluid.read_text())
assert "padding-left: 11pt" in fluid.read_text()
fluid_pdf, _ = compile_source(IMPORT + '#show: letmeout\n' + fluid_source, "fluid", "pdf")
fluid_native, _ = compile_source('#set page(width: 400pt, margin: 20pt)\nFluid', "fluid-native", "pdf")
assert fluid_pdf.read_bytes() == fluid_native.read_bytes(), "HTML width changed PDF"

# Nested scopes merge color maps and frame policies through CSS inheritance.
theme_fixture = '''#theme(dark-colors: ((black, yellow), (white, rgb("242424"))), dark-frames: none)[
  outer #text(fill: red)[explicit]
  #grid(fill: white, stroke: black)[cell]
  #line(stroke: black)
  #html.frame[#rect()]
  #theme(dark-colors: ((black, lime),), dark-frames: "invert")[inner #html.frame[#rect()]]
  #theme[inherit #html.frame[#rect()]]
  restored
]
sibling
'''
themes, _ = compile_source(IMPORT + '#show: letmeout\n' + theme_fixture, "themes", "html")
theme_html = themes.read_text()
assert theme_html.count('<letmeout-theme ') == 3
assert '--letmeout-dark-ffffff: #242424' in theme_html
assert '--letmeout-dark-000000: #ffdc00' in theme_html
assert '--letmeout-dark-000000: #01ff70' in theme_html
assert '--letmeout-dark-frame-filter: none' in theme_html
assert '--letmeout-dark-frame-filter: invert(1) hue-rotate(180deg)' in theme_html
assert 'background: light-dark(#ffffff, var(--letmeout-dark-ffffff,' in theme_html
for fmt in ("pdf", "svg"):
    themed, _ = compile_source(IMPORT + theme_fixture, "themes", fmt)
    plain, _ = compile_source(IMPORT + '#let theme(body, ..args) = context body\n' + theme_fixture, "themes-native", fmt)
    assert themed.read_bytes() == plain.read_bytes(), f"theme changed paged {fmt}"
for name, args in (("frames", 'dark-frames: "bad"'), ("colors", 'dark-colors: ((black, 1),)')):
    _, error = compile_source(IMPORT + '#theme(' + args + ')[x]', "theme-invalid-" + name, "html", success=False)
    assert "letmeout:" in error

NATIVE = "#let letmeout(body, ..args) = body\n"
for fmt in ("pdf", "png"):
    native, _ = compile_source(NATIVE + page_fixture, "native-page", fmt)
    patched, _ = compile_source(IMPORT + page_fixture, "patched-page", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"{fmt} page output changed"

stray, _ = compile_source(IMPORT + '#show: letmeout\nA\n#pagebreak(to: "even")\nB', "stray-pagebreak", "html")
assert 'class="letmeout-pagebreak"' in stray.read_text() and "break-before: verso" in stray.read_text()
# Plain `set page` is read; a nested page inherits and folds its margins.
inherit, _ = compile_source(IMPORT + '#show: letmeout\n#set page(margin: 1cm)\nA\n'
                            '#page(margin: (top: 2cm), width: 400pt)[a]', "page-inherit", "html", page_rules=True)
inherit_parts = inherit.read_text().split('<section')[1:]
assert len(inherit_parts) == 2
assert "padding-left: 4.7619cqi" in inherit_parts[0]
assert "padding-left: 7.0866cqi" in inherit_parts[1] and "padding-top: 14.1732cqi" in inherit_parts[1]
# Page settings inside a `context` wrapper (a template show rule after
# `show: letmeout`) cannot become blocks. HTML shows an error and the content
# instead of failing; paged output stays native.
WRAPPER = '#let wrap(body) = context { body }\n'
for name, rule in (("call", '#show: page.with(paper: "a4")'), ("set", '#set page(margin: 1cm)')):
    source = '#show: letmeout\n' + WRAPPER + '#show: wrap\n' + rule + '\nwrapped text'
    wrapped, _ = compile_source(IMPORT + source, "wrapped-page-" + name, "html", page_rules=True)
    wrapped_html = wrapped.read_text()
    assert 'class="letmeout-error"' in wrapped_html and "wrapped text" in wrapped_html
    assert "wrapped text" not in "".join(wrapped_html.split("<section")[1:])
    assert re.search(r'class="letmeout-error-excerpt">[^<]*<q>wrapped text</q>', wrapped_html)
    for fmt in ("pdf", "svg"):
        native, _ = compile_source(NATIVE + IMPORT + source, "native-wrapped-" + name, fmt)
        patched, _ = compile_source(IMPORT + source, "patched-wrapped-" + name, fmt)
        assert native.read_bytes() == patched.read_bytes(), f"{fmt} wrapped page output changed"
# The excerpt quotes the first heading or paragraph, shortened, without math.
quoted, _ = compile_source(IMPORT + '#show: letmeout\n' + WRAPPER + '#show: wrap\n#set page(margin: 1cm)\n'
                           'Ein Absatz mit $U = R I$ und so viel Text, dass er nach sechzig Zeichen endet.',
                           "wrapped-excerpt", "html", page_rules=True)
assert '<q>Ein Absatz mit … und so viel Text, dass er nach sechzig…</q>' in quoted.read_text()
# Contexts without page settings stay in the block, inline ones in their paragraph.
plain_context, _ = compile_source(IMPORT + '#show: letmeout\n#set page(width: 300pt)\n' + WRAPPER +
                                  'A #context page.width B\n\n#show: wrap\nC', "context-plain", "html", page_rules=True)
plain_context_html = plain_context.read_text()
assert 'letmeout-error' not in plain_context_html and plain_context_html.count('<section') == 1
assert re.search(r'<p>A <code[^>]*>.*300pt.*</code> B</p>', plain_context_html)
# A set rule around a context keeps the context's marks, so the page converges.
styled_context, styled_err = compile_source(IMPORT + '#show: letmeout\n#show: page.with()\n#set text(fill: red)\n'
                                            + WRAPPER + '#show: wrap\nD', "context-styled", "html")
assert "did not converge" not in styled_err, styled_err
assert styled_context.read_text().count('class="letmeout-page"') == 1
# The wrapper is fine before `show: letmeout`.
outer, _ = compile_source(IMPORT + WRAPPER + '#show: wrap\n#show: letmeout\n#show: page.with(width: 300pt)\nX',
                          "wrapped-outside", "html", page_rules=True)
assert 'letmeout-error' not in outer.read_text() and "max-width: 300pt" in outer.read_text()
# Target-specific content and rules, as in the `bullseye` package.
targets = (IMPORT + '#show: letmeout\n#set page(margin: 3cm)\n#show: by-target(html: body => { set page(margin: (x: 1cm)); body })\n'
           '#set document(title: "Targets", date: none)\n'
           '#by-target(html: [only-html], paged: [only-paged])\n'
           '#page(margin: (top: 2cm))[nested]\n#show: by-target(html: body => { set page(margin: 0pt); body })\n'
           '#show: by-target(html: body => [html-rule #body], paged: body => body)\nB')
target_html, _ = compile_source(targets, "targets", "html", page_rules=True)
target_text = target_html.read_text()
target_parts = target_text.split('<section')[1:]
assert "<title>Targets</title>" in target_text, "set document after show-target"
assert "only-html" in target_text and "only-paged" not in target_text
assert len(target_parts) == 3, len(target_parts)
# HTML margins replace only the sides they name, like a later `set page`.
assert "padding-left: 4.7619cqi" in target_parts[0] and "padding-top: 14.2857cqi" in target_parts[0]
assert "padding-top: 9.5238cqi" in target_parts[1]
assert "padding-left: 0cqi" in target_parts[2] and "html-rule B" in target_parts[2]
native_targets = targets.replace(IMPORT, '').replace('#show: letmeout\n', '')
native_targets = re.sub(r'#show: by-target\(.*\)\n', '', native_targets)
native_targets = re.sub(r'#by-target\(.*\)', 'only-paged', native_targets)
for fmt in ("pdf", "png"):
    native, _ = compile_source(native_targets, "native-targets", fmt)
    patched, _ = compile_source(targets, "patched-targets", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"{fmt} target output changed"
# Without `show: letmeout`, the rules still apply through their context fallback.
plain, _ = compile_source(IMPORT + '#show: show-target(html: body => [html: #body])\nA',
                          "targets-plain", "html")
assert "html: A" in plain.read_text()
_, error = compile_source(IMPORT + '#show: by-target(1cm)\nA', "by-target-positional", "html", success=False)
assert "unexpected argument" in error, error
# A setting that is not given keeps the surrounding one, also `none` and `auto`.
kept, _ = compile_source(IMPORT + '#show: letmeout\n#set page(header: [Kept], fill: none)\n'
                         '#show: by-target(html: body => { set page(margin: 1cm); body })\nA', "target-page-kept", "html", page_rules=True)
assert "Kept" in kept.read_text() and "padding-left: 4.7619cqi" in kept.read_text()
# The one-target shortcuts accept native wrappers and content.
short_source = (IMPORT + '#show: letmeout\n#set page(paper: "a4", margin: 2.5cm)\n'
                '#set document(title: "Short target rules", date: none)\n'
                '#show: html-only(page.with(width: auto, margin: 1em))\n'
                '#html-only[web-only]#paged-only[print-only]')
short_html, _ = compile_source(short_source, "target-shortcuts", "html", page_rules=True)
assert not re.search(r'class="letmeout-page-sheet"[^>]*max-width:', short_html.read_text())
assert "padding-left: 11pt" in short_html.read_text()
assert "web-only" in short_html.read_text() and "print-only" not in short_html.read_text()
assert "<title>Short target rules</title>" in short_html.read_text()
short_native = '#set page(paper: "a4", margin: 2.5cm)\n#set document(title: "Short target rules", date: none)\nprint-only'
for fmt in ("pdf", "png", "svg"):
    native, _ = compile_source(short_native, "target-shortcuts-native", fmt)
    patched, _ = compile_source(short_source, "target-shortcuts", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"html-only affected {fmt}"

# Missing HTML function branches are identity; paged functions are selected only
# for PDF/PNG/SVG. Check the native page.with wrapper, including page geometry.
paged_source = (IMPORT + '#show: letmeout\n#show: paged-only(page.with(width: 400pt, margin: 20pt))\nA')
paged_html, _ = compile_source(paged_source, "target-paged", "html")
assert 'max-width: 595.2755905511812pt' in paged_html.read_text()
assert 'max-width: 400pt' not in paged_html.read_text()
for fmt in ("pdf", "png", "svg"):
    native, _ = compile_source('#show: page.with(width: 400pt, margin: 20pt)\nA', "target-paged-native", fmt)
    patched, _ = compile_source(paged_source, "target-paged", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"paged-only wrapper changed native {fmt}"

# A function shortcut also works without the document adapter.
plain_short, _ = compile_source(IMPORT + '#show: html-only(body => [web #body])\nA', "target-short-plain", "html")
assert "web A" in plain_short.read_text()
for branches in ('html: body => body, paged: [text]', 'html: [text], paged: body => body'):
    _, error = compile_source(IMPORT + '#by-target(' + branches + ')', "target-mixed", "html", success=False)
    assert "do not mix" in error
# Existing names stay usable.
aliases, _ = compile_source(IMPORT + '#on-target(html: [old-target])\n#on-scheme(light: [old-scheme])', "target-aliases", "html")
assert "old-target" in aliases.read_text() and "old-scheme" in aliases.read_text()
# The package does not shadow `page` or `pagebreak`, so set rules keep working.
compile_source(IMPORT + '#set page(margin: 1cm)\n#set pagebreak(weak: true)\nA', "native-set", "pdf")
# The paper table must match the compiler for every paper.
compile_source('#import "/src/papers.typ": papers\n#for (name, size) in papers {\n'
               '  page(paper: name, context assert(std.page.width == size.at(0) and std.page.height == size.at(1), message: name))\n}',
               "papers", "pdf")

# `show: letmeout` adapts elements that Typst's HTML export ignores.
adapters_fixture = (ROOT / "tests/adapters/test.typ").read_text()
adapters_html, _ = compile_source(IMPORT + "#show: letmeout\n" + adapters_fixture, "adapters", "html", page_rules=True, ignored=("h",))
adapters_text = adapters_html.read_text()
for cls in ("letmeout-h", "letmeout-v", "letmeout-pad", "letmeout-hide", "letmeout-rect", "letmeout-square",
            "letmeout-circle", "letmeout-ellipse", "letmeout-shape-paint", "letmeout-box", "letmeout-block",
            "letmeout-rotate", "letmeout-scale", "letmeout-skew", "letmeout-move", "letmeout-stack",
            "letmeout-stack-space", "letmeout-columns", "letmeout-colbreak", "letmeout-place"):
    assert f'class="{cls}"' in adapters_text, cls
for css in ("margin-inline-start: 28.346456692913385pt", "margin-inline-start: -2pt",
            "margin-top: -2pt", "padding-left: 28.346456692913385pt", "visibility: hidden", "transform: rotate(30deg)",
            "transform: scale(1.5, 1)", "zoom: 1.5", "transform: skew(-12deg, 0deg)", "left: 5pt; top: 5pt",
            "flex-direction: row", "flex-direction: column", "flex-direction: row-reverse", "flex: 1 1 0",
            "column-count: 2", "break-after: column", "position: absolute", "right: 0; bottom: 0",
            "margin-block: 1em", "border-radius: 25cqmin",
            "mask-composite: exclude", "mask-image: url(", "break-inside: avoid", "overflow: clip",
            "vertical-align: calc(-1 * 2pt)", "text-decoration-thickness: 1.5pt", "text-underline-offset: 2pt",
            "text-decoration-style: dotted", "text-decoration-line: line-through", "width: 28.346456692913385pt",
            "height: 28.346456692913385pt", "inset: calc(-1 * 3pt) calc(-1 * 3pt)"):
    assert css in adapters_text, css
assert "\u2212" not in adapters_text, "negative numbers use an ASCII minus"
assert adapters_text.count("<letmeout-frame>") == 2, "polygon and curve become frames"
assert '<div>A plain block.</div>' in adapters_text and '<span style="display: inline-block">plain box</span>' in adapters_text
assert '<span style="text-decoration: underline">native</span>' in adapters_text
assert adapters_text.count('class="letmeout-hide"') == 2 and '<div class="letmeout-hide"' in adapters_text
# Paged output is unchanged by the adapters.
for fmt in ("pdf", "png", "svg"):
    native, _ = compile_source(adapters_fixture, "adapters-native", fmt)
    patched, _ = compile_source(IMPORT + "#show: letmeout\n" + adapters_fixture, "adapters", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"adapters changed {fmt}"
# What CSS cannot express keeps Typst's native HTML, with its warning.
fallback, stderr = compile_source(IMPORT + "#show: letmeout\n#rect(fill: tiling(size: (5pt, 5pt), square(size: 2pt)))\n"
                                  "#h(1fr) #v(1fr) #scale(x: 2cm)[s] #box(fill: tiling(size: (5pt, 5pt), square(size: 2pt)))[t]",
                                  "adapters-fallback", "html", ignored=("rect", "h", "v", "scale"))
for element in ("rect", "h", "v", "scale"):
    assert f"{element} was ignored" in stderr, element
assert '<span style="display: inline-block">t</span>' in fallback.read_text()
# Without `show: letmeout`, Typst's native HTML is unchanged.
plain_adapters, stderr = compile_source(IMPORT + "#rect[r] #pad(1em)[p]", "adapters-plain", "html", ignored=("rect", "pad"))
assert "letmeout-" not in plain_adapters.read_text() and "rect was ignored" in stderr

# `letmeout-extras.page` is native `page`, with HTML notes in its documentation.
page_api = ('#import "/lib.typ": *\n#show: letmeout\n#show: letmeout-extras.page.with(paper: "a5", margin: 1cm, numbering: "1")\n'
            'A\n#letmeout-extras.page(fill: aqua, header: [H])[B]\nC')
page_native = ('#import "/lib.typ": *\n#show: letmeout\n#show: page.with(paper: "a5", margin: 1cm, numbering: "1")\n'
               'A\n#page(fill: aqua, header: [H])[B]\nC')
for fmt in ("pdf", "png", "svg", "html"):
    native, _ = compile_source(page_native, "page-api-native", fmt, page_rules=True)
    wrapped, _ = compile_source(page_api, "page-api", fmt, page_rules=True)
    assert native.read_bytes() == wrapped.read_bytes(), f"letmeout-extras.page changed {fmt}"
# Only element functions take set rules, so a wildcard import of letmeout-extras breaks `set page`.
_, error = compile_source('#import "/lib.typ": *\n#import letmeout-extras: *\n#set page(margin: 1cm)\nA', "page-shadowed", "pdf", success=False)
assert "only element functions" in error
compile_source('#import "/lib.typ": *\n#import letmeout-extras: *\n#set std.page(margin: 1cm)\nA', "page-std", "pdf")

# `letmeout-extras.pagebreak` is an alias of native `pagebreak`, so its output is identical.
pagebreak_api = '#import "/lib.typ": *\n#show: letmeout\nA\n#letmeout-extras.pagebreak(to: "odd")\nB'
pagebreak_native = '#import "/lib.typ": *\n#show: letmeout\nA\n#pagebreak(to: "odd")\nB'
for fmt in ("pdf", "png", "svg", "html"):
    native, _ = compile_source(pagebreak_native, "pagebreak-api-native", fmt)
    wrapped, _ = compile_source(pagebreak_api, "pagebreak-api", fmt)
    assert native.read_bytes() == wrapped.read_bytes(), f"letmeout-extras.pagebreak changed {fmt}"
# A wildcard import of letmeout-extras keeps `set pagebreak` and `show pagebreak` working, since the alias is the element.
compile_source('#import "/lib.typ": *\n#import letmeout-extras: *\n#set pagebreak(weak: true)\nA', "pagebreak-shadowed", "pdf")
compile_source('#import "/lib.typ": *\n#import letmeout-extras: *\n#show pagebreak: it => [X]\nA', "pagebreak-show-shadowed", "pdf")

print("PASS: HTML grid, line, align; content, styling, frames, paints, and diagnostics")
print("PASS: show: letmeout with set page, nested pages, pagebreaks, and paper sizes")
print("PASS: show: letmeout styles the screen: margin, color scheme, fonts, and frames")
print("PASS: scoped themes, fluid HTML pages, and native MathML for scripts, cases, matrices, fractions, roots, and accents")
print("PASS: by-target, html-only, paged-only, compatibility aliases, and native target page wrappers")
print("PASS: show: letmeout adapts shapes, boxes, spacing, transforms, stacks, columns, placement, and decorations")
print("PASS: letmeout-extras.page matches native page in every format")
print("PASS: PDF, PNG, and SVG identical to native Typst; styling and cells preserved")
