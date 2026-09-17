# CallGate

A local risk-evidence and two-person authorization protocol prototype for voice requests to move money into a "safe account". It is not a production SDK.

**Current boundary:** The local review demo connects consenting microphone input (or text fallback), streaming transcription, advisory risk policy, a two-person challenge step, and one simulated action. Real human identity enrollment, registered out-of-band contacts, multi-tenant isolation, remote trusted transport, key lifecycle/storage, latency SLA, and enforcement over real tools are not implemented. It cannot block a bank transfer or control a phone call.

## Try the standalone sensor

See **Current Status** below before interpreting the demo or evaluation results.

Follow [本机运行与检查](START_HERE.md) for the existing environment, or [setup and API guide](docs/V2_PHASE1.md) for installation. With dependencies installed, run:

```powershell
python scripts/start_demo.py
```

This older standalone page isolates the speech-to-risk sensor and does not enter the confirmation workflow. Open `http://127.0.0.1:8765/`, click Start, and allow microphone access. Streaming transcription requires an AssemblyAI key in the local `.env` and an internet connection. Use synthetic English speech:

1. "Move your savings into the secure holding wallet." → `CHALLENGED`: verify before acting.
2. "Do not tell anyone." → `COOLING_OFF`: pause and verify independently.

These are expected baseline behaviors, not proof of scam detection accuracy. Recognition errors can change the result. Offline checks are available through `Check-CallGate.ps1` without a key or network access.

## What runs today

`Audio → AssemblyAI streaming transcript → English rule events → conversation state → score timeline → advisory Guardian`

- Events reference transcript segments and revisions. Corrections replace current evidence.
- Scores are heuristic reference values, not fraud probabilities or verified identities.
- The four implemented audio states are `UNVERIFIED`, `CHALLENGED`, `COOLING_OFF`, and `BLOCKED`. All provide advice; `BLOCKED` means a warning against sharing sensitive information, not an external action block.
- NetworkX projects current evidence in the connected demo. The participant can inspect deduplicated rule contributions and download an Ed25519-signed risk receipt. SQLite replay protection remains a separately tested primitive; the demo uses an in-memory gate.

## Current Status

**Unvalidated, author-labeled synthetic pilot; not a production service or an LLM agent.**

- Dataset: 60 synthetic pilot calls, split into 36 development and 24 initially held-out calls. The test subset contains 8 scam, 8 benign and 8 ambiguous calls; binary metrics use 16 calls. The proposed expansion to 600 new scenario families has not been performed.
- Independent review: no reviewers confirmed and no completed outreach recorded. Planned owner-led outreach: UCLA/TASL peers by September 20, 2026, with eligible Crystar peers as fallback; confirmation deadline September 23. These are plans, not evidence of completed review.
- Results: CallGate F1 **22.2%**, versus **30.8%** for the keyword baseline. CallGate detected 1 of 8 scam calls and falsely flagged 0 of 8 benign calls. The full report includes uncertainty intervals; this small synthetic result is not evidence of real-world superiority.
- Ablations: three evaluation-only policy removals produced zero binary-metric delta; the pilot did not exercise the distinguishing credential-block, secrecy-cooling or revision-sensitive sticky behavior. This does not establish that those components are ineffective.
- States: **four implemented** risk states: UNVERIFIED, CHALLENGED, COOLING_OFF, BLOCKED. This 24-call pilot observed only UNVERIFIED (23) and CHALLENGED (1). COOLING_OFF and BLOCKED have separate fixture tests; VERIFIED_BOUNDED and ESCALATED are earlier design concepts, not current Conversation states. No real-world state-coverage claim is made.
- Judgment: risk extraction, scoring and state decisions are deterministic rules. AssemblyAI supplies transcription in the live demo; the text-only pilot invoked neither ASR nor an LLM.
- Test exposure: the first test run is preserved and the set is now revealed. Subsequent changes on these cases cannot support final improvement claims.

### Full evaluation disclosure

This evaluation uses synthetic transcripts with provisional labels supplied by the same project assistant that authored the cases and had prior access to the CallGate implementation. Labels were not derived from CallGate predictions. No independent human annotation, adjudication, or inter-rater reliability study has been completed. A frozen holdout limits later tuning exposure but does not establish author independence or real-world validity.

### Inspect and reproduce

[Full pilot report, failure examples and figures](evaluation_v1/pilot_results/REPORT.md) · [Reproduction scope](evaluation_v1/README.md) · [Resume and interview claims](evaluation_v1/RESUME_AND_INTERVIEW.md)

With the repository dependencies installed, run from the repository root:

```powershell
python -m pytest -q -p no:cacheprovider
node --test tests/review_ui.test.cjs
python -m evaluation_v1.evaluate_pilot render
```

The recorded local checks passed 184 Python tests and 3 Node logic tests. These
are local checks, not a claim of a green remote CI run. Rendering uses committed
first-run calls, labels, predictions and clock samples; it makes no API calls and
does not rerun predictions. Fresh inference needs the original private inputs;
details and exact recorded environment are linked above. Local text timings are
not end-to-end speech latency; infrastructure cost remains unmeasured.

## Try the connected local protocol

Run `./Start-Review-Demo.ps1` in PowerShell, or `python -m scripts.start_review_demo` in the complete environment. The launcher prints two private entry links: participant on port 8766 and reviewer on 8767. The participant can use live AssemblyAI transcription or the offline text fallback; both feed the same risk and confirmation state. Nothing is installed by the launcher. Microphone use calls AssemblyAI; text fallback does not call a cloud service.

