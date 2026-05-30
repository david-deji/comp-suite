// =============================================================================
// 19-force-option-card-grid.js — FORCE / OPTION / CARD GRID
// =============================================================================
// Slide master definition + demo slide for layout 19: FORCE OPTION CARD GRID.
// Three-column card grid for narrative-first slides. Each column has:
//   - Top: card title (the "force", "option", or "question" label)
//   - Middle: body copy (the substance)
//   - Bottom: small footer note
// Used in narrative-frame-only mode (pre-engagement decks) and any deck where
// three parallel framings need equal visual weight.
//
// Override per-org by writing branding/<org>/masters/19-force-option-card-grid.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "19_FORCE_OPTION_CARD_GRID",
    background: { color: C.white },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 19  ·  FORCE OPTION CARD GRID"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "19_FORCE_OPTION_CARD_GRID" });

  // Slide title
  s.addText("[Three-column framing title]", {
    x: 0.5, y: 0.85, w: 12.3, h: 0.55,
    fontFace: F.heading, fontSize: 26, color: C.text,
    align: "left", valign: "top", bold: true, margin: 0
  });
  s.addText("Optional one-line subtitle that frames the three columns", {
    x: 0.5, y: 1.45, w: 12.3, h: 0.4,
    fontFace: F.body, fontSize: 13, color: C.textMuted,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Three columns: x positions at 0.5, 4.75, 9.0; width 4.0 each; gap 0.25
  const cols = [
    { x: 0.5,  label: "FORCE",    title: "[Force / driver name]",      body: "What's pushing the decision space — market shift, retention pain, statutory change. Two to four lines describing the force in concrete terms.",     footer: "Source: [where this comes from]" },
    { x: 4.75, label: "OPTION",   title: "[Option / response name]",   body: "What the organization can do in response. Two to four lines describing the option's shape, cost contour, and downstream implications.",            footer: "Trade-off: [primary trade-off]" },
    { x: 9.0,  label: "QUESTION", title: "[Question / open issue]",    body: "What the audience needs to decide or weigh in on. Two to four lines making the open question concrete enough to answer in the room.",              footer: "Decision needed by: [date]" }
  ];

  cols.forEach(col => {
    // Card background (light-fill rectangle with thin border)
    s.addShape(pres.shapes.RECTANGLE, {
      x: col.x, y: 2.05, w: 4.0, h: 4.5,
      fill: { color: C.offwhite || "F7F7F4" },
      line: { color: C.border || "E0E0DC", width: 0.5 }
    });

    // Column label (small, all-caps, accent color)
    s.addText(col.label, {
      x: col.x + 0.25, y: 2.25, w: 3.5, h: 0.3,
      fontFace: F.body, fontSize: 10, color: C.green || C.accent || "4AA447",
      align: "left", valign: "top", bold: true, charSpacing: 4, margin: 0
    });

    // Column title
    s.addText(col.title, {
      x: col.x + 0.25, y: 2.65, w: 3.5, h: 0.7,
      fontFace: F.heading, fontSize: 18, color: C.text,
      align: "left", valign: "top", bold: true, margin: 0
    });

    // Body copy
    s.addText(col.body, {
      x: col.x + 0.25, y: 3.5, w: 3.5, h: 2.4,
      fontFace: F.body, fontSize: 12, color: C.text,
      align: "left", valign: "top", margin: 0
    });

    // Footer note
    s.addText(col.footer, {
      x: col.x + 0.25, y: 6.05, w: 3.5, h: 0.4,
      fontFace: F.body, fontSize: 10, color: C.textMuted,
      align: "left", valign: "top", italic: true, margin: 0
    });
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
