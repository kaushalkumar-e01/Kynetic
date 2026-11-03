"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Check, FolderKanban, Loader2, Plus, Sparkles, Trash2 } from "lucide-react";
import { projectsApi } from "@/lib/api";
import type { ProjectResponse } from "@/types";
import { EvidenceBadge } from "@/components/AppShell";

export default function ProjectsView() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [sourceType, setSourceType] = useState("manual");

  const loadProjects = () => {
    setLoading(true);
    projectsApi
      .listProjects()
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load projects.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await projectsApi.createProject({
        name: name.trim(),
        description: description.trim() || undefined,
        repository_url: repoUrl.trim() || undefined,
        source_type: sourceType,
      });

      setStatusMessage(`Project "${name}" created successfully.`);
      setName("");
      setDescription("");
      setRepoUrl("");
      setShowAdd(false);
      loadProjects();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to create project.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnalyze = async (projectId: string) => {
    setAnalyzingId(projectId);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const analysis = await projectsApi.analyzeProject(projectId);
      setStatusMessage("Project analysis completed successfully.");
      setProjects((prev) =>
        prev.map((p) => (p.id === projectId ? { ...p, latest_analysis: analysis } : p))
      );
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Analysis failed.");
      }
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleDelete = async (projectId: string) => {
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await projectsApi.deleteProject(projectId);
      setStatusMessage("Project deleted.");
      setProjects((prev) => prev.filter((p) => p.id !== projectId));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to delete project.");
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
          <h2 style={{ fontSize: 18, margin: 0 }}>Project Evidence & Intelligence</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            The work behind your story. Connect repositories and manual descriptions to demonstrate practical capability.
          </p>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary" style={{ fontSize: 12 }}>
          <Plus size={14} /> {showAdd ? "Cancel" : "Add Project"}
        </button>
      </div>

      {showAdd && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
          <div className="card-kicker">Project Evidence</div>
          <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
            Register New Project
          </div>
          <form onSubmit={handleCreate}>
            <div className="grid-2">
              <div className="field">
                <label htmlFor="pName">Project Name</label>
                <input
                  id="pName"
                  className="input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Kinetic UI"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="pSource">Source Type</label>
                <select
                  id="pSource"
                  className="input"
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                >
                  <option value="manual">Manual Entry</option>
                  <option value="github">GitHub Repository</option>
                </select>
              </div>
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="pDesc">Project Description & Architecture</label>
              <textarea
                id="pDesc"
                className="input"
                style={{ minHeight: 60, resize: "vertical" }}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What does this project do? Mention technologies used (e.g. React, Next.js, FastAPI)..."
              />
            </div>

            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="pRepo">Repository or Demo URL (Optional)</label>
              <input
                id="pRepo"
                className="input"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/project-repo"
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: 16 }} disabled={submitting}>
              {submitting ? <Loader2 size={13} className="animate-spin" /> : <Plus size={13} />}
              Save Project
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : projects.length === 0 ? (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <FolderKanban size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No projects added yet</div>
          <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            Add your repositories or personal projects to generate project-backed capability signals.
          </p>
        </div>
      ) : (
        <div className="grid-2">
          {projects.map((p) => {
            const isAnalyzing = analyzingId === p.id;
            const analysis = p.latest_analysis;
            const techStack = analysis?.detected_technologies || [];

            return (
              <div className="card card-pad" key={p.id}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <EvidenceBadge kind="project" label="Project-supported" />
                      <span className="muted" style={{ fontSize: 10 }}>Source: {p.source_type}</span>
                    </div>
                    <h3 style={{ fontSize: 16, margin: "10px 0 6px" }}>{p.name}</h3>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button
                      onClick={() => handleAnalyze(p.id)}
                      className="btn btn-outline"
                      disabled={isAnalyzing}
                      style={{ fontSize: 11, padding: "5px 10px" }}
                      title="Analyze project"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 size={12} className="animate-spin" /> Analyzing...
                        </>
                      ) : (
                        <>
                          <Sparkles size={12} /> {analysis ? "Re-analyze" : "Analyze"}
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="icon-btn"
                      title="Delete project"
                      aria-label="Delete project"
                    >
                      <Trash2 size={13} color="#ff8787" />
                    </button>
                  </div>
                </div>

                <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, minHeight: 38, marginTop: 6 }}>
                  {p.description || "No description provided."}
                </p>

                {p.repository_url && (
                  <div style={{ fontSize: 11, marginTop: 8 }}>
                    <a
                      href={p.repository_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "var(--accent)", textDecoration: "underline" }}
                    >
                      {p.repository_url}
                    </a>
                  </div>
                )}

                {/* Analysis breakdown */}
                {analysis && (
                  <div
                    style={{
                      marginTop: 14,
                      padding: 12,
                      background: "var(--surface-2)",
                      borderRadius: 8,
                      border: "1px solid var(--line)",
                    }}
                  >
                    <div style={{ fontSize: 11, fontWeight: 600, color: "var(--teal)", marginBottom: 6 }}>
                      Detected Technologies & Architecture:
                    </div>
                    {techStack.length > 0 && (
                      <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 8 }}>
                        {techStack.map((tech, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: 10,
                              padding: "3px 6px",
                              background: "var(--surface)",
                              borderRadius: 4,
                            }}
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                    {analysis.architecture_summary && (
                      <p className="muted" style={{ fontSize: 11, lineHeight: 1.4 }}>
                        {analysis.architecture_summary}
                      </p>
                    )}
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
