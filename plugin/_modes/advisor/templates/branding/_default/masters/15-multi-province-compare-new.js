// =============================================================================
// 15-multi-province-compare-new.js — MULTI-PROVINCE COMPARE (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 15: MULTI-PROVINCE COMPARE (NEW).
// Override per-org by writing branding/<org>/masters/15-multi-province-compare-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "15_MULTI_PROVINCE",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 15  ·  MULTI-PROVINCE COMPARE"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "15_MULTI_PROVINCE" });
  addTitleSubtitle(s, "Multi-Province Compare — Compa-Ratio Heatmap",
    "Where each role sits relative to local market P50, by province");

  const roles = ["[Role A]", "[Role B]", "[Role C]", "[Role D]", "[Role E]"];
  const provinces = ["ONTARIO", "QUEBEC", "BRITISH COLUMBIA"];
  const data = [
    [0.92, 0.95, 1.05],
    [1.08, 1.02, 0.99],
    [1.00, 0.94, 1.12],
    [0.95, 0.98, 1.00],
    [1.15, 1.10, 1.06]
  ];

  const tableX = 0.5, tableY = 2.2;
  const labelColW = 2.5, dataColW = 3.0;
  const headerH = 0.50, rowH = 0.65;
  const tableW = labelColW + provinces.length * dataColW;

  s.addShape(pres.shapes.RECTANGLE, {
    x: tableX, y: tableY, w: tableW, h: headerH,
    fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
  });
  s.addText("Role", {
    x: tableX + 0.15, y: tableY, w: labelColW - 0.30, h: headerH,
    fontFace: F.body, fontSize: 11, color: C.white,
    align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });
  provinces.forEach((p, i) => {
    s.addText(p, {
      x: tableX + labelColW + i * dataColW, y: tableY,
      w: dataColW, h: headerH,
      fontFace: F.body, fontSize: 10, color: C.white,
      align: "center", valign: "middle", bold: true, charSpacing: 3, margin: 0
    });
  });

  data.forEach((row, ri) => {
    const y = tableY + headerH + ri * rowH;
    s.addShape(pres.shapes.RECTANGLE, {
      x: tableX, y, w: labelColW, h: rowH,
      fill: { color: ri % 2 ? C.white : C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
    });
    s.addText(roles[ri], {
      x: tableX + 0.15, y, w: labelColW - 0.30, h: rowH,
      fontFace: F.body, fontSize: 11, color: C.primaryDark,
      align: "left", valign: "middle", bold: true, margin: 0
    });
    row.forEach((v, ci) => {
      const x = tableX + labelColW + ci * dataColW;
      let bgColor, txtColor;
      if (v < 0.95)      { bgColor = C.redTint;    txtColor = C.red; }
      else if (v > 1.05) { bgColor = C.tealTint;   txtColor = C.accentTeal; }
      else               { bgColor = C.purpleTint; txtColor = C.primaryDark; }
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: dataColW, h: rowH,
        fill: { color: bgColor }, line: { color: C.borderGray, width: 0.5 }
      });
      s.addText((v * 100).toFixed(0) + "%", {
        x, y, w: dataColW, h: rowH,
        fontFace: F.body, fontSize: 13, color: txtColor,
        align: "center", valign: "middle", bold: true, margin: 0
      });
    });
  });

  s.addText("READING THIS HEATMAP", {
    x: 0.5, y: 6.0, w: 4.0, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.primaryDark,
    bold: true, charSpacing: 4, margin: 0
  });
  const legend = [
    { color: C.red,        text: "Below market (<95%)" },
    { color: C.primaryDark, text: "At market (95–105%)" },
    { color: C.accentTeal,       text: "Above market (>105%)" }
  ];
  legend.forEach((lg, i) => {
    const x = 0.5 + i * 3.5;
    s.addShape(pres.shapes.OVAL, {
      x, y: 6.4, w: 0.18, h: 0.18, fill: { color: lg.color }, line: { color: lg.color, width: 0 }
    });
    s.addText(lg.text, {
      x: x + 0.30, y: 6.30, w: 3.2, h: 0.35,
      fontFace: F.body, fontSize: 11, color: C.primaryDark,
      valign: "top", margin: 0
    });
  });

  s.addText("Compa = internal pay ÷ provincial market P50. Source: [Survey + year] per-province cuts.", {
    x: 0.5, y: 6.78, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
