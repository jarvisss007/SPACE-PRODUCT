// Golapada site checks: opens every built page in a real (headless) Chrome and fails loudly if
//   * the page's own script crashes (an uncaught error),
//   * a phone-width screen (375 px) has to scroll sideways,
//   * any row in a page's own checks table has turned red (class "bad" inside a "For experts" fold
//     or a table whose id contains "check"/"chk"),
//   * a page's HTML grows past its size budget.
// It also reports, without failing: console errors (often a live data feed being down), amber
// checks, and how long each page takes to load on a slow 4G phone (CPU slowed 4x).
//
// Runs on GitHub (see .github/workflows/site-checks.yml). Needs Node and Playwright there:
//   npm i --no-save playwright && npx playwright install --with-deps chromium
//   node tools/check_site.mjs            (all pages)   node tools/check_site.mjs tonight.html
import { createServer } from "node:http";
import { readFileSync, readdirSync, statSync, appendFileSync, existsSync } from "node:fs";
import { join, extname } from "node:path";
import { chromium } from "playwright";

const ROOT = new URL("../docs/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const KB = 1024;
const BUDGET = 250 * KB; // per page HTML
// Pages allowed over budget for now, each with a reason and the size it must not grow past.
const EXEMPT = {
  "spacecraft-archive.html": [960 * KB, "carries its whole mission catalogue inline; to be split into a data file"],
  "exoplanet-explorer.html": [720 * KB, "carries the planet catalogue inline; to be split into a data file"],
};
const SLOW4G = { offline: false, latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 };
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".json": "application/json", ".png": "image/png",
  ".webmanifest": "application/manifest+json", ".zip": "application/zip", ".css": "text/css", ".svg": "image/svg+xml" };

const server = createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (p.endsWith("/")) p += "index.html";
  const f = join(ROOT, p);
  if (!f.startsWith(ROOT) || !existsSync(f) || statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "content-type": TYPES[extname(f)] || "application/octet-stream" });
  res.end(readFileSync(f));
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${server.address().port}/`;

const only = process.argv.slice(2);
const pages = readdirSync(ROOT).filter((f) => f.endsWith(".html") && f !== "404.html" && (!only.length || only.includes(f))).sort();

// what to look at inside a loaded page (runs in the browser)
const PROBE = () => {
  const W = document.documentElement.clientWidth;
  const sideways = document.documentElement.scrollWidth - W;
  const culprits = [...document.querySelectorAll("body *")]
    .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > W + 1 && !e.closest(".scroll,.sa-in,.sa-panel"); })
    .slice(0, 3).map((e) => `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""}${e.className && typeof e.className === "string" ? "." + e.className.trim().split(/\s+/).join(".") : ""}`);
  const zones = [...document.querySelectorAll('details.gx, table[id*="check" i], table[id*="chk" i]')];
  const red = new Set(), amber = new Set();
  zones.forEach((z) => { z.querySelectorAll(".bad").forEach((e) => red.add(e)); z.querySelectorAll(".mid").forEach((e) => amber.add(e)); });
  const row = (e) => ((e.closest("tr") || e).textContent || "").replace(/\s+/g, " ").trim().slice(0, 140);
  return { sideways, culprits, red: [...red].map(row), amber: amber.size };
};

const browser = await chromium.launch();
const fails = [], warns = [], rows = [];
for (const page of pages) {
  const size = statSync(join(ROOT, page)).size;
  const [limit, why] = EXEMPT[page] || [BUDGET, ""];
  if (size > limit) fails.push(`${page}: ${Math.round(size / KB)} KB is over its ${Math.round(limit / KB)} KB budget${why ? ` (${why})` : ""}`);

  // 1) phone: slow 4G and a slower CPU, timed; then the checks
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const tab = await ctx.newPage();
  const crashes = [], consoleErrors = [];
  tab.on("pageerror", (e) => crashes.push(String(e.message || e).slice(0, 200)));
  tab.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160)); });
  const cdp = await ctx.newCDPSession(tab);
  await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", SLOW4G);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  const t0 = Date.now();
  let loadMs = null;
  try { await tab.goto(BASE + page, { waitUntil: "load", timeout: 60000 }); loadMs = Date.now() - t0; }
  catch (e) { fails.push(`${page}: did not finish loading on slow 4G within 60 s`); }
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 1 });
  await tab.waitForTimeout(2500); // let the page compute and draw
  const lcp = await tab.evaluate(() => new Promise((r) => {
    let v = null; try { new PerformanceObserver((l) => { const e = l.getEntries(); if (e.length) v = e[e.length - 1].startTime; }).observe({ type: "largest-contentful-paint", buffered: true }); } catch (_) {}
    setTimeout(() => r(v), 300);
  }));
  const p = await tab.evaluate(PROBE);
  await ctx.close();

  // 2) desktop: crashes only
  const ctx2 = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const tab2 = await ctx2.newPage();
  tab2.on("pageerror", (e) => crashes.push(`[desktop] ${String(e.message || e).slice(0, 200)}`));
  try { await tab2.goto(BASE + page, { waitUntil: "load", timeout: 30000 }); await tab2.waitForTimeout(1500); } catch (_) {}
  await ctx2.close();

  if (crashes.length) fails.push(`${page}: script error: ${[...new Set(crashes)].join(" | ")}`);
  if (p.sideways > 1) fails.push(`${page}: scrolls sideways by ${p.sideways}px on a 375px phone (widest: ${p.culprits.join(", ")})`);
  for (const r of p.red) fails.push(`${page}: red check: ${r}`);
  if (p.amber) warns.push(`${page}: ${p.amber} amber check(s)`);
  const ce = [...new Set(consoleErrors)].filter((m) => !/Failed to load resource/.test(m));
  if (ce.length) warns.push(`${page}: console: ${ce.slice(0, 2).join(" | ")}`);
  rows.push([page, Math.round(size / KB), loadMs, lcp == null ? null : Math.round(lcp), p.red.length ? "red" : p.amber ? "amber" : "ok"]);
  console.log(`${p.red.length || crashes.length || p.sideways > 1 ? "FAIL" : "ok  "} ${page}  ${Math.round(size / KB)} KB  load ${loadMs ?? "—"} ms  LCP ${lcp == null ? "—" : Math.round(lcp)} ms`);
}
await browser.close();
server.close();

const s = (ms) => (ms == null ? "—" : (ms / 1000).toFixed(1) + " s");
const md = [
  `## Golapada site checks: ${fails.length ? `${fails.length} problem(s)` : "all clear"}`, "",
  `${pages.length} pages. Load times are on a simulated slow 4G phone (1.6 Mbit/s, 150 ms, CPU slowed 4x).`, "",
  ...(fails.length ? ["### Problems", ...fails.map((f) => `- ${f}`), ""] : []),
  ...(warns.length ? ["### Notes (not failures)", ...warns.map((w) => `- ${w}`), ""] : []),
  "| Page | Size | Load | Largest paint | Checks |", "|---|---:|---:|---:|---|",
  ...rows.sort((a, b) => (b[2] ?? 0) - (a[2] ?? 0)).map(([p, kb, l, c, st]) => `| ${p} | ${kb} KB | ${s(l)} | ${s(c)} | ${st} |`),
].join("\n");
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, md + "\n");
console.log("\n" + md);
process.exit(fails.length ? 1 : 0);
