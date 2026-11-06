import ast
from typing import Dict, Any, List, Optional, Set


class CodeQualityVisitor(ast.NodeVisitor):
    def __init__(self, entry_point: str):
        self.entry_point = entry_point
        self.current_loop_depth = 0
        self.max_loop_depth = 0
        self.is_recursive = False
        self.has_base_case = False
        self.allocates_aux_memory = False
        self.condition_count = 0
        self.dunder_violations: List[str] = []
        self.hardcoded_literal_matches = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Scan inside function body
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_Call(self, node: ast.Call):
        # Detect recursion: function calls itself
        if isinstance(node.func, ast.Name) and node.func.id == self.entry_point:
            self.is_recursive = True
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        self.condition_count += 1
        # Check if If statement contains a return statement (classic base case pattern)
        for child in node.body:
            if isinstance(child, ast.Return):
                self.has_base_case = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Detect dunder attribute tampering (e.g., __class__, __subclasses__)
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.dunder_violations.append(node.attr)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        self.allocates_aux_memory = True
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set):
        self.allocates_aux_memory = True
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        self.allocates_aux_memory = True
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        self.allocates_aux_memory = True
        self.generic_visit(node)


class CodeEvaluatorService:
    """
    Advanced Code Evaluation, Complexity Analysis, Edge Case Synthesis & Anti-Cheating Engine.
    """

    @classmethod
    def analyze_ast(cls, code_str: str, entry_point: str) -> Dict[str, Any]:
        """
        Performs static AST analysis to extract loop nesting depth,
        recursion characteristics, and algorithmic complexity estimations.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {
                "valid_syntax": False,
                "error": str(e),
                "estimated_time_complexity": "unknown",
                "max_loop_depth": 0,
                "is_recursive": False,
                "quality_score": 0.0,
            }

        visitor = CodeQualityVisitor(entry_point)
        visitor.visit(tree)

        # Estimate time complexity from loop nesting depth
        if visitor.is_recursive:
            time_complexity = "O(2^n)" if visitor.max_loop_depth > 0 else "O(n)"
        elif visitor.max_loop_depth == 0:
            time_complexity = "O(1)"
        elif visitor.max_loop_depth == 1:
            time_complexity = "O(n)"
        elif visitor.max_loop_depth == 2:
            time_complexity = "O(n^2)"
        else:
            time_complexity = f"O(n^{visitor.max_loop_depth})"

        # Estimated space complexity
        space_complexity = "O(n)" if (visitor.allocates_aux_memory or visitor.is_recursive) else "O(1)"

        # Compute structured quality score (0 to 100)
        # Rewards modularity, appropriate loop nesting, and base cases for recursive calls
        quality_score = 80.0
        if visitor.max_loop_depth >= 3:
            quality_score -= 25.0  # Penalize high nesting depth
        if visitor.is_recursive and not visitor.has_base_case:
            quality_score -= 30.0  # Risk of stack overflow without base case
        if visitor.max_loop_depth == 1 or (visitor.is_recursive and visitor.has_base_case):
            quality_score += 15.0

        quality_score = max(10.0, min(100.0, quality_score))

        return {
            "valid_syntax": True,
            "estimated_time_complexity": time_complexity,
            "estimated_space_complexity": space_complexity,
            "max_loop_depth": visitor.max_loop_depth,
            "is_recursive": visitor.is_recursive,
            "has_base_case": visitor.has_base_case if visitor.is_recursive else True,
            "cyclomatic_complexity": visitor.condition_count + visitor.max_loop_depth + 1,
            "dunder_violations": visitor.dunder_violations,
            "quality_score": round(quality_score, 1),
        }

    @classmethod
    def detect_cheating_and_hardcoding(
        cls,
        code_str: str,
        entry_point: str,
        sample_test_cases: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Anti-Cheating Detection:
        1. Detects hardcoded matching against public sample test cases (e.g. if x == [1, 2]: return [0, 1]).
        2. Detects trivial constant returns (e.g. just `return 0` or `return []`).
        3. Detects forbidden dunder attribute reflection.
        """
        flags: List[str] = []
        is_hardcoded = False
        is_trivial_return = False

        try:
            tree = ast.parse(code_str)
        except Exception:
            return {"cheating_detected": False, "flags": []}

        # 1. Dunder introspection check
        visitor = CodeQualityVisitor(entry_point)
        visitor.visit(tree)
        if visitor.dunder_violations:
            flags.append(f"Security: forbidden dunder inspection ({', '.join(visitor.dunder_violations)})")

        # 2. Check for trivial constant return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == entry_point:
                body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
                if len(body) == 1 and isinstance(body[0], ast.Return):
                    if isinstance(body[0].value, ast.Constant):
                        is_trivial_return = True
                        flags.append("Trivial constant return without processing parameters.")

        # 3. Check for hardcoded input checks
        # Inspect string representations of sample test case inputs
        input_literals: Set[str] = set()
        for tc in sample_test_cases:
            for inp in tc.get("inputs", []):
                input_literals.add(str(inp))
                input_literals.add(repr(inp))

        # Check if AST Compare statements contain exact literal inputs
        code_lower = code_str.lower()
        hardcoded_matches = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # Check left or comparators for literal matches
                rep = ast.unparse(node) if hasattr(ast, "unparse") else ""
                for lit in input_literals:
                    if lit in rep and len(lit) > 1 and lit not in ("[]", "0", "1", "''", '""'):
                        hardcoded_matches += 1

        if hardcoded_matches >= 2:
            is_hardcoded = True
            flags.append("Hardcoded test case matching detected. Candidate code mimics outputs rather than generalizing.")

        cheating_detected = is_hardcoded or bool(visitor.dunder_violations)

        return {
            "cheating_detected": cheating_detected,
            "is_hardcoded": is_hardcoded,
            "is_trivial_return": is_trivial_return,
            "flags": flags,
        }

    @classmethod
    def generate_edge_cases(cls, sample_test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Synthesizes standard edge cases (e.g. empty inputs, single element, boundary limits)
        based on the input types observed in the sample test cases.
        """
        if not sample_test_cases:
            return []

        first_inputs = sample_test_cases[0].get("inputs", [])
        edge_cases = []

        # Analyze input types
        types = [type(x) for x in first_inputs]

        # Single list input (e.g. sort, reverse, search)
        if len(types) == 1 and types[0] is list:
            edge_cases.append({"inputs": [[]], "is_edge_case": True, "description": "Empty list boundary"})
            edge_cases.append({"inputs": [[42]], "is_edge_case": True, "description": "Single element boundary"})
            edge_cases.append({"inputs": [[1, 1, 1, 1]], "is_edge_case": True, "description": "All duplicate elements"})

        # Single string input
        elif len(types) == 1 and types[0] is str:
            edge_cases.append({"inputs": [""], "is_edge_case": True, "description": "Empty string boundary"})
            edge_cases.append({"inputs": ["a"], "is_edge_case": True, "description": "Single character string"})
            edge_cases.append({"inputs": ["   "], "is_edge_case": True, "description": "Whitespace only string"})

        # (list, int) inputs (e.g. two_sum, search, binary search)
        elif len(types) == 2 and types[0] is list and types[1] is int:
            edge_cases.append({"inputs": [[], 0], "is_edge_case": True, "description": "Empty list with zero target"})
            edge_cases.append({"inputs": [[5], 5], "is_edge_case": True, "description": "Single element matching target"})
            edge_cases.append({"inputs": [[-10, -5, 0, 5, 10], 0], "is_edge_case": True, "description": "Negative and zero integers"})

        # Single integer input (e.g. factorial, is_prime, fibonacci)
        elif len(types) == 1 and types[0] is int:
            edge_cases.append({"inputs": [0], "is_edge_case": True, "description": "Zero boundary"})
            edge_cases.append({"inputs": [1], "is_edge_case": True, "description": "Base case 1"})
            edge_cases.append({"inputs": [-1], "is_edge_case": True, "description": "Negative boundary"})

        return edge_cases


code_evaluator = CodeEvaluatorService()

