import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
email = f"feature1_{uuid.uuid4().hex[:6]}@kynetic.dev"

with httpx.Client(timeout=15.0) as client:
    # 1. Register user
    reg = client.post(f"{BASE}/auth/register", json={"email": email, "password": "Password123!", "display_name": "Resume Test"})
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    user_id = reg.json()["user"]["id"]
    cookies = reg.cookies

    # 2. Empty list
    res_list = client.get(f"{BASE}/resumes", cookies=cookies)
    assert res_list.status_code == 200 and len(res_list.json()) == 0, "Resumes not empty"

    # 3. Valid PDF with text
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
        b"(Maya Lin - Software Engineer - contact: mayalin@example.com) Tj\n"
        b"0 -20 Td (Education: BS Computer Science, Stanford University 2024) Tj\n"
        b"0 -20 Td (Experience: Backend Intern at CloudCorp, worked with Python, FastAPI, Docker, and PostgreSQL) Tj\n"
        b"0 -20 Td (Projects: Distributed Task Worker in React and TypeScript) Tj\n"
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
    files = {"file": ("resume_maya.pdf", pdf_content, "application/pdf")}
    up = client.post(f"{BASE}/resumes", files=files, cookies=cookies)
    assert up.status_code == 201, f"Upload failed: {up.text}"
    resume_data = up.json()
    resume_id = resume_data["id"]
    print(f"[OK] Uploaded resume {resume_id}")

    # 4. Trigger Analysis
    ana = client.post(f"{BASE}/resumes/{resume_id}/analyze", cookies=cookies)
    assert ana.status_code == 200, f"Analyze failed: {ana.text}"
    ana_data = ana.json()
    assert ana_data["status"] == "completed", f"Analysis status not completed: {ana_data}"
    ext = ana_data["extracted_profile"]
    skills = ext.get("claimed_skills", [])
    edu = ext.get("education", [])
    exp = ext.get("experience", [])
    print(f"[OK] Analysis completed: found {len(skills)} skills, {len(edu)} edu, {len(exp)} exp")
    assert len(skills) > 0, "No skills extracted"
    assert len(edu) > 0, "No education extracted"
    assert len(exp) > 0, "No experience extracted"

    # 5. Check Capabilities ingestion
    caps = client.get(f"{BASE}/capabilities", cookies=cookies)
    assert caps.status_code == 200
    caps_list = caps.json()
    assert len(caps_list) > 0, "No capabilities ingested from resume!"
    print(f"[OK] Capabilities created: {len(caps_list)} capabilities found in profile.")

    # 6. Check Persistence
    res_list2 = client.get(f"{BASE}/resumes", cookies=cookies)
    assert len(res_list2.json()) == 1
    assert res_list2.json()[0]["analysis"] is not None
    print(f"[OK] Persistence verified: resume has analysis attached.")

    # 7. Check Error Handling: Invalid file type
    bad_file = {"file": ("test.txt", b"not a pdf", "text/plain")}
    bad_up = client.post(f"{BASE}/resumes", files=bad_file, cookies=cookies)
    assert bad_up.status_code in [400, 422], f"Expected rejection of text/plain, got {bad_up.status_code}"
    print(f"[OK] Error handling verified: invalid mime rejected with {bad_up.status_code}")

    # 8. Delete Resume
    del_res = client.delete(f"{BASE}/resumes/{resume_id}", cookies=cookies)
    assert del_res.status_code == 200
    res_list3 = client.get(f"{BASE}/resumes", cookies=cookies)
    assert len(res_list3.json()) == 0
    print(f"[OK] Delete verified: resumes list now empty.")

print("=== FEATURE 1 ALL ACCEPTANCE CRITERIA VERIFIED ===")
