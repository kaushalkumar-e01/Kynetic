"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Check, Loader2, Plus, ShieldCheck, Zap } from "lucide-react";
import { skillsApi } from "@/lib/api";
import type { EvidenceRecordResponse, UserCapabilityResponse } from "@/types";
import { EvidenceBadge, type EvidenceKind } from "@/components/AppShell";

export default function CapabilitiesView() {
  const [capabilities, setCapabilities] = useState<UserCapabilityResponse[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceRecordResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingEvidence, setAddingEvidence] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // New evidence form state
  const [skillName, setSkillName] = useState("");
  const [category, setCategory] = useState("Technical");
  const [summary, setSummary] = useState("");
  const [confidence, setConfidence] = useState(0.7);

  const loadData = () => {
    setLoading(true);
    Promise.allSettled([skillsApi.listCapabilities(), skillsApi.listEvidence()]).then(
      ([capRes, evRes]) => {
        if (capRes.status === "fulfilled") setCapabilities(capRes.value);
        if (evRes.status === "fulfilled") setEvidenceList(evRes.value);
        setLoading(false);
      }
    );
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!skillName.trim() || !summary.trim()) return;

    setAddingEvidence(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await skillsApi.addEvidence({
        skill_name: skillName.trim(),
        category,
        summary: summary.trim(),
        confidence,
      });

      setStatusMessage(`Evidence for "${skillName}" added successfully.`);
      setSkillName("");
      setSummary("");
      setShowAddForm(false);
      loadData();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to add evidence.");
      }
    } finally {
      setAddingEvidence(false);
    }
  };

  const mapBandToEvidenceKind = (band: string): EvidenceKind => {
    if (band === "claimed") return "claimed";
    if (band === "proficient" || band === "advanced") return "assessed";
    return "project";
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
          <h2 style={{ fontSize: 18, margin: 0 }}>Persistent Capability Signals</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Claims, quiz assessments, and project proofs tracked separately with confidence bands.
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn btn-primary"
          style={{ fontSize: 12 }}
        >
          <Plus size={14} /> {showAddForm ? "Cancel" : "Add Self-Reported Evidence"}
        </button>
      </div>

      {showAddForm && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Self-Reported Signal</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Add Confirmed Skill Evidence
          </div>
          <form onSubmit={handleAddEvidence}>
            <div className="grid-2">
              <div className="field">
                <label htmlFor="skillName">Skill Name</label>
                <input
                  id="skillName"
                  className="input"
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  placeholder="e.g. Docker, PostgreSQL, React Native"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="category">Category</label>
                <select
                  id="category"
                  className="input"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="Technical">Technical</option>
                  <option value="Human">Human / Communication</option>
                  <option value="Domain">Domain / Industry</option>
                </select>
              </div>
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="summary">Evidence Summary & Context</label>
              <textarea
                id="summary"
                className="input"
                style={{ minHeight: 60, resize: "vertical" }}
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Describe what you built or where you applied this skill..."
                required
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="confidence">Self-Assessed Confidence: {Math.round(confidence * 100)}%</label>
              <input
                id="confidence"
                type="range"
                min="0.1"
                max="1.0"
                step="0.05"
                value={confidence}
                onChange={(e) => setConfidence(parseFloat(e.target.value))}
                style={{ width: "100%", accentColor: "var(--accent)", cursor: "pointer" }}
              />
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
              <button type="submit" className="btn btn-primary" disabled={addingEvidence}>
                {addingEvidence ? <Loader2 size={13} className="animate-spin" /> : <Plus size={13} />}
                Confirm & Record Evidence
              </button>
            </div>
          </form>
        </section>
      )}

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : capabilities.length === 0 ? (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <ShieldCheck size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No capabilities mapped yet</div>
          <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            Upload a resume or start a quiz assessment to begin mapping your verified capability bands.
          </p>
        </div>
      ) : (
        <div className="skill-grid">
          {capabilities.map((skill) => {
            const kind = mapBandToEvidenceKind(skill.estimated_band);
            return (
              <div className="card skill-card" key={skill.id}>
                <div className="skill-head">
                  <div>
                    <div className="skill-name">{skill.skill_name || "Skill"}</div>
                    <div className="skill-category">
                      {skill.category || "Technical"} · {skill.evidence_count} signal
                      {skill.evidence_count !== 1 ? "s" : ""}
                    </div>
                  </div>
                  <div className="skill-score">{Math.round(skill.score)}</div>
                </div>

                <div className="progress-track" style={{ marginTop: 14 }}>
                  <div className="progress-value" style={{ width: `${Math.round(skill.score)}%` }} />
                </div>

                <div className="skill-evidence" style={{ marginTop: 12, display: "flex", gap: 6 }}>
                  <EvidenceBadge kind={kind} label={skill.estimated_band} />
                  <span className="muted" style={{ fontSize: 10, alignSelf: "center" }}>
                    {Math.round(skill.confidence * 100)}% confidence
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Raw Evidence History Log */}
      <div style={{ marginTop: 36 }}>
        <div className="section-head">
          <div>
            <div className="eyebrow">Audit Trail</div>
            <h2 style={{ margin: "6px 0 0", fontSize: 18 }}>Recorded Evidence History</h2>
          </div>
        </div>

        {evidenceList.length === 0 ? (
          <p className="muted" style={{ fontSize: 12 }}>
            No individual evidence entries recorded yet.
          </p>
        ) : (
          <div className="card card-pad">
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {evidenceList.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    paddingBottom: 10,
                    borderBottom: "1px solid var(--line)",
                  }}
                >
                  <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <div className="activity-icon">
                      <Zap size={13} />
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>{ev.summary}</div>
                      <div className="muted" style={{ fontSize: 10, marginTop: 2 }}>
                        Source: <strong>{ev.source_type}</strong> · Confidence:{" "}
                        {Math.round(ev.confidence * 100)}%
                      </div>
                    </div>
                  </div>
                  <div className="muted" style={{ fontSize: 11 }}>
                    {new Date(ev.observed_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

