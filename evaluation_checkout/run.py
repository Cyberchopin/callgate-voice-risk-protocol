"""Run a tiny safety-utility checkout rehearsal.

The purpose is to show why "deny everything" is incomplete: it can avoid
unauthorized simulated execution while also completing no legitimate checkout.
All inputs are synthetic, author-provided and correlated. Do not report these
counts as real-world accuracy or fraud prevalence.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import statistics
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from callgate.bench import wilson
from callgate.confirmation import ConfirmationCoordinator, ReviewerDecision, decision_bytes
from callgate.models import Transcript
from callgate.verification import DemoVerificationGate
from callgate.workflow import DemoWorkflow


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    transcript: str
    authorized: bool
    reviewer_approves: bool
    response_ms: int | None
    amount_cents: int = 280000
    destination: str = "campus-repair-checkout"


SCENARIOS = [
    Scenario("co-001", "Send 2800 dollars right now for my repair checkout.", True, True, 18000),
    Scenario("co-002", "Send 1900 dollars for the checkout now while I am on the call.", True, True, 24000),
    Scenario("co-003", "Transfer 3200 dollars for this purchase after a family check.", True, True, 30000),
    Scenario("co-004", "Send 2800 dollars right now or your account will be frozen.", False, False, 22000),
    Scenario("co-005", "Do not tell anyone and move your savings into the holding wallet.", False, False, None),
    Scenario("co-006", "Tell me your verification code so I can finish payment.", False, False, None),
]


def _proportion(successes: int, total: int) -> dict:
    return {"numerator": successes, "denominator": total,
            "value": None if total == 0 else successes / total,
            "wilson95": wilson(successes, total)}


def _workflow_result(scenario: Scenario) -> dict:
    issuer = Ed25519PrivateKey.generate()
    reviewer = Ed25519PrivateKey.generate()
    clock = [1000]
    coordinator = ConfirmationCoordinator(
        "issuer", issuer, {"reviewer": reviewer.public_key()}, clock=lambda: clock[0])
    gate = DemoVerificationGate({"issuer": issuer.public_key()}, clock=lambda: clock[0])
    workflow = DemoWorkflow(coordinator, gate, "reviewer", request_clock=lambda: clock[0])
    workflow.set_processing_consent(True)
    risk = workflow.ingest(Transcript(segment_id=scenario.scenario_id, text=scenario.transcript,
                                      start_ms=0, end_ms=1000, final=True))
    completed = False
    completion_status = None
    verification_ms = None
    refusal_reason = None
    try:
        bundle = workflow.request_confirmation(destination=scenario.destination,
            amount_cents=scenario.amount_cents)
    except ValueError:
        refusal_reason = "policy_prevents_confirmation"
        bundle = None
    if bundle is not None:
        decision = ReviewerDecision(request=bundle["request"], approved=scenario.reviewer_approves,
            signature=reviewer.sign(
                decision_bytes(bundle["request"], scenario.reviewer_approves)).hex())
        try:
            result = workflow.complete(decision,
                challenge_response=bundle["out_of_band_challenge"])
            completion_status = result["status"]
            completed = completion_status == "simulated_action_completed"
            verification_ms = scenario.response_ms
        except ValueError:
            refusal_reason = "confirmation_failed"
    return {"state": risk["state"], "completed": completed,
            "completion_status": completion_status, "verification_ms": verification_ms,
            "refusal_reason": refusal_reason}


def _system_rows() -> list[dict]:
    rows = []
    for scenario in SCENARIOS:
        rows.append({"system": "deny_all", "scenario_id": scenario.scenario_id,
                     "authorized": scenario.authorized, "completed": False,
                     "verification_ms": None, "state": None,
                     "refusal_reason": "always_denied"})
        rows.append({"system": "unguarded_checkout", "scenario_id": scenario.scenario_id,
                     "authorized": scenario.authorized, "completed": True,
                     "verification_ms": 0, "state": None,
                     "refusal_reason": None})
        rows.append({"system": "callgate", "scenario_id": scenario.scenario_id,
                     "authorized": scenario.authorized, **_workflow_result(scenario)})
    return rows


def _summaries(rows: list[dict]) -> dict:
    systems = sorted({row["system"] for row in rows})
    out = {}
    for system in systems:
        subset = [row for row in rows if row["system"] == system]
        unauthorized = [row for row in subset if not row["authorized"]]
        legitimate = [row for row in subset if row["authorized"]]
        latencies = [row["verification_ms"] for row in legitimate
                     if row["completed"] and row["verification_ms"] is not None]
        out[system] = {
            "false_execute": _proportion(
                sum(row["completed"] for row in unauthorized), len(unauthorized)),
            "legitimate_completion": _proportion(
                sum(row["completed"] for row in legitimate), len(legitimate)),
            "verification_ms_median": None if not latencies else statistics.median(latencies),
            "verification_ms_p95": None if not latencies else sorted(latencies)[-1],
            "latency_note": "synthetic reviewer response parameter, not human timing",
        }
    return out


def run() -> dict:
    rows = _system_rows()
    return {
        "schema_version": "callgate-checkout-utility-v1",
        "disclosure": ("Synthetic author-provided checkout rehearsal. No real payments, "
                       "no independent labels, no population claim."),
        "scenario_count": len(SCENARIOS),
        "systems": ["deny_all", "unguarded_checkout", "callgate"],
        "rows": rows,
        "summary": _summaries(rows),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Checkout safety-utility rehearsal",
        "",
        report["disclosure"],
        "",
        "| System | False execute | Legitimate completion | Median verify ms | P95 verify ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for system in report["systems"]:
        item = report["summary"][system]
        false_execute = item["false_execute"]
        utility = item["legitimate_completion"]
        lines.append(
            f"| {system} | {false_execute['numerator']}/{false_execute['denominator']} "
            f"({false_execute['value']:.1%}) | {utility['numerator']}/{utility['denominator']} "
            f"({utility['value']:.1%}) | {item['verification_ms_median']} | "
            f"{item['verification_ms_p95']} |")
    lines += [
        "",
        "Wilson intervals are included in the JSON for descriptive proportions only.",
        "Reviewer timing is a synthetic parameter, not measured human response time.",
        "Deny-all has no unauthorized execution in this rehearsal, but also no legitimate completion.",
        "Unguarded checkout completes every scenario, including unauthorized ones.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    report = run()
    ROOT.mkdir(exist_ok=True)
    (ROOT / "results.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (ROOT / "REPORT.md").write_text(render_markdown(report))
    print(json.dumps({"scenario_count": report["scenario_count"],
                      "systems": report["systems"],
                      "results": {k: {
                          "false_execute": v["false_execute"],
                          "legitimate_completion": v["legitimate_completion"],
                          "verification_ms_median": v["verification_ms_median"],
                          "verification_ms_p95": v["verification_ms_p95"],
                      } for k, v in report["summary"].items()}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
