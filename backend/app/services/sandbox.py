import ast
import multiprocessing
from typing import Dict, Any, List

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "requests", "urllib", "shutil",
    "pty", "posix", "ctypes", "pickle", "shelve", "builtins", "importlib",
}

FORBIDDEN_CALLS = {
    "eval", "exec", "open", "compile", "__import__", "getattr", "setattr", "delattr",
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


def _execute_in_process(code_str: str, entry_point: str, test_cases: List[Dict[str, Any]], return_dict: dict):
    try:
        local_scope = {}
        # Execute code in clean restricted global environment
        restricted_globals = {
            "__builtins__": {
                "range": range, "len": len, "int": int, "float": float, "str": str,
                "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
                "min": min, "max": max, "sum": sum, "sorted": sorted, "abs": abs,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "round": round, "print": lambda *args: None,
            }
        }

        exec(code_str, restricted_globals, local_scope)

        if entry_point not in local_scope:
            return_dict["result"] = {
                "status": "error",
                "error_message": f"Entry point function '{entry_point}' not found in submitted code.",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
            }
            return

        target_fn = local_scope[entry_point]
        test_results = []
        passed_count = 0

        for tc in test_cases:
            inputs = tc.get("inputs", [])
            expected = tc.get("expected")

            try:
                actual = target_fn(*inputs)
                is_pass = actual == expected
                if is_pass:
                    passed_count += 1
                test_results.append({
                    "inputs": inputs,
                    "expected": expected,
                    "actual": actual,
                    "passed": is_pass,
                })
            except Exception as e:
                test_results.append({
                    "inputs": inputs,
                    "expected": expected,
                    "actual": None,
                    "error": str(e),
                    "passed": False,
                })

        all_passed = (passed_count == len(test_cases))
        return_dict["result"] = {
            "status": "passed" if all_passed else "failed",
            "passed_tests": passed_count,
            "total_tests": len(test_cases),
            "test_results": test_results,
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
        # Step 1: Static AST Security Analysis
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {
                "status": "error",
                "error_message": f"Syntax error in submitted code: {e}",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
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
            }

        # Step 2: In-Process Sandbox Execution with timeout
        # Using multiprocessing or thread pool to enforce execution deadline
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
            }

        return return_dict.get("result", {
            "status": "error",
            "error_message": "Execution terminated unexpectedly without result.",
            "passed_tests": 0,
            "total_tests": len(test_cases),
            "test_results": [],
        })


sandbox = CodeSandbox()

