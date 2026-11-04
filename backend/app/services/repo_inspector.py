import os
import re
import json
from typing import Dict, Any, List, Optional
import httpx

KNOWN_DEPENDENCY_TAGS = {
    # Python
    "fastapi": ("FastAPI", "framework"),
    "uvicorn": ("Uvicorn", "tool"),
    "sqlalchemy": ("SQLAlchemy", "database"),
    "alembic": ("Alembic", "tool"),
    "pydantic": ("Pydantic", "tool"),
    "pytest": ("Pytest", "tool"),
    "pypdf": ("PyPDF", "tool"),
    "django": ("Django", "framework"),
    "flask": ("Flask", "framework"),
    "celery": ("Celery", "backend"),
    "redis": ("Redis", "database"),
    "psycopg": ("PostgreSQL", "database"),
    "asyncpg": ("PostgreSQL", "database"),
    "pandas": ("Pandas", "tool"),
    "numpy": ("NumPy", "tool"),
    "torch": ("PyTorch", "framework"),
    "tensorflow": ("TensorFlow", "framework"),
    # JavaScript / TypeScript
    "next": ("Next.js", "framework"),
    "react": ("React", "framework"),
    "react-dom": ("React", "framework"),
    "tailwindcss": ("Tailwind CSS", "frontend"),
    "typescript": ("TypeScript", "language"),
    "eslint": ("ESLint", "tool"),
    "express": ("Express.js", "framework"),
    "vue": ("Vue.js", "framework"),
    "angular": ("Angular", "framework"),
    "svelte": ("Svelte", "framework"),
    "prisma": ("Prisma", "database"),
    "drizzle-orm": ("Drizzle ORM", "database"),
    "mongoose": ("MongoDB", "database"),
    "zustand": ("Zustand", "frontend"),
    "redux": ("Redux", "frontend"),
    "@reduxjs/toolkit": ("Redux Toolkit", "frontend"),
    "vitest": ("Vitest", "tool"),
    "jest": ("Jest", "tool"),
    "playwright": ("Playwright", "tool"),
    "cypress": ("Cypress", "tool"),
    "axios": ("Axios", "tool"),
    "lucide-react": ("Lucide Icons", "frontend"),
}

_REPO_ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}


