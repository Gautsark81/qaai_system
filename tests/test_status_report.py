# tests/test_status_report.py
import types
import status_report as sr

from unittest.mock import patch

# --------------------------
# Parsing utilities
# --------------------------


def test_parse_pytest_counts_basic():
    output = "collected 5 items\n3 passed, 2 failed"
    passed, failed, xfailed, errors, collected = sr.parse_pytest_counts(output)
    assert passed == 3
    assert failed == 2
    assert collected == 5
    assert errors == 0
    assert xfailed == 0


def test_parse_pytest_counts_with_errors():
    output = "collected 4 items\n2 passed, 1 failed, 1 error"
    passed, failed, xfailed, errors, collected = sr.parse_pytest_counts(output)
    assert passed == 2
    assert failed == 1
    assert errors == 1
    assert collected == 4


def test_parse_coverage_total_percent():
    report_text = "Name      Stmts   Miss  Cover\nTOTAL        50      5    90%"
    assert sr.parse_coverage_total_percent(report_text) == 90.0


def test_parse_coverage_file_percentages():
    report_text = "mod1.py      10      2    80%\nmod2.py  20  0   100%"
    rows = sr.parse_coverage_file_percentages(report_text)
    assert ("mod1.py", 80.0) in rows
    assert ("mod2.py", 100.0) in rows


# --------------------------
# Progress scoring utilities
# --------------------------


def test_compute_progress_score_full_points():
    test_summary = {"collected": 10, "passed": 10}
    breakdown = sr.compute_progress_score(
        test_summary,
        coverage_pct=95.0,
        stub_list=[],
        dhan_present=True,
        pm_present=True,
    )
    assert breakdown["percent"] == 100.0
    assert breakdown["test_points"] == 50.0
    assert breakdown["cov_points"] == 30.0
    assert breakdown["stub_points"] == 10.0
    assert breakdown["core_points"] == 10.0


def test_compute_progress_score_with_stubs_and_low_cov():
    test_summary = {"collected": 10, "passed": 5}
    breakdown = sr.compute_progress_score(
        test_summary,
        coverage_pct=45.0,
        stub_list=[("file", [(1, "stub")])],
        dhan_present=False,
        pm_present=True,
    )
    assert breakdown["percent"] < 100.0
    assert breakdown["stub_points"] <= 10.0
    assert breakdown["cov_points"] < 30.0
    assert breakdown["test_points"] == 25.0  # half of 50
    assert breakdown["core_points"] == 5.0


def test_render_progress_bar_bounds():
    assert "0%" in sr.render_progress_bar(0)
    assert "100%" in sr.render_progress_bar(100)
    bar = sr.render_progress_bar(55)
    assert "█" in bar and "░" in bar


# --------------------------
# run_cmd utility
# --------------------------


def test_run_cmd_success():
    res = sr.run_cmd(["echo", "hello"])
    assert res.returncode == 0
    assert "hello" in res.stdout


def test_run_cmd_failure():
    res = sr.run_cmd(["false"])
    assert res.returncode != 0


# --------------------------
# Smoke tests & coverage (mocked)
# --------------------------


@patch("status_report.run_cmd")
def test_run_smoke_tests_pass(mock_run):
    mock_run.return_value = types.SimpleNamespace(
        stdout="collected 1 item\n1 passed", stderr="", returncode=0
    )
    ok, info = sr.run_smoke_tests()
    assert ok is True
    assert info["passed"] == 1
    assert info["failed"] == 0


@patch("status_report.run_cmd")
def test_run_smoke_tests_fail(mock_run):
    mock_run.return_value = types.SimpleNamespace(
        stdout="collected 1 item\n1 failed", stderr="", returncode=1
    )
    ok, info = sr.run_smoke_tests()
    assert ok is False
    assert info["failed"] == 1


@patch("status_report.run_cmd")
def test_run_full_tests_with_coverage(mock_run, tmp_path):
    # First call = pytest run
    # Second call = coverage report
    # Third call = coverage html
    mock_run.side_effect = [
        types.SimpleNamespace(
            stdout="collected 2 items\n2 passed", stderr="", returncode=0
        ),
        types.SimpleNamespace(
            stdout="mod1.py  10  0  100%\nTOTAL  10  0  100%", stderr="", returncode=0
        ),
        types.SimpleNamespace(stdout="", stderr="", returncode=0),
    ]
    result = sr.run_full_tests_with_coverage()
    assert result["total_pct"] == 100.0
    assert ("mod1.py", 100.0) in result["file_coverages"]


# --------------------------
# Static analysis (mocked files)
# --------------------------


def test_count_todos_and_fixmes(tmp_path):
    f = tmp_path / "file.py"
    f.write_text("# TODO: something\n# FIXME: bug\n")
    res = sr.count_todos_fixes(str(tmp_path))
    assert res["todos"]
    assert res["fixmes"]


def test_detect_stubs_simple(tmp_path):
    f = tmp_path / "stub.py"
    f.write_text("def f():\n    pass\n")
    stubs = sr.detect_stubs(str(tmp_path))
    assert any("pass" in reason for _, info in stubs for _, reason in info)


# --------------------------
# Dependency audit
# --------------------------


@patch("status_report.run_cmd")
def test_dependency_audit_json(mock_run):
    mock_run.return_value = types.SimpleNamespace(
        stdout='[{"name": "pkg", "version": "1.0", "latest_version": "2.0"}]',
        stderr="",
        returncode=0,
    )
    outdated = sr.dependency_audit()
    assert ("pkg", "1.0", "2.0") in outdated


@patch("status_report.run_cmd")
def test_dependency_audit_text(mock_run):
    mock_run.return_value = types.SimpleNamespace(
        stdout="pkg (1.0) -> 2.0", stderr="", returncode=0
    )
    outdated = sr.dependency_audit()
    assert any("pkg" in o for o in outdated[0])


# --------------------------
# Notifications (mocked)
# --------------------------


@patch("status_report.requests.post")
def test_post_to_slack(mock_post):
    mock_post.return_value = types.SimpleNamespace(status_code=200, text="ok")
    sr.SLACK_WEBHOOK = "http://fake"
    sr.post_to_slack("title", "msg")
    assert mock_post.called


@patch("status_report.requests.post")
def test_post_to_telegram(mock_post):
    mock_post.return_value = types.SimpleNamespace(status_code=200, text="ok")
    sr.TELEGRAM_TOKEN = "abc"
    sr.TELEGRAM_CHAT_ID = "123"
    sr.post_to_telegram("hello")
    assert mock_post.called
