// =============================================================================
// 07-market-analysis-per-role.js — MARKET ANALYSIS — PER ROLE
// =============================================================================
// Slide master definition + demo slide for layout 7: MARKET ANALYSIS — PER ROLE.
// Override per-org by writing branding/<org>/masters/07-market-analysis-per-role.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "07_MARKET_ANALYSIS",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 7  ·  MARKET ANALYSIS — PER ROLE"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "07_MARKET_ANALYSIS" });
  addTitleSubtitle(s, "Market Analysis — [CODE]  |  [Role title]",
    "Summary of findings and market reference range");
  s.addText("KEY FINDINGS", {
    x: 0.5, y: 2.20, w: 6.5, h: 0.3,
    fontFace: F.body, fontSize: 11, color: C.primaryDark, bold: true, charSpacing: 4, margin: 0
  });
  const findings = [
    { h: "Start Rate", b: "Current $XX.XX/hr at [position]. Recently verified CBAs set Start Rates $X to $X above ours; FDS/SDM at $XX.XX.", accent: C.green },
    { h: "Top Rate",   b: "Thrifty Top Rate $XX.XX is $X.XX (10%/scaled/CBA) above market. P50 $XX.XX, postings sit closer to $XX.XX.", accent: C.accentTeal },
    { h: "Length of scale", b: "Scale length X,XXX hours is in line with / above / below CBA median (X,XXX hours).", accent: C.primaryDark },
    { h: "Forward signal",  b: "[Re-opener / negotiation / market trend] expected [date]. Outcome will set the next benchmark.", accent: C.vibrantPurple }
  ];
  // 2×2 card grid
  const findCardW = 3.15, findCardH = 1.95, findStartX = 0.5, findStartY = 2.55, findGapX = 0.20, findGapY = 0.18;
  findings.forEach((f, i) => {
    const c = i % 2, r = Math.floor(i / 2);
    const x = findStartX + c * (findCardW + findGapX);
    const y = findStartY + r * (findCardH + findGapY);
    // Card background
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: findCardW, h: findCardH,
      fill: { color: C.white }, line: { color: C.borderGray, width: 0.5 }
    });
    // Left accent strip — varies by finding
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.10, h: findCardH,
      fill: { color: f.accent }, line: { color: f.accent, width: 0 }
    });
    // Sub-header
    s.addText(f.h, {
      x: x + 0.25, y: y + 0.18, w: findCardW - 0.40, h: 0.40,
      fontFace: F.heading, fontSize: 14, color: C.primaryDark,
      align: "left", valign: "top", margin: 0
    });
    // Body
    s.addText(f.b, {
      x: x + 0.25, y: y + 0.65, w: findCardW - 0.40, h: findCardH - 0.75,
      fontFace: F.body, fontSize: 10, color: C.textGray,
      align: "left", valign: "top", margin: 0
    });
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.30, y: 2.20, w: 5.50, h: 1.3,
    fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
  });
  s.addText("REFERENCE MARKET RANGE", {
    x: 7.30, y: 2.30, w: 5.50, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.white, align: "center", charSpacing: 4, bold: true, margin: 0
  });
  s.addText("$XX.XX  —  $XX.XX", {
    x: 7.30, y: 2.65, w: 5.50, h: 0.7,
    fontFace: F.heading, fontSize: 30, color: C.white, align: "center", valign: "top", margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.30, y: 3.65, w: 5.50, h: 0.6,
    fill: { color: C.green }, line: { color: C.green, width: 0 }
  });
  s.addText("Competitiveness Ratio:  XXX% – XXX%", {
    x: 7.30, y: 3.65, w: 5.50, h: 0.6,
    fontFace: F.body, fontSize: 13, color: C.white, align: "center", valign: "middle", bold: true, margin: 0
  });
  const refRows = [
    [{ text: "Source", options: { fontFace: F.body, fontSize: 10, color: C.white, bold: true, fill: { color: C.primaryDark }, align: "left", margin: 0.05 } },
     { text: "P25",    options: { fontFace: F.body, fontSize: 10, color: C.white, bold: true, fill: { color: C.primaryDark }, align: "center", margin: 0.05 } },
     { text: "P50",    options: { fontFace: F.body, fontSize: 10, color: C.white, bold: true, fill: { color: C.primaryDark }, align: "center", margin: 0.05 } },
     { text: "P75",    options: { fontFace: F.body, fontSize: 10, color: C.white, bold: true, fill: { color: C.primaryDark }, align: "center", margin: 0.05 } }],
    [{ text: "StatCan", options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "left", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } }],
    [{ text: "CBAs",    options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.white }, align: "left", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.white }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.white }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.white }, align: "center", margin: 0.05 } }],
    [{ text: "Postings",options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "left", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } },
     { text: "$XX.XX",  options: { fontFace: F.body, fontSize: 10, color: C.primaryDark, fill: { color: C.purpleTint }, align: "center", margin: 0.05 } }]
  ];
  s.addTable(refRows, {
    x: 7.30, y: 4.40, w: 5.50, colW: [1.6, 1.3, 1.3, 1.3],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
