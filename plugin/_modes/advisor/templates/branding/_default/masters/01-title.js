// =============================================================================
// 01-title.js — TITLE
// =============================================================================
// Slide master definition + demo slide for layout 1: TITLE.
// Override per-org by writing branding/<org>/masters/01-title.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const LOGO_WHITE_LARGE = logoPaths.whiteLarge;

  pres.defineSlideMaster({
    title: "01_TITLE",
    background: { color: C.offwhite },
    objects: [
      { rect: { x: 0, y: 0, w: 5.32, h: 7.5, fill: { color: C.green } } },
      { image: { path: LOGO_WHITE_LARGE, x: 0.6, y: 0.55, w: 1.95, h: 0.52 } }
    ]
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "01_TITLE" });
  // Decorative: large pale purple-tint ellipse bleeding off bottom-right edge
  // Adds depth to the right column without competing with scope content
  s.addShape(pres.shapes.OVAL, {
    x: 9.5, y: 4.8, w: 6.0, h: 6.0,
    fill: { color: C.purpleTint }, line: { color: C.purpleTint, width: 0 }
  });
  s.addText("[Deck Title]\nGoes Here", {
    x: 0.6, y: 2.4, w: 4.5, h: 1.8,
    fontFace: F.heading, fontSize: 44, color: C.white,
    align: "left", valign: "top", margin: 0
  });
  s.addText("[Business Unit] | Compensation", {
    x: 0.6, y: 4.2, w: 4.5, h: 0.5,
    fontFace: F.body, fontSize: 16, color: C.white,
    align: "left", valign: "top", margin: 0
  });
  s.addText("[Geography] · Effective [Date]", {
    x: 0.6, y: 4.8, w: 4.5, h: 0.4,
    fontFace: F.body, fontSize: 12, color: C.white,
    align: "left", valign: "top", margin: 0
  });
  s.addText("Prepared by [Author] · [Team]", {
    x: 0.6, y: 6.55, w: 4.5, h: 0.3,
    fontFace: F.body, fontSize: 11, color: C.white,
    align: "left", valign: "top", italic: true, opacity: 0.85, margin: 0
  });
  s.addText("CONFIDENTIAL  |  INTERNAL USE ONLY", {
    x: 0.6, y: 7.05, w: 4.5, h: 0.35,
    fontFace: F.body, fontSize: 9, color: C.white,
    charSpacing: 4, margin: 0
  });

  s.addText("SCALES IN SCOPE", {
    x: 5.82, y: 0.85, w: 7.0, h: 0.4,
    fontFace: F.body, fontSize: 11, color: C.primaryDark,
    bold: true, charSpacing: 6, margin: 0
  });
  const scope = [
    { code: "[CODE 1]", role: "[Role title 1]", market: "Market P50: $XX.XX/hr" },
    { code: "[CODE 2]", role: "[Role title 2]", market: "Market P50: $XX.XX/hr" },
    { code: "[CODE 3]", role: "[Role title 3]", market: "Market P50: $XX.XX/hr" },
    { code: "[CODE 4]", role: "[Role title 4]", market: "Market P50: $XX.XX/hr" }
  ];
  const startY = 1.5, rowH = 1.3;
  scope.forEach((row, i) => {
    const y = startY + i * rowH;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.82, y: y + 0.10, w: 0.10, h: 0.95,
      fill: { color: C.green }, line: { color: C.green, width: 0 }
    });
    s.addText(row.code, {
      x: 6.05, y: y + 0.05, w: 6.5, h: 0.4,
      fontFace: F.body, fontSize: 13, color: C.primaryDark,
      bold: true, align: "left", valign: "top", margin: 0
    });
    s.addText(row.role, {
      x: 6.05, y: y + 0.45, w: 6.5, h: 0.4,
      fontFace: F.heading, fontSize: 16, color: C.primaryDark,
      align: "left", valign: "top", margin: 0
    });
    s.addText(row.market, {
      x: 6.05, y: y + 0.85, w: 6.5, h: 0.3,
      fontFace: F.body, fontSize: 10, color: C.textGray,
      italic: true, align: "left", valign: "top", margin: 0
    });
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
