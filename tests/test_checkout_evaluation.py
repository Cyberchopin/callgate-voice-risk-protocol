from pathlib import Path

from evaluation_checkout.run import SCENARIOS, render_markdown, run


def test_checkout_rehearsal_reports_raw_safety_and_utility_denominators():
    report = run()
    assert report["schema_version"] == "callgate-checkout-utility-v1"
    assert report["scenario_count"] == len(SCENARIOS)
    assert report["summary"]["deny_all"]["false_execute"]["numerator"] == 0
    assert report["summary"]["deny_all"]["legitimate_completion"] == {
        "numerator": 0,
        "denominator": 3,
        "value": 0.0,
        "wilson95": [0, 0.5615060804490177],
    }
    assert report["summary"]["unguarded_checkout"]["false_execute"]["numerator"] == 3
    assert report["summary"]["callgate"]["false_execute"]["numerator"] == 0
    assert report["summary"]["callgate"]["legitimate_completion"]["numerator"] == 3
    assert report["summary"]["callgate"]["legitimate_completion"]["denominator"] == 3
    assert report["summary"]["callgate"]["verification_ms_median"] == 24000
    assert report["summary"]["callgate"]["verification_ms_p95"] == 30000


def test_checkout_report_keeps_disclosure_and_baseline_comparison():
    text = render_markdown(run())
    assert "Synthetic author-provided checkout rehearsal" in text
    assert "deny_all | 0/3" in text
    assert "callgate | 0/3" in text
    assert "3/3" in text
    assert "not measured human response time" in text


def test_committed_checkout_results_match_regenerated_report():
    report_path = Path("evaluation_checkout/results.json")
    markdown_path = Path("evaluation_checkout/REPORT.md")
    if report_path.exists() and markdown_path.exists():
        assert "callgate-checkout-utility-v1" in report_path.read_text()
        assert markdown_path.read_text() == render_markdown(run())
