import ast
import multiprocessing
import time
from typing import Dict, Any, List

from app.services.code_evaluator import code_evaluator

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "requests", "urllib", "shutil",
    "pty", "posix", "ctypes", "pickle", "shelve", "builtins", "importlib",
    "http", "asyncio", "multiprocessing", "threading", "signal", "inspect",
    "gc", "socketserver", "ftplib", "telnetlib", "webbrowser",
}

FORBIDDEN_CALLS = {
    "eval", "exec", "open", "compile", "__import__", "getattr", "setattr", "delattr",
    "globals", "locals", "vars", "breakpoint", "input", "help", "memoryview",
}


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in FORBIDDEN_MODULES:
                self.errors.append(f"Importing module '{alias.name}' is prohibited for security reasons.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in FORBIDDEN_MODULES:
                self.errors.append(f"Importing from '{node.module}' is prohibited for security reasons.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            self.errors.append(f"Calling restricted built-in function '{node.func.id}' is prohibited.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr.startswith("__") and node.attr.endswith("__"):
            if node.attr not in ("__init__", "__iter__", "__next__", "__len__"):
                self.errors.append(f"Direct access to dunder attribute '{node.attr}' is prohibited.")
        self.generic_visit(node)


def _execute_in_process(code_str: str, entry_point: str, test_cases: List[Dict[str, Any]], return_dict: dict):
    try:
        import sys
        sys.setrecursionlimit(500)  # Recursion limit to guard against infinite call stacks

        exec_scope = {
            "__builtins__": {
                "range": range, "len": len, "int": int, "float": float, "str": str,
                "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
                "min": min, "max": max, "sum": sum, "sorted": sorted, "abs": abs,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "round": round, "pow": pow, "divmod": divmod, "all": all, "any": any,
                "print": lambda *args: None,
            }
        }

        exec(code_str, exec_scope, exec_scope)

        if entry_point not in exec_scope:
            return_dict["result"] = {
                "status": "error",
                "error_message": f"Entry point function '{entry_point}' not found in submitted code.",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
            }
            return

        target_fn = exec_scope[entry_point]
        test_results = []
        passed_count = 0
        total_time_ms = 0.0

        for tc in test_cases:
            inputs = tc.get("inputs", [])
            expected = tc.get("expected")
            is_hidden = bool(tc.get("hidden") or tc.get("is_hidden"))

            t0 = time.perf_counter()
            try:
                actual = target_fn(*inputs)
                duration_ms = round((time.perf_counter() - t0) * 1000.0, 3)
                total_time_ms += duration_ms

                is_pass = actual == expected
                if is_pass:
                    passed_count += 1
                test_results.append({
                    "inputs": "[Hidden Test Case]" if is_hidden else inputs,
                    "expected": "[Hidden Test Case]" if is_hidden else expected,
                    "actual": ("[Hidden Output]" if is_pass else "[Hidden Output Mismatch]") if is_hidden else actual,
                    "passed": is_pass,
                    "duration_ms": duration_ms,
                    "is_hidden": is_hidden,
                })
            except RecursionError:
                test_results.append({
                    "inputs": "[Hidden Test Case]" if is_hidden else inputs,
                    "expected": "[Hidden Test Case]" if is_hidden else expected,
                    "actual": None,
                    "error": "Maximum recursion depth exceeded (Stack Overflow Guard)",
                    "passed": False,
                    "duration_ms": round((time.perf_counter() - t0) * 1000.0, 3),
                    "is_hidden": is_hidden,
                })
            except Exception as e:
                test_results.append({
                    "inputs": "[Hidden Test Case]" if is_hidden else inputs,
                    "expected": "[Hidden Test Case]" if is_hidden else expected,
                    "actual": None,
                    "error": str(e),
                    "passed": False,
                    "duration_ms": round((time.perf_counter() - t0) * 1000.0, 3),
                    "is_hidden": is_hidden,
                })

        all_passed = (passed_count == len(test_cases))
        return_dict["result"] = {
            "status": "passed" if all_passed else "failed",
            "passed_tests": passed_count,
            "total_tests": len(test_cases),
            "test_results": test_results,
            "total_duration_ms": round(total_time_ms, 2),
            "error_message": None if all_passed else f"Passed {passed_count}/{len(test_cases)} tests.",
        }

    except Exception as e:
        return_dict["result"] = {
            "status": "error",
            "error_message": str(e),
            "passed_tests": 0,
            "total_tests": len(test_cases),
            "test_results": [],
        }


class CodeSandbox:
    @staticmethod
    def run_tests(
        code_str: str,
        entry_point: str,
        test_cases: List[Dict[str, Any]],
        timeout_seconds: float = 3.0,
    ) -> Dict[str, Any]:
        if not code_str or not str(code_str).strip():
            return {
                "status": "error",
                "error_message": "Empty code submission. Please provide a solution function.",
                "passed_tests": 0,
                "total_tests": len(test_cases) if test_cases else 0,
                "test_results": [],
                "quality_metrics": None,
                "integrity_flags": [],
            }

        # Step 1: Static AST Security & Quality Analysis
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {
                "status": "error",
                "error_message": f"Syntax error in submitted code: {e}",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "quality_metrics": None,
                "integrity_flags": [],
            }

        visitor = SecurityVisitor()
        visitor.visit(tree)
        if visitor.errors:
            return {
                "status": "forbidden",
                "error_message": "; ".join(visitor.errors),
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "quality_metrics": None,
                "integrity_flags": ["Security boundary violation"],
            }

        quality_metrics = code_evaluator.analyze_ast(code_str, entry_point)

        # Step 2: Anti-Cheating & Hardcoding Detection
        integrity_report = code_evaluator.detect_cheating_and_hardcoding(code_str, entry_point, test_cases)
        if integrity_report.get("cheating_detected"):
            return {
                "status": "cheating_detected",
                "error_message": "; ".join(integrity_report.get("flags", ["Anti-cheating check failed."])),
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "quality_metrics": quality_metrics,
                "integrity_flags": integrity_report.get("flags", []),
            }

        # Step 3: In-Process Sandbox Execution with timeout
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        process = multiprocessing.Process(
            target=_execute_in_process,
            args=(code_str, entry_point, test_cases, return_dict),
        )
        process.start()
        process.join(timeout=timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join()
            return {
                "status": "timeout",
                "error_message": f"Execution exceeded maximum timeout of {timeout_seconds} seconds.",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "quality_metrics": quality_metrics,
                "integrity_flags": integrity_report.get("flags", []),
            }

        exec_res = return_dict.get("result", {
            "status": "error",
            "error_message": "Execution terminated unexpectedly without result.",
            "passed_tests": 0,
            "total_tests": len(test_cases),
            "test_results": [],
        })

        exec_res["quality_metrics"] = quality_metrics
        exec_res["integrity_flags"] = integrity_report.get("flags", [])
        exec_res["sandbox_metadata"] = {
            "provider": "isolated_process_sandbox",
            "timeout_seconds": timeout_seconds,
            "recursion_limit": 500,
            "network_access": "disabled",
            "filesystem_access": "disabled",
        }
        return exec_res


sandbox = CodeSandbox()
