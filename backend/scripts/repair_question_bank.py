import sys
import os
import re
from collections import defaultdict

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal
from app.models.assessment import Question, AssessmentAttempt

def clean_title_for_question(q: Question) -> str:
    meta = q.evaluation_metadata or {}
    if meta.get("title") and not any(pat in meta["title"] for pat in ["Challenge #", "compute_", "solve_"]):
        return meta["title"]
    
    p = q.prompt.strip()
    
    # 1. Coding entry point mapping
    if q.question_type == "coding":
        entry = meta.get("entry_point") or ""
        if entry and not any(pat in entry for pat in ["compute_", "solve_dsa_", "calculate_"]):
            title_words = entry.replace("_", " ").split()
            return " ".join(w.capitalize() for w in title_words)
        
        # Match function name in prompt: `function_name(...)`
        func_match = re.search(r"`([a-zA-Z0-9_]+)\(", p)
        if func_match:
            fn = func_match.group(1)
            if not any(pat in fn for pat in ["compute_", "solve_dsa_", "calculate_"]):
                return " ".join(w.capitalize() for w in fn.replace("_", " ").split())
        
        if q.subtopic and q.subtopic != "General":
            return f"{q.subtopic} Challenge"
        return "Algorithm Challenge"

    # 2. Output prediction
    if q.question_type == "output_prediction":
        lang = (q.programming_language or "Code").capitalize()
        if q.subtopic and q.subtopic != "General":
            return f"{lang} {q.subtopic} Output"
        return f"{lang} Code Tracing"

    # 3. Debugging
    if q.question_type == "debugging":
        lang = (q.programming_language or "Code").capitalize()
        if q.subtopic and q.subtopic != "General":
            return f"{lang} {q.subtopic} Debugging"
        return f"{lang} Logic Defect"

    # 4. SQL
    if q.question_type == "sql":
        if "order" in p.lower():
            return "Order By & Sorting Query"
        elif "group by" in p.lower():
            return "Aggregation with Group By"
        elif "join" in p.lower():
            return "Relational Table Join"
        elif q.subtopic and q.subtopic != "General":
            return f"SQL {q.subtopic}"
        return "Relational Query Problem"

    # 5. Conceptual / MCQ
    first_sentence = p.split("\n")[0].split("?")[0].strip()
    if len(first_sentence) < 40 and len(first_sentence) > 5:
        return first_sentence
    elif q.subtopic and q.subtopic != "General":
        return f"{q.subtopic} Fundamentals"
    else:
        topic_name = q.topic.name if q.topic else "Technical"
        return f"{topic_name} Assessment"


def main():
    db = SessionLocal()
    try:
        all_q = db.query(Question).all()
        attempts = set(r[0] for r in db.query(AssessmentAttempt.question_id).all())
        
        print(f"Total questions before repair: {len(all_q)}")
        
        to_retire_ids = set()

        # A. Artificial identifiers
        for q in all_q:
            meta_str = str(q.evaluation_metadata or {})
            p = q.prompt or ""
            if any(pat in p or pat in meta_str for pat in [
                "compute_c_", "compute_cpp_", "compute_java_", "compute_python_",
                "calculate_js_", "solve_dsa_", "Challenge #", "Generated Problem"
            ]):
                to_retire_ids.add(q.id)

        # B. Language mismatch (Python code under C/C++/Java)
        for q in all_q:
            lang = (q.programming_language or "").lower()
            meta = q.evaluation_metadata or {}
            code_snippet = (q.prompt or "") + " " + str(meta.get("code") or "") + " " + str(meta.get("buggy_code") or "") + " " + str(meta.get("reference_solution") or "")
            if lang in ("c", "cpp", "java") and any(pat in code_snippet for pat in [
                "def ", "range(len(", ".append(", "print(len("
            ]):
                to_retire_ids.add(q.id)

        # C. Exact duplicate prompts across difficulties
        prompt_groups = defaultdict(list)
        for q in all_q:
            clean = q.prompt.strip()
            prompt_groups[clean].append(q)

        for prompt, qs in prompt_groups.items():
            if len(qs) > 1:
                # Prioritize keeping question referenced by attempts
                has_attempt = [q for q in qs if q.id in attempts]
                keeper = has_attempt[0] if has_attempt else qs[0]
                for q in qs:
                    if q.id != keeper.id:
                        to_retire_ids.add(q.id)

        # D. Execute retirement
        retired_count = 0
        preserved_attempt_refs = 0
        active_updated = 0

        for q in all_q:
            if q.id in to_retire_ids:
                q.is_active = False
                q.validation_status = "retired"
                retired_count += 1
                if q.id in attempts:
                    preserved_attempt_refs += 1
            else:
                q.is_active = True
                q.validation_status = "validated"
                if not q.title:
                    q.title = clean_title_for_question(q)
                active_updated += 1

        db.commit()

        print("=== QUESTION BANK REPAIR REPORT ===")
        print(f"Total questions in database: {len(all_q)}")
        print(f"Questions retired (excluded from future assessments): {retired_count}")
        print(f"Historically attempted questions safely retired without deletion: {preserved_attempt_refs}")
        print(f"Clean active validated questions retained: {active_updated}")

        # Verify active questions have titles
        active_qs = db.query(Question).filter(Question.is_active.is_(True), Question.validation_status == "validated").all()
        missing_titles = sum(1 for q in active_qs if not q.title)
        print(f"Active questions missing titles: {missing_titles}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

