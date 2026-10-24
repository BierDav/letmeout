#!/usr/bin/env python3
"""Compile real fixtures, inspect HTML, and compare paged exports to native Typst."""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/output"
OUTPUT.mkdir(exist_ok=True)


# Typst reports every `set page` in HTML, and packages cannot silence it.
PAGE_WARNING = "page set rule was ignored"


def compile_source(source, name, fmt, success=True, page_rules=False):
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


IMPORT = '#import "/lib.typ": *\n'
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
    'background: #fbf8f1', 'background: #1d2b3a', 'background: #eeeeff',
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
assert "4. Set rule" in parts[5] and "background: #eeeeff" in parts[5]

NATIVE = "#let letmeout(body) = body\n"
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
# Target-specific content and rules, as in the `bullseye` package.
targets = (IMPORT + '#show: letmeout\n#set page(margin: 3cm)\n#show: html-page(margin: (x: 1cm))\n'
           '#set document(title: "Targets", date: none)\n'
           '#on-target(html: [only-html], paged: [only-paged])\n'
           '#page(margin: (top: 2cm))[nested]\n#show: html-page(margin: 0pt)\n'
           '#show: show-target(html: body => [html-rule #body], paged: body => body)\nB')
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
native_targets = re.sub(r'#show: html-page\(.*\)\n', '', native_targets)
native_targets = re.sub(r'#on-target\(.*\)', 'only-paged', native_targets)
native_targets = re.sub(r'#show: show-target\(.*\)\n', '', native_targets)
for fmt in ("pdf", "png"):
    native, _ = compile_source(native_targets, "native-targets", fmt)
    patched, _ = compile_source(targets, "patched-targets", fmt)
    assert native.read_bytes() == patched.read_bytes(), f"{fmt} target output changed"
# Without `show: letmeout`, the rules still apply through their context fallback.
plain, _ = compile_source(IMPORT + '#show: show-target(html: body => [html: #body])\nA',
                          "targets-plain", "html")
assert "html: A" in plain.read_text()
_, error = compile_source(IMPORT + '#show: html-page(1cm)\nA', "html-page-positional", "html", success=False)
assert "unexpected argument" in error, error
# A setting that is not given keeps the surrounding one, also `none` and `auto`.
kept, _ = compile_source(IMPORT + '#show: letmeout\n#set page(header: [Kept], fill: none)\n'
                         '#show: html-page(margin: 1cm)\nA', "html-page-kept", "html", page_rules=True)
assert "Kept" in kept.read_text() and "padding-left: 4.7619cqi" in kept.read_text()
# The package does not shadow `page` or `pagebreak`, so set rules keep working.
compile_source(IMPORT + '#set page(margin: 1cm)\n#set pagebreak(weak: true)\nA', "native-set", "pdf")
# The paper table must match the compiler for every paper.
compile_source('#import "/src/papers.typ": papers\n#for (name, size) in papers {\n'
               '  page(paper: name, context assert(std.page.width == size.at(0) and std.page.height == size.at(1), message: name))\n}',
               "papers", "pdf")

print("PASS: HTML grid, line, align; content, styling, frames, paints, and diagnostics")
print("PASS: show: letmeout with set page, nested pages, pagebreaks, and paper sizes")
print("PASS: on-target, show-target, and html-page in HTML and paged output")
print("PASS: PDF, PNG, and SVG identical to native Typst; styling and cells preserved")
