import re
from typing import Dict, Any, List, Optional
from app.ai.base import BaseLLMProvider

COMMON_SKILLS = {
    # Languages
    "python": "language", "javascript": "language", "typescript": "language",
    "java": "language", "c++": "language", "c#": "language", "golang": "language", "go": "language",
    "ruby": "language", "rust": "language", "sql": "language", "html": "language", "css": "language",
    # Frameworks / Libraries
    "react": "framework", "next.js": "framework", "vue": "framework", "angular": "framework",
    "fastapi": "framework", "django": "framework", "flask": "framework", "express": "framework",
    "node.js": "framework", "spring boot": "framework", "tailwindcss": "framework",
    # Databases
    "postgresql": "database", "mysql": "database", "sqlite": "database",
    "mongodb": "database", "redis": "database", "cassandra": "database",
    # DevOps / Cloud
    "docker": "devops", "kubernetes": "devops", "aws": "cloud", "azure": "cloud", "gcp": "cloud",
    "git": "tool", "github": "tool", "ci/cd": "devops", "linux": "os",
    # Concepts
    "data structures": "concept", "algorithms": "concept", "rest api": "concept",
    "microservices": "concept", "oop": "concept", "machine learning": "concept",
}

DOC_URLS = {
    "fastapi": "https://fastapi.tiangolo.com/",
    "react": "https://react.dev/",
    "next.js": "https://nextjs.org/docs",
    "postgresql": "https://www.postgresql.org/docs/",
    "python": "https://docs.python.org/3/",
    "typescript": "https://www.typescriptlang.org/docs/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "docker": "https://docs.docker.com/",
    "kubernetes": "https://kubernetes.io/docs/",
    "redis": "https://redis.io/docs/",
    "node.js": "https://nodejs.org/en/docs",
    "express": "https://expressjs.com/",
    "django": "https://docs.djangoproject.com/",
    "flask": "https://flask.palletsprojects.com/",
    "tailwindcss": "https://tailwindcss.com/docs",
    "tailwind css": "https://tailwindcss.com/docs",
    "pytest": "https://docs.pytest.org/",
    "aws": "https://docs.aws.amazon.com/",
    "graphql": "https://graphql.org/learn/",
    "pandas": "https://pandas.pydata.org/docs/",
    "pytorch": "https://pytorch.org/docs/stable/index.html",
}

ROLE_DEFAULTS = {
    "frontend": ["TypeScript", "React", "Next.js", "Tailwind CSS"],
    "backend": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "fullstack": ["TypeScript", "React", "FastAPI", "PostgreSQL"],
    "devops": ["Docker", "Kubernetes", "AWS", "CI/CD"],
    "datascience": ["Python", "Pandas", "Scikit-Learn", "PyTorch"],
    "mobile": ["TypeScript", "React Native", "Mobile Architecture", "REST API"],
}


