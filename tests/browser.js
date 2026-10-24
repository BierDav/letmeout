// Run this expression with T3 preview_evaluate on tests/output/features.html.
(() => {
  const checks = [];
  const check = (name, condition) => {
    if (!condition) throw new Error(name);
    checks.push(name);
  };
  const box = element => element.getBoundingClientRect();
  const near = (a, b) => Math.abs(a - b) < 1;
  const aligns = [...document.querySelectorAll('.letmeout-align')];
  const vertical = ['Top', 'Middle', 'Bottom'].map(text =>
    aligns.find(element => element.textContent.trim() === text));
  const offsets = vertical.map(element => box(element.firstElementChild).y - box(element).y);
  check('Vertical alignment uses the grid row height',
    offsets[0] < offsets[1] && offsets[1] < offsets[2] && offsets[2] > 80);
  const rtl = aligns.filter(element => element.dir === 'rtl');
  check('Logical start/end flip in RTL; physical left/right stay fixed',
    box(rtl[0].firstElementChild).x > box(rtl[1].firstElementChild).x &&
    near(box(rtl[2].firstElementChild).x, box(rtl[2]).x) &&
    near(box(rtl[3].firstElementChild).right, box(rtl[3]).right));
  const lines = [...document.querySelectorAll('.letmeout-line')];
  const full = lines[1];
  check('A 100% line fills its container',
    near(box(full).width, box(full.querySelector('.letmeout-stroke')).width));
  const previousWidth = document.body.style.width;
  document.body.style.width = '360px';
  check('Percentage line resizes at narrow widths',
    near(box(full).width, 360) && near(box(full.querySelector('.letmeout-stroke')).width, 360));
  document.body.style.width = previousWidth;
  const erased = [...document.querySelectorAll('.letmeout-grid')].find(element =>
    element.textContent.includes('No top border'));
  check('An explicit none line removes underlying cell strokes',
    !erased.querySelector('.letmeout-grid-hline[data-grid-index="0"][data-grid-after="false"]'));
  check('Grid gradient strokes use CSS paint',
    [...erased.querySelectorAll('.letmeout-stroke-paint')].some(element =>
      getComputedStyle(element).backgroundImage.startsWith('linear-gradient(')));
  check('Generated wrappers preserve links', document.querySelector('a[href="https://typst.app"]'));
  check('Line geometry uses supported CSS math',
    CSS.supports('width', 'hypot(3px, 4px)') &&
    CSS.supports('transform', 'rotate(atan2(3px, 4px))'));
  return { passed: checks.length, checks };
})()
