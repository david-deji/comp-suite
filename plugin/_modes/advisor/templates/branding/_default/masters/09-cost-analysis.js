// =============================================================================
// 09-cost-analysis.js — COST ANALYSIS
// =============================================================================
// Slide master definition + demo slide for layout 9: COST ANALYSIS.
// Override per-org by writing branding/<org>/masters/09-cost-analysis.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "09_COST_ANALYSIS",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 9  ·  COST ANALYSIS"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "09_COST_ANALYSIS" });
  addTitleSubtitle(s, "Cost Analysis — [Option #X]",
    "Total annual cost by employee group, fully loaded for the [DATE] effective date");

  const byNumbers = [
    { val: "$X.XXM",  label: "TOTAL COST"           },
    { val: "X.XX%",   label: "% OF PAYROLL"         },
    { val: "X,XXX",   label: "TEAMMATES AFFECTED"   }
  ];
  const bnW = 1.65, bnStartX = 0.5, bnGap = 0.18;
  byNumbers.forEach((bn, i) => {
    const x = bnStartX + i * (bnW + bnGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.10, w: bnW, h: 0.80,
      fill: { color: C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
    });
    s.addText(bn.val, {
      x, y: 2.12, w: bnW, h: 0.45,
      fontFace: F.heading, fontSize: 18, color: C.primaryDark,
      align: "center", valign: "middle", margin: 0
    });
    s.addText(bn.label, {
      x, y: 2.58, w: bnW, h: 0.30,
      fontFace: F.body, fontSize: 8, color: C.textGray,
      align: "center", bold: true, charSpacing: 2, margin: 0
    });
  });

  // SUMMARY card — tinted background to match right-side weight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.10, w: 5.0, h: 2.30,
    fill: { color: C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
  });
  // Top accent strip
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.10, w: 5.0, h: 0.08,
    fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
  });
  s.addText("SUMMARY", {
    x: 0.70, y: 3.25, w: 4.6, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.primaryDark, bold: true, charSpacing: 4, margin: 0
  });
  s.addText([
    { text: "$X.XXM unavoidable (FYI / progression / mins)", options: { bullet: true, breakLine: true } },
    { text: "Top rate increases: $XX,XXX — X.X%",            options: { bullet: true, breakLine: true } },
    { text: "Structure adjustments: $XXX,XXX — X.X%",        options: { bullet: true, breakLine: true } },
    { text: "Lump sum to top-tier teammates: $XX,XXX",       options: { bullet: true, breakLine: true } },
    { text: "Includes movement of [notes] (not [excluded])", options: { bullet: true } }
  ], { x: 0.70, y: 3.60, w: 4.6, h: 1.7,
       fontFace: F.body, fontSize: 10, color: C.primaryDark, paraSpaceAfter: 2, margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.60, w: 5.0, h: 1.0,
    fill: { color: C.green }, line: { color: C.green, width: 0 }
  });
  s.addText("X.XX%", {
    x: 0.5, y: 5.60, w: 5.0, h: 0.70,
    fontFace: F.heading, fontSize: 32, color: C.white,
    align: "center", valign: "middle", margin: 0
  });
  s.addText("ANNUAL INCREASE BUDGET", {
    x: 0.5, y: 6.20, w: 5.0, h: 0.35,
    fontFace: F.body, fontSize: 9, color: C.white,
    align: "center", charSpacing: 4, bold: true, margin: 0
  });

  const costRows = [
    ["Employee Group",       "EE Ct.", "Avg Hrs", "Cur Top", "New Top", "Top Δ",     "Structure", "Progress."],
    ["[Group 1]",            "XXX",    "XXX",      "$XX.XX",   "$XX.XX",   "$X,XXX",    "$X,XXX",    "$X,XXX"],
    ["[Group 2]",            "XXX",    "XXX",      "$XX.XX",   "$XX.XX",   "$X,XXX",    "$X,XXX",    "$X,XXX"],
    ["[Group 3]",            "XXX",    "XXX",      "$XX.XX",   "$XX.XX",   "$X,XXX",    "$X,XXX",    "$X,XXX"],
    ["[Group 4]",            "XXX",    "XXX",      "$XX.XX",   "$XX.XX",   "$X,XXX",    "$X,XXX",    "$X,XXX"],
    ["[Group 5]",            "XXX",    "XXX",      "$XX.XX",   "$XX.XX",   "$X,XXX",    "$X,XXX",    "$X,XXX"],
    ["Subtotal",             "—",      "—",        "—",        "—",        "$XX,XXX",   "$XX,XXX",   "$XX,XXX"]
  ];
  const costTbl = costRows.map((r, ri) => r.map((cell, ci) => {
    const isHdr = ri === 0;
    const isSub = ri === costRows.length - 1;
    return {
      text: cell,
      options: {
        fontFace: F.body, fontSize: 9,
        color: isHdr ? C.white : C.primaryDark,
        bold: isHdr || isSub,
        align: ci === 0 ? "left" : "center",
        valign: "middle", margin: 0.04,
        fill: { color: isHdr ? C.primaryDark : (isSub ? C.greenTint : (ri % 2 ? C.white : C.purpleTint)) }
      }
    };
  }));
  s.addTable(costTbl, {
    x: 5.7, y: 3.15, w: 7.1, colW: [1.45, 0.55, 0.65, 0.85, 0.85, 0.75, 0.95, 1.05],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.7, y: 5.60, w: 7.1, h: 0.50,
    fill: { color: C.green }, line: { color: C.green, width: 0 }
  });
  s.addText("TOTAL ANNUAL COST", {
    x: 5.85, y: 5.60, w: 4.0, h: 0.50,
    fontFace: F.body, fontSize: 11, color: C.white,
    bold: true, charSpacing: 4, valign: "middle", margin: 0
  });
  s.addText("$X.XXM", {
    x: 9.85, y: 5.60, w: 2.8, h: 0.50,
    fontFace: F.heading, fontSize: 16, color: C.white,
    align: "right", valign: "middle", margin: 0
  });

  s.addText("Source: [HRIS data extract — date]. All figures fully loaded; assumes [bridge / progression rules]. See appendix for full methodology.", {
    x: 0.5, y: 6.78, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
