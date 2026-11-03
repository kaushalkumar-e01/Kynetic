import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
user_email = f"journey_{uuid.uuid4().hex[:6]}@kynetic.dev"

print("=" * 60)
print("STARTING KYNETIC COMBINED FIVE-FEATURE USER JOURNEY TEST")
print("=" * 60)

with httpx.Client(timeout=20.0) as client:
    # ---------------------------------------------------------
    # STEP 1: Register and Log In
    # ---------------------------------------------------------
    print("\n[Step 1] Registering and authenticating unified user...")
    reg = client.post(
        f"{BASE}/auth/register",
        json={"email": user_email, "password": "Password123!", "display_name": "Elena Rostova"},
    )
    assert reg.status_code == 201, f"Registration failed: {reg.text}"
    user_id = reg.json()["user"]["id"]
    cookies = reg.cookies
    print(f" -> User registered successfully: ID {user_id}")

    # Verify /auth/me
    me = client.get(f"{BASE}/auth/me", cookies=cookies)
    assert me.status_code == 200
    assert me.json()["email"] == user_email.lower()
    print(" -> Auth session cookie verified via /auth/me")

    # ---------------------------------------------------------
    # STEP 2: Upload a Resume
    # ---------------------------------------------------------
    print("\n[Step 2] Uploading technical PDF resume (Feature 1)...")
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R>> endobj\n"
        b"4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"5 0 obj <</Length 280>> stream\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"100 700 Td\n"
        b"(Elena Rostova - Full Stack Engineer - email: elena@kynetic.dev) Tj\n"
        b"0 -20 Td (Education: BS Software Engineering, Carnegie Mellon 2024) Tj\n"
        b"0 -20 Td (Experience: Software Intern building REST services with Python, FastAPI, and Docker) Tj\n"
        b"0 -20 Td (Projects: High-performance caching engine using Redis and PostgreSQL) Tj\n"
        b"0 -20 Td (Technical Skills: Python, TypeScript, React, FastAPI, Docker, Redis, PostgreSQL) Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000058 00000 n\n"
        b"0000000115 00000 n\n"
        b"0000000230 00000 n\n"
        b"0000000302 00000 n\n"
        b"trailer <</Size 6 /Root 1 0 R>>\n"
        b"startxref\n"
        b"630\n"
        b"%%EOF\n"
    )
    up = client.post(f"{BASE}/resumes", files={"file": ("elena_resume.pdf", pdf_content, "application/pdf")}, cookies=cookies)
    assert up.status_code == 201, f"Resume upload failed: {up.text}"
    resume_id = up.json()["id"]
    print(f" -> Resume uploaded: ID {resume_id}")

    # ---------------------------------------------------------
    # STEP 3: Verify Extracted Skills and Capabilities
    # ---------------------------------------------------------
    print("\n[Step 3] Analyzing resume and verifying capability ingestion...")
    ana = client.post(f"{BASE}/resumes/{resume_id}/analyze", cookies=cookies)
    assert ana.status_code == 200, f"Resume analyze failed: {ana.text}"
    ana_data = ana.json()
    claimed = ana_data["extracted_profile"]["claimed_skills"]
    print(f" -> AI extraction complete: {len(claimed)} skills detected ({', '.join(s['name'] for s in claimed[:4])}...)")

    caps = client.get(f"{BASE}/capabilities", cookies=cookies).json()
    assert len(caps) >= 5, f"Expected at least 5 ingested capabilities, got {len(caps)}"
    print(f" -> Capability profile verified: {len(caps)} initial claimed capabilities registered")

    # ---------------------------------------------------------
    # STEP 4: Complete a Skill Assessment
    # ---------------------------------------------------------
    print("\n[Step 4] Starting and completing a skill assessment (Feature 2)...")
    topics = client.get(f"{BASE}/assessment-topics", cookies=cookies).json()
    assert len(topics) > 0
    selected_topic = topics[0]["name"]

    ass = client.post(
        f"{BASE}/assessments",
        json={"mode": "quiz", "selected_topics": [selected_topic], "title": f"{selected_topic} Knowledge Check"},
        cookies=cookies,
    ).json()
    ass_id = ass["id"]
    q1 = ass["current_question"]
    assert q1 is not None

    # Submit answer
    opts = q1.get("options", [])
    ans = "False" if "False" in opts else opts[0]
    att = client.post(
        f"{BASE}/assessments/{ass_id}/answers",
        json={"question_id": q1["id"], "answer": ans},
        cookies=cookies,
    ).json()
    print(f" -> Question 1 evaluated: is_correct={att['is_correct']}, score={att['score']}")

    # Get results & complete
    res = client.get(f"{BASE}/assessments/{ass_id}/results", cookies=cookies).json()
    assert res["status"] == "completed"
    print(f" -> Assessment completed with score: {res['average_score']}%")

    # ---------------------------------------------------------
    # STEP 5: Create and Analyze a Project
    # ---------------------------------------------------------
    print("\n[Step 5] Creating and analyzing a practical project (Feature 3)...")
    proj = client.post(
        f"{BASE}/projects",
        json={
            "name": "Kynetic Realtime Analytics Service",
            "description": "High throughput telemetry processor built using Python, FastAPI, Docker, and Redis.",
            "source_type": "github",
            "repository_url": "https://github.com/elena/kynetic-analytics",
        },
        cookies=cookies,
    ).json()
    proj_id = proj["id"]
    print(f" -> Project created: '{proj['name']}' (ID: {proj_id})")

    p_ana = client.post(f"{BASE}/projects/{proj_id}/analyze", cookies=cookies).json()
    assert p_ana["status"] == "completed"
    assert len(p_ana["detected_technologies"]) > 0
    print(f" -> Project analyzed: detected techs={p_ana['detected_technologies']}")

    # ---------------------------------------------------------
    # STEP 6: Enter Job Description and Generate Placement Match
    # ---------------------------------------------------------
    print("\n[Step 6] Running placement matcher against career opportunity (Feature 4)...")
    match_job_desc = (
        "We are looking for a Senior Software Engineer with strong experience in "
        "Python, FastAPI, Docker, Kubernetes, and PostgreSQL to design robust APIs."
    )
    match_res = client.post(
        f"{BASE}/placement/matches",
        json={
            "role_title": "Senior Software Engineer - Cloud Platform",
            "job_description": match_job_desc,
        },
        cookies=cookies,
    ).json()
    match_id = match_res["id"]
    score = match_res["estimated_score"]
    bd = match_res["match_breakdown"]
    print(f" -> Placement match calculated: {score}% alignment score")
    print(f"    (Matched: {bd['matched_count']}, Partial/Claimed: {bd['partial_count']}, Missing: {bd['missing_count']})")
    assert score > 0.0, "Score should reflect user's real capabilities!"

    # ---------------------------------------------------------
    # STEP 7: Create a Career Goal
    # ---------------------------------------------------------
    print("\n[Step 7] Setting a targeted career goal (Feature 5)...")
    goal = client.post(
        f"{BASE}/goals",
        json={
            "title": "Lead Backend Platform Engineer",
            "goal_type": "placement",
            "description": "Transition to platform leadership by demonstrating advanced distributed systems mastery.",
            "target_date": "2026-12-31",
        },
        cookies=cookies,
    ).json()
    goal_id = goal["id"]
    print(f" -> Career Goal created: '{goal['title']}' (ID: {goal_id})")

    # ---------------------------------------------------------
    # STEP 8: Generate a Personalized Learning Roadmap
    # ---------------------------------------------------------
    print("\n[Step 8] Generating personalized capability roadmap...")
    rm = client.post(
        f"{BASE}/roadmaps",
        json={
            "title": "Distributed Cloud Systems Roadmap",
            "description": "Sequential capability progression toward Lead Backend Platform Engineer.",
            "goal_id": goal_id,
            "target_skills": ["Python", "FastAPI", "Docker", "Kubernetes"],
        },
        cookies=cookies,
    ).json()
    rm_id = rm["id"]
    milestones = rm["milestones"]
    assert len(milestones) == 5
    print(f" -> Roadmap generated with {len(milestones)} milestones. Initial progress: {rm['progress_percentage']}%")

    # ---------------------------------------------------------
    # STEP 9: Complete a Milestone
    # ---------------------------------------------------------
    print("\n[Step 9] Completing roadmap milestone 1...")
    m1 = milestones[0]
    client.patch(
        f"{BASE}/roadmaps/{rm_id}/milestones/{m1['id']}",
        json={"status": "completed"},
        cookies=cookies,
    )
    rm_check = client.get(f"{BASE}/roadmaps/{rm_id}", cookies=cookies).json()
    assert rm_check["progress_percentage"] == 20.0
    print(f" -> Milestone marked completed. Progress dynamically recalculated to: {rm_check['progress_percentage']}%")

    # ---------------------------------------------------------
    # STEP 10: Refresh the Application & Verify Full Persistence
    # ---------------------------------------------------------
    print("\n[Step 10] Simulating application refresh and verifying cross-domain data persistence...")
    # 1. Resume & Analysis
    resumes_refetch = client.get(f"{BASE}/resumes", cookies=cookies).json()
    assert len(resumes_refetch) == 1
    assert resumes_refetch[0]["analysis"] is not None
    print(" -> [VERIFIED] Resume and AI extraction persisted.")

    # 2. Capabilities Profile
    caps_refetch = client.get(f"{BASE}/capabilities", cookies=cookies).json()
    assert len(caps_refetch) >= 5
    print(f" -> [VERIFIED] Capability profile with {len(caps_refetch)} skills persisted.")

    # 3. Assessment History
    ass_refetch = client.get(f"{BASE}/assessments", cookies=cookies).json()
    assert len(ass_refetch) == 1
    assert ass_refetch[0]["status"] == "completed"
    print(" -> [VERIFIED] Skill assessment record persisted.")

    # 4. Project & Analysis
    proj_refetch = client.get(f"{BASE}/projects", cookies=cookies).json()
    assert len(proj_refetch) == 1
    assert proj_refetch[0]["latest_analysis"] is not None
    print(" -> [VERIFIED] Project and technical insights persisted.")

    # 5. Placement Match
    match_refetch = client.get(f"{BASE}/placement/matches", cookies=cookies).json()
    assert len(match_refetch) == 1
    assert match_refetch[0]["id"] == match_id
    print(" -> [VERIFIED] Placement evaluation breakdown persisted.")

    # 6. Goals
    goals_refetch = client.get(f"{BASE}/goals", cookies=cookies).json()
    assert len(goals_refetch) == 1
    assert goals_refetch[0]["title"] == "Lead Backend Platform Engineer"
    print(" -> [VERIFIED] Career goal persisted.")

    # 7. Roadmap & Progress
    rm_refetch = client.get(f"{BASE}/roadmaps", cookies=cookies).json()
    assert len(rm_refetch) == 1
    assert rm_refetch[0]["progress_percentage"] == 20.0
    print(" -> [VERIFIED] Roadmap milestones and 20.0% progress persisted.")

print("\n" + "=" * 60)
print("SUCCESS: ALL FIVE MANDATORY FEATURES VERIFIED END-TO-END!")
print("=" * 60)
