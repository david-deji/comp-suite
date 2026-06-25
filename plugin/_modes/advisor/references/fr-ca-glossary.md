# FR-CA Glossary — Approved Translation Vocabulary

Loaded by SKILL.md when `deck.language: fr-ca` is set in the engagement config (or when the user explicitly requests French output mid-engagement). The glossary is the **single source of truth** for English ↔ Quebec French translations of every term the skill emits in a deck, footnote, callout, audience-facing artifact, or chart axis label.

This is a closed glossary by design: an unapproved term is a friction point that gets surfaced to the user, not silently translated. Amateur translation in a comp deck (especially the wrong term for a Quebec audience) is a credibility hit — the bilingual config flag is opt-in precisely so the deck either ships in Quebec-correct French or doesn't ship in French at all.

---

## Canonical resolution (where the glossary lives)

This bundled `references/fr-ca-glossary.md` file is the **seed and fallback**. When local `$STATE_ROOT` has `vocabulary/fr-ca-glossary.yaml`, that file becomes canonical and replaces this one for every engagement on that org (per `references/library-resolution.md` § Vocabulary glossary). The bundled file remains the load-bearing default when no promoted canonical exists yet.

Resolution order:

```
1. vocabulary/fr-ca-glossary.yaml in local $STATE_ROOT (canonical when present)
2. references/fr-ca-glossary.md (bundled seed/fallback, always present)
```

Per-engagement additions accumulate in `engagements/<slug>/fr-ca-additions.yaml` regardless of which canonical is active. `/glossary promote` (see § Section 8.5) walks the union of all engagement-level addition files, presents each candidate, on approval merges into `vocabulary/fr-ca-glossary.yaml` (creating it from this bundled seed on first promotion).

---

## The approval rule

When `deck.language: fr-ca`, every audience-facing French string emitted by the skill MUST be sourced from this glossary. Procedure on encountering a term not in the glossary:

1. **Stop**. Do not improvise a translation.
2. **Surface to user**. Pattern: "I need a French translation for `[term]`. The glossary doesn't have it. Suggested: `[suggestion 1]` or `[suggestion 2]`. Pick one, propose your own, or skip the section."
3. **On user approval**, append the term to this glossary AND save it to local `$STATE_ROOT` at `engagements/<slug>/fr-ca-additions.yaml` so future cycles inherit it.
4. **Surface a session-end summary** of all terms added during the engagement, so the user can review the full vocabulary added.

Skill never silently translates. Skill never asks the user mid-section for more than 3 unapproved terms in a row — if 4+ unapproved terms accumulate, pause and offer to either revisit the glossary in bulk or fall back to English for that section.

---

## Section 1 — Slide section names + standard structure

| English | FR-CA approved | Notes |
|---|---|---|
| Cover | Couverture | Title slide |
| Executive Summary | Sommaire de la direction | Avoid "Résumé exécutif" (anglicism) |
| Market Context | Contexte du marché | |
| Findings | Constats | NOT "Découvertes" or "Résultats" |
| Methodology | Méthodologie | |
| Options | Options | |
| Scenarios | Scénarios | |
| Do-Nothing Baseline | Statu quo (référence) | NOT "Ne-rien-faire" |
| Recommendation | Recommandation | |
| Decision Ask | Demande de décision | |
| Risks | Risques | |
| Mandatory Cost Floor | Seuil minimal de coûts obligatoires | |
| Discretionary Lift | Hausse discrétionnaire | |
| Assumptions | Hypothèses | NOT "Présomptions" (legal term) |
| Data Sources | Sources de données | |
| Appendix | Annexe | |
| Glossary | Glossaire | |
| Sign-off | Approbation | |
| Question Bank | Questions de la commanditaire / du commanditaire | Match gender to `engagement_scope.budget_owner_role` |

---

## Section 2 — Compensation terminology (core)

