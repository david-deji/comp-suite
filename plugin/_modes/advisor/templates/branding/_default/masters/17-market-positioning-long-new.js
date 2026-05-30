// =============================================================================
// 17-market-positioning-long-new.js — MARKET POSITIONING — LONG (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 17: MARKET POSITIONING — LONG (NEW).
// Override per-org by writing branding/<org>/masters/17-market-positioning-long-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "17_MARKET_POSITIONING_LONG",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 17  ·  MARKET POSITIONING — LONG"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "17_MARKET_POSITIONING_LONG" });
  addTitleSubtitle(s, "Market Positioning — Full Roster",
    "Where every in-scope role sits relative to market — long-form view");

  const longRows = [
    ["Scale",   "Internal Title",  "Start Rate", "Mkt Start", "Compa St.", "Top Rate", "Mkt Top", "Compa Top"],
    ["[CODE 1]", "[Role title 1]",  "$XX.XX", "$XX.XX", "100%", "$XX.XX", "$XX.XX", "100%"],
    ["[CODE 2]", "[Role title 2]",  "$XX.XX", "$XX.XX", "92%",  "$XX.XX", "$XX.XX", "94%"],
    ["[CODE 3]", "[Role title 3]",  "$XX.XX", "$XX.XX", "108%", "$XX.XX", "$XX.XX", "110%"],
    ["[CODE 4]", "[Role title 4]",  "$XX.XX", "$XX.XX", "97%",  "$XX.XX", "$XX.XX", "99%"],
    ["[CODE 5]", "[Role title 5]",  "$XX.XX", "$XX.XX", "118%", "$XX.XX", "$XX.XX", "115%"],
    ["[CODE 6]", "[Role title 6]",  "$XX.XX", "$XX.XX", "92%",  "$XX.XX", "$XX.XX", "94%"],
    ["[CODE 7]", "[Role title 7]",  "$XX.XX", "$XX.XX", "100%", "$XX.XX", "$XX.XX", "102%"],
    ["[CODE 8]", "[Role title 8]",  "$XX.XX", "$XX.XX", "95%",  "$XX.XX", "$XX.XX", "98%"],
    ["[CODE 9]", "[Role title 9]",  "$XX.XX", "$XX.XX", "112%", "$XX.XX", "$XX.XX", "108%"],
    ["[CODE 10]","[Role title 10]", "$XX.XX", "$XX.XX", "89%",  "$XX.XX", "$XX.XX", "91%"],
    ["[CODE 11]","[Role title 11]", "$XX.XX", "$XX.XX", "103%", "$XX.XX", "$XX.XX", "100%"],
    ["[CODE 12]","[Role title 12]", "$XX.XX", "$XX.XX", "98%",  "$XX.XX", "$XX.XX", "97%"]
  ];

  const tableRows = longRows.map((r, ri) => r.map((cell, ci) => {
    const isHeader = ri === 0;
    const opts = {
      fontFace: F.body, fontSize: 9,
      color: isHeader ? C.white : C.primaryDark,
      bold: isHeader, valign: "middle",
      align: ci <= 1 ? "left" : "center",
      margin: 0.03
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
    x: 0.5, y: 2.2, w: 12.3,
    colW: [1.0, 3.0, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });

  const legend = [
    { color: C.red,        text: "Below market (<95%)" },
    { color: C.primaryDark, text: "At market (95–105%)" },
    { color: C.accentTeal,       text: "Above market (>105%)" }
  ];
  legend.forEach((lg, i) => {
    const x = 0.5 + i * 3.5;
    s.addShape(pres.shapes.OVAL, {
      x, y: 6.45, w: 0.16, h: 0.16, fill: { color: lg.color }, line: { color: lg.color, width: 0 }
    });
    s.addText(lg.text, {
      x: x + 0.27, y: 6.37, w: 3.2, h: 0.30,
      fontFace: F.body, fontSize: 10, color: C.primaryDark,
      valign: "top", margin: 0
    });
  });
  s.addText("Source: [Survey + year] · Compa = internal ÷ market.  Use Layout 17 for ≥8 roles; ≤7 use Layout 6.", {
    x: 0.5, y: 6.75, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
