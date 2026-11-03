"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Check, Loader2, Plus, Sparkles, Target } from "lucide-react";
import { placementApi } from "@/lib/api";
import type { JobMatchResponse } from "@/types";

export default function PlacementView() {
  const [matches, setMatches] = useState<JobMatchResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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

    setMatching(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const match = await placementApi.createJobMatch({
        role_title: roleTitle.trim(),
        job_description: jobDescription.trim(),
      });

      setStatusMessage(`Placement analysis complete: ${Math.round(match.estimated_score)}% alignment score.`);
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
                placeholder="e.g. Frontend Software Engineer (Intern / New Grad)"
                required
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="jobDesc">Job Description / Requirements Text</label>
              <textarea
                id="jobDesc"
                className="input"
                style={{ minHeight: 90, resize: "vertical" }}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description or requirements section here (e.g. Requires React, TypeScript, APIs, Git)..."
                required
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
            Paste a target role description to see where your verified evidence aligns and where skill gaps remain.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {matches.map((m) => {
            const breakdown = (m.match_breakdown || {}) as Record<string, unknown>;
            const matchedSkills = (breakdown.matched_skills as Array<{ skill?: string; status?: string }>) || [];
            const missingSkills = (breakdown.missing_skills as Array<{ skill?: string; status?: string }>) || [];

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
                  <div className="score-ring" style={{ width: 56, height: 56 }}>
                    <strong>{Math.round(m.estimated_score)}</strong>
                    <small>%</small>
                  </div>
                </div>

                <div className="progress-track" style={{ marginTop: 16 }}>
                  <div className="progress-value" style={{ width: `${Math.round(m.estimated_score)}%` }} />
                </div>

                {/* Breakdown details */}
                <div className="grid-2" style={{ marginTop: 18 }}>
                  <div
                    style={{
                      background: "var(--surface-2)",
                      padding: 12,
                      borderRadius: 8,
                      border: "1px solid var(--line)",
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--teal)", marginBottom: 8 }}>
                      Demonstrated & Matched Skills ({matchedSkills.length})
                    </div>
                    {matchedSkills.length === 0 ? (
                      <p className="muted" style={{ fontSize: 11 }}>None matched yet.</p>
                    ) : (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {matchedSkills.map((s, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: 11,
                              padding: "3px 7px",
                              background: "rgba(0, 209, 178, 0.12)",
                              color: "var(--teal)",
                              borderRadius: 4,
                            }}
                          >
                            {s.skill || JSON.stringify(s)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div
                    style={{
                      background: "var(--surface-2)",
                      padding: 12,
                      borderRadius: 8,
                      border: "1px solid var(--line)",
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", marginBottom: 8 }}>
                      Identified Capability Gaps ({missingSkills.length})
                    </div>
                    {missingSkills.length === 0 ? (
                      <p className="muted" style={{ fontSize: 11 }}>No significant gaps identified.</p>
                    ) : (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {missingSkills.map((s, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: 11,
                              padding: "3px 7px",
                              background: "rgba(108, 99, 255, 0.15)",
                              color: "#c0bcff",
                              borderRadius: 4,
                            }}
                          >
                            {s.skill || JSON.stringify(s)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {m.limitations && m.limitations.length > 0 && (
                  <div style={{ marginTop: 14, fontSize: 11, color: "var(--muted)" }}>
                    <div style={{ fontWeight: 600, marginBottom: 4 }}>Explainable Next Steps:</div>
                    <ul style={{ paddingLeft: 18, lineHeight: 1.5 }}>
                      {m.limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
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
