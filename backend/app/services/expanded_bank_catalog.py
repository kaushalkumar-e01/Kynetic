"""
Expanded Bank Catalog for Kynetic Question Bank Overhaul
Generates ~1,655 high-quality, validated, non-duplicate technical questions
across Programming Languages, DSA, SQL, Web Development, and CS Fundamentals.
"""

from typing import Dict, Any, List, Tuple

DIFFICULTY_TIERS = [
    ("very_easy", 1),
    ("easy", 2),
    ("medium", 3),
    ("hard", 4),
    ("very_hard", 5),
    ("expert", 6),
]


def make_starter_codes(func_name: str, py_args: str, py_ret: str, js_args: str, c_args: str, c_ret: str, cpp_ret: str, java_ret: str) -> Dict[str, str]:
    """Generates standard starter codes for all 6 major languages."""
    return {
        "python": f"def {func_name}({py_args}) -> {py_ret}:\n    # Write your solution here\n    pass\n",
        "javascript": f"function {func_name}({js_args}) {{\n    // Write your solution here\n}}\n",
        "typescript": f"function {func_name}({js_args}): any {{\n    // Write your solution here\n}}\n",
        "c": f"{c_ret} {func_name}({c_args}) {{\n    // Write your solution here\n}}\n",
        "cpp": f"class Solution {{\npublic:\n    {cpp_ret} {func_name}({c_args}) {{\n        // Write your solution here\n    }}\n}};\n",
        "java": f"class Solution {{\n    public {java_ret} {func_name}({c_args}) {{\n        // Write your solution here\n    }}\n}}\n",
    }

