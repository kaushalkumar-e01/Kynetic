import sqlite3
import re
from typing import Dict, Any, Tuple
import logging

from app.services.sandbox import sandbox

logger = logging.getLogger("kynetic.assessment.validator")


class QuestionValidator:
    """
    Validation engine ensuring every question in Kynetic meets strict
    content, execution, schema, and correctness criteria before entering
    the active question bank.
    """

    BANNED_PATTERNS = [
        "compute_c_", "compute_cpp_", "compute_java_", "compute_python_",
        "calculate_js_", "solve_dsa_", "Challenge #", "Generated Problem",
        "[C] Challenge", "[Java] Challenge", "[Python] Challenge", "[C++] Challenge", "[JS] Challenge",
        "compute_js_", "solve_python_", "process_1", "process_2", "process_3"
    ]

    @classmethod
    def _check_general_quality(cls, q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        prompt = q_data.get("prompt", "")
        title = q_data.get("title") or meta.get("title", "")
        entry_point = meta.get("entry_point", "")
        lang = str(q_data.get("programming_language") or "").lower().strip()

        combined_text = f"{title} {prompt} {entry_point}"
        for pat in cls.BANNED_PATTERNS:
            if pat.lower() in combined_text.lower():
                return False, f"Question contains banned artificial pattern '{pat}'. Professional naming required."

        # Check language mismatch using precise regex boundaries
        code_str = f"{prompt} {meta.get('code', '')} {meta.get('buggy_code', '')} {meta.get('reference_solution', '')}"
        if lang in ("c", "cpp", "java"):
            python_indicators = [r"\bdef\s+[a-zA-Z_]", r"\brange\(len\(", r"\by\.append\(", r"\bprint\(len\(", r"\belif\s+"]
            for py_pat in python_indicators:
                if re.search(py_pat, code_str):
                    return False, f"Language mismatch: Question classified as '{lang}' contains Python syntax ('{py_pat}')."

        return True, ""

    @staticmethod
    def validate_question(q_data: Dict[str, Any], validate_code: bool = True) -> Tuple[bool, str]:
        prompt = q_data.get("prompt", "").strip()
        if not prompt or len(prompt) < 10:
            return False, "Prompt is missing or too short (minimum 10 characters required)."

        meta = q_data.get("evaluation_metadata", {}) or {}

        quality_valid, quality_msg = QuestionValidator._check_general_quality(q_data, meta)
        if not quality_valid:
            return False, quality_msg

        q_type = str(q_data.get("question_type", "")).lower().strip()

        if q_type in ("multiple_choice", "mcq"):
            return QuestionValidator._validate_mcq(q_data, meta)
        elif q_type == "multi_select":
            return QuestionValidator._validate_multi_select(q_data, meta)
        elif q_type == "output_prediction":
            return QuestionValidator._validate_output_prediction(q_data, meta)
        elif q_type == "coding":
            return QuestionValidator._validate_coding(q_data, meta, validate_code=validate_code)
        elif q_type == "debugging":
            return QuestionValidator._validate_debugging(q_data, meta)
        elif q_type == "sql":
            return QuestionValidator._validate_sql(q_data, meta, validate_code=validate_code)
        elif q_type == "conceptual":
            return QuestionValidator._validate_conceptual(q_data, meta)
        else:
            return False, f"Unknown question type: '{q_type}'"

    @staticmethod
    def _validate_mcq(q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        options = q_data.get("options", [])
        if not options or len(options) < 2:
            return False, "MCQ questions must have at least 2 options."

        correct_ans = meta.get("correct_answer")
        if correct_ans is None or str(correct_ans).strip() == "":
            return False, "MCQ question missing 'correct_answer' in evaluation_metadata."

        option_texts = [
            opt if isinstance(opt, str) else opt.get("text", "")
            for opt in options
        ]
        if str(correct_ans).strip() not in [o.strip() for o in option_texts]:
            return False, f"Correct answer '{correct_ans}' is not in options list."

        return True, "Valid MCQ question."

    @staticmethod
    def _validate_multi_select(q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        options = q_data.get("options", [])
        if not options or len(options) < 3:
            return False, "Multi-select questions must have at least 3 options."

        correct_answers = meta.get("correct_answers", [])
        if not correct_answers or not isinstance(correct_answers, list):
            return False, "Multi-select question must provide list of 'correct_answers'."

        option_texts = [
            opt if isinstance(opt, str) else opt.get("text", "")
            for opt in options
        ]
        for ans in correct_answers:
            if str(ans).strip() not in [o.strip() for o in option_texts]:
                return False, f"Correct answer item '{ans}' not found in options."

        return True, "Valid Multi-Select question."

    @staticmethod
    def _validate_output_prediction(q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        expected = meta.get("expected_output") or meta.get("correct_answer")
        if expected is None or str(expected).strip() == "":
            return False, "Output prediction question missing 'expected_output'."
        code = meta.get("code") or q_data.get("prompt", "")
        if not code:
            return False, "Output prediction question must include code."
        return True, "Valid Output Prediction question."

    @staticmethod
    def _validate_coding(q_data: Dict[str, Any], meta: Dict[str, Any], validate_code: bool = True) -> Tuple[bool, str]:
        entry_point = meta.get("entry_point")
        if not entry_point:
            return False, "Coding question must specify an 'entry_point' function name."

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", entry_point):
            return False, f"Entry point '{entry_point}' is not a valid function identifier."

        test_cases = meta.get("test_cases", [])
        if not test_cases or len(test_cases) < 2:
            return False, "Coding question must have at least 2 validated test cases."

        for tc in test_cases:
            if "inputs" not in tc or "expected" not in tc:
                return False, "Each test case must specify 'inputs' and 'expected'."

        # If a reference solution is supplied and language is Python, verify it in the sandbox
        ref_solution = meta.get("reference_solution")
        lang = (q_data.get("programming_language") or "").lower()
        if validate_code and ref_solution and (lang == "python" or not lang):
            exec_res = sandbox.run_tests(ref_solution, entry_point, test_cases)
            if exec_res.get("status") != "passed":
                return False, f"Reference solution failed test validation: {exec_res.get('error_message')}"

        return True, "Valid Coding question."

    @staticmethod
    def _validate_debugging(q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        buggy_code = meta.get("buggy_code") or q_data.get("prompt", "")
        if not buggy_code:
            return False, "Debugging question missing 'buggy_code'."

        fix = meta.get("correct_fix") or meta.get("correct_answer")
        if not fix:
            return False, "Debugging question missing 'correct_fix'."

        return True, "Valid Debugging question."

    @staticmethod
    def _validate_sql(q_data: Dict[str, Any], meta: Dict[str, Any], validate_code: bool = True) -> Tuple[bool, str]:
        schema_ddl = meta.get("schema_ddl")
        ref_query = meta.get("reference_query")
        if not schema_ddl:
            return False, "SQL question missing 'schema_ddl' in evaluation_metadata."
        if not ref_query:
            return False, "SQL question missing 'reference_query' in evaluation_metadata."

        if not validate_code:
            return True, "Valid SQL question."

        # Verify reference query in an isolated in-memory SQLite database
        try:
            conn = sqlite3.connect(":memory:")
            cur = conn.cursor()
            cur.executescript(schema_ddl)
            cur.execute(ref_query)
            rows = cur.fetchall()
            conn.close()
            if rows is None:
                return False, "Reference query returned None."
        except Exception as e:
            return False, f"SQL reference query failed execution against schema: {e}"

        return True, "Valid SQL question."

    @staticmethod
    def _validate_conceptual(q_data: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[bool, str]:
        rubric = meta.get("rubric") or meta.get("key_concepts")
        if not rubric:
            return False, "Conceptual question missing 'rubric' or 'key_concepts' evaluation guide."
        return True, "Valid Conceptual question."


question_validator = QuestionValidator()

