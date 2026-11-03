import httpx
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
email_a = f"feature2_a_{uuid.uuid4().hex[:6]}@kynetic.dev"
email_b = f"feature2_b_{uuid.uuid4().hex[:6]}@kynetic.dev"

with httpx.Client(timeout=15.0) as client:
    # 1. Register User A
    reg_a = client.post(f"{BASE}/auth/register", json={"email": email_a, "password": "Password123!", "display_name": "Quiz User A"})
    assert reg_a.status_code == 201
    cookies_a = reg_a.cookies

    # 2. List Topics
    top_resp = client.get(f"{BASE}/assessment-topics", cookies=cookies_a)
    assert top_resp.status_code == 200
    topics = top_resp.json()
    assert len(topics) > 0, "No topics returned!"
    topic_name = topics[0]["name"]
    print(f"[OK] Fetched {len(topics)} topics. Selected: '{topic_name}'")

    # 3. Create Assessment
    ass_resp = client.post(
        f"{BASE}/assessments",
        json={"mode": "quiz", "selected_topics": [topic_name], "title": f"{topic_name} Test"},
        cookies=cookies_a,
    )
    assert ass_resp.status_code == 201
    ass_data = ass_resp.json()
    ass_id = ass_data["id"]
    curr_q = ass_data.get("current_question")
    assert curr_q is not None, "No initial question returned!"
    print(f"[OK] Created assessment {ass_id}. Q1 prompt: {curr_q['prompt'][:40]}...")

    # 4. Submit Answer for Q1
    q1_id = curr_q["id"]
    # If Python Programming Q1: "What is the output of `bool([])` in Python?", correct is "False"
    options = curr_q.get("options", [])
    ans = "False" if "False" in options else options[0]
    ans_resp = client.post(
        f"{BASE}/assessments/{ass_id}/answers",
        json={"question_id": q1_id, "answer": ans},
        cookies=cookies_a,
    )
    assert ans_resp.status_code == 200
    att1 = ans_resp.json()
    print(f"[OK] Submitted Q1 answer '{ans}'. is_correct={att1['is_correct']}, score={att1['score']}")

    # 5. Fetch next adaptive question
    next_resp = client.get(f"{BASE}/assessments/{ass_id}", cookies=cookies_a)
    assert next_resp.status_code == 200
    q2 = next_resp.json().get("current_question")
    if q2:
        q2_options = q2.get("options", [])
        q2_ans = q2_options[0] if q2_options else "test"
        ans_resp2 = client.post(
            f"{BASE}/assessments/{ass_id}/answers",
            json={"question_id": q2["id"], "answer": q2_ans},
            cookies=cookies_a,
        )
        assert ans_resp2.status_code == 200
        print(f"[OK] Submitted Q2 answer. is_correct={ans_resp2.json()['is_correct']}")

    # 6. Complete and get summary results
    res_resp = client.get(f"{BASE}/assessments/{ass_id}/results", cookies=cookies_a)
    assert res_resp.status_code == 200
    summary = res_resp.json()
    assert summary["status"] == "completed"
    assert summary["total_questions"] >= 1
    print(f"[OK] Completed assessment: total={summary['total_questions']}, correct={summary['correct_answers']}, avg_score={summary['average_score']}%")

    # 7. Verify capability evidence
    caps = client.get(f"{BASE}/capabilities", cookies=cookies_a).json()
    assert len(caps) > 0, "No capabilities recorded from assessment!"
    print(f"[OK] Capabilities verified: {len(caps)} capabilities updated with assessed signals.")

    # 8. Verify history persistence
    hist = client.get(f"{BASE}/assessments", cookies=cookies_a).json()
    assert len(hist) >= 1
    assert hist[0]["id"] == ass_id
    assert hist[0]["status"] == "completed"
    print(f"[OK] History persistence verified: found {len(hist)} past assessments.")

    # 9. Error handling: User B cross-access test
    reg_b = client.post(f"{BASE}/auth/register", json={"email": email_b, "password": "Password123!", "display_name": "Quiz User B"})
    cookies_b = reg_b.cookies
    cross_access = client.get(f"{BASE}/assessments/{ass_id}", cookies=cookies_b)
    assert cross_access.status_code == 404, f"Expected 404 for cross-user access, got {cross_access.status_code}"
    print(f"[OK] Cross-user isolation verified: User B got 404 accessing User A assessment.")

    # Non-existent question ID test
    bad_q = client.post(
        f"{BASE}/assessments/{ass_id}/answers",
        json={"question_id": "non-existent-id", "answer": "True"},
        cookies=cookies_a,
    )
    assert bad_q.status_code == 404
    print(f"[OK] Non-existent question rejected with 404.")

print("=== FEATURE 2 ALL ACCEPTANCE CRITERIA VERIFIED ===")
