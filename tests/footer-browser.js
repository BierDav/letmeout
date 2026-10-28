// Evaluate on tests/output/fractional-footer.html after running tests/check.py.
(() => {
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  const near = (a, b) => Math.abs(a - b) < 1;
  const footer = document.querySelector('footer p');
  check(footer, 'Single-line footer must participate in paragraph layout');
  const [left, spacer, right] = footer.children;
  const a = left.getBoundingClientRect(), b = right.getBoundingClientRect();
  const row = footer.getBoundingClientRect();
  check(near(a.top, b.top), 'Footer labels must stay on the same row');
  check(near(a.left, row.left) && near(b.right, row.right), 'Footer labels must reach opposite edges');
  check(spacer.getBoundingClientRect().width > 0, 'Footer spacer must consume remaining width');
  const spaces = [...document.querySelectorAll('p > .letmeout-h')].filter(e => !e.closest('footer'));
  check(near(spaces[1].getBoundingClientRect().width, 2 * spaces[0].getBoundingClientRect().width),
    'Fractional spaces must share remaining width in a 1:2 ratio');
  check(document.documentElement.scrollWidth <= innerWidth, 'Fractional spacing must fit the viewport');
  return {passed: 5};
})()
