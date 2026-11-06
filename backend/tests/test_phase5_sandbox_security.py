import pytest
from app.services.sandbox import sandbox
from app.services.code_evaluator import code_evaluator


def test_ast_time_and_space_complexity_analysis():
    # 1. Constant Time O(1)
    const_code = """
def get_first(arr):
    return arr[0] if arr else None
"""
    m1 = code_evaluator.analyze_ast(const_code, "get_first")
    assert m1["estimated_time_complexity"] == "O(1)"
    assert m1["max_loop_depth"] == 0

    # 2. Linear Time O(n)
    linear_code = """
def sum_all(arr):
    total = 0
    for x in arr:
        total += x
    return total
"""
    m2 = code_evaluator.analyze_ast(linear_code, "sum_all")
    assert m2["estimated_time_complexity"] == "O(n)"
    assert m2["max_loop_depth"] == 1

    # 3. Quadratic Time O(n^2)
    quad_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    m3 = code_evaluator.analyze_ast(quad_code, "bubble_sort")
    assert m3["estimated_time_complexity"] == "O(n^2)"
    assert m3["max_loop_depth"] == 2
    assert m3["quality_score"] < m2["quality_score"]  # Penalized for higher nesting depth

    # 4. Recursive Function Detection
    rec_code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    m4 = code_evaluator.analyze_ast(rec_code, "fib")
    assert m4["is_recursive"] is True
    assert m4["has_base_case"] is True


def test_anti_cheating_hardcoded_test_case_detection():
    sample_tests = [
        {"inputs": [[2, 7, 11, 15], 9], "expected": [0, 1]},
        {"inputs": [[3, 2, 4], 6], "expected": [1, 2]},
    ]

    # Cheating candidate hardcodes the sample test case inputs
    cheating_code = """
def two_sum(nums, target):
    if nums == [2, 7, 11, 15] and target == 9:
        return [0, 1]
    if nums == [3, 2, 4] and target == 6:
        return [1, 2]
    return []
"""
    cheat_report = code_evaluator.detect_cheating_and_hardcoding(cheating_code, "two_sum", sample_tests)
    assert cheat_report["cheating_detected"] is True
    assert cheat_report["is_hardcoded"] is True
    assert any("hardcoded" in f.lower() for f in cheat_report["flags"])

    # Sandbox rejection for hardcoded cheating
    res = sandbox.run_tests(cheating_code, "two_sum", sample_tests)
    assert res["status"] == "cheating_detected"
    assert res["passed_tests"] == 0


def test_anti_cheating_dunder_tampering_detection():
    # Attempting to access object subclasses or internal dunder attributes
    dunder_tampering_code = """
def solve():
    return ().__class__.__subclasses__()
"""
    res = sandbox.run_tests(dunder_tampering_code, "solve", [{"inputs": [], "expected": []}])
    assert res["status"] in ("forbidden", "cheating_detected")


def test_recursion_stack_overflow_guard():
    # Infinite recursion without base case
    infinite_recursion_code = """
def recurse(n):
    return recurse(n + 1)
"""
    res = sandbox.run_tests(infinite_recursion_code, "recurse", [{"inputs": [1], "expected": 100}])
    # The sandbox must not crash or kill the host process; it catches the Stack Overflow safely
    assert res["status"] in ("failed", "error")
    assert any("recursion" in str(r.get("error", "")).lower() for r in res.get("test_results", []))


def test_execution_timeout_on_infinite_loop():
    infinite_loop_code = """
def hang():
    while True:
        pass
    return True
"""
    res = sandbox.run_tests(infinite_loop_code, "hang", [{"inputs": [], "expected": True}], timeout_seconds=1.0)
    assert res["status"] == "timeout"
    assert "timeout" in res["error_message"].lower()


def test_edge_case_generator_synthesis():
    # 1. Edge cases for list input
    list_tc = [{"inputs": [[1, 2, 3]], "expected": [3, 2, 1]}]
    edges1 = code_evaluator.generate_edge_cases(list_tc)
    assert len(edges1) >= 2
    assert any(e["inputs"] == [[]] for e in edges1)

    # 2. Edge cases for string input
    str_tc = [{"inputs": ["hello"], "expected": "olleh"}]
    edges2 = code_evaluator.generate_edge_cases(str_tc)
    assert len(edges2) >= 2
    assert any(e["inputs"] == [""] for e in edges2)

    # 3. Edge cases for (list, int)
    two_sum_tc = [{"inputs": [[2, 7], 9], "expected": [0, 1]}]
    edges3 = code_evaluator.generate_edge_cases(two_sum_tc)
    assert len(edges3) >= 2
    assert any(e["inputs"] == [[], 0] for e in edges3)

