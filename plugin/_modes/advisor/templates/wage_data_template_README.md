# Wage Data CSV Templates — Read Before Uploading

These templates are the **only data format** the compensation-advisor skill needs for Phase 4 cost modeling. They contain the minimum columns required for accurate calculations and intentionally exclude every PII field that could turn a Claude conversation into a privacy incident.

## Why these templates exist

The skill computes wage-scale and merit-band costs from your workforce data. It does not need:

- Employee names
- Employee IDs (legacy, payroll, government)
- Hire dates, birth dates, or any date that could identify someone
- Home addresses, postal codes, phone numbers, or email addresses
- Manager names or org-chart relationships
- Performance-rating text, comments, or termination reasons
- Salary history, bonus history, or any time-series per individual
- Disability, leave, or accommodation flags
- Anything tagged "personal" or "sensitive" in your HRIS

If any of those fields are in your upload, the skill will **refuse to proceed** and ask you to re-export using one of these templates. The warning is enforced because by the time PII reaches the conversation, it's already in context — re-uploading a clean file doesn't undo the original exposure.

**The right time to filter PII is before export, not after.** That's why this README lives next to the templates.

## Which template do I use?

| Workforce type | Template | When |
|---|---|---|
| Union step-rate hourly (UFCW grocery, similar) | `wage_data_template_step.csv` | Most retail and DC populations |
| Salaried merit-based with bands | `wage_data_template_merit.csv` | Store managers, department managers, pharmacy managers, corporate-style salaried roles |
| Mixed workforce (some step, some merit) | Both files, separately | Submit one of each — the skill costs them independently and combines totals |

If you don't know which applies to your scope, look at how pay is administered. Step-rate roles advance based on hours worked or time-in-role and have a fixed scale. Merit-based roles have salary bands (min / mid / max) and individual salaries that vary based on performance, time-in-role, or both.

## Step-rate template — column reference

```
job_code,job_title,location_code,classification,current_step,hourly_rate,weekly_hours,experience_hours
```

| Column | What it means | Why the skill needs it |
|---|---|---|
| `job_code` | Internal job code (e.g., NOC code, your HRIS job ID, no employee tie) | Drives `search_roles` lookup and CBA matching |
| `job_title` | Human-readable role title | Skill display + market role matching |
| `location_code` | Internal store/site code (e.g., "QC-MTL-001"). **Not address.** | Province inference for multi-province costing |
| `classification` | Union local + role family (e.g., "UFCW-501-Retail") | CBA scale lookup via `get_cba_wage_scale` |
| `current_step` | The step the row belongs to (1, 2, 3, …) | Step-rate scenario calculation |
| `hourly_rate` | Current hourly rate at this step in this location | Base for all scenario math |
| `weekly_hours` | Standard weekly hours for the row (32 for PT, 40 for FT) | Annualization (hourly × weekly × 52) |
| `experience_hours` | Cumulative hours worked at this step (drives progression) | Mandatory cost floor — normal step progression projection |

**One row per employee** at their current step. So if you have 50 deli associates at step 2 in Montréal store 001, you'll have 50 rows. This is per-employee but **anonymized** — the skill never sees who any particular row is.

If you can't easily produce per-employee rows from your HRIS, the skill also accepts aggregated rows (one row per `job_code × location_code × current_step` combination, with `weekly_hours` representing the average and `experience_hours` representing the cohort midpoint). State that you're using aggregated rows when you upload — the skill switches to a different progression-modeling approach (uniform approximation tagged `[ESTIMATED]`).

## Merit-based template — column reference

```
job_code,job_title,location_code,grade,annual_salary,band_min,band_mid,band_max,weekly_hours,years_in_role
```

| Column | What it means | Why the skill needs it |
|---|---|---|
| `job_code` | Internal job code | Market role matching |
| `job_title` | Human-readable role title | Display + matching |
| `location_code` | Internal store/site code (no address) | Province inference |
| `grade` | Salary grade (e.g., "M3") | Band lookup |
| `annual_salary` | Current annual salary | Compa-ratio + scenario math |
| `band_min` | Minimum of the salary band for this grade | Floor adjustment scenario, position-in-range |
| `band_mid` | Midpoint of the salary band | Compa-ratio (`current / mid`) |
| `band_max` | Maximum of the salary band | Red-circle detection |
| `weekly_hours` | Standard weekly hours (almost always 40 for salaried) | Annualization sanity check |
| `years_in_role` | Years the employee has been in this role (rounded) | Compression detection (compares 0-2yr cohort vs 3-5yr cohort) |

