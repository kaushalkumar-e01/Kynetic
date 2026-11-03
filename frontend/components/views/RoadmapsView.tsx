"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  BookOpen,
  Check,
  CheckCircle2,
  Circle,
  ExternalLink,
  ListChecks,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import { roadmapsApi } from "@/lib/api";
import type { RoadmapResponse } from "@/types";
import TechMultiSelect from "@/components/ui/TechMultiSelect";

export default function RoadmapsView() {
  const [roadmaps, setRoadmaps] = useState<RoadmapResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGen, setShowGen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);

  const loadRoadmaps = () => {
    setLoading(true);
    roadmapsApi
      .listRoadmaps()
      .then((data) => {
        setRoadmaps(data);
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load roadmaps.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadRoadmaps();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setGenerating(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await roadmapsApi.createRoadmap({
        title: title.trim(),
        description: description.trim() || undefined,
        target_skills: selectedSkills.length > 0 ? selectedSkills : undefined,
      });

      setStatusMessage("Personalized capability roadmap and milestone curriculum generated successfully.");
      setTitle("");
      setDescription("");
      setSelectedSkills([]);
      setShowGen(false);
      loadRoadmaps();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to generate roadmap.");
      }
    } finally {
      setGenerating(false);
    }
  };

  const toggleMilestone = async (roadmapId: string, milestoneId: string, currentStatus: string) => {
    const nextStatus = currentStatus === "completed" ? "pending" : "completed";
    try {
      await roadmapsApi.updateMilestone(roadmapId, milestoneId, { status: nextStatus });
      loadRoadmaps();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      }
    }
  };

  const handleDeleteRoadmap = async (roadmapId: string) => {
    if (!confirm("Are you sure you want to delete this roadmap and all its milestones?")) return;
    try {
      await roadmapsApi.deleteRoadmap(roadmapId);
      setStatusMessage("Roadmap deleted.");
      setRoadmaps((prev) => prev.filter((r) => r.id !== roadmapId));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to delete roadmap.");
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
          <h2 style={{ fontSize: 18, margin: 0 }}>Capability Learning Roadmaps</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Focused, milestone-driven paths connecting capability gaps to verifiable evidence.
          </p>
        </div>
        <button onClick={() => setShowGen(!showGen)} className="btn btn-primary" style={{ fontSize: 12 }}>
          <Plus size={14} /> {showGen ? "Cancel" : "Create Roadmap"}
        </button>
      </div>

      {showGen && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Momentum</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Generate Personalized Roadmap
          </div>
          <form onSubmit={handleGenerate}>
            <div className="field">
              <label htmlFor="rmTitle">Roadmap Title / Career Track</label>
              <input
                id="rmTitle"
                className="input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Backend Platform Engineering or Frontend Next.js Mastery"
                required
              />
            </div>

            <div style={{ marginTop: 12 }}>
              <TechMultiSelect
                selected={selectedSkills}
                onChange={setSelectedSkills}
                label="Target Skills & Technologies"
                placeholder="Choose target skills (or leave blank for automatic role curriculum)..."
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="rmDesc">Description & Scope (Optional)</label>
              <textarea
                id="rmDesc"
                className="input"
                style={{ minHeight: 60, resize: "vertical" }}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Target outcomes, career goals, or milestone focus..."
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: 16 }} disabled={generating}>
              {generating ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
              Generate Roadmap & Curriculum
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : roadmaps.length === 0 ? (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <Activity size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No roadmaps active</div>
          <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            Generate a personalized roadmap to turn your identified skill gaps into tangible milestones.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {roadmaps.map((r) => (
            <div className="card card-pad" key={r.id}>
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
                        background: "rgba(0, 209, 178, 0.12)",
                        color: "var(--teal)",
                      }}
                    >
                      {r.status}
                    </span>
                    {r.goal_id && <span className="muted" style={{ fontSize: 10 }}>Linked to Career Goal</span>}
                  </div>
                  <h3 style={{ fontSize: 16, margin: "10px 0 4px" }}>{r.title}</h3>
                  {r.description && <p className="muted" style={{ fontSize: 12 }}>{r.description}</p>}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 18, fontWeight: 700, color: "var(--teal)" }}>
                      {Math.round(r.progress_percentage || 0)}%
                    </div>
                    <div className="muted" style={{ fontSize: 10 }}>Completed</div>
                  </div>
                  <button
                    onClick={() => handleDeleteRoadmap(r.id)}
                    className="icon-btn"
                    title="Delete roadmap"
                    aria-label="Delete roadmap"
                  >
                    <Trash2 size={14} color="#ff8787" />
                  </button>
                </div>
              </div>

              <div className="progress-track" style={{ marginTop: 14 }}>
                <div className="progress-value" style={{ width: `${Math.round(r.progress_percentage || 0)}%` }} />
              </div>

              {/* Milestones list */}
              <div style={{ marginTop: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 10 }}>
                  Progression Milestones ({r.milestones?.length || 0}):
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {(r.milestones || []).map((ms) => {
                    const done = ms.status === "completed";
                    const resources = (ms.resources || []) as Array<{
                      title?: string;
                      url?: string;
                      action?: string;
                      objectives?: string[];
                      note?: string;
                    }>;

                    return (
                      <div
                        key={ms.id}
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: 6,
                          padding: "12px 14px",
                          borderRadius: 8,
                          background: done ? "rgba(0, 209, 178, 0.06)" : "var(--surface-2)",
                          border: "1px solid var(--line)",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                          <button
                            onClick={() => toggleMilestone(r.id, ms.id, ms.status)}
                            style={{
                              background: "none",
                              border: "none",
                              padding: 0,
                              cursor: "pointer",
                              color: done ? "var(--teal)" : "var(--muted)",
                              marginTop: 2,
                            }}
                            title={done ? "Mark pending" : "Mark completed"}
                          >
                            {done ? <CheckCircle2 size={18} /> : <Circle size={18} />}
                          </button>
                          <div style={{ flex: 1 }}>
                            <div
                              style={{
                                fontSize: 13,
                                fontWeight: 600,
                                textDecoration: done ? "line-through" : "none",
                                color: done ? "var(--muted)" : "var(--fg)",
                              }}
                            >
                              {ms.title}
                            </div>
                            {ms.description && (
                              <p className="muted" style={{ fontSize: 11, marginTop: 3 }}>
                                {ms.description}
                              </p>
                            )}
                          </div>
                          <span
                            style={{
                              fontSize: 10,
                              textTransform: "uppercase",
                              color: done ? "var(--teal)" : "var(--muted)",
                              fontWeight: 600,
                            }}
                          >
                            {ms.status}
                          </span>
                        </div>

                        {/* Learning objectives if available */}
                        {resources.some((res) => res.objectives && res.objectives.length > 0) && (
                          <div style={{ paddingLeft: 30, marginTop: 4 }}>
                            {resources
                              .filter((res) => res.objectives && res.objectives.length > 0)
                              .map((res, i) => (
                                <div key={i}>
                                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--teal)", marginBottom: 2, display: "flex", alignItems: "center", gap: 4 }}>
                                    <ListChecks size={11} /> {res.title}:
                                  </div>
                                  <ul style={{ paddingLeft: 14, fontSize: 10, margin: "2px 0 6px", color: "var(--muted)", lineHeight: 1.4 }}>
                                    {res.objectives!.map((obj, oi) => (
                                      <li key={oi}>{obj}</li>
                                    ))}
                                  </ul>
                                </div>
                              ))}
                          </div>
                        )}

                        {/* Attached Learning Resources */}
                        {resources.length > 0 && (
                          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", paddingLeft: 30, marginTop: 4 }}>
                            {resources
                              .filter((res) => res.url || res.note)
                              .map((res, i) => (
                                <span
                                  key={i}
                                  style={{
                                    fontSize: 10,
                                    color: "var(--accent)",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 4,
                                    background: "var(--surface)",
                                    padding: "2px 8px",
                                    borderRadius: 4,
                                    border: "1px solid var(--line)",
                                  }}
                                >
                                  <BookOpen size={10} />
                                  {res.url ? (
                                    <a
                                      href={res.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      style={{ color: "var(--accent)", display: "flex", alignItems: "center", gap: 2 }}
                                    >
                                      {res.title} <ExternalLink size={9} />
                                    </a>
                                  ) : (
                                    <span>{res.title}: {res.note}</span>
                                  )}
                                </span>
                              ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
