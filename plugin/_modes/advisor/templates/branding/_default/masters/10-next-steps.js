// =============================================================================
// 10-next-steps.js — NEXT STEPS
// =============================================================================
// Slide master definition + demo slide for layout 10: NEXT STEPS.
// Override per-org by writing branding/<org>/masters/10-next-steps.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "10_NEXT_STEPS",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 10  ·  NEXT STEPS & TIMELINES"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "10_NEXT_STEPS" });
  addTitleSubtitle(s, "Next Steps & Timelines",
    "Decision points and implementation timeline to the [DATE] effective date");

  // Timeline overview — 3-stat strip mirroring slide 9 pattern
  const timelineStats = [
    { val: "X",         label: "ACTION ITEMS"   },
    { val: "X WEEKS",   label: "TO GO-LIVE" },
    { val: "[DATE]",    label: "TARGET GO-LIVE" }
  ];
  const tsW = 1.65, tsStartX = 0.5, tsGap = 0.18;
  timelineStats.forEach((ts, i) => {
    const x = tsStartX + i * (tsW + tsGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.10, w: tsW, h: 0.80,
      fill: { color: C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.10, w: tsW, h: 0.06,
      fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
    });
    s.addText(ts.val, {
      x, y: 2.18, w: tsW, h: 0.40,
      fontFace: F.heading, fontSize: 16, color: C.primaryDark,
      align: "center", valign: "middle", margin: 0
    });
    s.addText(ts.label, {
      x, y: 2.60, w: tsW, h: 0.28,
      fontFace: F.body, fontSize: 8, color: C.textGray,
      align: "center", bold: true, charSpacing: 2, margin: 0
    });
  });

  const stepRows = [
    ["Action Item",                                            "Owner",                      "Target Date"],
    ["Confirm strategic alignment on priorities and scope",    "[Stakeholder + Comp Team]",  "[Date]"],
    ["Present recommended options to [VP] for approval",       "Comp Team",                  "[Date]"],
    ["Last day to submit scales for configuration ([SYSTEM])", "Comp Team",                  "[Date]"],
    ["Prepare teammate communication materials",               "HR + Comp",                  "[Window]"],
    ["Stores receive communication guide and teammate memos",  "HR Comms",                   "[Date]"],
    ["Implement new scales effective [date]",                  "Payroll + HR",               "[Date]"],
    ["New rates appear on teammates' pay stubs",               "Payroll",                    "[Date]"]
  ];
  const tblRows = stepRows.map((r, ri) => r.map((cell, ci) => {
    const isHdr = ri === 0;
    return {
      text: cell,
      options: {
        fontFace: F.body, fontSize: 11,
        color: isHdr ? C.white : C.primaryDark,
        bold: isHdr,
        align: "left",
        valign: "middle", margin: 0.06,
        fill: { color: isHdr ? C.primaryDark : (ri % 2 ? C.white : C.purpleTint) }
      }
    };
  }));
  s.addTable(tblRows, {
    x: 0.5, y: 3.10, w: 12.3, colW: [7.0, 3.0, 2.3],
    border: { type: "solid", color: C.borderGray, pt: 0.5 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.95, w: 12.3, h: 0.95,
    fill: { color: C.green }, line: { color: C.green, width: 0 }
  });
  s.addText("DECISION ASK", {
    x: 0.5, y: 6.05, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.white,
    align: "center", charSpacing: 4, bold: true, margin: 0
  });
  s.addText("Approve [Option #X] for [DATE] effective date — total cost $X.XXM (X.XX% of payroll)", {
    x: 0.5, y: 6.36, w: 12.3, h: 0.5,
    fontFace: F.heading, fontSize: 18, color: C.white,
    align: "center", valign: "top", margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
