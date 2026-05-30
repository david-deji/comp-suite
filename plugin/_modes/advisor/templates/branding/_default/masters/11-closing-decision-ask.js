// =============================================================================
// 11-closing-decision-ask.js — CLOSING / DECISION ASK
// =============================================================================
// Slide master definition + demo slide for layout 11: CLOSING / DECISION ASK.
// Override per-org by writing branding/<org>/masters/11-closing-decision-ask.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { makeFooter, masterObjects } = helpers;
  const LOGO_LARGE = logoPaths.large;

  pres.defineSlideMaster({
    title: "11_CLOSING_DECISION",
    background: { color: C.offwhite },
    objects: masterObjects(
      { image: { path: LOGO_LARGE, x: 5.4, y: 0.6, w: 2.5, h: 0.67 } },
      makeFooter()
    )
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "11_CLOSING_DECISION" });
  s.addText("DECISION ASK", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.4,
    fontFace: F.body, fontSize: 12, color: C.primaryDark,
    align: "center", charSpacing: 8, bold: true, margin: 0
  });
  s.addText("Approve [Option #X] for [DATE] effective date —\ntotal cost $X.XXM (X.XX% of payroll)", {
    x: 1.0, y: 2.10, w: 11.3, h: 1.6,
    fontFace: F.heading, fontSize: 32, color: C.primaryDark,
    align: "center", valign: "top", margin: 0
  });
  s.addText("NEXT ACTIONS", {
    x: 0.5, y: 4.05, w: 12.3, h: 0.35,
    fontFace: F.body, fontSize: 10, color: C.primaryDark,
    align: "center", bold: true, charSpacing: 4, margin: 0
  });
  s.addText([
    { text: "[Action 1 — owner — date]", options: { bullet: true, breakLine: true } },
    { text: "[Action 2 — owner — date]", options: { bullet: true, breakLine: true } },
    { text: "[Action 3 — owner — date]", options: { bullet: true } }
  ], { x: 4.0, y: 4.45, w: 5.3, h: 1.5,
       fontFace: F.body, fontSize: 14, color: C.primaryDark,
       align: "left", valign: "top", paraSpaceAfter: 4, margin: 0 });
  s.addText("[Author] · [Title] · [email] · [Date]", {
    x: 0.5, y: 6.55, w: 12.3, h: 0.4,
    fontFace: F.body, fontSize: 11, color: C.textGray,
    align: "center", italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
