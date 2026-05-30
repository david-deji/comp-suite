// =============================================================================
// 12-blank-flex.js — BLANK / FLEX
// =============================================================================
// Slide master definition + demo slide for layout 12: BLANK / FLEX.
// Override per-org by writing branding/<org>/masters/12-blank-flex.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "12_BLANK_FLEX",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 12  ·  BLANK / FLEX"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "12_BLANK_FLEX" });
  addTitleSubtitle(s, "[Slide title — replace this placeholder]",
    "Use this layout for ad-hoc content that doesn't fit other layouts");
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.2, w: 12.3, h: 4.6,
    fill: { color: C.white }, line: { color: C.borderGray, width: 1, dashType: "dash" }
  });
  s.addText("Blank canvas — drop charts, illustrations, or any custom content here.\nLayout retains the deck chrome (logo, footer, layout-tag) so this slide always reads as part of the deck.", {
    x: 1.0, y: 4.0, w: 11.3, h: 1.0,
    fontFace: F.body, fontSize: 14, color: C.textMuted,
    align: "center", italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
