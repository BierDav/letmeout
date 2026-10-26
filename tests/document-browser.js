// Run on tests/output/document-adapters.html with T3 preview_evaluate.
(() => {
  const checks = [];
  const check = (name, ok) => {
    if (!ok) throw new Error(name);
    checks.push(name);
  };
  const title = [...document.querySelectorAll('span')].find(e => e.textContent === 'Display title');
  const font = getComputedStyle(title);
  check('Display typography survives', font.fontSize === '48px' && font.fontWeight === '300' &&
    font.fontStyle === 'italic' && parseFloat(font.letterSpacing) < 0);
  const cell = [...document.querySelectorAll('.letmeout-grid-cell-body')]
    .find(e => e.textContent === 'An inline title with spaces');
  const range = document.createRange();
  const textNodes = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
  const textRects = [];
  while (textNodes.nextNode()) {
    if (!textNodes.currentNode.textContent.trim()) continue;
    range.selectNodeContents(textNodes.currentNode);
    textRects.push(...range.getClientRects());
  }
  const rows = new Set(textRects.filter(r => r.width > 0).map(r => Math.round(r.y)));
  check('Inline words in grid cells share one line', rows.size === 1);
  const aligned = ['Top', 'Middle', 'Bottom'].map(t =>
    [...document.querySelectorAll('.letmeout-align')].find(e => e.textContent === t));
  const offsets = aligned.map(e => e.firstElementChild.getBoundingClientRect().y - e.getBoundingClientRect().y);
  check('Native alignment uses the available row height', offsets[0] < offsets[1] && offsets[1] < offsets[2]);
  const frame = document.querySelector('letmeout-frame > svg');
  check('Layout callbacks preserve the image', frame && frame.querySelector('image') && frame.getBoundingClientRect().height > 100);
  const chips = [...document.querySelectorAll('.letmeout-box')].filter(e => e.textContent.includes('chip'));
  check('All chips survive', chips.filter(e => e.textContent.includes('chip')).length === 5);
  for (const width of ['360px', '280px']) {
    document.body.style.width = width;
    const paints = chips.map(e => e.querySelector('.letmeout-shape-paint').getBoundingClientRect());
    check(`Chips wrap at ${width}`, new Set(paints.map(r => Math.round(r.y))).size > 1);
    check(`Wrapped paint layers stay apart at ${width}`, paints.every((a, i) => paints.slice(i + 1)
      .every(b => a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top)));
    check(`Page fits at ${width}`, document.documentElement.scrollWidth <= innerWidth);
  }
  document.body.style.width = '';
  const chipText = chips[0].querySelector('span[style*="font-size"]');
  const chipStyle = getComputedStyle(chips[0]);
  const natural = parseFloat(getComputedStyle(chipText).lineHeight);
  check('Chip padding excludes paragraph leading', Math.abs(chips[0].getBoundingClientRect().height -
    natural - parseFloat(chipStyle.paddingTop) - parseFloat(chipStyle.paddingBottom)) < 1);
  const link = document.querySelector('a[href="https://example.com/plain"]');
  check('Links have no automatic underline', getComputedStyle(link).textDecorationLine === 'none');
  const explicit = document.querySelector('a[href="https://example.com/underlined"] span[style*="text-decoration"]');
  check('Explicit link underlines survive', explicit && getComputedStyle(explicit).textDecorationLine === 'underline');
  const paragraphs = [...document.querySelectorAll('p')].filter(e => /^Paragraph (one|two)\.$/.test(e.textContent.trim()));
  check('Paragraph boundaries have no browser margins', getComputedStyle(paragraphs[0]).marginTop === '0px' &&
    getComputedStyle(paragraphs[1]).marginBottom === '0px');
  check('Line spacing uses font metrics plus Typst leading', Math.abs(parseFloat(getComputedStyle(paragraphs[0]).lineHeight) - 19.44) < 0.5);
  check('Paragraph spacing follows Typst', getComputedStyle(paragraphs[1]).marginTop === '8px');
  const fit = [...document.querySelectorAll('.letmeout-fit')].find(e => e.textContent.includes('Decorated image'));
  const scroller = fit.querySelector(':scope > .letmeout-scroll');
  check('Fitting grids let shadows overflow', getComputedStyle(scroller).overflow === 'visible');
  check('Rounded image clipping stays native', !!scroller.querySelector('svg clipPath'));
  document.body.style.width = '120px';
  check('Oversized grids still scroll', getComputedStyle(scroller).overflowX === 'auto' && scroller.scrollWidth > scroller.clientWidth);
  document.body.style.width = '';
  const contents = [...document.querySelectorAll('.letmeout-grid-cell-body')];
  const card = contents.find(e => e.textContent.includes('Section label'));
  const heading = card.querySelector('.letmeout-block');
  const company = [...card.querySelectorAll('.letmeout-grid')].find(e => e.textContent.includes('Company label'));
  check('Heading spacing is not stretched by a tall grid row', Math.abs(company.getBoundingClientRect().top - heading.getBoundingClientRect().bottom - 8) < 1);
  const project = [...card.querySelectorAll('p')].find(e => e.textContent.trim() === 'Project label');
  const body = [...card.querySelectorAll('p')].find(e => e.textContent.trim() === 'Project body.');
  check('Project spacing follows explicit vertical space', Math.abs(body.getBoundingClientRect().top - project.getBoundingClientRect().bottom - 8 / 3) < 1);
  const role = [...document.querySelectorAll('.letmeout-grid')].find(e => e.textContent.includes('Role label') && e.textContent.includes('School label'));
  const first = role.querySelector('[data-grid-x="0"][data-grid-y="0"]');
  const second = role.querySelector('[data-grid-x="0"][data-grid-y="1"]');
  check('Padded dates do not inflate the role row', Math.abs(first.getBoundingClientRect().height - (4 + 7 * 0.658) * 4 / 3) < 1);
  check('Role to school spacing follows the row gutter', Math.abs(second.getBoundingClientRect().top - first.getBoundingClientRect().bottom - 20 / 3) < 1);
  const names = ['Given name', 'Family name'].map(t =>
    [...document.querySelectorAll('.letmeout-text-block')].find(e => e.textContent === t));
  check('Stacked name blocks honor their own text edges', getComputedStyle(names[0]).textBoxEdge === 'text alphabetic' &&
    getComputedStyle(names[1]).textBoxEdge === 'cap text');
  check('Large names have no extra line-box gap', Math.abs(names[1].getBoundingClientRect().top -
    names[0].parentElement.getBoundingClientRect().bottom) < 1);
  return { passed: checks.length, checks };
})()
