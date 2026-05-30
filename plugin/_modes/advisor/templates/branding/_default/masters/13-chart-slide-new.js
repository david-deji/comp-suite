// =============================================================================
// 13-chart-slide-new.js — CHART SLIDE (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 13: CHART SLIDE (NEW).
// Override per-org by writing branding/<org>/masters/13-chart-slide-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "13_CHART",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 13  ·  CHART SLIDE"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "13_CHART" });
  addTitleSubtitle(s, "[Chart title — what this chart shows]",
    "[Optional subtitle — methodology snippet or framing]");

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.2, w: 8.5, h: 4.0,
    fill: { color: C.white }, line: { color: C.borderGray, width: 1, dashType: "dash" }
  });
  const barData = [
    { lbl: "[Group 1]", val: 0.92, color: C.red          },
    { lbl: "[Group 2]", val: 1.08, color: C.accentTeal         },
    { lbl: "[Group 3]", val: 1.00, color: C.primaryDark   },
    { lbl: "[Group 4]", val: 0.95, color: C.primaryDark   },
    { lbl: "[Group 5]", val: 1.15, color: C.accentTeal         }
  ];
  const chartX = 1.20, chartY = 2.50, chartW = 7.50, chartH = 3.30;
  const baselineY = chartY + chartH * 0.50;
  const barW = chartW / barData.length * 0.55;
  const gap = chartW / barData.length;
  barData.forEach((b, i) => {
    const x = chartX + i * gap + (gap - barW) / 2;
    const barH = (b.val - 0.85) / 0.30 * chartH;
    const y = chartY + chartH - barH;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: barW, h: barH,
      fill: { color: b.color }, line: { color: b.color, width: 0 }
    });
    s.addText(b.lbl, {
      x: x - 0.2, y: chartY + chartH + 0.05, w: barW + 0.4, h: 0.25,
      fontFace: F.body, fontSize: 9, color: C.textGray,
      align: "center", valign: "top", margin: 0
    });
    s.addText((b.val * 100).toFixed(0) + "%", {
      x: x - 0.1, y: y - 0.30, w: barW + 0.2, h: 0.25,
      fontFace: F.body, fontSize: 9, color: b.color,
      align: "center", bold: true, valign: "top", margin: 0
    });
  });
  s.addShape(pres.shapes.LINE, {
    x: chartX, y: baselineY, w: chartW, h: 0,
    line: { color: C.textMuted, width: 1, dashType: "dash" }
  });
  s.addText("Market P50 (compa = 1.00)", {
    x: chartX, y: baselineY - 0.30, w: 2.5, h: 0.25,
    fontFace: F.body, fontSize: 8, color: C.textMuted,
    italic: true, margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 9.30, y: 2.2, w: 3.50, h: 4.0,
    fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
  });
  s.addText("KEY TAKEAWAY", {
    x: 9.50, y: 2.40, w: 3.10, h: 0.4,
    fontFace: F.body, fontSize: 11, color: C.white,
    bold: true, charSpacing: 4, margin: 0
  });
  s.addText("[One-sentence headline finding from this chart]", {
    x: 9.50, y: 2.85, w: 3.10, h: 1.3,
    fontFace: F.heading, fontSize: 17, color: C.white,
    align: "left", valign: "top", margin: 0
  });
  s.addText([
    { text: "[Supporting point 1]", options: { bullet: true, breakLine: true } },
    { text: "[Supporting point 2]", options: { bullet: true, breakLine: true } },
    { text: "[Implication for decision]", options: { bullet: true } }
  ], { x: 9.50, y: 4.30, w: 3.10, h: 1.7,
       fontFace: F.body, fontSize: 11, color: C.white,
       align: "left", valign: "top", paraSpaceAfter: 6, margin: 0 });

  s.addText("Source: [Survey + year] · [Geo] · n=[N] postings · Compa = internal pay ÷ market P50.", {
    x: 0.5, y: 6.50, w: 8.5, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
