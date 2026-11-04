import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
email_a = f"feature4_a_{uuid.uuid4().hex[:6]}@kynetic.dev"
email_b = f"feature4_b_{uuid.uuid4().hex[:6]}@kynetic.dev"

with httpx.Client(timeout=15.0) as client:
    # 1. Register User A
    reg_a = client.post(f"{BASE}/auth/register", json={"email": email_a, "password": "Password123!", "display_name": "Placement User A"})
    assert reg_a.status_code == 201
    cookies_a = reg_a.cookies

    # 2. Upload valid resume with extractable skills (Python, FastAPI, React, Docker)
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
        b"(Alex Rivera - Software Engineer - contact: alex@example.com) Tj\n"
        b"0 -20 Td (Education: BS Computer Science, UC Berkeley 2024) Tj\n"
        b"0 -20 Td (Experience: Software Engineer at CloudCorp, worked with Python, FastAPI, and Docker) Tj\n"
        b"0 -20 Td (Projects: Web Platform in React and TypeScript) Tj\n"
        b"0 -20 Td (Technical Skills: Python, TypeScript, React, FastAPI, Docker) Tj\n"
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
    up = client.post(f"{BASE}/resumes", files={"file": ("alex.pdf", pdf_content, "application/pdf")}, cookies=cookies_a)
    assert up.status_code == 201
    res_id = up.json()["id"]
    ana = client.post(f"{BASE}/resumes/{res_id}/analyze", cookies=cookies_a)
    assert ana.status_code == 200

    # 3. Verify empty initial matches
    m_init = client.get(f"{BASE}/placement/matches", cookies=cookies_a)
    assert m_init.status_code == 200 and len(m_init.json()) == 0

    # 4. Evaluate Job Match: requires Python, FastAPI, Docker, and Golang
    role_title = "Backend Engineer - Platform"
    job_desc = "Seeking an experienced Backend Engineer skilled in Python, FastAPI, Docker, and Golang to scale microservices."
    m_create = client.post(
        f"{BASE}/placement/matches",
        json={"role_title": role_title, "job_description": job_desc},
        cookies=cookies_a,
    )
    assert m_create.status_code == 201, f"Failed to create job match: {m_create.text}"
    match_data = m_create.json()
    match_id = match_data["id"]
    score = match_data["estimated_score"]
    breakdown = match_data.get("match_breakdown", {})
    matched = breakdown.get("matched_skills", [])
    partial = breakdown.get("partial_skills", [])
    missing = breakdown.get("missing_skills", [])
    print(f"[OK] Job match created (ID: {match_id}): score={score}%, matched={len(matched)}, partial={len(partial)}, missing={len(missing)}")

    # Verify score is calculated realistically (Python, FastAPI, Docker should be partial claims, Golang missing)
    total_skills = len(matched) + len(partial) + len(missing)
    assert total_skills > 0, "No skills extracted from job description!"
    assert len(partial) > 0, "Expected partial claimed skills from resume!"
    assert len(missing) > 0, "Expected missing skill (Golang)!"
    print(f"[OK] Verified match calculation: {len(partial)} present claims, {len(missing)} missing gaps. Score: {score}%.")

    # 5. Verify Persistence
    m_list = client.get(f"{BASE}/placement/matches", cookies=cookies_a).json()
    assert len(m_list) == 1
    assert m_list[0]["id"] == match_id
    m_detail = client.get(f"{BASE}/placement/matches/{match_id}", cookies=cookies_a).json()
    assert m_detail["role_title"] == role_title
    print(f"[OK] Persistence verified: match successfully retrieved by ID.")

    # 6. Error handling: validation of job description min length 20
    bad_req = client.post(
        f"{BASE}/placement/matches",
        json={"role_title": "Short Role", "job_description": "too short"},
        cookies=cookies_a,
    )
    assert bad_req.status_code == 422, f"Expected 422 for short job description, got {bad_req.status_code}"
    print(f"[OK] Validation verified: short job description rejected with 422.")

    # 7. Cross-user isolation
    reg_b = client.post(f"{BASE}/auth/register", json={"email": email_b, "password": "Password123!", "display_name": "Placement User B"})
    cookies_b = reg_b.cookies
    cross_get = client.get(f"{BASE}/placement/matches/{match_id}", cookies=cookies_b)
    assert cross_get.status_code == 404, f"Expected 404 for cross-user placement match, got {cross_get.status_code}"
    print(f"[OK] Cross-user isolation verified: User B got 404 accessing User A's match.")

print("=== FEATURE 4 ALL ACCEPTANCE CRITERIA VERIFIED ===")
