"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Check, Goal, Loader2, Plus, Trash2 } from "lucide-react";
import { goalsApi } from "@/lib/api";
import type { GoalResponse } from "@/types";

export default function GoalsView() {
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [goalType, setGoalType] = useState("placement");
  const [description, setDescription] = useState("");
  const [targetDate, setTargetDate] = useState("");

  const loadGoals = () => {
    setLoading(true);
    goalsApi
      .listGoals()
      .then((data) => {
        setGoals(data);
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load goals.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await goalsApi.createGoal({
        title: title.trim(),
        goal_type: goalType,
        description: description.trim() || undefined,
        target_date: targetDate || undefined,
      });

      setStatusMessage("Career goal created successfully.");
      setTitle("");
      setDescription("");
      setTargetDate("");
      setShowAdd(false);
      loadGoals();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to create goal.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (goalId: string) => {
    if (!confirm("Are you sure you want to delete this goal?")) return;
    try {
      await goalsApi.deleteGoal(goalId);
      setStatusMessage("Goal deleted.");
      setGoals((prev) => prev.filter((g) => g.id !== goalId));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to delete goal.");
      }
    }
  };

  return (
    <div>
      {statusMessage && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            background: "rgba(0, 209, 178, 0.12)",
            border: "1px solid rgba(0, 209, 178, 0.35)",
            borderRadius: 8,
            color: "var(--teal)",
            fontSize: 12,
            marginBottom: 16,
          }}
        >
          <Check size={15} />
          <span>{statusMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            background: "rgba(255, 107, 107, 0.12)",
            border: "1px solid rgba(255, 107, 107, 0.35)",
            borderRadius: 8,
            color: "#ff8787",
            fontSize: 12,
            marginBottom: 16,
          }}
        >
          <AlertCircle size={15} />
          <span>{errorMessage}</span>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 18, margin: 0 }}>Career & Capability Goals</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Set direction without rigid sequences. Kynetic connects roadmaps and placement matching to your goals.
          </p>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary" style={{ fontSize: 12 }}>
          <Plus size={14} /> {showAdd ? "Cancel" : "Add Goal"}
        </button>
      </div>

      {showAdd && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Direction</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Create New Goal
          </div>
          <form onSubmit={handleCreate}>
            <div className="grid-2">
              <div className="field">
                <label htmlFor="goalTitle">Goal Title</label>
                <input
                  id="goalTitle"
                  className="input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Target Frontend Engineer Internship"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="goalType">Goal Type</label>
                <select
                  id="goalType"
                  className="input"
                  value={goalType}
                  onChange={(e) => setGoalType(e.target.value)}
                >
                  <option value="placement">Placement / Job Seeking</option>
                  <option value="learning">Skill & Learning Mastery</option>
                  <option value="project">Project Execution</option>
                </select>
              </div>
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="goalDesc">Description & Motivation</label>
              <textarea
                id="goalDesc"
                className="input"
                style={{ minHeight: 60, resize: "vertical" }}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What capabilities do you want to demonstrate for this goal?"
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="targetDate">Target Date (Optional)</label>
              <input
                id="targetDate"
                type="date"
                className="input"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: 16 }} disabled={submitting}>
              {submitting ? <Loader2 size={13} className="animate-spin" /> : <Plus size={13} />}
              Save Goal
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : goals.length === 0 ? (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <Goal size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No goals defined yet</div>
          <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            Add a career or learning goal to give direction to your roadmaps and capability milestones.
          </p>
        </div>
      ) : (
        <div className="grid-2">
          {goals.map((g) => (
            <div className="card card-pad" key={g.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 700,
                      textTransform: "uppercase",
                      padding: "3px 7px",
                      borderRadius: 4,
                      background: "var(--accent-soft)",
                      color: "var(--accent)",
                    }}
                  >
                    {g.goal_type}
                  </span>
                  <h3 style={{ fontSize: 15, margin: "10px 0 6px" }}>{g.title}</h3>
                </div>
                <button
                  onClick={() => handleDelete(g.id)}
                  className="icon-btn"
                  title="Delete goal"
                  aria-label="Delete goal"
                >
                  <Trash2 size={14} color="#ff8787" />
                </button>
              </div>

              {g.description && (
                <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, minHeight: 36, marginTop: 6 }}>
                  {g.description}
                </p>
              )}

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: 16,
                  paddingTop: 12,
                  borderTop: "1px solid var(--line)",
                  fontSize: 11,
                }}
              >
                <span className="muted">Status: <strong style={{ color: "var(--teal)" }}>{g.status}</strong></span>
                {g.target_date && (
                  <span className="muted">Target: {new Date(g.target_date).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
