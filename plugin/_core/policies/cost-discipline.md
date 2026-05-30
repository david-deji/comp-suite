# Cost Discipline

Be deliberate about API spend, tool costs, and recurring subscriptions. The failure mode is not "we spent on something useful" — it's "we spent on a test loop we forgot was running."

## Musts

- When iterating against a paid API, cap the experiment before starting — number of calls or dollar budget, whichever is tighter. State the cap to the founder before launching the iteration.
- Default to the cheapest tier (model, quality level, batch size) that proves the point. Scale only after the cheap version validates the approach.
- For long-running or recurring spend (subscriptions, scheduled jobs, persistent agents), record a review date when adding it. WHY: subscriptions decay into "we forgot we still pay for this" without a forcing function.
- Confirm pricing on the official docs before the first paid API call, not after the bill arrives. Pricing changes — model assumptions about cost are routinely off.

## Must-Nots

- Never run open-ended retry/iteration loops against a paid API without an exit condition.
- Never leave a paid API call inside a polling loop without a backoff and a budget exit.
- Never assume a "small" API call is free — verify pricing before the first call.
- Never spin up a paid background agent or scheduled job without telling the founder the recurring cost.

## Preferences

- Prefer one cheap test that disproves a hypothesis over five expensive tests that confirm it.
- Prefer regenerating cleanly at the right inputs over post-processing a bad output, when the regen cost is comparable.
- Prefer cached or stored outputs over re-running the same paid call across sessions.

## Why

A single inadvertent loop on a paid endpoint can drain a TM-scale account in minutes. The discipline is not frugality for its own sake — it is catching the predictable mistakes (unbounded loops, forgotten subscriptions, untested pricing assumptions) before they compound.
