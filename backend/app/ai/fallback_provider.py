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
                        f"Implement automated tests and performance optimizations adhering to industry standards.",
                    ],
                },
                {
                    "type": "practice",
                    "title": f"Verify {skill} via Kynetic Assessment",
                    "action": "assessment",
                    "skill": skill,
                },
            ]
            if user_score >= 60.0:
                resources.append({
                    "type": "status_note",
                    "title": "Baseline Verified",
                    "note": f"Demonstrated {user_score:.0f}% proficiency in {skill}. Focus on advanced production architecture.",
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
        if "skill" in prompt_lower or "gap" in prompt_lower:
            return "Based on your verified capabilities and claimed skills, focus on completing validated assessments and pushing live code repositories to improve your capability confidence."
        elif "resume" in prompt_lower:
            return "Your resume claims have been ingested. Make sure to ground them with technical evidence in Assessments and Projects to make them credible to recruiters."
        return f"I am your Kynetic career co-pilot. I can help analyze your capabilities, explore placement matches, and generate learning roadmaps. (Question: '{user_prompt[:50]}...')"
