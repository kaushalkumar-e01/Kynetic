"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  Check,
  ChevronDown,
  ChevronUp,
  FileSearch,
  HelpCircle,
  Lightbulb,
  Loader2,
  Plus,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import { placementApi } from "@/lib/api";
import type { JobMatchResponse } from "@/types";

export default function PlacementView() {
  const [matches, setMatches] = useState<JobMatchResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedMatchId, setExpandedMatchId] = useState<string | null>(null);

  const [roleTitle, setRoleTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const loadMatches = () => {
    setLoading(true);
    placementApi
      .listJobMatches()
      .then((data) => {
        setMatches(data);
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load placement matches.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadMatches();
  }, []);

  const handleRunMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleTitle.trim() || !jobDescription.trim()) return;

    if (jobDescription.trim().length < 20) {
      setErrorMessage("Job description must contain at least 20 characters for meaningful requirement extraction.");
      return;
    }

    setMatching(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const match = await placementApi.createJobMatch({
        role_title: roleTitle.trim(),
        job_description: jobDescription.trim(),
      });

      setStatusMessage(`Placement evaluation complete: ${Math.round(match.estimated_score)}% alignment score based on your verified capability evidence.`);
      setRoleTitle("");
      setJobDescription("");
      setShowMatchForm(false);
      loadMatches();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Placement match failed.");
      }
    } finally {
      setMatching(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedMatchId((prev) => (prev === id ? null : id));
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
          <h2 style={{ fontSize: 18, margin: 0 }}>Placement & Job Matching</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Compare real job descriptions against your verified capability map with explainable skill gap breakdowns.
          </p>
        </div>
        <button
          onClick={() => setShowMatchForm(!showMatchForm)}
          className="btn btn-primary"
          style={{ fontSize: 12 }}
        >
          <Plus size={14} /> {showMatchForm ? "Cancel" : "Evaluate Job Match"}
        </button>
      </div>

      {showMatchForm && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Opportunity Evaluation</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Match Role Against Your Capabilities
          </div>
          <form onSubmit={handleRunMatch}>
            <div className="field">
              <label htmlFor="roleTitle">Target Role Title</label>
              <input
                id="roleTitle"
                className="input"
                value={roleTitle}
                onChange={(e) => setRoleTitle(e.target.value)}
                placeholder="e.g. Backend Software Engineer (Python / FastAPI)"
                required
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <label htmlFor="jobDesc">Job Description & Technical Requirements</label>
                <span className="muted" style={{ fontSize: 11 }}>Minimum 20 characters</span>
              </div>
              <textarea
                id="jobDesc"
                className="input"
                style={{ minHeight: 90, resize: "vertical" }}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description or technical requirements here (e.g. We are looking for an engineer proficient with Python, FastAPI, Docker, and PostgreSQL)..."
                required
                minLength={20}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: 16 }} disabled={matching}>
              {matching ? (
                <>
                  <Loader2 size={13} className="animate-spin" /> Evaluating Evidence Signals...
                </>
              ) : (
                <>
                  <Sparkles size={13} /> Run Placement Matching
                </>
              )}
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : matches.length === 0 ? (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <Target size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No placement evaluations yet</div>
          <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            Paste a target role description above to see where your verified evidence aligns and where skill gaps remain.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {matches.map((m) => {
            const breakdown = (m.match_breakdown || {}) as Record<string, unknown>;
            const matchedSkills = (breakdown.matched_skills as Array<{ skill?: string; band?: string; user_score?: number }>) || [];
            const partialSkills = (breakdown.partial_skills as Array<{ skill?: string; band?: string; user_score?: number }>) || [];
            const missingSkills = (breakdown.missing_skills as Array<{ skill?: string; band?: string }>) || [];
            const isExpanded = expandedMatchId === m.id;

            return (
              <div className="card card-pad" key={m.id}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div className="card-kicker">Evaluated Role</div>
                    <h3 style={{ fontSize: 16, margin: "6px 0 4px" }}>{m.role_title}</h3>
                    <div className="muted" style={{ fontSize: 11 }}>
                      Evaluated on {new Date(m.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div className="score-ring" style={{ width: 56, height: 56 }}>
                      <strong>{Math.round(m.estimated_score)}</strong>
                      <small>%</small>
                    </div>
                  </div>
                </div>

                <div className="progress-track" style={{ marginTop: 14 }}>
                  <div className="progress-value" style={{ width: `${Math.round(m.estimated_score)}%` }} />
                </div>

                {/* 3-Column Breakdown details */}
                <div className="grid-2" style={{ marginTop: 16, gap: 12 }}>
                  {/* Matched Skills */}
                  <div
                    style={{
                      background: "var(--surface-2)",
                      padding: 12,
                      borderRadius: 8,
                      border: "1px solid var(--line)",
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--teal)", marginBottom: 8, display: "flex", alignItems: "center", gap: 5 }}>
                      <TrendingUp size={13} /> Verified Matches ({matchedSkills.length})
                    </div>
                    {matchedSkills.length === 0 ? (
                      <p className="muted" style={{ fontSize: 11 }}>No verified matches for this role yet.</p>
                    ) : (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {matchedSkills.map((s, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: 11,
                              padding: "3px 8px",
                              background: "rgba(0, 209, 178, 0.12)",
                              color: "var(--teal)",
                              borderRadius: 4,
                              border: "1px solid rgba(0, 209, 178, 0.25)",
                            }}
                          >
                            {s.skill} <span style={{ opacity: 0.7, fontSize: 10 }}>· {s.band || "proficient"}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Partial / Developing Skills */}
                  <div
                    style={{
                      background: "var(--surface-2)",
                      padding: 12,
                      borderRadius: 8,
                      border: "1px solid var(--line)",
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent-2)", marginBottom: 8, display: "flex", alignItems: "center", gap: 5 }}>
                      <Lightbulb size={13} /> Developing / Claimed ({partialSkills.length})
                    </div>
                    {partialSkills.length === 0 ? (
                      <p className="muted" style={{ fontSize: 11 }}>No partial matches.</p>
                    ) : (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {partialSkills.map((s, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: 11,
                              padding: "3px 8px",
                              background: "rgba(255, 187, 0, 0.12)",
                              color: "var(--amber)",
                              borderRadius: 4,
                              border: "1px solid rgba(255, 187, 0, 0.25)",
                            }}
                          >
                            {s.skill} <span style={{ opacity: 0.7, fontSize: 10 }}>· {s.band || "claimed"}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Missing Skills */}
                <div
                  style={{
                    background: "var(--surface-2)",
                    padding: 12,
                    borderRadius: 8,
                    border: "1px solid var(--line)",
                    marginTop: 12,
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#ff8787", marginBottom: 8, display: "flex", alignItems: "center", gap: 5 }}>
                    <AlertCircle size={13} /> Missing Capability Gaps ({missingSkills.length})
                  </div>
                  {missingSkills.length === 0 ? (
                    <p className="muted" style={{ fontSize: 11 }}>No missing skill requirements found.</p>
                  ) : (
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {missingSkills.map((s, idx) => (
                        <span
                          key={idx}
                          style={{
                            fontSize: 11,
                            padding: "3px 8px",
                            background: "rgba(255, 107, 107, 0.12)",
                            color: "#ff8787",
                            borderRadius: 4,
                            border: "1px solid rgba(255, 107, 107, 0.25)",
                          }}
                        >
                          {s.skill} <span style={{ opacity: 0.7, fontSize: 10 }}>· unverified</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Limitations and Actionable Next Steps */}
                {m.limitations && m.limitations.length > 0 && (
                  <div style={{ marginTop: 14, fontSize: 11, color: "var(--muted)" }}>
                    <div style={{ fontWeight: 600, marginBottom: 4, color: "var(--text)" }}>Actionable Insights & Limitations:</div>
                    <ul style={{ paddingLeft: 18, lineHeight: 1.5, margin: 0 }}>
                      {m.limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Toggle Extracted Requirements Preview */}
                <div style={{ marginTop: 12, display: "flex", justifyContent: "flex-end" }}>
                  <button
                    onClick={() => toggleExpand(m.id)}
                    className="btn btn-outline"
                    style={{ fontSize: 11, padding: "4px 8px" }}
                  >
                    {isExpanded ? (
                      <>
                        <ChevronUp size={12} /> Hide Extracted Requirements
                      </>
                    ) : (
                      <>
                        <ChevronDown size={12} /> View Extracted Requirements
                      </>
                    )}
                  </button>
                </div>

                {isExpanded && (
                  <div
                    style={{
                      marginTop: 10,
                      padding: 12,
                      background: "var(--surface)",
                      borderRadius: 6,
                      border: "1px solid var(--line)",
                      fontSize: 11,
                      lineHeight: 1.5,
                      color: "var(--muted)",
                    }}
                  >
                    <div style={{ fontWeight: 600, color: "var(--text)", marginBottom: 6 }}>
                      Target Skills Extracted from Job Description:
                    </div>
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {((m.extracted_requirements as { skills?: string[] })?.skills || []).map((sk, idx) => (
                        <span key={idx} style={{ fontSize: 10, padding: "3px 6px", background: "var(--surface-2)", borderRadius: 4, border: "1px solid var(--line)" }}>
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