1. Participant: explicitly allow processing of fictional test content, analyze the prefilled safe-account sentence, then submit the fictional amount and destination.
2. The participant receives a six-digit one-time challenge and sends it through a separate demo channel.
3. Reviewer: read the request, check the exact amount and destination, enter the challenge, then approve or deny.
4. Participant: refresh the result. Approval permits one simulated action only. New transcript content or consent withdrawal invalidates pending confirmation; secrecy/credential states prevent a new request.

Each role has a different bearer capability. Approval requires both the reviewer capability and the participant's one-time challenge; the reviewer API cannot read that challenge. Three wrong challenge attempts cancel the request. This is a minimal two-person control, not identity verification: no person or outside contact channel is enrolled, and the two users could collude or share both secrets. The reviewer private key is generated only inside the reviewer process; the participant backend receives its public key. Both processes and the host remain trusted.

Keys and pending state are ephemeral; restart invalidates old entries. This launcher uses an in-memory replay gate and one session per startup. Tests exercise authenticated audio ingress, shared workflow state, real loopback HTTP across both processes, repeat approval rejection, and reviewer unavailability. Live provider accuracy and latency are not established by those mocked integration tests.

During a live run, the participant page shows received audio duration, local risk-engine time, and an observed end-of-speech-to-alert proxy. The proxy combines provider timestamps with the local server clock and is not an SLA measurement. Cost is shown only when `CALLGATE_ASR_USD_PER_HOUR` is set from the operator's current provider terms; otherwise it reports that the rate is unconfigured. The estimate covers ASR only. This path has no LLM, TTS, or SIP charge.

The page aggregates the latest 100 admitted streams and exports a versioned JSON measurement report. Completion, failure, intentional cancellation, and disconnect are counted separately. Failure rate uses only completed + failed streams; disconnect cause is unknown. Alert P50/P95 includes only completed streams with a new final risk transition and valid audio timestamps. Missing, negative, or out-of-range timing estimates remain unavailable. Per-stream engine timing is its maximum ingest time. The report contains numeric samples and fixed outcome labels, no audio, transcripts, challenge codes or session identifiers; the launcher automatically commits completed stream records to callgate-metrics.sqlite3 and restores the last 100 on restart. An unfinished stream can still be lost on process crash. The application factory defaults to memory unless metrics_database is supplied. Stop the service and remove the database to clear retained metrics. Downloaded files remain until the operator removes them.

Use “查看风险依据” for evidence and “下载签名决策回执” for a signed current-risk snapshot. The receipt omits speech but retains a session ID; it is not an anonymous performance report or an action permission. Verify it offline with `python -m scripts.verify_receipt RECEIPT.json --public-key EXPECTED_HEX --session EXPECTED_SESSION`. The expected key must have been retained independently from the authenticated `GET /api/receipt-key` response; accepting a key bundled in an untrusted receipt proves no issuer identity. Receipt keys are disposable per broker startup, without rotation or revocation infrastructure.

Each microphone connection receives a fresh ingress namespace because provider turn numbers restart at zero. The participant page displays provider transcript text separately from the risk result, so a recognition error can be distinguished from an English-rule coverage gap. The supplied phrases are reproducible examples, not the only accepted audio; the current deterministic extractor deliberately recognizes a limited set of English risk expressions.

## Reuse and project contribution

AssemblyAI supplies streaming transcription; Silero and Pipecat integrations provide optional voice processing components; NetworkX, cryptography and SQLite supply graph, signature and persistence primitives. CallGate adds revision-aware evidence handling, cross-turn action/secrecy rules, advisory policy, and tests of scoped credentials and replay rejection.

This is an integration prototype. Comparative superiority over other projects has not been established. See the [source comparison and reuse notes](docs/V2_RESEARCH.md) for research context.

## Evidence and next milestone

The [local report](scambench/LOCAL_RESULTS.md) records regression tests and 25 same-author synthetic development cases. This is an internal synthetic regression suite despite the legacy `scambench/` directory name; it is not an industry benchmark and does not estimate real-world accuracy. An independently authored, frozen evaluation dataset is still needed. Engine timings and scripted audio timestamps do not establish live speech-to-alert latency.

Next: measure live alert latency, false interventions, and actual service cost on the connected path. Reviewer identity enrollment and production integration remain later milestones.

## Reference material

Consent withdrawal and scenario reset cancel active provider tasks on the broker, even if the browser does not disconnect. Audio callbacks are bound to a processing generation so late results cannot enter a newly consented scenario. The provider adapter bounds final draining to ten seconds and rejects unsolicited early termination. The broker admits one live stream at a time, limits it to 90 seconds, and rejects confirmation requests/decisions until audio processing finishes; the browser stops recording after 60 seconds. These controls do not delete data already sent to the provider or establish legal consent from every speaker.

- [Run and API details](docs/V2_PHASE1.md)
- [Local results](scambench/LOCAL_RESULTS.md)
- [Build history and disclosure](BUILD_LOG.md)
- [Current delivery and mathematics/ZK boundaries](docs/DELIVERY_STATUS.md)

The remaining documents in `docs/`, including architecture, threat model, product strategy and pitch plans, are design/reference material. Their future capabilities are not implementation claims. Original research is preserved at commit `16c469ae78f22f06df757595b8b36edd9359086e`.

## License

[MIT](LICENSE). Reused libraries and models retain their respective licenses and attribution.
