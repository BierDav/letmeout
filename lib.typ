// Import with `: *` to bridge layout functions to HTML.
#import "src/grid.typ": grid
#import "src/line.typ": line
#import "src/align.typ": align
#import "src/document.typ": letmeout
// Content, show rules, and page settings for one export target.
#import "src/target.typ": on-target, show-target, html-page
// Typst functions cannot inherit another function's associated definitions.
// These native element aliases also support set/show rules and .with().
#let grid-cell = std.grid.cell
#let grid-hline = std.grid.hline
#let grid-vline = std.grid.vline
#let grid-header = std.grid.header
#let grid-footer = std.grid.footer
