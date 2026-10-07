# LA Hacks feature attribution

Source baseline: `e72e85a22a6ec0ef19f0a9ee07b4093eb8af7753`.
The baseline commit contains the following existing capabilities; it is a containment reference, not a claim that each feature originated in that commit.

| Capability | Attribution | Source | Containing commit |
|---|---|---|---|
| Live AssemblyAI and text fallback | PRE_EXISTING | `callgate/review_transport.py`, `scripts/start_review_demo.py` | `e72e85a` |
| English rules and four-state policy | PRE_EXISTING | `callgate/engine.py` | `e72e85a` |
| Revision-aware evidence graph and receipts | PRE_EXISTING | `callgate/evidence_graph.py`, `callgate/receipt.py` | `e72e85a` |
| Separate-role scoped simulated approval | PRE_EXISTING | `callgate/confirmation.py`, `callgate/workflow.py` | `e72e85a` |
| Bounded numeric SQLite measurements | PRE_EXISTING | `callgate/live_metrics.py` | `e72e85a` |
| Author-labeled pilot and frozen first run | PRE_EXISTING | `evaluation_v1/` | `42f0af8`, contained in `e72e85a` |
| P0–P5 documentation/data/check tools | PRE_EXISTING once merged | This patch; no product feature implementation | Pending user PR commit |

## Event additions — leave empty until actually built

User-directed final-product implementation began before the future event. The local increment below must not be attributed to that future event. After the user's PR, record its real commit SHA.

| New local capability | Actual attribution | Evidence |
|---|---|---|
| Bounded bilingual text extraction and monotone policy | BUILT_NOW, pending user PR | `callgate/safety_policy.py`, property/fixture tests |
| Session authorization-denial latch | BUILT_NOW, pending user PR | `callgate/workflow.py`, denial/expiry tests |
| Direct protected-action rejection and visible UI test | BUILT_NOW, pending user PR | `callgate/review_transport.py`, `participant.html` |
| Counterfactual-plus-valid-approval rehearsal | BUILT_NOW, pending user PR | `scripts/proof_demo.py` |
| Truth/claims/input validation and documentation | BUILT_NOW, pending user PR | `CLAIMS.md`, `evaluation_v2/`, `docs/` |

| Intended addition | Attribution | Start/finish commit | Evidence |
|---|---|---|---|
| Evidence monotonicity with revision semantics | | | |
| Mandarin / code-switch evidence extraction | | | |
| Enrolled, claimed-identity-bound contact challenge | | | |
| Self-approval rejection and independently scoped gateway | | | |
| Detector-failure replay over controlled simulator | | | |
| Joint authorization safety and legitimate-request utility evaluation | | | |

## Rules audit

Saved-contact increment merged as `6855522`. Current follow-up: multiple synthetic saved contacts with distinct reviewer processes and bearer routes, BUILT_NOW; source `scripts/start_review_demo.py`, `callgate/review_transport.py`, tests in `test_multiple_contacts.py` and `test_review_process.py`. Remote device delivery and verified human enrollment remain incomplete.

Owner squash-merged the previously pending local increment as `1882e3d` on 2026-10-06. The pending labels above describe the original audit snapshot. Current follow-up adds trusted-startup saved-contact routing and credential-origin checks (`callgate/contacts.py`, `tests/test_contact_binding.py`); BUILT_NOW, not future-event work. Independent human enrollment and remote delivery remain incomplete.

Official URL: https://la-ai-hackathon-2026.devpost.com/rules
Accessed 2026-10-05. Pre-existing open source is allowed; only clearly disclosed new event features are judged. The page also contains an April deadline inconsistent with the October event header. Confirm final timing with organizers; do not invent an exact coding duration.
