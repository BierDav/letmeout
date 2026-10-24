// `#show: letmeout` lets the native `page` APIs shape the HTML document:
// `set page`, `page(..)[..]`, `show: page.with(..)`, and `pagebreak`.
// Set rules run no code and their styles cannot be inspected, so the document
// is probed: an invisible probe under every style node records the page
// settings in effect there. The document is split into page blocks only where
// those settings change, so other set rules never break the content apart.
#import "css.typ": direction
#import "target.typ": resolve
#import "page.typ": kind, visible-count, merge-args, settings, section, html-pagebreak

#let probe-label = <letmeout-probe>

// The raw page settings. Two places share a page block when these are equal.
#let page-key() = (
  width: std.page.width, height: std.page.height, flipped: std.page.flipped,
  margin: std.page.margin, binding: std.page.binding, columns: std.page.columns,
  fill: std.page.fill, numbering: std.page.numbering, number-align: std.page.number-align,
  header: std.page.header, header-ascent: std.page.header-ascent,
  footer: std.page.footer, footer-descent: std.page.footer-descent,
  background: std.page.background, foreground: std.page.foreground,
)

#let probe-value() = (
  key: page-key(), lang: text.lang, dir: direction(), gutter: std.columns.gutter,
)

#let wrap-all(body, wraps) = wraps.rev().fold(body, (acc, w) => w.at(0)(acc, w.at(1)))

// Style nodes get ids in pre-order. `runs` walks the same nodes in the same order.
#let probes(it, wraps, next) = {
  let k = kind(it)
  if k == "sequence" {
    let items = ()
    for child in it.children {
      let r = probes(child, wraps, next)
      items += r.items
      next = r.next
    }
    return (items: items, next: next)
  }
  if k == "styled" {
    let inner = wraps + ((it.func(), it.styles),)
    let id = next
    let probe = wrap-all(context [#metadata((id: id) + probe-value())#probe-label], inner)
    let r = probes(it.child, inner, next + 1)
    return (items: (probe,) + r.items, next: r.next)
  }
  (items: (), next: next)
}

#let block-of(item) = {
  if visible-count(item.body) == 0 { return item.body }
  let s = settings(merge-args((:), item.info.key))
  s.gutter = item.info.gutter
  section(s, item.body, true, true, lang: item.info.lang, dir: item.info.dir)
}

// Render runs of equal page settings as blocks. A style node whose subtree
// changes the page settings is kept outside the blocks and wraps them: Typst
// does not allow page styles inside an HTML element.
#let parts(it, info, found, next) = {
  let k = kind(it)
  if k == "sequence" {
    let items = ()
    for child in it.children {
      let r = parts(child, info, found, next)
      next = r.next
      for item in r.items {
        if (item.kind == "flow" and items.len() > 0 and items.last().kind == "flow"
          and items.last().info.key == item.info.key) {
          let last = items.pop()
          items.push(last + (body: last.body + item.body))
        } else { items.push(item) }
      }
    }
    return (items: items, next: next)
  }
  if k == "styled" {
    // Before the probes are measured, assume that every node changes the
    // page settings, so no page style ever lands inside a block.
    let probed = found.at(str(next), default: none)
    let own = if probed == none { info } else { probed }
    let r = parts(it.child, own, found, next + 1)
    if probed != none and r.items.all(i => i.kind == "flow" and i.info.key == info.key) {
      // Keep the original node, so its set rules stay inside one block.
      return (items: ((kind: "flow", body: it, info: own),), next: r.next)
    }
    let rendered = r.items.map(i => if i.kind == "flow" { block-of(i) } else { i.body }).join()
    return (items: ((kind: "content", body: it.func()(rendered, it.styles)),), next: r.next)
  }
  (items: ((kind: "flow", body: it, info: info),), next: next)
}

#let html-document(body) = {
  let root = probe-value()
  // Probes render nothing. Their values are read back below.
  probes(body, (), 0).items.join()
  context {
    let found = (:)
    for m in query(probe-label) { found.insert(str(m.value.id), m.value) }
    let items = parts(body, root, found, 0).items
    if items.len() == 0 { items = ((kind: "flow", body: [], info: root),) }
    for item in items {
      if item.kind == "flow" { block-of(item) } else { item.body }
    }
  }
}

// Leading set rules stay outermost. Typst requires `set document` before any
// content, so it must not end up inside a page block.
#let hoist(body) = {
  let k = kind(body)
  if k == "sequence" {
    let children = body.children
    while children.len() > 0 and kind(children.first()) in ("space", "parbreak") {
      children = children.slice(1)
    }
    if children.len() == 1 { return hoist(children.first()) }
  }
  if k == "styled" { return body.func()(hoist(body.child), body.styles) }
  context html-document(body)
}

// Paged output returns the document untouched.
#let letmeout(body) = context {
  if target() != "html" { return body }
  show std.pagebreak: it => context {
    if target() == "html" { html-pagebreak(it) } else { it }
  }
  // Native `page` calls add an invisible flush. Blocks already end the page.
  show place.flush: it => context { if target() != "html" { it } }
  hoist(resolve(body))
}
