#!/usr/bin/env node
// Re-measure section heights of the BUILT clone at 1440px (R9). Optional tool:
// verify_all.py never runs it; it only reads what this script recorded in
// extraction/measured-values.json -> sectionHeights.
//
//   npx vite build --outDir <scratch>/dist && npx vite preview --outDir <scratch>/dist --port <port>
//   NODE_PATH="$(npm root -g)" node design-repo/extraction/measure_sections.mjs --url http://localhost:<port>/ [--write]
//
// Playwright is resolved through NODE_PATH (or PLAYWRIGHT_MODULE); no machine
// path is stored in this repo. --write updates measured-values.json in place.
import { createRequire } from 'module'
import { readFileSync, writeFileSync } from 'fs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const REPO = dirname(dirname(fileURLToPath(import.meta.url)))
const args = process.argv.slice(2)
const url = args.includes('--url') ? args[args.indexOf('--url') + 1] : null
if (!url) { console.error('usage: measure_sections.mjs --url http://localhost:<port>/ [--write]'); process.exit(2) }
const req = createRequire(import.meta.url)
const { chromium } = req(process.env.PLAYWRIGHT_MODULE || 'playwright')

const templates = JSON.parse(readFileSync(join(REPO, 'templates/templates.json'), 'utf8')).templates
const graph = JSON.parse(readFileSync(join(REPO, 'compatibility/graph.json'), 'utf8'))
const VIEWPORT = { width: 1440, height: 900 }

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: VIEWPORT })
const out = { viewport: VIEWPORT, measuredOn: new Date().toISOString().slice(0, 10), method: 'Playwright chromium, built clone (vite build + vite preview), networkidle + 2.5s settle, getBoundingClientRect().height of the in-flow wrapper of each node (the Handoff wrapper where one exists)', pages: {} }
for (const [tid, t] of Object.entries(templates)) {
  for (const route of t.routes) {
    await page.goto(new URL(route, url).href, { waitUntil: 'networkidle' })
    await page.waitForTimeout(2500)
    // nodes are located by their anchor id; the dark transition (graph
    // toneModel.handoffSection) has none and is located by the trigger it hosts,
    // #overview-screen-trigger (README structural notes; src/components/DarkTransition.jsx).
    const spec = t.nodes.map((n) => ({ section: n.section, region: n.region, anchorId: n.anchorId }))
    if (!t.nodes.some((n) => n.section === graph.toneModel.handoffSection)) throw new Error('template has no handoff section')
    const trig = 'overview-screen-trigger'
    const res = await page.evaluate(({ spec, trig }) => {
      const main = document.querySelector('main')
      const wrapperOf = (el) => { let e = el; while (e && e.parentElement && e.parentElement.parentElement !== main) e = e.parentElement; return e }
      const sections = {}
      for (const n of spec) {
        let el = null
        if (n.region === 'header') el = document.querySelector('header')
        else if (n.region === 'footer') el = document.querySelector('footer')
        else if (n.anchorId) el = wrapperOf(document.getElementById(n.anchorId))
        else el = wrapperOf(document.getElementById(trig))
        if (!el) { sections[n.section] = null; continue }
        const cs = getComputedStyle(el)
        sections[n.section] = { heightPx: Math.round(el.getBoundingClientRect().height * 100) / 100, position: cs.position, tag: el.tagName.toLowerCase() }
      }
      return { pageHeightPx: document.documentElement.scrollHeight, sections }
    }, { spec, trig })
    out.pages[tid] = { route, ...res }
  }
}
await browser.close()
if (args.includes('--write')) {
  const p = join(REPO, 'extraction/measured-values.json')
  const mv = JSON.parse(readFileSync(p, 'utf8'))
  mv.sectionHeights = out
  writeFileSync(p, JSON.stringify(mv, null, 2) + '\n')
  console.log('wrote sectionHeights for', Object.keys(out.pages).join(', '))
} else console.log(JSON.stringify(out, null, 2))