class FallbackAIProvider(BaseLLMProvider):
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        text_lower = resume_text.lower()

        # Extract skills
        detected_skills = []
        for skill_name, category in COMMON_SKILLS.items():
            pattern = r"(?<!\w)" + re.escape(skill_name) + r"(?!\w)"
            if re.search(pattern, text_lower):
                detected_skills.append({
                    "name": skill_name.title() if len(skill_name) > 3 else skill_name.upper(),
                    "category": category,
                })

        # Basic email and phone extraction
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
        candidate_email = email_match.group(0) if email_match else None

        # Identify sections
        sections = {"education": [], "experience": [], "projects": []}
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

        current_section = None
        for line in lines:
            lower = line.lower()
            matched_section = None
            if any(h in lower for h in ["education", "academic", "university", "college", "degree"]):
                matched_section = "education"
            elif any(h in lower for h in ["experience", "employment", "work history", "internship"]):
                matched_section = "experience"
            elif any(h in lower for h in ["projects", "personal projects", "academic projects"]):
                matched_section = "projects"
            elif any(h in lower for h in ["skills", "technical skills", "certifications"]):
                current_section = None
                continue

            if matched_section:
                current_section = matched_section
                parts = line.split(":", 1)
                if len(parts) > 1 and len(parts[1].strip()) > 3:
                    sections[current_section].append(parts[1].strip())
                continue

            if current_section and len(line) > 3:
                sections[current_section].append(line)

        strengths = [
            f"Demonstrated background with {len(detected_skills)} identified technical competencies.",
            "Clear technical project and educational history provided in resume.",
        ]
        if any(s["category"] == "database" for s in detected_skills):
            strengths.append("Foundational database systems exposure.")
        if any(s["category"] == "framework" for s in detected_skills):
            strengths.append("Modern application framework knowledge.")

        suggestions = [
            "Validate claimed skills through Kynetic skill assessments to generate verified evidence.",
            "Connect related GitHub repositories to support project implementations with practical code evidence.",
            "Add measurable metric outcomes (e.g. % performance increase, latency reduction) to project descriptions.",
        ]

        return {
            "status": "completed",
            "extracted_profile": {
                "candidate_email": candidate_email,
                "education": sections["education"][:5],
                "experience": sections["experience"][:8],
                "projects": sections["projects"][:6],
                "claimed_skills_count": len(detected_skills),
            },
            "claimed_skills": detected_skills,
            "strengths": strengths,
            "suggestions": suggestions,
            "model_metadata": {
                "provider": "rule-based-fallback",
                "version": "1.0.0",
                "note": "Deterministic fallback extractor (no external LLM key required).",
            },
        }

    def analyze_repository(self, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Provides deterministic fallback analysis from parsed repo files and heuristics."""
        detected_tech = repo_context.get("detected_technologies", [])
        major_features = repo_context.get("major_features", [])
        strengths = repo_context.get("technical_strengths", [])
        missing_reqs = repo_context.get("missing_requirements", [])
        recommendations = repo_context.get("recommendations", [])
        inspected_files = repo_context.get("inspected_files", [])
        arch_summary = repo_context.get("architecture_summary", "")
        purpose = repo_context.get("purpose", "")

        return {
            "purpose": purpose or f"Software application built with {', '.join(detected_tech[:4]) or 'modern technologies'}.",
            "detected_technologies": detected_tech,
            "demonstrated_skills": detected_tech,
            "architecture_summary": arch_summary or f"Modular architecture implementing {', '.join(detected_tech[:3])}.",
            "major_features": major_features or ["Core service implementation", "Structured data and API layer"],
            "technical_strengths": strengths or ["Standard dependency management", "Modular organization"],
            "architectural_weaknesses": ["Requires continuous integration and expanded automated test coverage."],
            "missing_requirements": missing_reqs or ["Automated testing suite", "Docker containerization"],
            "recommendations": recommendations or ["Add unit tests", "Configure CI/CD"],
            "inspected_files": inspected_files,
            "model_metadata": {
                "provider": "deterministic-fallback",
                "version": "1.0.0",
                "note": "Parsed directly via manifest and file structure inspection.",
            },
        }

    def analyze_job_match(
        self,
        job_description: str,
        candidate_capabilities: List[Dict[str, Any]],
        candidate_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        lines = job_description.split("\n")
        req_lines = []
        pref_lines = []
        current_section = "mandatory"

        pref_headers = ["preferred", "nice to have", "bonus", "plus", "desired", "good to have", "pluses"]
        req_headers = ["requirements", "qualifications", "must have", "required", "minimum qualifications", "what you bring", "basic qualifications", "role responsibilities"]

        for line in lines:
            line_lower = line.strip().lower()
            if any(h in line_lower for h in pref_headers) and len(line_lower) < 45:
                current_section = "preferred"
                continue
            elif any(h in line_lower for h in req_headers) and len(line_lower) < 45:
                current_section = "mandatory"
                continue

            if current_section == "preferred":
                pref_lines.append(line)
            else:
                req_lines.append(line)

        def extract_skills(text: str) -> List[str]:
            found = set()
            t_lower = text.lower()
            for kw in COMMON_SKILLS.keys():
                pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
                if re.search(pattern, t_lower):
                    found.add(kw.title() if len(kw) > 3 else kw.upper())
            return sorted(list(found))

        req_skills = extract_skills("\n".join(req_lines))
        pref_skills = extract_skills("\n".join(pref_lines))
        pref_skills = [p for p in pref_skills if p not in req_skills]

        if not req_skills and not pref_skills:
            req_skills = ["Python", "REST API", "SQL"]

        cap_map = {c.get("skill_name", "").lower(): c for c in candidate_capabilities}
        action_plan = []
        for s in req_skills:
            if s.lower() not in cap_map:
                action_plan.append(f"Add a project demonstrating {s} or complete an assessment to fulfill this mandatory requirement.")

        return {
            "mandatory_skills": req_skills,
            "preferred_skills": pref_skills,
            "action_plan": action_plan[:5],
            "alignment_explanation": f"Evaluation parsed {len(req_skills)} mandatory requirements and {len(pref_skills)} preferred qualifications against candidate capability evidence.",
            "model_metadata": {
                "provider": "deterministic-fallback",
                "version": "1.0.0",
                "note": "Section-aware rule-based parsing engine.",
            },
        }

    def generate_personalized_roadmap(
        self,
        role_title: str,
        role_description: Optional[str],
        candidate_capabilities: List[Dict[str, Any]],
        target_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if target_skills and len(target_skills) > 0:
            skills = target_skills
        else:
            combined = f"{role_title} {role_description or ''}".lower()
            if any(w in combined for w in ["frontend", "react", "ui", "client"]):
                skills = ROLE_DEFAULTS["frontend"]
            elif any(w in combined for w in ["devops", "cloud", "infra", "sre", "kubernetes"]):
                skills = ROLE_DEFAULTS["devops"]
            elif any(w in combined for w in ["data", "machine learning", "ml", "ai"]):
                skills = ROLE_DEFAULTS["datascience"]
            elif any(w in combined for w in ["full stack", "fullstack"]):
                skills = ROLE_DEFAULTS["fullstack"]
            elif any(w in combined for w in ["mobile", "android", "ios"]):
                skills = ROLE_DEFAULTS["mobile"]
            else:
                skills = ROLE_DEFAULTS["backend"]

        cap_scores = {c.get("skill_name", "").lower(): c.get("score", 0.0) for c in candidate_capabilities}

        milestones = []
        for idx, skill in enumerate(skills, start=1):
            key = skill.lower().strip()
            doc_url = DOC_URLS.get(key, f"https://devdocs.io/{key.replace(' ', '-').replace('.', '')}")
            user_score = cap_scores.get(key, 0.0)

            resources = [
                {
                    "type": "documentation",
                    "title": f"Official {skill} Documentation & Reference",
                    "url": doc_url,
                },
                {
                    "type": "learning_objectives",
                    "title": f"Key Competency Objectives for {skill}",
                    "objectives": [
                        f"Understand core paradigms, standard libraries, and architectural patterns of {skill}.",
                        f"Design modular, reusable, and type-safe components or services using {skill}.",
                        "Implement automated tests and performance optimizations adhering to industry standards.",
                    ],
                },
                {
                    "type": "practice",
                    "title": f"Verify {skill} via Kynetic Assessment",
                    "action": "assessment",
                    "skill": skill,
                },
            ]
            if user_score > 0.0:
                if user_score >= 85.0:
                    rec_level = "Level 6 (Expert)"
                    target_focus = "solve advanced algorithmic problems, edge-case optimizations, and production concurrency challenges to achieve 10/10 mastery."
                elif user_score >= 65.0:
                    rec_level = "Level 4–5 (Hard to Very Hard)"
                    target_focus = "deepen algorithmic reasoning, dynamic programming, and systems optimization."
                elif user_score >= 45.0:
                    rec_level = "Level 3 (Medium)"
                    target_focus = "reinforce data structure manipulation and multi-step algorithmic problem solving."
                else:
                    rec_level = "Level 1–2 (Very Easy to Easy)"
                    target_focus = "solidify core language syntax, control structures, and basic operations."

                resources.append({
                    "type": "adaptive_recommendation",
                    "title": f"Target Assessment Level: {rec_level}",
                    "note": f"Current calibrated baseline: {user_score:.0f}%. Next milestone focus: {target_focus}",
                })

            milestones.append({
                "title": f"Milestone {idx}: Core & Advanced {skill}",
                "description": f"Master fundamental concepts, practical idioms, design patterns, and enterprise best practices for {skill}." + (f" (Current baseline: {user_score:.0f}%)" if user_score >= 60 else ""),
                "ordering": idx,
                "resources": resources,
            })

        # Capstone milestone
        capstone_idx = len(skills) + 1
        milestones.append({
            "title": f"Milestone {capstone_idx}: Integrated Portfolio Project",
            "description": f"Synthesize your mastery by architecting, testing, and deploying an end-to-end production application integrating {', '.join(skills[:3])} with automated testing and documentation.",
            "ordering": capstone_idx,
            "resources": [
                {
                    "type": "project",
                    "title": "Register & Analyze Project in Kynetic",
                    "action": "project",
                    "suggested_stack": skills[:4],
                },
                {
                    "type": "documentation",
                    "title": "Production Deployment & Architecture Checklist",
                    "url": "https://github.com",
                },
            ],
        })

        return {
            "milestones": milestones,
            "model_metadata": {
                "provider": "deterministic-fallback",
                "version": "1.0.0",
                "note": "Personalized curriculum generated from verified capability signals.",
            },
        }

    def generate_chat_response(self, user_prompt: str, context: Dict[str, Any]) -> str:
        prompt_lower = user_prompt.lower()
        capabilities = context.get("capabilities", []) or context.get("top_skills", [])
        cap_names = [c.get("skill") or c.get("skill_name") for c in capabilities if c.get("skill") or c.get("skill_name")]

        # Developer configuration notice when Gemini is selected but API key is missing
        from app.core.config import settings
        notice = ""
        if (settings.LLM_PROVIDER or "").lower() == "gemini" and not settings.effective_gemini_api_key:
            notice = (
                "> 💡 **Setup Notice**: Live Gemini AI requires an API key. Add `GEMINI_API_KEY=your_key` in `backend/.env` for real-time model responses. "
                "(Displaying Kynetic deterministic engineering knowledge response below)\n\n"
            )

        has_workspace_context = bool(context and any(v for v in context.values() if v))
        if not has_workspace_context:
            if "pointer" in prompt_lower or "c programming" in prompt_lower or (prompt_lower.startswith("c ") and "code" in prompt_lower):
                return notice + (
                    "### Pointers & Memory in C\n\n"
                    "A **pointer** is a variable that stores the memory address of another variable. "
                    "In C, pointers provide direct access to hardware memory and dynamic heap allocation.\n\n"
                    "- **Address-of (`&`)**: Gets the memory location of a variable (e.g., `int *ptr = &x;`).\n"
                    "- **Dereference (`*`)**: Accesses the value stored at the address (e.g., `int val = *ptr;`).\n"
                    "- **Heap Allocation**: Allocate dynamic memory using `malloc(bytes)` or `calloc(num, size)` and always release it with `free(ptr)` to avoid memory leaks."
                )
            if "c++" in prompt_lower or "cpp" in prompt_lower:
                return notice + (
                    "### Modern C++ Principles\n\n"
                    "Modern C++ (C++11 through C++20) emphasizes safety, zero-cost abstractions, and automatic resource management:\n\n"
                    "- **RAII (Resource Acquisition Is Initialization)**: Object lifetimes manage resource acquisition and automatic destruction.\n"
                    "- **Smart Pointers**: Replace raw `new`/`delete` with `std::unique_ptr` (exclusive ownership) and `std::shared_ptr` (reference-counted shared ownership).\n"
                    "- **STL Containers & Algorithms**: Efficient contiguous structures (`std::vector`), lookup tables (`std::unordered_map`), and parallel algorithms."
                )
            if "dsa" in prompt_lower or "data structure" in prompt_lower or "algorithm" in prompt_lower or "binary search" in prompt_lower:
                return notice + (
                    "### Data Structures & Algorithms Core Concepts\n\n"
                    "- **Time & Space Complexity**: Measured using Big-O notation ($O(1)$, $O(\\log n)$, $O(n)$, $O(n \\log n)$, $O(n^2)$).\n"
                    "- **Linear Foundations**: Arrays (contiguous cache-friendly memory), Hash Tables (amortized $O(1)$ lookups), Linked Lists (pointer traversal).\n"
                    "- **Hierarchical**: Binary Search Trees, Heaps/Priority Queues ($O(\\log n)$ insertion/removal), and Graphs (BFS/DFS traversal).\n"
                    "- **Optimization Paradigms**: Two-pointer sliding windows, Divide & Conquer (Merge Sort), Dynamic Programming (overlapping subproblems)."
                )
            if "sql" in prompt_lower or "database" in prompt_lower or "mysql" in prompt_lower or "join" in prompt_lower:
                return notice + (
                    "### Relational Databases & SQL\n\n"
                    "- **ACID Guarantees**: Atomicity, Consistency, Isolation, and Durability ensure reliable transaction processing.\n"
                    "- **Relational Joins**: `INNER JOIN` (matching rows in both tables), `LEFT JOIN` (all left rows plus matching right rows), and self-joins for hierarchies.\n"
                    "- **Indexing (B-Tree)**: Indexes provide $O(\\log n)$ row lookups on indexed columns; avoid functions in `WHERE` clauses to keep predicates sargable.\n"
                    "- **Normalization**: 1NF (atomic values), 2NF (remove partial key dependencies), 3NF (remove transitive dependencies)."
                )
            if "python" in prompt_lower:
                return notice + (
                    "### Python Architecture & Idioms\n\n"
                    "**Python** is a high-level, dynamically typed language known for expressiveness and clean syntax:\n\n"
                    "- **Data Model**: Everything is an object with type, identity (`id`), and value. Differentiates mutable types (`list`, `dict`, `set`) from immutable types (`int`, `str`, `tuple`).\n"
                    "- **Resource Management**: Context managers (`with` statement) guarantee automatic resource cleanup via `__enter__` and `__exit__`.\n"
                    "- **Generators (`yield`)**: Lazy stream evaluation that processes massive datasets with constant $O(1)$ memory consumption."
                )
            if "react" in prompt_lower or "frontend" in prompt_lower or "next.js" in prompt_lower:
                return notice + (
                    "### Modern Frontend & React Architecture\n\n"
                    "- **Component Trees**: Declarative UI built with typed props and modular JSX components.\n"
                    "- **Hooks Lifecycle**: `useState` for local reactive state, `useEffect` for side effects, and `useMemo`/`useCallback` for performance.\n"
                    "- **Next.js App Router**: Hybrid rendering combining Server Components (zero client JS footprint) and interactive Client Components (`'use client'`)."
                )
            if "docker" in prompt_lower or "devops" in prompt_lower or "container" in prompt_lower:
                return notice + (
                    "### Containerization & Docker\n\n"
                    "- **Images vs Containers**: An image is an immutable template; a container is a lightweight, isolated runnable instance sharing the host OS kernel.\n"
                    "- **Multi-Stage Builds**: Drastically reduce production image sizes by separating compile-time dependencies from minimal runtime environments."
                )
            if "rest" in prompt_lower or "api" in prompt_lower:
                return notice + (
                    "### RESTful API Architecture\n\n"
                    "**REST (Representational State Transfer)** uses standard HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) with stateless requests and JSON payloads. "
                    "Status codes indicate outcomes: `2xx` (Success), `3xx` (Redirect), `4xx` (Client Error), `5xx` (Server Error)."
                )
            if "git" in prompt_lower:
                return notice + (
                    "### Git Distributed Version Control\n\n"
                    "**Git** tracks file revisions using directed acyclic graphs of SHA commit hashes. "
                    "Key commands: `git status`, `git add`, `git commit -m`, `git branch`, and `git merge`."
                )
            return notice + (
                f"### Analysis: {user_prompt}\n\n"
                f"This topic is an integral part of professional software engineering. "
                "To explore this systematically, you can view our step-by-step **Curated Learning Roadmaps** (under Roadmaps) or take a self-directed technical assessment in **Assessments**."
            )

        if "skill" in prompt_lower or "gap" in prompt_lower:
            if cap_names:
                return notice + f"Based on your verified capabilities including {', '.join(cap_names)}, focus on completing validated assessments and pushing live code repositories to improve your capability confidence."
            return notice + "Based on your verified capabilities and claimed skills, focus on completing validated assessments and pushing live code repositories to improve your capability confidence."
        elif "resume" in prompt_lower:
            return notice + "Your resume claims have been ingested. Make sure to ground them with technical evidence in Assessments and Projects to make them credible to recruiters."
        return notice + f"I am your Kynetic career co-pilot. I can help analyze your capabilities, explore placement matches, and generate learning roadmaps. (Question: '{user_prompt[:50]}...')"

    def generate_question_batch(
        self,
        skill_or_topic: str,
        category: str,
        difficulty: str,
        question_type: str,
        batch_size: int,
        programming_language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = []
        lang = (programming_language or "python").lower()

        # Natural problem templates for fallback generation
        coding_templates = [
            {
                "title": "Count Positive Numbers",
                "entry_point": "count_positives",
                "desc": "Given a list of integers, return the count of strictly positive numbers (> 0).",
                "examples": "Example 1:\nInput: nums = [1, -2, 3, -4, 5]\nOutput: 3\nExplanation: Positive numbers are 1, 3, and 5.\n\nExample 2:\nInput: nums = [-1, -2, -3]\nOutput: 0",
                "constraints": ["1 <= nums.length <= 10^4", "-10^5 <= nums[i] <= 10^5"],
                "test_cases": [
                    {"inputs": [[1, -2, 3, -4, 5]], "expected": 3},
                    {"inputs": [[-1, -2, -3]], "expected": 0},
                    {"inputs": [[10, 20]], "expected": 2},
                    {"inputs": [[]], "expected": 0},
                ],
                "py_ref": "def count_positives(nums):\n    return sum(1 for x in nums if x > 0)",
                "starters": {
                    "python": "def count_positives(nums: list[int]) -> int:\n    # Return count of positive integers\n    pass\n",
                    "javascript": "function countPositives(nums) {\n    // Return count of positive integers\n}\n",
                    "typescript": "function countPositives(nums: number[]): number {\n    // Return count of positive integers\n}\n",
                    "c": "int count_positives(int* nums, int numsSize) {\n    // Return count of positive integers\n}\n",
                    "cpp": "class Solution {\npublic:\n    int countPositives(std::vector<int>& nums) {\n        // Return count of positive integers\n    }\n};\n",
                    "java": "class Solution {\n    public int countPositives(int[] nums) {\n        // Return count of positive integers\n    }\n}\n",
                },
            },
            {
                "title": "Find Maximum Element",
                "entry_point": "find_maximum",
                "desc": "Given a non-empty list of integers, return the maximum element.",
                "examples": "Example 1:\nInput: nums = [3, 7, 2, 9, 4]\nOutput: 9\n\nExample 2:\nInput: nums = [-5, -1, -10]\nOutput: -1",
                "constraints": ["1 <= nums.length <= 10^4", "-10^5 <= nums[i] <= 10^5"],
                "test_cases": [
                    {"inputs": [[3, 7, 2, 9, 4]], "expected": 9},
                    {"inputs": [[-5, -1, -10]], "expected": -1},
                    {"inputs": [[42]], "expected": 42},
                ],
                "py_ref": "def find_maximum(nums):\n    return max(nums)",
                "starters": {
                    "python": "def find_maximum(nums: list[int]) -> int:\n    # Return maximum element\n    pass\n",
                    "javascript": "function findMaximum(nums) {\n    // Return maximum element\n}\n",
                    "typescript": "function findMaximum(nums: number[]): number {\n    // Return maximum element\n}\n",
                    "c": "int find_maximum(int* nums, int numsSize) {\n    // Return maximum element\n}\n",
                    "cpp": "class Solution {\npublic:\n    int findMaximum(std::vector<int>& nums) {\n        // Return maximum element\n    }\n};\n",
                    "java": "class Solution {\n    public int findMaximum(int[] nums) {\n        // Return maximum element\n    }\n}\n",
                },
            },
            {
                "title": "Sum Array Elements",
                "entry_point": "sum_elements",
                "desc": "Given an array of integers, compute and return the total sum of all elements.",
                "examples": "Example 1:\nInput: nums = [1, 2, 3, 4]\nOutput: 10\n\nExample 2:\nInput: nums = [-1, 1]\nOutput: 0",
                "constraints": ["0 <= nums.length <= 10^4", "-10^4 <= nums[i] <= 10^4"],
                "test_cases": [
                    {"inputs": [[1, 2, 3, 4]], "expected": 10},
                    {"inputs": [[-1, 1]], "expected": 0},
                    {"inputs": [[]], "expected": 0},
                ],
                "py_ref": "def sum_elements(nums):\n    return sum(nums)",
                "starters": {
                    "python": "def sum_elements(nums: list[int]) -> int:\n    # Return sum of all elements\n    pass\n",
                    "javascript": "function sumElements(nums) {\n    // Return sum of all elements\n}\n",
                    "typescript": "function sumElements(nums: number[]): number {\n    // Return sum of all elements\n}\n",
                    "c": "int sum_elements(int* nums, int numsSize) {\n    // Return sum of all elements\n}\n",
                    "cpp": "class Solution {\npublic:\n    int sumElements(std::vector<int>& nums) {\n        // Return sum of all elements\n    }\n};\n",
                    "java": "class Solution {\n    public int sumElements(int[] nums) {\n        // Return sum of all elements\n    }\n}\n",
                },
            },
            {
                "title": "Reverse String",
                "entry_point": "reverse_string",
                "desc": "Given a string `s`, return the string reversed.",
                "examples": "Example 1:\nInput: s = \"hello\"\nOutput: \"olleh\"\n\nExample 2:\nInput: s = \"Kynetic\"\nOutput: \"citenyK\"",
                "constraints": ["0 <= s.length <= 10^4"],
                "test_cases": [
                    {"inputs": ["hello"], "expected": "olleh"},
                    {"inputs": ["Kynetic"], "expected": "citenyK"},
                    {"inputs": [""], "expected": ""},
                ],
                "py_ref": "def reverse_string(s):\n    return s[::-1]",
                "starters": {
                    "python": "def reverse_string(s: str) -> str:\n    # Return reversed string\n    pass\n",
                    "javascript": "function reverseString(s) {\n    // Return reversed string\n}\n",
                    "typescript": "function reverseString(s: string): string {\n    // Return reversed string\n}\n",
                    "c": "char* reverse_string(char* s) {\n    // Return reversed string\n}\n",
                    "cpp": "class Solution {\npublic:\n    std::string reverseString(std::string s) {\n        // Return reversed string\n    }\n};\n",
                    "java": "class Solution {\n    public String reverseString(String s) {\n        // Return reversed string\n    }\n}\n",
                },
            },
        ]

        for idx in range(1, batch_size + 1):
            if question_type == "coding":
                tmpl = coding_templates[(idx - 1) % len(coding_templates)]
                title = f"{tmpl['title']} (Variant {idx})" if idx > len(coding_templates) else tmpl["title"]
                prompt = (
                    f"### {title}\n\n"
                    f"{tmpl['desc']}\n\n"
                    f"{tmpl['examples']}\n\n"
                    f"**Constraints:**\n"
                    + "\n".join(f"- {c}" for c in tmpl["constraints"])
                )
                results.append({
                    "title": title,
                    "prompt": prompt,
                    "subtopic": skill_or_topic,
                    "options": [],
                    "evaluation_metadata": {
                        "title": title,
                        "entry_point": tmpl["entry_point"],
                        "starter_codes": tmpl["starters"],
                        "starter_code": tmpl["starters"].get(lang, tmpl["starters"]["python"]),
                        "test_cases": tmpl["test_cases"],
                        "reference_solution": tmpl["py_ref"],
                        "constraints": tmpl["constraints"],
                    },
                })
            elif question_type == "sql":
                title = f"Filter High Value Products (Tier {idx})"
                results.append({
                    "title": title,
                    "prompt": (
                        f"### {title}\n\n"
                        f"Given the `products` table containing inventory data, write an SQL query to retrieve "
                        f"the `name` and `price` of all active products with price greater than or equal to {idx * 50}, "
                        f"ordered by `price` descending.\n\n"
                        f"**Schema:** `products(id INT, name TEXT, price INT, is_active INT)`"
                    ),
                    "subtopic": skill_or_topic,
                    "options": [],
                    "evaluation_metadata": {
                        "title": title,
                        "schema_ddl": (
                            f"CREATE TABLE products (id INT, name TEXT, price INT, is_active INT);\n"
                            f"INSERT INTO products VALUES (1, 'Widget A', {idx * 50 + 20}, 1), "
                            f"(2, 'Widget B', {idx * 50 - 10}, 1), (3, 'Widget C', {idx * 50 + 80}, 0);"
                        ),
                        "reference_query": f"SELECT name, price FROM products WHERE is_active = 1 AND price >= {idx * 50} ORDER BY price DESC;",
                    },
                })
            elif question_type == "output_prediction":
                target_val = (idx * 4 + 2)
                title = f"List Comprehension Evens Output (Index {idx})"
                code_snippet = f"nums = [x for x in range({target_val}) if x % 2 == 0]\nprint(len(nums))"
                expected = str(target_val // 2)
                results.append({
                    "title": title,
                    "prompt": f"### {title}\n\nWhat will be the stdout output of the following {lang.title()} code snippet?\n\n```python\n{code_snippet}\n```",
                    "subtopic": skill_or_topic,
                    "options": [expected, str(target_val), str(target_val // 2 - 1), "Error"],
                    "evaluation_metadata": {
                        "title": title,
                        "code": code_snippet,
                        "expected_output": expected,
                        "correct_answer": expected,
                        "explanation": f"The range(0, {target_val}) produces {target_val} integers. Exactly {expected} of them are even numbers.",
                    },
                })
            elif question_type == "debugging":
                title = f"Concurrent Modification Defect (Scope {idx})"
                buggy = (
                    f"def remove_target_values(items, target):\n"
                    f"    for i in range(len(items)):\n"
                    f"        if items[i] == target:\n"
                    f"            del items[i]\n"
                    f"    return items"
                )
                results.append({
                    "title": title,
                    "prompt": (
                        f"### {title}\n\n"
                        f"Identify the runtime defect in the following function designed to remove matching target values from a collection:\n\n"
                        f"```python\n{buggy}\n```"
                    ),
                    "subtopic": skill_or_topic,
                    "options": [
                        "Mutating a list while iterating over its index range causes IndexError or skips adjacent items",
                        "Missing type annotation causes Python compiler rejection",
                        "The del keyword cannot be applied to list indices",
                        "Variables cannot be compared using the == equality operator in Python",
                    ],
                    "evaluation_metadata": {
                        "title": title,
                        "buggy_code": buggy,
                        "correct_fix": "Mutating a list while iterating over its index range causes IndexError or skips adjacent items",
                        "explanation": "Deleting elements during range iteration shrinks the list dynamically, causing index out of range or skipping adjacent items. Use list comprehension or iterate backwards.",
                    },
                })
            elif question_type == "conceptual":
                title = f"{skill_or_topic} Architectural Principles (Tier {idx})"
                results.append({
                    "title": title,
                    "prompt": (
                        f"### {title}\n\n"
                        f"Analyze the performance, concurrency, and memory trade-offs of {skill_or_topic}. "
                        f"Discuss cache locality, asymptotic time complexity, and heap versus stack allocation."
                    ),
                    "subtopic": skill_or_topic,
                    "options": [],
                    "evaluation_metadata": {
                        "title": title,
                        "rubric": "Addresses cache locality, heap vs stack memory allocation, and asymptotic time complexity bounds.",
                        "key_concepts": ["cache locality", "time complexity", "memory layout", "concurrency"],
                    },
                })
            else:  # multiple_choice
                title = f"{skill_or_topic} Execution Architecture (Level {idx})"
                results.append({
                    "title": title,
                    "prompt": (
                        f"### {title}\n\n"
                        f"What is the primary design characteristic of {skill_or_topic} regarding memory safety and execution determinism?"
                    ),
                    "subtopic": skill_or_topic,
                    "options": [
                        "Deterministic state transitions with structured lifecycle and boundary validation",
                        "Automatic asynchronous multiprocessing across all hardware threads without locks",
                        "Global execution of unverified binaries directly in ring 0",
                        "Complete omission of data structure boundary validation",
                    ],
                    "evaluation_metadata": {
                        "title": title,
                        "correct_answer": "Deterministic state transitions with structured lifecycle and boundary validation",
                        "explanation": f"Core design principle of {skill_or_topic} guarantees structured state transitions and memory boundary safety.",
                    },
                })

        return results
