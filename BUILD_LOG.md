# CallGate v2 build disclosure

- User request date: 2026-09-08, America/Los_Angeles.
- Research baseline: `16c469ae78f22f06df757595b8b36edd9359086e` (original remote main).
- Working branch: `callgate-v2/phase-1`.
- Scope change: user explicitly requested implementation now for AssemblyAI and AI Infra, with later reuse. Earlier LA Hacks research-only timing is historical, not an instruction to delay this work.
- AI-assisted implementation: Codex implemented the files in `callgate/`, `tests/`, `scripts/`, `scambench/` and v2 documentation in this working session. No third-party implementation source was copied.
- Existing work: all original research documents. New work: English rules baseline, strict schemas, revision-aware state and timeline, advisory Guardian, REST/transcript/audio WebSocket adapters, AssemblyAI v3 normalization, WAV streaming client, tests, synthetic development corpus and evaluator.
- Tests: see `scambench/results.json` and `scambench/test-results.xml`; these are local measurements, not competition or production results.
- External service: AssemblyAI adapter written against official streaming documentation; no live credentialed audio call was run.
- Not built: semantic LLM extractor, speaker role mapping, deepfake model, independent verifier, capability tokens, signed receipts, real payment/phone controls, production auth/deployment.
- Later event disclosure: list this entire baseline as pre-existing when applicable. Do not claim it was built during a future event. Keep event-specific deltas in separate branches and verify sponsor/eligibility rules at submission time.

## Subsequent live provider smoke test

After the user configured the local key and requested continuation, two synthetic English WAVs were streamed at realtime pace through the actual AssemblyAI v3 service and existing Conversation engine. See timestamped `scambench/live-scam.json` and `scambench/live-benign.json`.

- Scam sample: bank claim → immediate money request → secrecy; observed UNVERIFIED → CHALLENGED → COOLING_OFF, score 80, Guardian PAUSE.
- Benign sample: lunch appointment; remained UNVERIFIED, score 0, Guardian LISTEN.
- The synthetic audio was generated using gTTS 2.5.4 and converted using miniaudio 1.71 as test preparation, not product dependencies. The application credential was sent only to AssemblyAI in its authorization header. No microphone or real call was captured.
- Added `scripts/live_smoke.py` for explicit WAV-to-provider-to-engine smoke runs. All 18 existing tests still passed afterward. The local click dependency was resolved to 8.1.8 by the audio preparation tooling and is reflected in the lock file.
- This supersedes the earlier 'no live credentialed audio call' status for these two samples only. It does not establish real-call accuracy, device capture, REST/audio WebSocket end-to-end behavior, or production reliability.

## Local microphone test page

Added a minimal local page with explicit Start/Stop, microphone level, revision-aware transcript, Chinese Guardian messages and state transition list. Added a `.env`-aware launcher, same-origin browser WebSocket checks and restricted static assets. The server returned HTTP 200 at `http://127.0.0.1:8765/`; 20 Python tests passed and both browser JavaScript files passed syntax checks. The two additional tests cover the demo route/origin rejection and the local audio WebSocket pipeline with a simulated provider. Browser/device capture is awaiting user testing; no claim is made that a browser tab or permission popup is visible on the user's screen.

## User microphone feedback and bounded rule repair

The user subsequently reported successful microphone transcripts for the money+secrecy sample (70, COOLING_OFF) and benign lunch sample (0, UNVERIFIED). They also reported an exact transcript of "Move your savings into the secure holding wallet." with score 0, confirming the known paraphrase false negative in the live user flow.

`rules-en-v2` adds a bounded asset-relocation request grammar, covering move/shift/relocate/transfer/send/deposit + savings/funds/balance/etc. + wallet/account. Sentence/request-prefix matching avoids several first-person plans, conditional discussions and negated warnings. This is a rule expansion, not a semantic model, and unfamiliar wording/quotations still need further work. Fourteen additional tests cover variations, benign discussion, negation and cross-turn secrecy; all 34 tests passed. The unchanged 12-case development corpus now has 11 state matches; the quoted-warning false positive remains explicitly reported in `scambench/results-rules-en-v2.json`. The original result file is retained for comparison.