| English | FR-CA approved | Notes |
|---|---|---|
| Compensation | Rémunération globale | NEVER "compensation" — it means damages in Quebec French |
| Total rewards | Rémunération globale | Same term covers both |
| Base salary | Salaire de base | |
| Total cash compensation | Rémunération en espèces totale | |
| Total direct compensation (TDC) | Rémunération directe totale (RDT) | Use the FR-CA acronym |
| Hourly rate | Taux horaire | |
| Annual salary | Salaire annuel | |
| Pay structure | Structure salariale | |
| Pay band | Échelle salariale | NOT "bande salariale" |
| Pay scale / wage grid | Grille salariale | |
| Step rate | Échelon | |
| Top step / job rate | Taux maximal / taux de la pleine compétence | |
| Step 1 / entry rate | Échelon 1 / taux d'entrée | |
| Merit increase | Augmentation au mérite | |
| Across-the-board (ATB) | Augmentation générale (AG) | Use the FR-CA acronym |
| Cost of Living Adjustment (COLA) | Indexation au coût de la vie (ICV) | |
| Compa-ratio | Ratio comparatif | NOT "compa-ratio" — translate fully |
| Group compa-ratio | Ratio comparatif global | |
| Position-in-range | Position dans l'échelle | |
| Market percentile | Centile du marché | |
| P50 / median | P50 / médiane | Keep P50 numeric form |
| P25, P75, etc. | P25, P75, etc. | Numeric form unchanged |
| Pay positioning | Positionnement salarial | |
| Lead the market | Mener le marché | |
| Match the market | Suivre le marché | |
| Lag the market | Retarder par rapport au marché | NOT "rester en arrière" |
| Pay philosophy | Philosophie de rémunération | |
| Pay equity | Équité salariale | Capital E in formal contexts (Loi sur l'équité salariale) |
| Pay gap | Écart salarial | |
| Compression | Compression salariale | |
| Roll-up factor | Facteur de majoration | Benefits + pension + premiums riding on base wage |
| Payroll burden | Charges sociales / charges patronales | "Charges sociales" preferred in Quebec |
| Headcount | Effectif | NOT "tête de personnel" |
| FTE (Full-Time Equivalent) | ETP (Équivalent temps plein) | Use the FR-CA acronym |
| Voluntary turnover | Roulement volontaire | NOT "rotation volontaire" |
| Retention | Rétention | |
| Replacement cost | Coût de remplacement | |
| Recruiting / recruitment | Recrutement | NOT "recrutage" |
| Workforce | Main-d'œuvre | |
| Hiring | Embauche | |
| Bonus / incentive plan | Régime d'intéressement / régime de primes | |
| Short-term incentive (STI) | Régime d'intéressement à court terme (RICT) | |
| Long-term incentive (LTI) | Régime d'intéressement à long terme (RILT) | |
| Equity / stock-based comp | Rémunération à base d'actions | |
| Vesting | Acquisition (des droits) | |
| Performance rating | Cote de rendement | NOT "évaluation de performance" |
| Merit matrix | Matrice d'augmentation au mérite | |

---

## Section 3 — Quebec labour terms (statutes, agencies, social charges)

| English | FR-CA approved | Notes |
|---|---|---|
| QC Pay Equity Act | Loi sur l'équité salariale | Always cite full name on first use |
| Federal Pay Equity Act | Loi sur l'équité salariale (fédérale) | Disambiguate from QC version |
| Labour Standards Act (QC) | Loi sur les normes du travail | |
| Civil Code of Quebec | Code civil du Québec (CCQ) | |
| Canada Labour Code | Code canadien du travail | |
| CNESST | CNESST | Acronym only — no expansion needed for Quebec audience |
| (CNESST expanded — only when needed) | Commission des normes, de l'équité, de la santé et de la sécurité du travail | First-use expansion only |
| CCDP / CHRC | CCDP / Commission canadienne des droits de la personne | |
| CDPDJ | CDPDJ / Commission des droits de la personne et des droits de la jeunesse | |
| Provincial minimum wage | Salaire minimum provincial | |
| Collective agreement | Convention collective | |
| Collective bargaining | Négociation collective | |
| Bargaining unit | Unité de négociation | |
| Reopener clause | Clause de réouverture | |
| Grievance | Grief | |
| Union | Syndicat | |
| UFCW (Local 501 / Local 175) | TUAC (section locale 501 / section locale 175) | TUAC is the Quebec acronym |
| CPP / Canada Pension Plan | RPC / Régime de pensions du Canada | Quebec employer must distinguish from QPP |
| QPP / Quebec Pension Plan | RRQ / Régime de rentes du Québec | |
| EI / Employment Insurance | AE / Assurance-emploi | |
| QPIP / Quebec Parental Insurance Plan | RQAP / Régime québécois d'assurance parentale | |
| HSF / Health Services Fund | FSS / Fonds des services de santé | Quebec employer payroll tax |
| WSDRF / Workforce Skills Development and Recognition Fund | LCMM / Loi favorisant le développement et la reconnaissance des compétences de la main-d'œuvre | "Loi du 1%" — informal name |
| EHT / Employer Health Tax (ON) | EHT / Employer Health Tax (Ontario) | Keep English — Ontario tax, untranslated |
| Effective date | Date d'entrée en vigueur | |
| Retroactive pay | Paie rétroactive | NOT "salaire rétroactif" |
| Predominance (pay equity) | Prédominance | Loi sur l'équité salariale art. 54 sense |
| Maintenance exercise (pay equity) | Exercice de maintien | Loi sur l'équité salariale art. 76.1 sense |

---

## Section 4 — Audience archetypes

| English | FR-CA approved | Notes |
|---|---|---|
| Board | Conseil d'administration | |
| C-suite | Direction | NOT "Suite-C" |
| CEO | Président-directeur général (PDG) | |
| CFO | Directeur financier / Directrice financière (DF) | Match gender |
| CHRO | Chef des ressources humaines (CRH) | |
| VP HR | Vice-président RH / Vice-présidente RH | Match gender |
| VP Operations | Vice-président des opérations / Vice-présidente des opérations | Match gender |
| HR leadership | Direction RH | |
| HR business partner | Partenaire d'affaires RH | |
| HR ops / comp team | Équipe de rémunération | |
| Compensation committee | Comité de rémunération | |
| Line managers | Gestionnaires opérationnels | |
| Front-line employees | Employés de première ligne / Employées de première ligne | Match gender or use neutral phrasing |
| Union representatives | Représentants syndicaux / Représentantes syndicales | |

---

## Section 5 — Standard footnotes

The skill's standard footnotes (data source citations, payroll burden caveats, methodology disclaimers) are pre-translated below. When `deck.language: fr-ca`, use these verbatim.

Each citation pattern below corresponds to one or more verified-source tags from the canonical 11-tag vocabulary in `references/tools-available.md` § Verified-source discipline (`[statcan-wage]`, `[live-postings]`, `[cba]`, `[indeed-company]`, `[econometric]`, `[statutory]`, `[market-data]`, `[survey-house]`, `[user-provided-cba]`, `[professional-judgment]`, `[assumption]`). The Market MCP citation covers `[statcan-wage]` / `[live-postings]` / `[market-data]`; the CBA citation covers `[cba]` and `[user-provided-cba]`; the Indeed citation covers `[indeed-company]`; the Web fetch citation covers `[statutory]` and `[econometric]`; the User-provided data citation covers `[user-provided-cba]` and analyst-provided survey blocks. When a tag has no verifiable source, omit the footnote and tag the claim `[professional-judgment]` or `[assumption]` per `references/judgment-notes.md`.

### Data source citations

- **Market MCP citation**: `Source : Market MCP, données de [SOURCE], extraction [YYYY-MM-DD]` (example: `Source : Market MCP, données EERH de Statistique Canada, extraction 2026-04-21`)
- **CBA citation**: `Source : Convention collective [PARTIE], section locale [N], en vigueur jusqu'au [DATE]`
- **Indeed citation**: `Source : Affichages Indeed, période [N] mois, extraction [YYYY-MM-DD]`
- **Web fetch citation**: `Source : [URL], consulté le [YYYY-MM-DD]`
- **User-provided data**: `Source : Données fournies par le client, [DESCRIPTION]`

### Payroll burden caveat (jurisdiction-specific — pre-translated)

- **Quebec (QC)**: `Les coûts présentés sont des hausses de salaire de base seulement. Les charges sociales de l'employeur (RPC/RRQ, AE, RQAP, FSS) ajoutent environ 12-15 % au Québec.`
- **Ontario (ON)**: `Les coûts présentés sont des hausses de salaire de base seulement. Les charges sociales de l'employeur (RPC, AE, EHT) ajoutent environ 10-12 % en Ontario.`
- **Other / unspecified**: `Les coûts présentés sont des hausses de salaire de base seulement. Les charges sociales de l'employeur (variables selon la province) doivent être ajoutées au coût total projeté.`

### Methodology disclaimers

- **Aging methodology**: `Données du marché ajustées au [YYYY-MM-DD] selon une tendance annuelle de [X] %.`
- **Job-matching disclaimer**: `Appariement des postes basé sur la portée, le niveau, l'industrie et la taille du chiffre d'affaires.`
- **Sample-size caveat**: `Échantillon limité ([N] observations) — interpréter avec prudence.`
- **Geo-adjustment**: `Données ajustées géographiquement (différentiel régional appliqué).` OR `Données nationales non ajustées géographiquement.`

---

## Section 6 — Anti-anglicisms (banned in Quebec French)

These English-derived terms are commonly seen in HR documents but are wrong or jarring in Quebec French. The skill MUST NOT emit them.

| Banned anglicism | Use instead |
|---|---|
| Bénéfices (for benefits) | Avantages sociaux |
| Compensation (for pay) | Rémunération |
| Senior (for senior employee) | Cadre supérieur / employé d'expérience |
| Junior (for junior employee) | Débutant / employé en début de carrière |
| Performant (for high-performing) | À haut rendement |
| Aligner (in strategy sense) | Harmoniser / arrimer |
| Définitivement (for definitely) | Certainement / sans aucun doute |
| Application (for job application) | Candidature |
| Appliquer (for apply for a job) | Postuler |
| Opportunité (for opportunity in business sense) | Occasion / possibilité |
| Référence (for reference in performance sense) | Recommandation |
| Position (for job position) | Poste |
| Adresser (for to address an issue) | Aborder / traiter |
| Initier (for to initiate / start) | Lancer / amorcer |
| Délivrer (for to deliver in business sense) | Livrer / produire |
| Réaliser (for to realize / understand) | Se rendre compte |
| Statut (for status) | État (in business sense) / situation |
| Chèque-paie (for paycheck) | Paie / talon de paie |
| Fringe benefits | Avantages indirects |
| Bonus (as standalone noun) | Prime / boni |
| Package (for compensation package) | Ensemble de rémunération |
| Briefer (for to brief someone) | Informer / mettre au courant |
| Challenger (for to challenge an idea) | Remettre en question |

---

## Section 7 — Number, date, and currency formatting

When `deck.language: fr-ca`, all numeric formatting follows Quebec conventions:

- **Decimal separator**: comma. `4 000 000,50 $` NOT `4,000,000.50 $`
- **Thousands separator**: non-breaking space. `4 000 000` NOT `4,000,000`
- **Currency symbol position**: after the number, with a non-breaking space. `4 000 000,50 $` NOT `$4,000,000.50`
- **Percentage**: with non-breaking space. `12,5 %` NOT `12.5%`
- **Date format**: `JJ-MM-AAAA` or `JJ MMMM AAAA`. `21 avril 2026` or `2026-04-21` (ISO acceptable). NEVER `04/21/2026` (US format).
- **Time format**: 24-hour. `14 h 32` (with non-breaking spaces) NOT `2:32 PM`.

The pptx skill must apply these formats to every number / date / currency cell. If a chart library (e.g., the JS chart code in `template_assets/branding/_default/masters/13-chart-slide-new.js` and `15-multi-province-compare-new.js`) uses default English formatting, override at chart creation time.

---

## Section 8 — Adding terms to the glossary

When the skill encounters an English term not in this glossary during a `deck.language: fr-ca` engagement:

1. **Surface immediately** to the user (do not batch — the user catches drift early).
2. **Suggest 1-2 candidates** drawn from authoritative Quebec sources (Office québécois de la langue française, Termium, comp-industry Quebec publications). Pattern:

> "I need a French translation for `[English term]`. Glossary doesn't have it. Suggested:
> - **[Candidate 1]** — [one-line rationale, e.g., 'Termium-recommended; used in Loi sur les normes du travail']
> - **[Candidate 2]** — [rationale]
>
> Pick one, propose your own, or use the English term verbatim with a footnote."

3. **On user approval**, append to this glossary in the appropriate section + write the addition to `engagements/<slug>/fr-ca-additions.yaml` in local `$STATE_ROOT` (per `references/persistence-and-ledger.md`). Format:

```yaml
fr_ca_additions:
  - english: "Total rewards committee"
    fr_ca: "Comité de la rémunération globale"
    section: "audience-archetypes"
    approved_in_engagement: "pharmacy-fy26"
    approved_at: 2026-04-21T15:32:00
```

4. **At engagement close**, surface a session-end summary: "Added 4 terms to the FR-CA glossary this engagement: [list]. Saved to `engagements/pharmacy-fy26/fr-ca-additions.yaml`. Future engagements will inherit these."

5. **Periodic glossary review** via `/glossary promote` (see § Section 8.5).

---

## Section 8.5 — `/glossary promote` command

Walks the union of all `engagements/*/fr-ca-additions.yaml` files in local `$STATE_ROOT`, presents each unique candidate term, and on user approval merges into the canonical `vocabulary/fr-ca-glossary.yaml`.

**Trigger conditions:**

- Manual: user invokes `/glossary promote` at any time.
- Suggested: at session start when the count of unpromoted candidates across all engagements exceeds 10. The skill surfaces: "You have 14 unpromoted FR-CA additions across 3 engagements. Run `/glossary promote` to review and merge."

**Procedure:**

1. **Verify market backend is reachable** (authenticated). On auth failure, abort: "Glossary promotion requires the market backend. Authenticate and re-run."
2. **Discover candidates.** Read every `fr-ca-additions.yaml` under `engagements/` in local `$STATE_ROOT`. Aggregate into a candidate list keyed by `english` term. When multiple engagements added the same term with different `fr_ca` values, surface the conflict explicitly: "Term `Total rewards committee` has two candidates: `Comité de la rémunération globale` (pharmacy-fy26), `Comité des récompenses globales` (atlantic-retail-fy26). Pick one for canonical."
3. **Present each candidate** in turn:

> "Candidate 1 of 14: `Total rewards committee`
> - Proposed FR-CA: **Comité de la rémunération globale**
> - Section: `audience-archetypes`
> - Approved in: pharmacy-fy26 (2026-04-21)
> - Other engagements that used this term: atlantic-retail-fy26
>
> Approve, edit, reject, or skip?"

4. **On approve**: append to in-memory `vocabulary/fr-ca-glossary.yaml` (creating it from the bundled seed if not yet present in repo). On edit: prompt for revised FR-CA, then approve. On reject: log to `vocabulary/_rejected.yaml` so future engagements don't re-prompt the same term. On skip: leave for next promotion run.
5. **At end**: present summary "Promoting N terms, rejecting M, skipping K. Commit?" On confirm, single close-time write sequence: `vocabulary: promote N terms (<engagement_slugs>)`. Touched files: `vocabulary/fr-ca-glossary.yaml`, `vocabulary/_rejected.yaml` (if any rejections).
6. **Cleanup**: each promoted term is marked in its source `engagements/*/fr-ca-additions.yaml` with `promoted_at: <date>` so future `/glossary promote` runs skip it. The source files are NOT deleted — they preserve the per-engagement audit trail.

**Idempotency**: re-running `/glossary promote` after a successful run finds no candidates (everything already marked promoted). Surface "No new candidates to promote since last run on YYYY-MM-DD."

**Conflict with bundled glossary**: the bundled `references/fr-ca-glossary.md` is read-only. If the user wants a term in this bundled file changed (e.g., disagree with the canonical Quebec terminology), promote a *replacement* via `/glossary promote` to `vocabulary/fr-ca-glossary.yaml` — that file overrides the bundled glossary per the resolution order at the top of this file.

---

## Section 9 — When NOT to use this glossary

- **English-language engagement** (`deck.language: en` or unset). Glossary loads only when language is fr-ca.
- **Internal notes / chat** between user and skill — these stay in whatever language the user is writing in. Glossary applies only to audience-facing French output.
- **Quoted statute text**. When citing a statute (per `references/council-mode.md` § Statutory discipline), quote the verbatim text from the official source — do not paraphrase via the glossary. The glossary's "Loi sur l'équité salariale" entry is the *name*; the article text quoted from `legisquebec.gouv.qc.ca` is the *content*, and that quote is canonical.
- **Proper nouns**. Company names, person names, brand names stay as-is. The glossary covers common nouns and standard phrases.
- **Numerical or symbolic content**. Currency symbols, percentage figures, ISO dates pass through formatting rules in Section 7 — they don't need glossary lookup.

---

## Section 10 — Quality gate

Before delivering a French deck, verify:

- [ ] `deck.language: fr-ca` was set in the active engagement config
- [ ] Every slide title was sourced from Section 1 (or added via approval workflow)
- [ ] Every comp term was sourced from Section 2 (or added via approval workflow)
- [ ] Every Quebec labour reference uses the Section 3 form (TUAC not UFCW, RPC/RRQ not CPP, etc.)
- [ ] Every audience reference uses the Section 4 form
- [ ] Standard footnotes use the Section 5 verbatim text — payroll burden caveat in Quebec French for QC, in Ontario form for ON
- [ ] No banned anglicism from Section 6 appears anywhere in the deck
- [ ] All numbers, dates, currency follow Section 7 formatting (decimal comma, non-breaking thousands separator, currency symbol after, 24-hour time, ISO or French long-form dates)
- [ ] Any statute citation quotes the verbatim French text from the source URL (not glossary paraphrase)
- [ ] Engagement-end summary lists all glossary additions made during the engagement
- [ ] Additions saved to `engagements/<slug>/fr-ca-additions.yaml` in local `$STATE_ROOT`

A QA failure on any item above blocks Phase 7 delivery. Surface the failure to the user with the offending term + slide number + suggested fix.
