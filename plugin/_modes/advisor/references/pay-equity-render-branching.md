# Render Branching — CNESST vs side-deliverable

The pay equity protocol produces two classes of output. Each class has its own
rendering rule. Loaded by `references/pay-equity-qc-protocol.md` at any
`render_document` call site and at side-deliverable production.

## The two classes

| Class | Examples | Brand kit | Audience archetype | Language |
|-------|----------|-----------|-------------------|----------|
| **Statutory CNESST** | The 7 affichage `.template.md` files in `template_assets/pay_equity_cnesst/`, plus the 16 `RENDERED:document_type` values when wrapped in an affichage | **NO** | **NO** | **Always French** (regardless of `operator.language`) |
| **Side-deliverable** | Executive deck, board memo, workforce explainer, internal summary | **YES** (per `engagement-config.deck.brand` or `side_deliverables[i].brand`) | **YES** (per `side_deliverables[i].audience_archetypes`) | Engagement language; per-deliverable override allowed |

## Detection rule

When `render_document` is invoked OR when the orchestration code is about to
produce any pay-equity-related output, classify as follows:

1. Look up the requested deliverable in the **statutory stem table** below.
2. If it matches → **statutory**. No brand kit, no archetype, French.
3. If it does not match → **side-deliverable**. Apply brand kit and archetype.

### Statutory stem table

```
affichage-initial-10-49
affichage-initial-interim
affichage-initial-final
nouvel-affichage-initial
affichage-maintien
nouvel-affichage-maintien
demes-prep
inventaire-classes        (LLM-narrative substitute in v1)
grille-evaluation         (LLM-narrative substitute in v1)
rapport-comparaison       (LLM-narrative substitute in v1)
ajustements               (LLM-narrative substitute in v1)
comite-pv                 (LLM-narrative substitute in v1)
provenance-donnees        (LLM-narrative substitute in v1)
justification-methode     (LLM-narrative substitute in v1)
```

The 16 `RENDERED:document_type` values (`classes`, `grid`, `scores`, `gaps`,
`regression_summary`, `adjustments`, `payment_schedule`, `retroactive`,
`interest`, `maintenance_events`, `maintenance_classes`, `maintenance_adjustments`,
`maintenance_payment`, `maintenance_interest`, `committee_composition`,
`provenance`) are **always statutory** when produced as standalone outputs or
when inlined into a statutory template.

## Why statutory output ignores the brand kit

Affichages and CNESST forms are statutorily-shaped: the law dictates what
information appears, in what order, and in what language. Brand kit theming
(typography, logos, color palettes, footer boilerplate) is irrelevant — the
reader of record is the CNESST inspector or the workforce, and the template
controls voice. Applying a brand kit risks introducing visual elements that
distract from regulatory compliance or, worse, are interpreted as substantive
content. Statutory output is deliberately plain.

## Why statutory output ignores audience archetype

Same logic: affichages address a fixed audience (the workforce) in a
fixed register (legalistic, French). Audience archetype framing
(reframing for a "board member" vs a "warehouse worker") is appropriate
for side-deliverables but corrupts statutory output.

## Why side-deliverables apply both

A side-deliverable (executive deck, workforce memo) is a comp-advisor
deliverable using pay equity findings as content. It needs the brand voice the
operator has configured for the engagement and should be calibrated for the
audience that will read it. Comp-advisor's existing brand-kit and persona
mechanics apply unchanged.

## English translation of statutory deliverables

When the operator requests an English version of an affichage (operator
language is `en`, OR explicit "produce an English version" request):

1. Render French version first (the legal artifact).
2. Render English version with `language="en"` to
   `affichages/YYYY-MM-DD-<stem>-en.md`.
3. Prepend the courtesy header to the English version:
   ```
   Ce document est une traduction. La version française fait foi.
   ```
4. Both files commit to the persistence folder.

The English version is a courtesy translation; the French version is the legal
artifact. Operators must understand this distinction before distributing.

## Loi 25 disclaimer (always present, always French)

Both statutory and side-deliverable outputs include the Loi 25 footer:

```
Ce document a été produit à l'aide d'un outil automatisé. Il doit être révisé
par une personne qualifiée avant utilisation aux fins de conformité à la Loi
sur l'équité salariale.
```

- Affichage documents: footer at bottom, after all legally mandated content.
- All other documents: immediately after the title block, before the first content section.

No suppression flag. No language override. Per `pay-equity-mcp/CLAUDE.md` (preserved verbatim).

## Side-deliverable activation surface

Operator triggers a side-deliverable in one of two ways:

1. **At /init**: declare in `pay-equity-engagement.yaml` `side_deliverables[]`
   upfront. Each entry specifies `kind`, `audience_archetypes`, and optional
   `brand` and `language` overrides.
2. **Mid-engagement**: ask the skill ("Make me an executive deck on the gap
   findings"). Skill prompts for archetype + brand and appends to the array
   before producing the deliverable.

In both paths, the side-deliverable production goes through comp-advisor's
existing deck/document machinery — only the *content* is sourced from the pay
equity engagement state. The render branching rule above is the gate that
decides which mode applies.
