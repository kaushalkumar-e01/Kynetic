"""
Shared helpers for question catalog generation.
"""
from typing import Dict, Any, List
import re

DIFFICULTY_TIERS = [
    ("very_easy", 1),
    ("easy", 2),
    ("medium", 3),
    ("hard", 4),
    ("very_hard", 5),
    ("expert", 6),
]


def make_starter_codes(
    func_name: str,
    py_sig: str = "def solve(nums: list[int]) -> int:\n    pass\n",
    js_sig: str = "function solve(nums) {\n}\n",
    ts_sig: str = "function solve(nums: number[]): number {\n}\n",
    c_sig: str = "int solve(int* nums, int numsSize) {\n}\n",
    cpp_sig: str = "class Solution {\npublic:\n    int solve(std::vector<int>& nums) {\n    }\n};\n",
    java_sig: str = "class Solution {\n    public int solve(int[] nums) {\n    }\n}\n",
) -> Dict[str, str]:
    """Return standard starter code templates for 6 major languages."""
    return {
        "python": py_sig,
        "javascript": js_sig,
        "typescript": ts_sig,
        "c": c_sig,
        "cpp": cpp_sig,
        "java": java_sig,
    }


def balance_options(correct_answer: str, distractors: List[str], seed_index: int) -> List[str]:
    """
    Distributes the correct answer evenly across positions 0, 1, 2, 3 (A, B, C, D)
    based on seed_index % 4, without altering the correct answer string.
    Ensures 25% A, 25% B, 25% C, 25% D across the catalog.
    """
    clean_distractors = [d for d in distractors if str(d).strip().lower() != str(correct_answer).strip().lower()]
    # Pad if less than 3 distractors
    while len(clean_distractors) < 3:
        clean_distractors.append(f"Alternative approach {len(clean_distractors) + 1}")
    
    target_pos = seed_index % 4
    opts: List[str] = []
    d_idx = 0
    for i in range(4):
        if i == target_pos:
            opts.append(correct_answer)
        else:
            opts.append(clean_distractors[d_idx % len(clean_distractors)])
            d_idx += 1
    return opts


def format_coding_prompt(
    title: str,
    description: str,
    examples: List[Dict[str, Any]],
    constraints: List[str],
) -> str:
    """Format professional LeetCode-style Markdown problem prompt."""
    lines = [f"### {title}\n", f"{description}\n"]
    for idx, ex in enumerate(examples, start=1):
        lines.append(f"**Example {idx}:**")
        lines.append("```")
        lines.append(f"Input: {ex['input']}")
        lines.append(f"Output: {ex['output']}")
        if "explanation" in ex and ex["explanation"]:
            lines.append(f"Explanation: {ex['explanation']}")
        lines.append("```\n")

    if constraints:
        lines.append("**Constraints:**")
        for c in constraints:
            lines.append(f"- {c}")

    return "\n".join(lines)


def get_title_root(title: str) -> str:
    """Extract semantic base title stripped of '(Case X)', '(Topic Y)', etc."""
    if not title:
        return ""
    t = re.sub(r"\(Level\s+\d+[^)]*\)", "", title, flags=re.IGNORECASE)
    t = re.sub(r"\(Case\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\(Topic\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\(Pattern\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\(Scenario\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip().lower()
