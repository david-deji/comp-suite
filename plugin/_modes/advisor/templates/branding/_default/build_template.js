// =============================================================================
// build_template.js — modular brand-template entry point (v3, Batch E)
// =============================================================================
// Loads theme tokens from theme/{palette,typography}.json, requires each master
// snippet from masters/, calls register({pres, C, F, helpers, logoPaths}) on
// each, then writes the .pptx. Per-org overrides resolve at require-time via
// the resolver below: branding/<org>/masters/<file>.js wins over
// branding/_default/masters/<file>.js when both exist.
//
// PRODUCTION TOGGLE
// -----------------
// INCLUDE_LAYOUT_TAGS — when true, each content slide shows a "LAYOUT N · NAME"
// breadcrumb at top-left. Helpful during template orientation; should be FALSE
// for any deck that ships to a real audience.
//
// USAGE
//   node build_template.js                 # uses _default brand kit
//   ORG=telos node build_template.js       # uses _default + branding/telos overrides
//
// OUTPUT
//   ./<ORG||'default'>_Comp_Deck_Template.pptx
// =============================================================================

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { makeHelpers } = require("./masters/_helpers");

const INCLUDE_LAYOUT_TAGS = true;  // <-- flip to false for production decks
const ORG = process.env.ORG || "_default";
const ROOT = __dirname;                                      // branding/_default
const BRANDING_ROOT = path.dirname(ROOT);                    // branding/
const ORG_ROOT = path.join(BRANDING_ROOT, ORG);              // branding/<org>

// =============================================================================
// 1. Theme resolution — palette/typography/footnotes/logos
// =============================================================================
// For each token file, prefer branding/<org>/theme/<file> if it exists, else
// fall back to branding/_default/theme/<file>. Palette + typography support
// partial override (deep merge); logos and footnotes are full-file replacement.

function loadJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }

function resolveThemeFile(filename) {
  const orgPath = path.join(ORG_ROOT, "theme", filename);
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

// =============================================================================
// 2. Presentation init
// =============================================================================
const pres = new pptxgen();
pres.layout  = "LAYOUT_WIDE";  // 13.3" × 7.5"
pres.author  = process.env.AUTHOR  || "Compensation Team";
pres.company = process.env.COMPANY || ORG;
pres.title   = process.env.TITLE   || "Compensation Market Review — Template";
pres.subject = "Reusable template for compensation market reviews";

const helpers = makeHelpers(C, F, logoPaths, INCLUDE_LAYOUT_TAGS);

// =============================================================================
// 3. Master resolution — load every master from _default, override per file
// =============================================================================
// Order matters: layout 01 → 18. Resolution per file:
//   if branding/<org>/masters/<file>.js exists, require that
//   else require branding/_default/masters/<file>.js

function resolveMaster(filename) {
  const orgPath = path.join(ORG_ROOT, "masters", filename);
  const defaultPath = path.join(ROOT, "masters", filename);
  return fs.existsSync(orgPath) ? orgPath : defaultPath;
}

const defaultMastersDir = path.join(ROOT, "masters");
const masterFiles = fs.readdirSync(defaultMastersDir)
  .filter(f => /^\d{2}-.*\.js$/.test(f))
  .sort();

console.error(`[build_template] org=${ORG}  masters=${masterFiles.length}`);

for (const f of masterFiles) {
  const resolved = resolveMaster(f);
  const isOverride = resolved !== path.join(defaultMastersDir, f);
  console.error(`  ${f}  ${isOverride ? "(override)" : ""}`);
  const mod = require(resolved);
  if (typeof mod.register !== "function") {
    throw new Error(`Master ${f} does not export a register() function`);
  }
  try {
    mod.register({ pres, C, F, helpers, logoPaths });
  } catch (e) {
    throw new Error(`Master ${f} failed to register: ${e.message}`);
  }
}

// =============================================================================
// 4. Write
// =============================================================================
const outName = `${ORG === "_default" ? "default" : ORG}_Comp_Deck_Template.pptx`;
pres.writeFile({ fileName: outName }).then(name => {
  console.error(`[build_template] wrote ${name}`);
});