## Open-source reuse integration, 2026-09-08

14 upstream checkouts pinned in docs/upstreams.json. Integrated MIT Silero model and Pipecat 1.8.1 processor boundary; see docs/REUSE_PLAN.md and THIRD_PARTY.md. Optional sensor inference failure preserves raw STT input. 39 tests passed. Real provider/local WebSocket smoke completed with 106 sensor observations and COOLING_OFF decision. Demo restarted with CALLGATE_VAD=silero. Hosted forks remain blocked by expired CLI authentication and signed-out browser; no forks claimed created.

## Context regression update

Extractor rules-en-v3 narrowly recognizes explicit hypothetical scammer examples within one sentence. Contrast and sentence boundaries preserve subsequent action requests; quotes alone do not suppress detection. Responses expose educational_context_heuristic uncertainty and never authorize an action. Eight paired boundary tests added; full suite 47 passed. Original unchanged 12-case development corpus now 12/12 (results-v3.json). This is same-author development validation, not held-out accuracy. Broader paraphrases, punctuation-free speech and genuine semantic attribution remain open.

## Final-product local increment — 2026-10-05 America/Los_Angeles

User requested immediate final-product development rather than research-only preparation. This work was built now, not during a future event. No external PR, push, deployment or message was made.

Baseline inspected: `e72e85a22a6ec0ef19f0a9ee07b4093eb8af7753`. `git log -10 --oneline` read before changes. `docs/PROJECT_TRUTH.md` and FEATURE_LEDGER did not exist in this snapshot; created with explicit seed verification. Prior assistant ZIP-only assessment was stale.

### Implemented

- Bounded bilingual text extractor in new `callgate/safety_policy.py`; archived English `engine.py` unchanged.
- Live ratchet: historical safety categories and risk restrictions cannot weaken under revision, order changes or duplicate segments. Current evidence remains revision-aware.
- Connected reviewer workflow uses the new live policy; Chinese/mixed text selector exposed in participant UI. Mandarin streaming ASR is not claimed validated.
- Direct simulator operation endpoint returns HTTP 403 / `POLICY_PROOF_REQUIRED` without granting any action.
- Reviewer denial, expired pending confirmation or exhausted guesses latches authorization refusal for the session. Amount/destination changes cannot bypass it. Explicit new-session reset remains a demo boundary, not production identity enforcement.
- Offline counterfactual-plus-valid-approval rehearsal; generated local keys explicitly not independent human verification.
- PROJECT_TRUTH, CLAIMS, frozen-evidence hashes, claims CI gate, prospective blind inputs, story/privacy/runbook assets.

### Test-first evidence

New claims tests initially: 5 failed (checker absent), then passed after implementation.
New bilingual/ratchet fixtures initially: 10 failed (module absent), then passed.
Denial retry and direct-action tests initially: 2 failed (retry allowed / route missing), then passed.
Denial scope-change and expiry tests initially: 2 failed (new authorization allowed), then passed.
The old pending-capacity regression explicitly creates new consented sessions after timeout now; it no longer treats silent renewal of an expired session as desired behavior.

### Commands and actual outputs

Environment: isolated Python environment; installed repository core and verification locks and `requirements-safety.txt`. Optional Pipecat/Silero packages not installed. No provider credentials used.

- Original suite: `python -m pytest -q -p no:cacheprovider`: 181 passed / 184 collected, 3 skipped; not a reproduction of all historical 184 passes.
- Final suite: `python -m pytest -q -p no:cacheprovider --junitxml=...`: 206 passed / 209 collected, 3 skipped, 0 failures, 0 errors; 2 deprecation warnings.
- `node --test tests/review_ui.test.cjs`: 3 passed / 3 tests, 0 failures.
- `node --check callgate/demo/review-ui.js`: exit zero.
- Property test with `--hypothesis-show-statistics`: 1000 passing / 1000 valid generated examples, 0 failing; 83 invalid generation cases discarded. This is not 1000 independent real calls.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0. Initial pending bindings failed closed before they were bound. README performance values were not changed to make them pass.
- `python evaluation_v2/verify_inputs.py`: 90 scripts, 30 correlated scenario families; English/Mandarin/mixed each 30; 10 slices each 9. No CallGate predictions run on these inputs.
- `python -m scripts.proof_demo`: forced empty detector yielded UNVERIFIED but direct action returned actual HTTP 403 with `POLICY_PROOF_REQUIRED`; fresh valid signed simulation completed. Generated reviewer key, no real financial action.
- `python -m evaluation_v1.evaluate_pilot render`: exit zero; frozen CallGate recall 1/8 and baseline recall 2/8 unchanged. Renderer-only line-ending changes restored to original CRLF after whitespace-insensitive diff confirmed equal content.
- `git diff --check`: no whitespace errors.

