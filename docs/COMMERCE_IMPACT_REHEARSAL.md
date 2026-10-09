# Commerce impact rehearsal

This is a controlled checkout simulator for the sponsor-facing story. It is not
a product metric, a real-shopping study, an independent label set, or a fraud
prevalence estimate.

Run:

```bash
python -m evaluation_checkout.run
```

The script writes:

- `evaluation_checkout/results.json`: machine-readable rows, raw numerators and denominators, Wilson intervals for descriptive proportions.
- `evaluation_checkout/REPORT.md`: short human-readable table.

## What it compares

| System | Behavior in the rehearsal |
|---|---|
| `deny_all` | Never completes a protected checkout. |
| `unguarded_checkout` | Completes every protected checkout attempt. |
| `callgate` | Uses the existing transcript, policy, challenge, reviewer signature and simulated gate path. |

## What the current result shows

The generated report makes the deny-all tradeoff visible: it can avoid
unauthorized simulated execution while completing no legitimate checkout. It
also makes the unguarded checkout tradeoff visible: it completes legitimate
requests but also completes unauthorized ones.

CallGate's result in this rehearsal depends on the synthetic scenario design
and simulated reviewer responses. It demonstrates that the same protected path
can complete a legitimate, reviewer-approved checkout while refusing scam-like
or blocked cases. It does not prove real consumer conversion, real fraud
prevention, or real contact response timing.

## Allowed pitch wording

"We added a reproducible checkout rehearsal that reports safety and utility
together, so a deny-all gate cannot look successful just because it blocks
everything."

## Not allowed

- Do not claim a payment network integration.
- Do not claim the numbers are real-world accuracy.
- Do not claim independent labels or human-response measurements.
- Do not compare this author-written rehearsal to the frozen v1 voice-risk pilot.
