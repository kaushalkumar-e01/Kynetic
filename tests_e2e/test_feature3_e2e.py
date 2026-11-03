import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
email_a = f"feature3_a_{uuid.uuid4().hex[:6]}@kynetic.dev"
email_b = f"feature3_b_{uuid.uuid4().hex[:6]}@kynetic.dev"

with httpx.Client(timeout=15.0) as client:
    # 1. Register User A
    reg_a = client.post(f"{BASE}/auth/register", json={"email": email_a, "password": "Password123!", "display_name": "Project User A"})
    assert reg_a.status_code == 201
    cookies_a = reg_a.cookies

    # 2. Verify empty projects list
    p_init = client.get(f"{BASE}/projects", cookies=cookies_a)
    assert p_init.status_code == 200 and len(p_init.json()) == 0

    # 3. Create Project
    p_create = client.post(
        f"{BASE}/projects",
        json={
            "name": "Cloud Native Task Worker",
            "description": "High-throughput task orchestrator written in Python, FastAPI, Docker, Redis, and React frontend.",
            "source_type": "manual",
            "repository_url": "https://github.com/developer/cloud-worker",
        },
        cookies=cookies_a,
    )
    assert p_create.status_code == 201
    proj = p_create.json()
    proj_id = proj["id"]
    print(f"[OK] Created project '{proj['name']}' (ID: {proj_id})")

    # 4. Trigger Analysis
    ana_resp = client.post(f"{BASE}/projects/{proj_id}/analyze", cookies=cookies_a)
    assert ana_resp.status_code == 200
    analysis = ana_resp.json()
    assert analysis["status"] == "completed"
    techs = analysis.get("detected_technologies", [])
    skills = analysis.get("demonstrated_skills", [])
    recs = analysis.get("recommendations", [])
    print(f"[OK] Analysis complete: Detected Techs={techs}, Demonstrated Skills={skills}, Recs Count={len(recs)}")
    assert len(techs) > 0, "No technologies detected!"
    assert len(skills) > 0, "No skills demonstrated!"

    # 5. Check Capabilities Ingestion
    caps = client.get(f"{BASE}/capabilities", cookies=cookies_a).json()
    assert len(caps) > 0, "No capabilities updated from project evidence!"
    print(f"[OK] Capabilities verified: {len(caps)} capabilities associated with project evidence.")

    # 6. Update Project (Edit)
    upd_resp = client.patch(
        f"{BASE}/projects/{proj_id}",
        json={
            "name": "Cloud Native Task Worker v2",
            "description": "Updated description with enhanced microservice architecture.",
        },
        cookies=cookies_a,
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["name"] == "Cloud Native Task Worker v2"
    print(f"[OK] Updated project name to '{upd_resp.json()['name']}'")

    # 7. Verify Persistence
    p_fetch = client.get(f"{BASE}/projects/{proj_id}", cookies=cookies_a)
    assert p_fetch.status_code == 200
    assert p_fetch.json()["name"] == "Cloud Native Task Worker v2"
    assert p_fetch.json()["latest_analysis"] is not None
    print(f"[OK] Persistence verified: updated title and latest analysis attached.")

    # 8. Cross-User Isolation
    reg_b = client.post(f"{BASE}/auth/register", json={"email": email_b, "password": "Password123!", "display_name": "Project User B"})
    cookies_b = reg_b.cookies
    cross_access = client.get(f"{BASE}/projects/{proj_id}", cookies=cookies_b)
    assert cross_access.status_code == 404, f"Expected 404 for cross-user project, got {cross_access.status_code}"
    cross_edit = client.patch(f"{BASE}/projects/{proj_id}", json={"name": "Hacked"}, cookies=cookies_b)
    assert cross_edit.status_code == 404
    print(f"[OK] Cross-user isolation verified: User B cannot access or modify User A's project.")

    # 9. Delete Project
    del_p = client.delete(f"{BASE}/projects/{proj_id}", cookies=cookies_a)
    assert del_p.status_code == 200
    p_final = client.get(f"{BASE}/projects", cookies=cookies_a)
    assert len(p_final.json()) == 0
    print(f"[OK] Project deleted: projects list now empty.")

print("=== FEATURE 3 ALL ACCEPTANCE CRITERIA VERIFIED ===")
