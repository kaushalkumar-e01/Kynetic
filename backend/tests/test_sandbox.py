from app.services.sandbox import sandbox


def test_sandbox_ast_blocks_forbidden_imports():
    # Attempt to import os
    res = sandbox.run_tests(
        code_str="import os\ndef solution(): pass",
        entry_point="solution",
        test_cases=[],
    )
    assert res["status"] == "forbidden"
    assert "os" in res["error_message"]

    # Attempt to import subprocess
    res2 = sandbox.run_tests(
        code_str="import subprocess\ndef solution(): pass",
        entry_point="solution",
        test_cases=[],
    )
    assert res2["status"] == "forbidden"
    assert "subprocess" in res2["error_message"]


def test_sandbox_ast_blocks_forbidden_calls():
    res = sandbox.run_tests(
        code_str="def solution(): eval('1 + 1')",
        entry_point="solution",
        test_cases=[],
    )
    assert res["status"] == "forbidden"
    assert "eval" in res["error_message"]


def test_sandbox_runs_valid_algorithm():
    code = """
def reverse_string(s: str) -> str:
    return s[::-1]
"""
    test_cases = [
        {"inputs": ["kynetic"], "expected": "citenyk"},
        {"inputs": ["hello"], "expected": "olleh"},
    ]
    res = sandbox.run_tests(code, "reverse_string", test_cases)
    assert res["status"] == "passed"
    assert res["passed_tests"] == 2
    assert res["total_tests"] == 2


def test_sandbox_handles_failed_test():
    code = """
def reverse_string(s: str) -> str:
    return s  # Incorrect implementation
"""
    test_cases = [
        {"inputs": ["abc"], "expected": "cba"},
    ]
    res = sandbox.run_tests(code, "reverse_string", test_cases)
    assert res["status"] == "failed"
    assert res["passed_tests"] == 0

