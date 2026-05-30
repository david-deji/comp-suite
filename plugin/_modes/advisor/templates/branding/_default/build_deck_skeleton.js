// =============================================================================
// build_deck_skeleton.js — masters-only registration boilerplate
// =============================================================================
// Use this INSTEAD OF build_template.js when you are building deck content
// inline (e.g. from a skill-generated script) rather than opening the
// regenerated template in PowerPoint. This file registers all masters via
// defineMaster() only — no demo slides are added, so your pres object starts
// clean and every subsequent addSlide() call produces real content.
//
// USAGE
//   const { pres, deps } = require('./build_deck_skeleton');
//   const s = pres.addSlide({ masterName: '01_TITLE' });
//   // ... add content ...
//   pres.writeFile({ fileName: 'my-deck.pptx' });
// =============================================================================

const fs   = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { makeHelpers } = require("./masters/_helpers");

const INCLUDE_LAYOUT_TAGS = false;   // skeleton never shows breadcrumbs
const ORG = process.env.ORG || "_default";
const ROOT         = __dirname;                            // branding/_default
const BRANDING_ROOT = path.dirname(ROOT);                  // branding/
const ORG_ROOT     = path.join(BRANDING_ROOT, ORG);        // branding/<org>

// ---------------------------------------------------------------------------
// 1. Theme resolution — same deep-merge logic as build_template.js
// ---------------------------------------------------------------------------
function loadJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }

function resolveThemeFile(filename) {
  const orgPath     = path.join(ORG_ROOT, "theme", filename);
  const defaultPath = path.join(ROOT, "theme", filename);
  return fs.existsSync(orgPath) ? orgPath : defaultPath;
}

function deepMerge(base, over) {
  if (over === undefined) return base;
  if (typeof base !== "object" || base === null) return over;
  if (typeof over !== "object" || over === null) return over;
  const out = { ...base };
  for (const k of Object.keys(over)) {
    out[k] = deepMerge(base[k], over[k]);
  }
  return out;
}

const paletteDefault = loadJson(path.join(ROOT, "theme", "palette.json"));
const typoDefault    = loadJson(path.join(ROOT, "theme", "typography.json"));
const paletteOrg = fs.existsSync(path.join(ORG_ROOT, "theme", "palette.json"))
  ? loadJson(path.join(ORG_ROOT, "theme", "palette.json")) : {};
const typoOrg = fs.existsSync(path.join(ORG_ROOT, "theme", "typography.json"))
  ? loadJson(path.join(ORG_ROOT, "theme", "typography.json")) : {};

const C = deepMerge(paletteDefault, paletteOrg);
const F = deepMerge(typoDefault, typoOrg);

const logoPaths = {
  large:      resolveThemeFile("logo-large.png"),
  small:      resolveThemeFile("logo-small.png"),
  whiteLarge: resolveThemeFile("logo-white-large.png"),
  whiteSmall: resolveThemeFile("logo-white-small.png"),
  svg:        resolveThemeFile("logo.svg")
};

// ---------------------------------------------------------------------------
// 2. Presentation init
// ---------------------------------------------------------------------------
const pres = new pptxgen();
pres.layout  = "LAYOUT_WIDE";   // 13.3" × 7.5"
pres.author  = process.env.AUTHOR  || "Compensation Team";
pres.company = process.env.COMPANY || ORG;
pres.title   = process.env.TITLE   || "Compensation Deck";

const helpers = makeHelpers(C, F, logoPaths, INCLUDE_LAYOUT_TAGS);
const deps = { pres, C, F, helpers, logoPaths };

// ---------------------------------------------------------------------------
// 3. Register all masters via defineMaster() — no demo slides
// ---------------------------------------------------------------------------
function resolveMaster(filename) {
  const orgPath     = path.join(ORG_ROOT, "masters", filename);
  const defaultPath = path.join(ROOT, "masters", filename);
  return fs.existsSync(orgPath) ? orgPath : defaultPath;
}

const masters = [
  require(resolveMaster("01-title.js")),
  require(resolveMaster("02-toc.js")),
  require(resolveMaster("03-stat-callout.js")),
  require(resolveMaster("04-section-divider.js")),
  require(resolveMaster("05-two-column-comparison.js")),
  require(resolveMaster("06-market-positioning-table.js")),
  require(resolveMaster("07-market-analysis-per-role.js")),
  require(resolveMaster("08-wage-scale-proposal.js")),
  require(resolveMaster("09-cost-analysis.js")),
  require(resolveMaster("10-next-steps.js")),
  require(resolveMaster("11-closing-decision-ask.js")),
  require(resolveMaster("12-blank-flex.js")),
  require(resolveMaster("13-chart-slide-new.js")),
  require(resolveMaster("14-methodology-new.js")),
  require(resolveMaster("15-multi-province-compare-new.js")),
  require(resolveMaster("16-risks-alternatives-new.js")),
  require(resolveMaster("17-market-positioning-long-new.js")),
  require(resolveMaster("18-toc-expanded-new.js")),
  require(resolveMaster("19-force-option-card-grid.js")),
  require(resolveMaster("20-narrative-section-divider.js")),
  require(resolveMaster("21-executive-summary-callout.js")),
];

masters.forEach(m => m.defineMaster(deps));

// ---------------------------------------------------------------------------
// 4. Export — deck builders add their own slides then call pres.writeFile()
// ---------------------------------------------------------------------------
module.exports = { pres, deps };