class RepositoryInspector:
    @staticmethod
    def parse_repo_url(url: str) -> tuple[str, str]:
        clean = url.strip().rstrip("/").replace(".git", "")
        match = re.search(r"github\.com/([^/]+)/([^/]+)", clean)
        if not match:
            raise ValueError(f"Invalid GitHub repository URL: '{url}'")
        return match.group(1), match.group(2)

    @classmethod
    def inspect_repository(
        cls,
        repository_url: str,
        access_token: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        owner, repo = cls.parse_repo_url(repository_url)

        # Check Cache
        cache_key = f"{owner}/{repo}".lower()
        if not force_refresh and cache_key in _REPO_ANALYSIS_CACHE:
            return dict(_REPO_ANALYSIS_CACHE[cache_key])

        headers = {
            "User-Agent": "Kynetic-Code-Intelligence/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        if access_token and not access_token.startswith("gho_mock_token_"):
            headers["Authorization"] = f"Bearer {access_token}"

        inspected_files: Dict[str, str] = {}
        repo_metadata: Dict[str, Any] = {}
        languages_data: Dict[str, int] = {}
        is_private = False
        accessible = True

        # 1. Fetch Repo Metadata from GitHub API
        try:
            with httpx.Client(timeout=3.0, headers=headers) as client:
                repo_resp = client.get(f"https://api.github.com/repos/{owner}/{repo}")
                if repo_resp.status_code == 200:
                    repo_metadata = repo_resp.json()
                    is_private = repo_metadata.get("private", False)
                else:
                    accessible = False

                if accessible:
                    lang_resp = client.get(f"https://api.github.com/repos/{owner}/{repo}/languages")
                    if lang_resp.status_code == 200:
                        languages_data = lang_resp.json()
        except Exception:
            accessible = False

        # 2. Check Candidate Manifest & Source Files
        candidate_paths = [
            "README.md", "readme.md",
            "package.json", "frontend/package.json", "client/package.json", "web/package.json",
            "requirements.txt", "backend/requirements.txt", "api/requirements.txt",
            "pyproject.toml", "backend/pyproject.toml",
            "Cargo.toml", "go.mod", "pom.xml",
            "Dockerfile", "backend/Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            "tsconfig.json", "frontend/tsconfig.json",
            ".github/workflows/ci.yml", ".github/workflows/main.yml",
            # Sampled architecture modules
            "backend/app/main.py", "backend/app/api/v1/api.py", "backend/app/models/project.py",
            "frontend/app/page.tsx", "frontend/components/AppShell.tsx",
            "server/index.js", "src/index.ts", "src/App.tsx",
            "backend/tests/test_projects.py", "tests/test_main.py",
        ]

        # Fetch files via raw GitHub only if repo is accessible
        if accessible:
            default_branch = repo_metadata.get("default_branch", "main")
            with httpx.Client(timeout=2.0, headers=headers) as client:
                for path in candidate_paths[:12]:
                    if path in inspected_files:
                        continue
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
                    try:
                        resp = client.get(raw_url)
                        if resp.status_code == 200 and len(resp.text.strip()) > 0:
                            inspected_files[path] = resp.text
                    except Exception:
                        pass

        # 3. Local Workspace Fallback Inspection (if repository matches local Kynetic)
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        if not inspected_files or repo.lower() in ["kynetic", "kynetic-platform"]:
            for path in candidate_paths:
                local_path = os.path.join(workspace_root, path.replace("/", os.sep))
                if os.path.exists(local_path) and path not in inspected_files:
                    try:
                        with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if content.strip():
                                inspected_files[path] = content
                    except Exception:
                        pass

        # If completely inaccessible and no files found
        if not accessible and not inspected_files:
            return {
                "accessible": False,
                "is_private": is_private,
                "owner": owner,
                "repo": repo,
                "purpose": f"Private or inaccessible GitHub repository: {owner}/{repo}.",
                "detected_technologies": [],
                "architecture_summary": "Repository inspection was restricted. Connect your GitHub account with authorized permissions to analyze private repositories.",
                "demonstrated_skills": [],
                "missing_requirements": ["Repository access permissions."],
                "recommendations": ["Connect your GitHub account in Integrations to grant read access to this repository."],
                "inspected_files": [],
                "model_metadata": {"provider": "deterministic-fallback", "version": "1.0.0"},
            }

        # 4. Synthesize Baseline Heuristics from Inspected Files
        detected_tech = set()
        demonstrated_skills = set()
        parsed_dependencies: List[str] = []

        # Languages from API
        for lang in languages_data.keys():
            detected_tech.add(lang)
            demonstrated_skills.add(lang)

        # Inspect package.json
        has_frontend = False
        frontend_framework = None
        for p_key, content in inspected_files.items():
            if "package.json" in p_key:
                has_frontend = True
                try:
                    pkg = json.loads(content)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    for d_name in deps.keys():
                        parsed_dependencies.append(d_name)
                        clean_d = d_name.lower()
                        if clean_d in KNOWN_DEPENDENCY_TAGS:
                            tag, cat = KNOWN_DEPENDENCY_TAGS[clean_d]
                            detected_tech.add(tag)
                            demonstrated_skills.add(tag)
                            if cat == "framework" and not frontend_framework:
                                frontend_framework = tag
                except Exception:
                    pass

        # Inspect requirements.txt / pyproject.toml
        has_backend = False
        backend_framework = None
        for r_key, content in inspected_files.items():
            if "requirements.txt" in r_key or "pyproject.toml" in r_key:
                has_backend = True
                detected_tech.add("Python")
                demonstrated_skills.add("Python")
                for line in content.split("\n"):
                    clean_line = line.strip().split("==")[0].split(">=")[0].split("<=")[0].strip().lower()
                    if clean_line:
                        parsed_dependencies.append(clean_line)
                    if clean_line in KNOWN_DEPENDENCY_TAGS:
                        tag, cat = KNOWN_DEPENDENCY_TAGS[clean_line]
                        detected_tech.add(tag)
                        demonstrated_skills.add(tag)
                        if cat == "framework" and not backend_framework:
                            backend_framework = tag

        # Other manifests
        if any("Cargo.toml" in k for k in inspected_files):
            detected_tech.add("Rust")
            demonstrated_skills.add("Rust")
        if any("go.mod" in k for k in inspected_files):
            detected_tech.add("Go")
            demonstrated_skills.add("Go")

        # Containerization & CI/CD inspection
        has_docker = any("Dockerfile" in k or "docker-compose" in k for k in inspected_files)
        if has_docker:
            detected_tech.add("Docker")
            demonstrated_skills.add("Docker")

        has_cicd = any(".github/workflows" in k for k in inspected_files)
        if has_cicd:
            detected_tech.add("GitHub Actions")
            demonstrated_skills.add("CI/CD")

        has_tests = any("test" in dep for dep in parsed_dependencies) or any("pytest" in dep for dep in parsed_dependencies)

        # Extract Purpose & Features from README or Description
        readme_content = inspected_files.get("README.md") or inspected_files.get("readme.md") or ""
        repo_desc = repo_metadata.get("description") or ""

        major_features: List[str] = []
        if readme_content:
            for match in re.finditer(r"(?:^|\n)[-*+]\s+([^\n]{15,120})", readme_content):
                feat = match.group(1).strip()
                if not any(h in feat.lower() for h in ["license", "contributing", "http", "install"]):
                    major_features.append(feat)
                if len(major_features) >= 5:
                    break

        if not major_features:
            major_features = [
                f"Core {backend_framework or frontend_framework or 'software'} implementation modules.",
                "Configured dependency manifest and environment configuration.",
                "Modular source architecture with structured separation of concerns.",
            ]

        purpose = repo_desc or (
            f"Software engineering project '{repo}' by {owner}, implementing {', '.join(list(detected_tech)[:4])}."
        )

        arch_parts = []
        if has_frontend and frontend_framework:
            arch_parts.append(f"{frontend_framework} UI layer")
        elif has_frontend:
            arch_parts.append("Node.js client application")

        if has_backend and backend_framework:
            arch_parts.append(f"{backend_framework} Python backend service")
        elif has_backend:
            arch_parts.append("Python application backend")

        if any(d in detected_tech for d in ["PostgreSQL", "SQLAlchemy", "MySQL", "MongoDB"]):
            arch_parts.append("relational database persistence with ORM")

        if has_docker:
            arch_parts.append("Docker containerized runtime")

        arch_summary = (
            f"Multi-tier architecture comprising {' integrated with '.join(arch_parts) or 'modular services'}. "
            f"Inspected {len(inspected_files)} repository configuration and manifest files directly."
        )

        strengths = []
        if "FastAPI" in detected_tech or "Next.js" in detected_tech:
            strengths.append(f"Modern high-performance frameworks ({', '.join(s for s in ['FastAPI', 'Next.js', 'React'] if s in detected_tech)}).")
        if "TypeScript" in detected_tech:
            strengths.append("Type-safe frontend development utilizing strict TypeScript interfaces.")
        if "SQLAlchemy" in detected_tech and "Alembic" in detected_tech:
            strengths.append("Database versioning and schema migrations managed via SQLAlchemy & Alembic.")
        if has_docker:
            strengths.append("Containerized environment configuration for consistent deployments.")
        if len(strengths) == 0:
            strengths.append("Clean repository structure with standard dependency declarations.")

        missing_reqs = []
        recommendations = []

        if not has_docker:
            missing_reqs.append("Containerization: Missing Dockerfile and docker-compose.yml for reproducible execution.")
            recommendations.append("Add a Dockerfile and docker-compose setup to enable multi-service container orchestration.")
        else:
            recommendations.append("Optimize multi-stage Docker build layers to minimize production image footprint.")

        if not has_cicd:
            missing_reqs.append("CI/CD Automation: Missing GitHub Actions workflow for automated test runs on pull requests.")
            recommendations.append("Configure a .github/workflows/ci.yml pipeline to execute automated linting and tests on every commit.")
        else:
            recommendations.append("Enhance GitHub Actions pipeline with automated preview deployments and security vulnerability scanning.")

        if not has_tests:
            missing_reqs.append("Testing: No automated unit testing framework (pytest/vitest) detected in manifests.")
            recommendations.append("Introduce automated unit test suites with coverage reports.")
        else:
            recommendations.append("Maintain comprehensive test coverage for core business logic and API endpoints.")

        if "Next.js" in detected_tech and "FastAPI" in detected_tech:
            recommendations.append("Generate end-to-end typed API client bindings directly from FastAPI's OpenAPI specification (/api/v1/openapi.json).")

        # 5. Query LLM Provider (Gemini if configured, else FallbackAIProvider)
        repo_context = {
            "owner": owner,
            "repo": repo,
            "metadata": repo_metadata,
            "inspected_files": list(inspected_files.keys()),
            "sampled_code": {k: inspected_files[k][:2500] for k in list(inspected_files.keys())[:12]},
            "detected_technologies": sorted(list(detected_tech)),
            "demonstrated_skills": sorted(list(demonstrated_skills)),
            "purpose": purpose,
            "architecture_summary": arch_summary,
            "major_features": major_features[:5],
            "technical_strengths": strengths,
            "missing_requirements": missing_reqs,
            "recommendations": recommendations[:4],
        }

        model_metadata = {"provider": "deterministic-fallback", "version": "1.0.0"}
        from app.ai.factory import get_llm_provider
        try:
            llm = get_llm_provider()
            ai_result = llm.analyze_repository(repo_context)
            if ai_result and isinstance(ai_result, dict):
                for t in ai_result.get("detected_technologies", []):
                    detected_tech.add(t)
                for s in ai_result.get("demonstrated_skills", []):
                    demonstrated_skills.add(s)

                if ai_result.get("purpose"):
                    purpose = ai_result["purpose"]
                if ai_result.get("architecture_summary"):
                    arch_summary = ai_result["architecture_summary"]
                if ai_result.get("major_features"):
                    major_features = ai_result["major_features"]
                if ai_result.get("technical_strengths"):
                    strengths = ai_result["technical_strengths"]
                if ai_result.get("missing_requirements"):
                    missing_reqs = ai_result["missing_requirements"]
                if ai_result.get("recommendations"):
                    recommendations = ai_result["recommendations"]
                if ai_result.get("model_metadata"):
                    model_metadata = ai_result["model_metadata"]
        except Exception:
            pass

        final_result = {
            "accessible": True,
            "is_private": is_private,
            "owner": owner,
            "repo": repo,
            "purpose": purpose,
            "detected_technologies": sorted(list(detected_tech)),
            "architecture_summary": arch_summary,
            "demonstrated_skills": sorted(list(demonstrated_skills)),
            "major_features": major_features[:5],
            "technical_strengths": strengths,
            "missing_requirements": missing_reqs,
            "recommendations": recommendations[:4],
            "inspected_files": list(inspected_files.keys()),
            "model_metadata": model_metadata,
        }

        # Save to memory cache
        _REPO_ANALYSIS_CACHE[cache_key] = final_result
        return final_result


repo_inspector = RepositoryInspector()
