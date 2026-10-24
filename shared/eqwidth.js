#!/usr/bin/env node
// eqwidth.js -- desktop-first calibration check for display equations and
// data tables.
//
// Loads each page in a headless browser at a viewport wide enough for the
// full reading column (the "normal" width: the column is capped at 46rem by
// shared/kit.css, so every viewport from about 800px up gives the same
// layout) and measures, against the inner width of its card, the ink of
// every display equation -- each row of an aligned group (align*, gather*)
// counts as one equation -- and the width of every data table.  Anything
// above the threshold is too wide for the page: the fix is breaking the
// equation (or re-laying the table) in the source, never scrolling or
// scaling it.  course.py runs this as part of the check suite.
//
//   node shared/eqwidth.js --threshold 0.90 --viewport 1280x1024 file:///...html ...
//
// Output: one JSON line {equations, tables, threshold, max, maxTable,
// over:[...]}; exit 0 when everything is within the threshold, 2 when
// something is over, 1 on a technical failure (browser launch etc.).  Needs
// puppeteer -- the copy that ships with pa11y is enough: course.py puts it on
// NODE_PATH -- and honors PUPPETEER_EXECUTABLE_PATH for the browser.
//
// Markup, as BookML emits it: every display equation sits in a box carrying
// the class bml_equation_container -- a lone equation is its own box and
// holds one <math display="block">, whose block box fills the column while
// its children carry the ink; an aligned group is one box holding a row
// (.ltx_equation) per equation, each row a run of cells with inline <math>.
// A row's ink runs from the leftmost to the rightmost of its maths.

const args = process.argv.slice(2);
let threshold = 0.9, viewport = [1280, 1024];
const urls = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--threshold') threshold = parseFloat(args[++i]);
  else if (args[i] === '--viewport') viewport = args[++i].split('x').map(Number);
  else urls.push(args[i]);
}

const puppeteer = require('puppeteer');

(async () => {
  const launch = { headless: true, args: ['--allow-file-access-from-files'] };
  if (process.env.PUPPETEER_EXECUTABLE_PATH) launch.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
  const browser = await puppeteer.launch(launch);
  const page = await browser.newPage();
  await page.setViewport({ width: viewport[0], height: viewport[1] });
  const rows = [];
  for (const url of urls) {
    await page.goto(url, { waitUntil: 'load' });
    const found = await page.evaluate(() => {
      const out = [];
      const innerOf = el => {
        const card = el.closest('section.ltx_subsection') || el.closest('.ltx_page_main') || document.body;
        const cr = card.getBoundingClientRect(), cs = getComputedStyle(card);
        return cr.width - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0);
      };
      // the horizontal extent of a set of elements: leftmost edge to rightmost
      const extent = els => {
        let l = Infinity, r = -Infinity;
        for (const e of els) {
          const b = e.getBoundingClientRect();
          if (b.width > 0) { l = Math.min(l, b.left); r = Math.max(r, b.right); }
        }
        return r > l ? r - l : 0;
      };
      const push = (kind, ink, inner, alt) => out.push({
        kind, ink: Math.round(ink), inner: Math.round(inner),
        ratio: inner ? Math.round(1000 * ink / inner) / 1000 : 0, alt: alt.slice(0, 60) });
      document.querySelectorAll('.bml_equation_container').forEach(box => {
        const inner = innerOf(box);
        const eqRows = box.querySelectorAll('.ltx_equation');   // the rows of an aligned group
        for (const row of (eqRows.length ? eqRows : [box])) {
          const maths = [...row.querySelectorAll('math')];
          if (!maths.length) continue;
          const els = maths.flatMap(m => m.getAttribute('display') === 'block' ? [...m.children] : [m]);
          push('equation', extent(els), inner, maths.map(m => m.getAttribute('alttext') || '').join(' '));
        }
      });
      // data tables: the table's own width
      document.querySelectorAll('table.ltx_tabular').forEach(t => {
        if (t.parentElement.closest('table.ltx_tabular')) return;   // nested: the outer one counts
        push('table', t.getBoundingClientRect().width, innerOf(t),
             'table: ' + (t.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 50));
      });
      return out;
    });
    for (const x of found) rows.push({ page: url.split('/').pop(), ...x });
  }
  await browser.close();
  const over = rows.filter(x => x.ratio > threshold).sort((a, b) => b.ratio - a.ratio);
  const maxOf = kind => rows.filter(x => x.kind === kind).reduce((a, b) => (!a || b.ratio > a.ratio ? b : a), null);
  console.log(JSON.stringify({ equations: rows.filter(x => x.kind === 'equation').length,
                               tables: rows.filter(x => x.kind === 'table').length,
                               threshold, max: maxOf('equation'), maxTable: maxOf('table'), over }));
  process.exit(over.length ? 2 : 0);
})().catch(e => { console.error(String((e && e.stack) || e)); process.exit(1); });