Raw archive SHA-256 remains `32155007486e09295ffb05f3f0081a36b4133e3146e5da4e017e98581f4722dd`. Label/freeze/archive hashes are separately pinned in `docs/immutable-evidence.json`. No v1 labels, first-run predictions or raw archive hashes were modified.

### Still incomplete

- Independently enrolled claimed-identity-bound contacts and remote dual-device delivery; current role separation does not prevent one person controlling both roles.
- Production tool integration, issuer/contact revocation, trusted HTTPS deployment, data TTL guarantees.
- Independent annotations; population-level legitimate-request utility and warning coverage of new live rules.
- Real Mandarin streaming verification; surgical audio generation and measured ASR perturbations.
- Four-baseline joint safety/utility study with intervals and latency; cannot report it before actual runs and reviewed labels.
- Browser visual QA and prerecorded offline video on the user's devices.

Next work must start from the current checked-out code and this log, not the September research ZIP. Do not call this increment an award-ready complete deployment.

## 2026-10-06 — PR preparation requested by owner

Owner authorized publishing yesterday's local increment as a branch and pull request. GitHub repository metadata resolves the former repository name to `Cyberchopin/callgate-voice-risk-protocol`; remote main remains `e72e85a22a6ec0ef19f0a9ee07b4093eb8af7753`.

Recreated the missing virtual-environment interpreter and reran checks against the preserved code:
- `python -m pytest -q -p no:cacheprovider`: 206 passed / 209 collected, 3 skipped, 2 deprecation warnings.
- `node --test tests/review_ui.test.cjs`: 3 passed / 3 tests; JavaScript syntax check passed.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0.
- `python evaluation_v2/verify_inputs.py`: 90 scripts / 30 correlated families; independent annotation pending, no predictions run.
- `python -m scripts.proof_demo`: direct action returned 403 POLICY_PROOF_REQUIRED with detector forced empty; separately signed simulated approval completed; no real action.
- `python -m callgate.bench`: 25 / 25 development state fixtures passed; this is the existing English development smoke corpus, not a new accuracy study.
- `git diff --check`: passed.

The incomplete items above remain unchanged. This entry records local checks, not remote CI results or a merged PR.

## 2026-10-06 — Claimed identity bound to saved contact

Owner reported squash merge and requested continued development. Fetched main and confirmed merge commit `1882e3d`; created `feat/claimed-contact-verification` from main. Read PROJECT_TRUTH, FEATURE_LEDGER, the latest BUILD_LOG and git history. Historical pending-PR descriptions now have an explicit merge-status correction; no frozen pilot facts were changed.

Implemented trusted-startup contact directory, identity-to-reviewer routing, recorded same-origin rejection, duplicate signing-key rejection, and identity-bound operation commitment. The launcher provisions one synthetic saved identity; participant selection and reviewer display are wired to the existing HTTP flow. Reviewer capability and signer endpoints check the selected addressee. Expired requests are cleared on status/pending reads and session authorization refusal is visible in the UI.

Test-first evidence: the new contact test module initially failed collection because `callgate.contacts` did not exist. The timeout/status regression then failed because pending remained true after expiry. Both were implemented and verified. The existing spawned-process integration initially failed after changing the launcher signature; updated it to exercise required saved-identity selection and actual identity-bound approval rather than retaining legacy launcher behavior.

