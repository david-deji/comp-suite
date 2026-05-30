// =============================================================================
// 08-wage-scale-proposal.js — WAGE SCALE PROPOSAL
// =============================================================================
// Slide master definition + demo slide for layout 8: WAGE SCALE PROPOSAL.
// Override per-org by writing branding/<org>/masters/08-wage-scale-proposal.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "08_WAGE_SCALE_PROPOSAL",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 8  ·  WAGE SCALE PROPOSAL"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "08_WAGE_SCALE_PROPOSAL" });
  addTitleSubtitle(s, "Wage Scale Proposal — [CODE]  |  [Role title]",
    "Proposed step grid with reference market range and proposal notes");
  const gridRows = [
    ["Exp. Range", "Current",  "Option #1", "Option #2"],
    ["0–999",      "$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["1,000–1,999","$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["2,000–2,999","$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["3,000–3,999","$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["4,000–4,999","$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["5,000+",     "$XX.XX",   "$XX.XX",    "$XX.XX"],
    ["Top Rate Δ", "—",        "X.X%",      "X.X%"],
    ["Lump Sum",   "—",        "$XXX",      "$XXX"]
  ];
  const tblRows = gridRows.map((r, ri) => r.map((cell, ci) => {
    const isHdr = ri === 0;
    const isMeta = ri >= gridRows.length - 2;
    return {
      text: cell,
      options: {
        fontFace: F.body, fontSize: 11,
        color: isHdr ? C.white : C.primaryDark,
        bold: isHdr || isMeta,
        align: ci === 0 ? "left" : "center",
        valign: "middle", margin: 0.05,
        fill: { color: isHdr ? C.primaryDark : (isMeta ? C.greenTint : (ri % 2 ? C.white : C.purpleTint)) }
      }
    };
  }));
  s.addTable(tblRows, {
    x: 0.5, y: 2.2, w: 6.5, colW: [1.6, 1.6, 1.65, 1.65],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.30, y: 2.20, w: 5.50, h: 1.0,
    fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
  });
  s.addText("REFERENCE MARKET RANGE", {
    x: 7.30, y: 2.28, w: 5.50, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.white, align: "center", charSpacing: 4, bold: true, margin: 0
  });
  s.addText("$XX.XX  —  $XX.XX", {
    x: 7.30, y: 2.55, w: 5.50, h: 0.55,
    fontFace: F.heading, fontSize: 26, color: C.white, align: "center", valign: "top", margin: 0
  });

  const mini = [
    { src: "STATCAN P50",  val: "$XX.XX" },
    { src: "CBA MEDIAN",   val: "$XX.XX" },
    { src: "POSTINGS P50", val: "$XX.XX" }
  ];
  const miniW = 1.78, miniStartX = 7.30, miniGap = 0.08;
  mini.forEach((m, i) => {
    const x = miniStartX + i * (miniW + miniGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.30, w: miniW, h: 0.75,
      fill: { color: C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
    });
    s.addText(m.src, {
      x, y: 3.34, w: miniW, h: 0.25,
      fontFace: F.body, fontSize: 8, color: C.primaryDark,
      align: "center", bold: true, charSpacing: 2, margin: 0
    });
    s.addText(m.val, {
      x, y: 3.58, w: miniW, h: 0.40,
      fontFace: F.heading, fontSize: 16, color: C.primaryDark,
      align: "center", valign: "top", margin: 0
    });
  });

  s.addText("PROPOSAL NOTES", {
    x: 7.30, y: 4.20, w: 5.50, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.primaryDark, bold: true, charSpacing: 4, margin: 0
  });
  s.addText([
    { text: "Option #1", options: { bullet: true, bold: true, breakLine: true } },
    { text: "[First action — e.g., accelerate progression]", options: { bullet: true, indentLevel: 1, breakLine: true } },
    { text: "[Second action]", options: { bullet: true, indentLevel: 1, breakLine: true } },
    { text: "[Top rate change & lump sum]", options: { bullet: true, indentLevel: 1, breakLine: true } },
    { text: "Option #2", options: { bullet: true, bold: true, breakLine: true } },
    { text: "[First action — e.g., accelerate progression]", options: { bullet: true, indentLevel: 1, breakLine: true } },
    { text: "[Second action]", options: { bullet: true, indentLevel: 1, breakLine: true } },
    { text: "[Top rate change & lump sum]", options: { bullet: true, indentLevel: 1 } }
  ], { x: 7.30, y: 4.55, w: 5.50, h: 2.4,
       fontFace: F.body, fontSize: 11, color: C.primaryDark, paraSpaceAfter: 2, margin: 0 });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
