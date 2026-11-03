import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
test_email = f"intel_test_{uuid.uuid4().hex[:6]}@kynetic.dev"

print("============================================================")
print("TESTING KYNETIC CORE INTELLIGENCE UPGRADES")
print("============================================================")

with httpx.Client(timeout=30.0) as client:
    # 1. Register test user
    reg = client.post(f"{BASE}/auth/register", json={"email": test_email, "password": "Password123!", "display_name": "Intel Tester"})
    assert reg.status_code == 201
    cookies = reg.cookies
    print("[Step 1] Registered and authenticated user.")

    # 2. Test Real Project Intelligence with Repository Code Inspection
    p_create = client.post(
        f"{BASE}/projects",
        json={
            "name": "Kynetic Platform",
            "source_type": "github",
            "repository_url": "https://github.com/kaushalkumar-e01/Kynetic",
            "technologies": ["FastAPI", "Next.js", "TypeScript", "PostgreSQL"],
        },
        cookies=cookies,
    )
    assert p_create.status_code == 201
    proj = p_create.json()
    proj_id = proj["id"]
    print(f"[Step 2] Registered project with GitHub repository: '{proj['repository_url']}'")

    # Analyze project
    p_analyze = client.post(f"{BASE}/projects/{proj_id}/analyze", cookies=cookies)
    assert p_analyze.status_code == 200
    analysis = p_analyze.json()

    # Verify actual repository inspection
    assert len(analysis["detected_technologies"]) >= 4, "Should detect multiple technologies"
    assert "FastAPI" in analysis["detected_technologies"]
    assert "Next.js" in analysis["detected_technologies"]
    assert "TypeScript" in analysis["detected_technologies"]

    # Verify computed schema properties from source_snapshot
    assert len(analysis["major_features"]) > 0, "Should extract key features"
    assert len(analysis["technical_strengths"]) > 0, "Should identify technical strengths"
    assert len(analysis["inspected_files"]) > 0, "Should list inspected repository files"
    print(f"[Step 2b] Code Inspection Verified: Inspected files={analysis['inspected_files']}")
    print(f" -> Major Features Extracted: {analysis['major_features'][:2]}")
    print(f" -> Technical Strengths Identified: {analysis['technical_strengths'][:2]}")

    # Verify capabilities were ingested with verified status
    caps_resp = client.get(f"{BASE}/capabilities", cookies=cookies)
    assert caps_resp.status_code == 200
    caps = caps_resp.json()
    assert len(caps) >= 4, "Demonstrated skills should be ingested into capability profile"
    print(f"[Step 2c] Capability profile updated with {len(caps)} verified skills from repository inspection.")

    # 3. Test Weighted Placement Matching with Mandatory vs Preferred Breakdown
    job_desc = """
    We are seeking a Senior Full Stack Engineer to lead our core products team.

    Minimum Requirements & Qualifications:
    - 3+ years of experience with Python, FastAPI, and TypeScript.
    - Deep knowledge of PostgreSQL database modeling and query optimization.
    - Proven experience with Docker containerization in Linux environments.

    Preferred Qualifications (Nice to Have):
    - Experience with Kubernetes orchestration.
    - Familiarity with Next.js frontend architecture and Tailwind CSS.
    - Experience with Redis caching mechanisms.
    """
    match_resp = client.post(
        f"{BASE}/placement/matches",
        json={
            "role_title": "Senior Full Stack Engineer",
            "job_description": job_desc,
        },
        cookies=cookies,
    )
    assert match_resp.status_code == 201
    match = match_resp.json()

    assert match["estimated_score"] > 0.0
    breakdown = match["match_breakdown"]
    assert "matched_skills" in breakdown
    assert "partial_skills" in breakdown
    assert "missing_skills" in breakdown
    assert "action_plan" in breakdown
    assert len(breakdown["action_plan"]) > 0, "Should provide actionable recommendations for gaps"

    # Verify provenance and requirement_type on skills
    all_breakdown_items = breakdown["matched_skills"] + breakdown["partial_skills"] + breakdown["missing_skills"]
    assert any(item.get("requirement_type") == "mandatory" for item in all_breakdown_items)
    assert any(item.get("requirement_type") == "preferred" for item in all_breakdown_items)
    assert any("Verified:" in (item.get("provenance") or "") for item in breakdown["matched_skills"])
    print(f"[Step 3] Weighted Placement Match Verified: Score={match['estimated_score']}%")
    print(f" -> Action Plan: {breakdown['action_plan'][:2]}")

    # 4. Test Differentiated Career Roadmaps
    # Create Frontend Roadmap
    fe_roadmap_resp = client.post(
        f"{BASE}/roadmaps",
        json={
            "title": "Frontend Web Engineer Path",
            "description": "Master Modern Frontend Architecture",
            "target_skills": ["TypeScript", "React", "Next.js", "Tailwind CSS"],
        },
        cookies=cookies,
    )
    assert fe_roadmap_resp.status_code == 201
    fe_roadmap = fe_roadmap_resp.json()
    assert len(fe_roadmap["milestones"]) == 5  # 4 skills + 1 capstone

    # Verify structured learning objectives & docs
    m1_resources = fe_roadmap["milestones"][0]["resources"]
    assert any(r.get("type") == "documentation" for r in m1_resources)
    assert any(r.get("type") == "learning_objectives" for r in m1_resources)
    print(f"[Step 4] Differentiated Roadmap Verified: Generated {len(fe_roadmap['milestones'])} sequenced milestones with rich documentation links and learning objectives.")

print("============================================================")
print("SUCCESS: CORE INTELLIGENCE UPGRADES FULLY VERIFIED!")
print("============================================================")