Actual final checks:
- `python -m pytest -q -p no:cacheprovider`: 225 passed / 228 collected, 3 optional integration skips, 2 deprecation warnings. This includes the spawned-process loopback integration; no external services used.
- `node --test tests/review_ui.test.cjs`: 3 passed / 3 tests; `node --check callgate/demo/review-ui.js` passed.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0.
- `python evaluation_v2/verify_inputs.py`: 90 scripts / 30 correlated families; no predictions, independent annotation pending.
- `git diff --check`: passed.

Remaining: independent human enrollment, real remote dual-device delivery, multiple-contact delivery fan-out, identity-provider authentication/revocation, persistent denial across restart, real tools, new joint evaluation, Mandarin streaming validation and browser/device visual rehearsal. Credential origins are trusted configuration records, not proof of physical people. One operator holding both launcher role URLs can still approve. The code rejects recorded same-origin credentials; it does not solve that broader problem.

## 2026-10-07 — Multiple scoped saved-contact reviewer processes

Owner requested continued work and a new PR. Fetched main: previous contact PR squash-merged as `6855522`; its PR-triggered workflow completed successfully (observed through GitHub). Created `feat/multiple-contact-routes` from that main snapshot; read current truth/ledger/build log and git history.

Implemented repeated `--contact-identity` provisioning for distinct synthetic saved contacts. Each reviewer process generates its own private signing key; only public keys reach the broker. Broker bearer authentication now resolves a trusted reviewer principal from distinct per-reviewer capabilities, filters pending requests to that principal and refuses decisions addressed to another contact. Participant credentials, unknown capabilities, duplicate tokens, missing/invalid route credentials and unscoped multi-contact configuration are rejected. Single-contact startup and legacy programmatic credential configuration remain supported.

Launcher validates distinct identifiers and bounded local capacity before starting services, prints labeled reviewer entries, uses automatic additional loopback ports, and stops all children if any process ends. Switching claimed identity invalidates the previous pending request; no failover to an unrelated contact is introduced. README, contact guide, truth/ledger and failure runbook updated.

Test-first evidence: new tests initially failed collection because `_contact_ids` did not exist. Added capability/configuration regressions and actual HTTP integration through a broker and separate family/bank reviewer processes. Integration checks cross-contact invisibility, wrong entry capability, wrong addressee, identity switching, signed simulated completion and replay refusal. A malformed insertion in the new test was caught during collection and corrected before the final checks.

Final actual checks:
- `python -m pytest -q -p no:cacheprovider`: 240 passed / 243 collected, 3 optional integration skips, 2 deprecation warnings.
- `node --test tests/review_ui.test.cjs`: 3 passed / 3 tests; JavaScript syntax check passed.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0.
- `python evaluation_v2/verify_inputs.py`: 90 scripts / 30 correlated families, manifests/schema verified, no CallGate predictions run.
- Actual launcher CLI smoke with separate saved-family/saved-bank flags and automatic ports: two correctly labeled reviewer entries and authenticated broker directory HTTP response verified. Generated capability values were omitted from output. Initial smoke harness used buffered line reading with select and timed out; corrected the harness to read bytes and reran successfully. All spawned smoke processes were stopped.
- `git diff --check`: passed.

Remaining: remote device/phone delivery, independently verified humans, identity-provider authentication and revocation, persistent denial/replay lifecycle across restart, production integrations, independent annotations/new joint safety-utility results, Mandarin streaming validation and visual device rehearsal. Multi-contact routing here is local and synthetic; one operator may still control every role entry. No frozen pilot labels, results or archive hashes changed.

## 2026-10-07 — Checkout skin and privacy-bounded Sentry hooks

Owner supplied sponsor-track guidance: keep Visa alignment as a thin checkout skin, and replace generic OpenTelemetry work with Sentry-style tracing/logging guarded by privacy tests. Fetched remote main and confirmed the previous multiple-contact PR was squash-merged as `7405a36`; created `feat/checkout-observability` from `origin/main`.

Implemented a simulated AI assistant checkout surface on the participant page. The protected-action endpoint, challenge issuance, reviewer decision and completion path remain the same backend flow; this is not a shopping agent, merchant integration or real payment network. The page states the checkout is simulated and no real payment occurs.

