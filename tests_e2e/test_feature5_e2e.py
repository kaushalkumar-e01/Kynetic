import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
email_a = f"feature5_a_{uuid.uuid4().hex[:6]}@kynetic.dev"
email_b = f"feature5_b_{uuid.uuid4().hex[:6]}@kynetic.dev"

with httpx.Client(timeout=15.0) as client:
    # 1. Register User A
    reg_a = client.post(f"{BASE}/auth/register", json={"email": email_a, "password": "Password123!", "display_name": "Roadmap User A"})
    assert reg_a.status_code == 201
    cookies_a = reg_a.cookies

    # 2. Create Career Goal
    g_create = client.post(
        f"{BASE}/goals",
        json={
            "title": "Become Senior Cloud Engineer",
            "goal_type": "placement",
            "description": "Master distributed systems, Kubernetes, and FastAPI microservices.",
            "target_date": "2027-01-01",
        },
        cookies=cookies_a,
    )
    assert g_create.status_code == 201, f"Failed to create goal: {g_create.text}"
    goal = g_create.json()
    goal_id = goal["id"]
    print(f"[OK] Created Goal '{goal['title']}' (ID: {goal_id})")

    # 3. Edit Goal
    g_patch = client.patch(
        f"{BASE}/goals/{goal_id}",
        json={"title": "Become Lead Cloud Engineer", "status": "active"},
        cookies=cookies_a,
    )
    assert g_patch.status_code == 200
    assert g_patch.json()["title"] == "Become Lead Cloud Engineer"
    print(f"[OK] Edited Goal title: '{g_patch.json()['title']}'")

    # 4. Generate Roadmap linked to Goal
    rm_create = client.post(
        f"{BASE}/roadmaps",
        json={
            "title": "Lead Cloud Architecture Roadmap",
            "description": "Targeted milestones for scalable cloud systems.",
            "goal_id": goal_id,
            "target_skills": ["Python", "Docker", "Kubernetes", "PostgreSQL"],
        },
        cookies=cookies_a,
    )
    assert rm_create.status_code == 201, f"Failed to create roadmap: {rm_create.text}"
    rm = rm_create.json()
    rm_id = rm["id"]
    milestones = rm.get("milestones", [])
    assert len(milestones) == 5, f"Expected 5 milestones (4 skills + 1 capstone), got {len(milestones)}"
    initial_progress = rm.get("progress_percentage", 0)
    print(f"[OK] Generated Roadmap '{rm['title']}' with {len(milestones)} sequenced milestones. Initial progress: {initial_progress}%")

    # 5. Complete Milestone 1
    m1 = milestones[0]
    m1_id = m1["id"]
    m_patch = client.patch(
        f"{BASE}/roadmaps/{rm_id}/milestones/{m1_id}",
        json={"status": "completed"},
        cookies=cookies_a,
    )
    assert m_patch.status_code == 200
    assert m_patch.json()["status"] == "completed"
    print(f"[OK] Completed Milestone 1: '{m1['title']}'")

    # 6. Verify Progress Calculation
    rm_updated = client.get(f"{BASE}/roadmaps/{rm_id}", cookies=cookies_a).json()
    new_progress = rm_updated.get("progress_percentage", 0)
    expected_progress = round(1 / len(milestones) * 100.0, 1) # 20.0%
    assert new_progress == expected_progress, f"Expected {expected_progress}%, got {new_progress}%"
    print(f"[OK] Progress calculation verified: updated from {initial_progress}% to {new_progress}%.")

    # 7. Complete Milestone 2
    m2 = milestones[1]
    client.patch(
        f"{BASE}/roadmaps/{rm_id}/milestones/{m2['id']}",
        json={"status": "completed"},
        cookies=cookies_a,
    )
    rm_updated2 = client.get(f"{BASE}/roadmaps/{rm_id}", cookies=cookies_a).json()
    new_progress2 = rm_updated2.get("progress_percentage", 0)
    expected_progress2 = round(2 / len(milestones) * 100.0, 1) # 40.0%
    assert new_progress2 == expected_progress2, f"Expected {expected_progress2}%, got {new_progress2}%"
    print(f"[OK] Progress calculation verified after 2nd milestone: now {new_progress2}%.")

    # 8. Persistence Verification (simulating page reload)
    rm_list = client.get(f"{BASE}/roadmaps", cookies=cookies_a).json()
    assert len(rm_list) == 1
    assert rm_list[0]["progress_percentage"] == new_progress2
    g_list = client.get(f"{BASE}/goals", cookies=cookies_a).json()
    assert len(g_list) == 1
    assert g_list[0]["title"] == "Become Lead Cloud Engineer"
    print(f"[OK] Persistence verified: Goals and Roadmaps retained on re-fetch.")

    # 9. Cross-User Isolation
    reg_b = client.post(f"{BASE}/auth/register", json={"email": email_b, "password": "Password123!", "display_name": "Roadmap User B"})
    cookies_b = reg_b.cookies
    cross_goal = client.get(f"{BASE}/goals/{goal_id}", cookies=cookies_b)
    assert cross_goal.status_code == 404, f"Expected 404, got {cross_goal.status_code}"
    cross_rm = client.get(f"{BASE}/roadmaps/{rm_id}", cookies=cookies_b)
    assert cross_rm.status_code == 404, f"Expected 404, got {cross_rm.status_code}"
    print(f"[OK] Cross-user isolation verified: User B received 404 for User A goals & roadmaps.")

    # 10. Clean Delete
    del_rm = client.delete(f"{BASE}/roadmaps/{rm_id}", cookies=cookies_a)
    assert del_rm.status_code == 200
    del_g = client.delete(f"{BASE}/goals/{goal_id}", cookies=cookies_a)
    assert del_g.status_code == 200
    assert len(client.get(f"{BASE}/roadmaps", cookies=cookies_a).json()) == 0
    assert len(client.get(f"{BASE}/goals", cookies=cookies_a).json()) == 0
    print(f"[OK] Delete verified: roadmaps and goals cleaned up successfully.")

print("=== FEATURE 5 ALL ACCEPTANCE CRITERIA VERIFIED ===")