**One row per employee.** Same anonymization principle as the step template — per-row, but no identifier ties any row to a specific person.

## What to remove from your HRIS export before saving the template

If you're exporting from SuccessFactors / SAP / Workday and modifying to fit the template, **delete these columns first** before doing anything else:

- `Employee ID`, `Worker ID`, `Person ID`, `User ID`, `Login`, `Username`
- `Employee Name`, `First Name`, `Last Name`, `Preferred Name`, `Display Name`
- `Date of Birth`, `Hire Date`, `Original Hire Date`, `Termination Date`, `Last Day Worked`
- `Email`, `Phone`, `Mobile`, `Personal Email`
- `Address`, `Street`, `City` (city is OK if you really need it; prefer location_code), `Postal Code`, `Province` (province is OK; prefer location_code that infers it), `Country`
- `Manager`, `Manager ID`, `Manager Name`, `Reports To`, `Direct Reports`
- `Performance Rating`, `Rating Description`, `Last Review Date`, `Manager Comments`
- `Bonus History`, `Salary History`, `Last Increase Date`, `Last Increase Amount`
- `Disability Status`, `Accommodation Notes`, `Leave Status`, `Leave Reason`
- `Gender`, `Ethnicity`, `Self-ID`, `Veteran Status`
- `Banking`, `Tax ID`, `SIN`, `SSN`, `NAS`

If your HRIS doesn't make this easy, ask your HRIS team to build a saved query / data view that exports only the template columns. One-time setup, every future engagement is clean.

## What if my data has different column names?

Save the file with **exactly these column names** (case-insensitive, but spelling matters). The skill matches on the canonical column names — fuzzy matching is intentionally disabled for these templates because the whole point is a clean predictable contract. If your HRIS calls `hourly_rate` something else (e.g., "Taux horaire"), rename the column in the CSV before uploading.

## How the skill uses the templates

When you upload a file matching one of these templates:

1. The skill detects the canonical column set and skips the column-mapping prompt entirely (saves ~2 minutes of friction).
2. The skill confirms the row count and template type ("16 rows, step-rate template — Acme QC retail, 3 classifications, 2 locations").
3. The skill proceeds straight to Phase 2 data validation and Phase 4 costing.

If you upload a file that **doesn't** match the templates (e.g., a raw HRIS export), the skill will:

1. Scan column names for any of the disallowed PII fields listed above.
2. If any are found, **refuse to proceed**. Instruct you to re-export using the template.
3. If no PII fields are found but the columns don't match the canonical set, fall back to the legacy column-mapping behavior (slower, more error-prone).

Always prefer the templates.

## Common questions

**"Why per-employee instead of aggregated?"**
You asked, and you're right — per-employee gives the skill richer data for progression projection and compression detection without adding any meaningful PII risk because the templates exclude every identifier. Aggregated is still accepted as a fallback but loses precision.

**"Can I add columns the template doesn't have?"**
Yes, the skill ignores extra columns. But if you add a column, double-check it's not PII — extra columns are scanned by the same disallowed-fields check.

**"What about FT/PT?"**
Inferred from `weekly_hours` (32 or fewer = PT, 33+ = FT). No separate column needed.

**"What about location → province mapping?"**
The skill maintains a small lookup of Acme `location_code` prefixes to provinces (`QC-MTL` → Quebec, `ON-TOR` → Ontario, etc.). If your location codes don't follow that pattern, you can either rename them or paste a one-time mapping at session start.

**"What if I'm asked for performance rating in a merit scenario?"**
The skill handles merit matrix scenarios using the **distribution approximation** (normal distribution around compa-ratio mean=1.0, sigma=0.09) when individual performance ratings aren't available. Tagged `[ESTIMATED]`. If you need rating-driven precision, a separate workflow exists where you provide aggregated counts per performance × compa-ratio quartile cell — ask in Phase 4 and the skill will walk you through it without ever needing per-employee ratings.

---

When in doubt: smaller files are better than larger ones. The skill needs less than you think.
