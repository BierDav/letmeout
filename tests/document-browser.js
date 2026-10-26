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
  check('Paragraph spacing follows Typst', Math.abs(paragraphs[1].getBoundingClientRect().top -
    paragraphs[0].getBoundingClientRect().bottom - 8) < 1);
  check('Paint layers do not add spacing before the first paragraph', Math.abs(paragraphs[0].getBoundingClientRect().top -
    paragraphs[0].closest('.letmeout-block').getBoundingClientRect().top) < 1);
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
  check('Vertical space adds to paragraph spacing', Math.abs(body.getBoundingClientRect().top - project.getBoundingClientRect().bottom - 56 / 3) < 1);
  const role = [...document.querySelectorAll('.letmeout-grid')].find(e => e.textContent.includes('Role label') && e.textContent.includes('School label'));
  const first = role.querySelector('[data-grid-x="0"][data-grid-y="0"]');
  const second = role.querySelector('[data-grid-x="0"][data-grid-y="1"]');
  check('Padded dates do not inflate the role row', Math.abs(first.getBoundingClientRect().height - (4 + 7 * 0.658) * 4 / 3) < 1);
  check('Role to school spacing follows the row gutter', Math.abs(second.getBoundingClientRect().top - first.getBoundingClientRect().bottom - 20 / 3) < 1);
  const names = ['Given name', 'Family name'].map(t =>
    [...document.querySelectorAll('.letmeout-text-block')].find(e => e.textContent === t));
  check('Stacked name blocks reserve native descenders', getComputedStyle(names[1]).textBoxTrim === 'trim-both' &&
    parseFloat(getComputedStyle(names[1]).paddingBlockEnd) > 0);
  check('Large names have no extra line-box gap', Math.abs(names[1].getBoundingClientRect().top -
    names[0].parentElement.getBoundingClientRect().bottom) < 1);
  const subtitle = [...document.querySelectorAll('p')].find(e => e.textContent === 'Display subtitle');
  check('Subtitle preserves explicit breathing room below descenders', Math.abs(subtitle.getBoundingClientRect().top -
    names[1].parentElement.getBoundingClientRect().bottom - 32 / 3) < 1);
  const metricName = [...document.querySelectorAll('.letmeout-text-block')].find(e => e.textContent === 'Display gyjq');
  const metricSubtitle = [...document.querySelectorAll('p')].find(e => e.textContent === 'Metric subtitle');
  const nameInk = metricName.querySelector('span');
  const subtitleInk = metricSubtitle.querySelector('span');
  const sameFont = (a, b) => ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle'].every(k =>
    getComputedStyle(a)[k] === getComputedStyle(b)[k]);
  check('Display trimming uses the visible font metrics', sameFont(metricName, nameInk));
  check('Subtitle trimming uses the visible font metrics', sameFont(metricSubtitle, subtitleInk));
  // Read actual glyph extents from the browser font, rather than treating a
  // line-box rectangle as proof that the ink cannot overlap its neighbour.
  const inkBounds = (container, ink) => {
    const marker = document.createElement('span');
    marker.style.cssText = 'display:inline-block;width:0;height:0;margin:0;padding:0;vertical-align:baseline';
    container.append(marker);
    const baseline = marker.getBoundingClientRect().top;
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.font = getComputedStyle(ink).font;
    const metrics = ctx.measureText(ink.textContent);
    marker.remove();
    return {top: baseline - metrics.actualBoundingBoxAscent, bottom: baseline + metrics.actualBoundingBoxDescent};
  };
  check('Display descenders and subtitle ink preserve their gap', inkBounds(metricSubtitle, subtitleInk).top -
    inkBounds(metricName, nameInk).bottom >= 10);
  const fallbackRule = [...document.styleSheets].flatMap(sheet => [...sheet.cssRules]).find(rule =>
    rule.conditionText === 'not (text-box-trim: trim-both)');
  check('Older browsers have a text-metric fallback', !!fallbackRule);
  const fallback = document.createElement('style');
  // Enable the generated fallback in this modern browser, while disabling
  // trimming itself. This tests the real rule rather than supplying a fix.
  fallback.textContent = '.letmeout-text-block, p { text-box-trim: none !important; }' +
    fallbackRule.cssText.replace('not (text-box-trim: trim-both)', '(display: block)');
  document.head.append(fallback);
  check('Untrimmed browser fallback keeps subtitle clear of descenders', inkBounds(metricSubtitle, subtitleInk).top -
    inkBounds(metricName, nameInk).bottom >= 10);
  fallback.remove();
  const textBlock = text => [...document.querySelectorAll('.letmeout-text-block')].find(e => e.textContent === text);
  const flow = ['Flow block A', 'Flow block B', 'Flow grid A', 'Flow grid B'].map(textBlock);
  check('Block and grid spacing add to strong vertical space', flow.slice(1).every((e, i) =>
    Math.abs(e.getBoundingClientRect().top - flow[i].getBoundingClientRect().bottom - 16) < 1));
  const explicitEdges = textBlock('Explicit edges');
  check('Explicit above overrides automatic grid spacing', Math.abs(explicitEdges.getBoundingClientRect().top -
    flow[3].getBoundingClientRect().bottom - 8 / 3) < 1);
  const afterZero = [...document.querySelectorAll('p')].find(e => e.textContent === 'After explicit zero');
  check('Explicit below zero overrides paragraph spacing', Math.abs(afterZero.getBoundingClientRect().top -
    explicitEdges.getBoundingClientRect().bottom) < 1);
  const wrapped = [...document.querySelectorAll('.letmeout-grid')].find(e => e.textContent.includes('Wrapped plain words'));
  const wrappedCells = [...wrapped.querySelectorAll('.letmeout-grid-cell')];
  check('Mixed-style wrapping keeps the same leading as plain text', Math.abs(
    wrappedCells[0].getBoundingClientRect().height - wrappedCells[1].getBoundingClientRect().height) < 1 &&
    Math.abs(parseFloat(getComputedStyle(wrappedCells[1].querySelector('p')).lineHeight) - 19.44) < 0.5);
  check('Grid row gutters survive mixed-style text', Math.abs(wrappedCells[2].getBoundingClientRect().top -
    wrappedCells[0].getBoundingClientRect().bottom - 28 / 3) < 1);
  const fractional = [...document.querySelectorAll('[data-fraction]')];
  check('Heading line stays in its growing box and paragraph', fractional[0].closest('p').textContent === 'Flexible heading' &&
    fractional[0].querySelector('.letmeout-line').getBoundingClientRect().width > 100);
  check('Fractional box baseline shifts raise the heading rule', parseFloat(getComputedStyle(fractional[0]).top) < 0);
  const near = (a, b) => Math.abs(a - b) < 1;
  for (const width of ['', '280px']) {
    document.body.style.width = width;
    check(`Fractional boxes share remaining width at ${width || 'desktop'}`, near(
      fractional[2].getBoundingClientRect().width, 2 * fractional[1].getBoundingClientRect().width));
    check(`Heading line fills only its box at ${width || 'desktop'}`, fractional.every(e => near(
      e.getBoundingClientRect().width, e.querySelector('.letmeout-line').getBoundingClientRect().width)));
  }
  document.body.style.width = '';
  const weak = ['Weak first', 'Weak second'].map(t => [...document.querySelectorAll('p')].find(e => e.textContent === t));
  check('Weak space collapses with the larger adjacent paragraph spacing', Math.abs(
    weak[1].getBoundingClientRect().top - weak[0].getBoundingClientRect().bottom - 16) < 1);
  const shorthand = textBlock('Spacing shorthand').closest('.letmeout-block');
  check('Block spacing shorthand resolves both edges', shorthand.style.getPropertyValue('--letmeout-above') === '5pt' &&
    shorthand.style.getPropertyValue('--letmeout-below') === '5pt');
  for (const [label, width, height] of [['Small frame follower', 320 / 3, 400 / 3], ['Narrow frame follower', 160 / 3, 200 / 3]]) {
    const follower = textBlock(label).closest('.letmeout-block');
    const image = follower.parentElement.querySelector('letmeout-frame > svg');
    check(`${label} preserves native frame size and aspect ratio`, near(image.getBoundingClientRect().width, width) &&
      near(image.getBoundingClientRect().height, height));
    check(`${label} preserves spacing after the visible frame`, near(follower.getBoundingClientRect().top -
      image.getBoundingClientRect().bottom, 12));
  }
  return { passed: checks.length, checks };
})()