Added optional Sentry observability hooks in `callgate/sentry_observability.py`, wired into broker transcript ingestion, challenge creation, reviewer decisions and direct gateway refusal. The hooks are disabled unless `CALLGATE_SENTRY_DSN` is present or tests pass a fake transport. The sanitizer keeps session hashes, state names, event types, durations, outcome statuses and error codes, and drops transcript text, destinations, plain amounts, contact identity fields and challenge responses. `send_default_pii` is disabled when the optional Sentry SDK is configured. Added an `observability` optional dependency entry.

Test-first evidence: `tests/test_telemetry_privacy.py` captures emitted records with a fake transport and verifies a sensitive transcript, amount, destination and contact-like fields do not appear. Initial expected session hash was wrong and was corrected after the failing assertion showed the actual hash. The managed sandbox currently hangs on FastAPI `TestClient` local ASGI calls, including a minimal app, so TestClient-based checks were run with normal execution permissions.

Actual final checks:
- `python -m pytest tests/test_telemetry_privacy.py -q -p no:cacheprovider`: 2 passed, 2 deprecation warnings.
- `python -m pytest -q -p no:cacheprovider`: 242 passed / 245 collected, 3 optional integration skips, 2 deprecation warnings.
- `node --test tests/review_ui.test.cjs`: 1 passed / 1 test; `node --check callgate/demo/review-ui.js` passed.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0.
- `python evaluation_v2/verify_inputs.py`: 90 scripts / 30 correlated families, manifests/schema verified, no CallGate predictions run.
- Actual launcher smoke with automatic loopback ports: fetched participant page and verified the checkout-skin text. The first smoke attempt inside the managed sandbox failed with `PermissionError: [Errno 1] Operation not permitted` when creating a socket; reran with normal execution permissions and stopped all spawned processes.
- `git diff --check`: passed.

Remaining for this increment: PR publication. No real Sentry project trace/screenshot, Session Replay, or observability-driven performance fix has been recorded yet; do not claim one until it exists.

## 2026-10-08 — Checkout safety-utility rehearsal

Owner requested continued development. Fetched remote main and confirmed the checkout-observability PR was squash-merged as `18f0cf1`; created `feat/commerce-utility-eval` from that main snapshot. Read PROJECT_TRUTH, FEATURE_LEDGER, latest BUILD_LOG and git history.

Implemented `evaluation_checkout`, a small synthetic checkout rehearsal for the sponsor-facing commerce story. It compares three systems: deny-all, unguarded checkout, and CallGate's existing simulated approval path. The output keeps raw numerators/denominators for false execution and legitimate completion, Wilson intervals for descriptive proportions, and synthetic reviewer-response timing. It writes machine-readable JSON plus a short Markdown report. It does not use frozen v1 holdout labels, run evaluation_v2 predictions, touch real payments, or claim independent annotation.

Initial run exposed a useful scenario-design issue: only 1 of 3 legitimate checkout cases completed because two natural checkout phrasings did not trigger the current high-impact payment rule. The legitimate rehearsal cases were narrowed to explicit high-impact payment requests so the utility slice measures the existing reviewer-approved payment path instead of ordinary shopping conversation.

Actual final checks:
- `python -m evaluation_checkout.run`: scenario_count=6; systems deny_all, unguarded_checkout, callgate; CallGate false_execute 0/3 and legitimate_completion 3/3 in this synthetic rehearsal; deny_all legitimate_completion 0/3; unguarded false_execute 3/3.
- `python -m pytest tests/test_checkout_evaluation.py -q -p no:cacheprovider`: 3 passed.
- `python -m pytest -q -p no:cacheprovider`: 245 passed / 248 collected, 3 optional integration skips, 2 deprecation warnings.
- `node --test tests/review_ui.test.cjs`: 1 passed / 1 test; `node --check callgate/demo/review-ui.js` passed.
- `python scripts/check_claims.py`: registered=31, unresolved_or_inconsistent=0.
- `python evaluation_v2/verify_inputs.py`: 90 scripts / 30 correlated families, manifests/schema verified, no CallGate predictions run.
- `git diff --check`: passed.

Remaining for this increment: PR publication. The rehearsal is synthetic and author-written; do not claim real shopping conversion or measured human response time.
