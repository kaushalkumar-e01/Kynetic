"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  Check,
  CheckCircle2,
  Circle,
  Edit2,
  Goal,
  Loader2,
  MapPin,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { goalsApi, roadmapsApi } from "@/lib/api";
import type { GoalResponse } from "@/types";
import RoleSelect from "@/components/ui/RoleSelect";

export default function GoalsView() {
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [generatingRoadmapId, setGeneratingRoadmapId] = useState<string | null>(null);

  // New goal state
  const [title, setTitle] = useState("");
  const [goalType, setGoalType] = useState("placement");
  const [description, setDescription] = useState("");
  const [targetDate, setTargetDate] = useState("");

  // Edit goal state
  const [editingGoal, setEditingGoal] = useState<GoalResponse | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editTargetDate, setEditTargetDate] = useState("");
  const [editStatus, setEditStatus] = useState("active");
  const [updating, setUpdating] = useState(false);

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

      setStatusMessage(`Career goal "${title}" created successfully.`);
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

  const handleStartEdit = (g: GoalResponse) => {
    setEditingGoal(g);
    setEditTitle(g.title);
    setEditDescription(g.description || "");
    setEditTargetDate(g.target_date || "");
    setEditStatus(g.status || "active");
    setErrorMessage(null);
    setStatusMessage(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingGoal || !editTitle.trim()) return;

    setUpdating(true);
    setErrorMessage(null);

    try {
      const updated = await goalsApi.updateGoal(editingGoal.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
        target_date: editTargetDate || undefined,
        status: editStatus,
      });

      setStatusMessage(`Goal "${updated.title}" updated successfully.`);
      setEditingGoal(null);
      loadGoals();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to update goal.");
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleToggleStatus = async (goal: GoalResponse) => {
    const nextStatus = goal.status === "completed" ? "active" : "completed";
    try {
      await goalsApi.updateGoal(goal.id, { status: nextStatus });
      setGoals((prev) =>
        prev.map((g) => (g.id === goal.id ? { ...g, status: nextStatus } : g))
      );
      setStatusMessage(`Goal marked as ${nextStatus}.`);
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  const handleGenerateRoadmapForGoal = async (goal: GoalResponse) => {
    setGeneratingRoadmapId(goal.id);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await roadmapsApi.createRoadmap({
        title: `${goal.title} Roadmap`,
        description: goal.description || `Milestone roadmap targeted towards ${goal.title}`,
        goal_id: goal.id,
      });
      setStatusMessage(`Roadmap created for goal "${goal.title}"! Open Roadmaps view to track your milestones.`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to generate roadmap.");
      }
    } finally {
      setGeneratingRoadmapId(null);
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

      {/* Edit Goal Form */}
      {editingGoal && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "2px solid var(--accent)", background: "var(--surface)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Edit Goal</div>
              <h3 style={{ margin: "4px 0", fontSize: 16 }}>Update &ldquo;{editingGoal.title}&rdquo;</h3>
            </div>
            <button onClick={() => setEditingGoal(null)} className="icon-btn" title="Cancel edit">
              <X size={16} />
            </button>
          </div>
          <form onSubmit={handleSaveEdit}>
            <div className="grid-2">
              <div className="field">
                <label htmlFor="editGTitle">Goal Title</label>
                <input
                  id="editGTitle"
                  className="input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="editGStatus">Status</label>
                <select
                  id="editGStatus"
                  className="input"
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="paused">Paused</option>
                </select>
              </div>
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="editGDesc">Description</label>
              <textarea
                id="editGDesc"
                className="input"
                style={{ minHeight: 60, resize: "vertical" }}
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="editGTarget">Target Date</label>
              <input
                id="editGTarget"
                type="date"
                className="input"
                value={editTargetDate}
                onChange={(e) => setEditTargetDate(e.target.value)}
              />
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
              <button type="submit" className="btn btn-primary" disabled={updating}>
                {updating ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />} Save Changes
              </button>
              <button type="button" onClick={() => setEditingGoal(null)} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Add Goal Form */}
      {showAdd && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Direction</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Create New Goal
          </div>
          <form onSubmit={handleCreate}>
            <div className="grid-2">
              <RoleSelect
                value={title}
                onChange={setTitle}
                label="Target Career Goal / Role"
                placeholder="Select a career track or enter custom role..."
                required
              />
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
          {goals.map((g) => {
            const isCompleted = g.status === "completed";
            const isGenRoadmap = generatingRoadmapId === g.id;

            return (
              <div className="card card-pad" key={g.id}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          textTransform: "uppercase",
                          padding: "3px 7px",
                          borderRadius: 4,
                          background: isCompleted ? "rgba(0, 209, 178, 0.12)" : "var(--accent-soft)",
                          color: isCompleted ? "var(--teal)" : "var(--accent)",
                        }}
                      >
                        {g.goal_type}
                      </span>
                      <span className="muted" style={{ fontSize: 10 }}>· Status: {g.status}</span>
                    </div>
                    <h3
                      style={{
                        fontSize: 16,
                        margin: "10px 0 6px",
                        textDecoration: isCompleted ? "line-through" : "none",
                        color: isCompleted ? "var(--muted)" : "var(--text)",
                      }}
                    >
                      {g.title}
                    </h3>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button
                      onClick={() => handleToggleStatus(g)}
                      className="icon-btn"
                      title={isCompleted ? "Mark active" : "Mark completed"}
                      aria-label={isCompleted ? "Mark active" : "Mark completed"}
                    >
                      {isCompleted ? <CheckCircle2 size={15} color="var(--teal)" /> : <Circle size={15} />}
                    </button>
                    <button
                      onClick={() => handleStartEdit(g)}
                      className="icon-btn"
                      title="Edit goal"
                      aria-label="Edit goal"
                    >
                      <Edit2 size={13} color="var(--accent)" />
                    </button>
                    <button
                      onClick={() => handleDelete(g.id)}
                      className="icon-btn"
                      title="Delete goal"
                      aria-label="Delete goal"
                    >
                      <Trash2 size={14} color="#ff8787" />
                    </button>
                  </div>
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
                    alignItems: "center",
                    marginTop: 14,
                    paddingTop: 10,
                    borderTop: "1px solid var(--line)",
                    fontSize: 11,
                  }}
                >
                  <span className="muted">
                    {g.target_date ? `Target: ${new Date(g.target_date).toLocaleDateString()}` : "No deadline"}
                  </span>
                  <button
                    onClick={() => handleGenerateRoadmapForGoal(g)}
                    className="btn btn-outline"
                    style={{ fontSize: 10, padding: "3px 8px" }}
                    disabled={isGenRoadmap}
                    title="Generate Roadmap for this Goal"
                  >
                    {isGenRoadmap ? (
                      <Loader2 size={11} className="animate-spin" />
                    ) : (
                      <Sparkles size={11} color="var(--accent)" />
                    )}
                    Generate Roadmap
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
