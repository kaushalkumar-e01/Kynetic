import pytest
from app.services.sandbox import sandbox
from app.models.user import User
from app.core.security import get_password_hash
from app.db.session import engine


def test_sandbox_masks_hidden_test_cases():
    code = """
def solution(nums):
    return sum(nums)
"""
    test_cases = [
        {"inputs": [[1, 2, 3]], "expected": 6, "hidden": False},
        {"inputs": [[10, 20, 30]], "expected": 60, "hidden": True},
        {"inputs": [[-1, 1]], "expected": 0, "is_hidden": True},
    ]
    res = sandbox.run_tests(code, "solution", test_cases)
    assert res["status"] == "passed"
    assert res["passed_tests"] == 3
    assert len(res["test_results"]) == 3

    # Public test case 0
    assert res["test_results"][0]["is_hidden"] is False
    assert res["test_results"][0]["inputs"] == [[1, 2, 3]]
    assert res["test_results"][0]["expected"] == 6

    # Hidden test case 1
    assert res["test_results"][1]["is_hidden"] is True
    assert res["test_results"][1]["inputs"] == "[Hidden Test Case]"
    assert res["test_results"][1]["expected"] == "[Hidden Test Case]"
    assert res["test_results"][1]["actual"] == "[Hidden Output]"
    assert res["test_results"][1]["passed"] is True

    # Hidden test case 2
    assert res["test_results"][2]["is_hidden"] is True
    assert res["test_results"][2]["inputs"] == "[Hidden Test Case]"
    assert res["test_results"][2]["expected"] == "[Hidden Test Case]"
    assert res["test_results"][2]["actual"] == "[Hidden Output]"
    assert res["test_results"][2]["passed"] is True


def test_sandbox_blocks_extended_forbidden_modules():
    forbidden_payloads = [
        ("import threading", "threading"),
        ("import asyncio", "asyncio"),
        ("import multiprocessing", "multiprocessing"),
        ("import inspect", "inspect"),
        ("import webbrowser", "webbrowser"),
    ]
    for code, mod in forbidden_payloads:
        res = sandbox.run_tests(code, "solution", [])
        assert res["status"] == "forbidden"
        assert mod in res["error_message"]


def test_sandbox_blocks_extended_forbidden_calls():
    forbidden_calls = [
        "def solution(): return globals()",
        "def solution(): return locals()",
        "def solution(): return vars()",
        "def solution(): return breakpoint()",
    ]
    for code in forbidden_calls:
        res = sandbox.run_tests(code, "solution", [])
        assert res["status"] == "forbidden"


def test_sqlite_pragmas_enabled_on_connection():
    with engine.connect() as conn:
        fk_status = conn.exec_driver_sql("PRAGMA foreign_keys;").scalar()
        assert fk_status == 1, "Foreign keys must be enabled (PRAGMA foreign_keys = 1)"

