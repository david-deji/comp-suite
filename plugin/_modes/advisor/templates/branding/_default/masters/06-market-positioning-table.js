// =============================================================================
// 06-market-positioning-table.js — MARKET POSITIONING TABLE
// =============================================================================
// Slide master definition + demo slide for layout 6: MARKET POSITIONING TABLE.
// Override per-org by writing branding/<org>/masters/06-market-positioning-table.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "06_MARKET_POSITIONING",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 6  ·  MARKET POSITIONING TABLE"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "06_MARKET_POSITIONING" });
  addTitleSubtitle(s, "[Market Positioning at a Glance]",
    "Where we sit today relative to market — internal pay vs P50, P75 with compa-ratios");
  const rows = [
    ["Scale",   "Internal Title",  "Start Rate", "Mkt. Ref. Start", "Compa Start", "Top Rate", "Mkt. Ref. Top", "Compa Top"],
    ["[CODE 1]","[Role title 1]",  "$XX.XX",     "$XX.XX",          "100%",        "$XX.XX",   "$XX.XX",         "100%"],
    ["[CODE 2]","[Role title 2]",  "$XX.XX",     "$XX.XX",          "X%",          "$XX.XX",   "$XX.XX",         "X%"],
    ["[CODE 3]","[Role title 3]",  "$XX.XX",     "$XX.XX",          "X%",          "$XX.XX",   "$XX.XX",         "X%"],
    ["[CODE 4]","[Role title 4]",  "$XX.XX",     "$XX.XX",          "118%",        "$XX.XX",   "$XX.XX",         "115%"],
    ["[CODE 5]","[Role title 5]",  "$XX.XX",     "$XX.XX",          "92%",         "$XX.XX",   "$XX.XX",         "94%"]
  ];
  const tableRows = rows.map((r, ri) => r.map((cell, ci) => {
    const isHeader = ri === 0;
    const opts = {
      fontFace: F.body, fontSize: 11,
      color: isHeader ? C.white : C.primaryDark,
      bold: isHeader, valign: "middle",
      align: ci <= 1 ? "left" : "center",
      margin: 0.05
    };
    if (isHeader) opts.fill = { color: C.primaryDark };
    else opts.fill = { color: ri % 2 === 0 ? C.purpleTint : C.white };
    if (!isHeader && (ci === 4 || ci === 7)) {
      const v = parseFloat(cell.replace("%", ""));
      if (!isNaN(v)) {
        if (v < 95) opts.color = C.red;
        else if (v > 105) opts.color = C.accentTeal;
        opts.bold = true;
      }
    }
    return { text: cell, options: opts };
  }));
  s.addTable(tableRows, {
    x: 0.5, y: 2.2, w: 12.3, h: 3.3,
    colW: [1.1, 3.0, 1.4, 1.5, 1.3, 1.4, 1.5, 1.1],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });
  s.addText("READING THIS TABLE", {
    x: 0.5, y: 5.7, w: 4.0, h: 0.3,
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
      x, y: 6.1, w: 0.18, h: 0.18, fill: { color: lg.color }, line: { color: lg.color, width: 0 }
    });
    s.addText(lg.text, {
      x: x + 0.30, y: 6.0, w: 3.2, h: 0.35,
      fontFace: F.body, fontSize: 11, color: C.primaryDark,
      valign: "top", margin: 0
    });
  });
  s.addText("Source: [Survey + year] · postings (last [N] mo.) · Compa = internal ÷ market · Use Layout 17 for ≥8 roles.", {
    x: 0.5, y: 6.55, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
