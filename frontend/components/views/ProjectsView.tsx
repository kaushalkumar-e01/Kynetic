"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  Check,
  Edit2,
  FolderKanban,
  Lightbulb,
  ListChecks,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
  Wrench,
  X,
} from "lucide-react";
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

  // New project state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [sourceType, setSourceType] = useState("manual");

  // Edit project state
  const [editingProject, setEditingProject] = useState<ProjectResponse | null>(null);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editRepoUrl, setEditRepoUrl] = useState("");
  const [updating, setUpdating] = useState(false);

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

      setStatusMessage(`Project "${name}" created successfully. You can now analyze it to extract demonstrated skills.`);
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

  const handleStartEdit = (p: ProjectResponse) => {
    setEditingProject(p);
    setEditName(p.name);
    setEditDescription(p.description || "");
    setEditRepoUrl(p.repository_url || "");
    setErrorMessage(null);
    setStatusMessage(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProject || !editName.trim()) return;

    setUpdating(true);
    setErrorMessage(null);

    try {
      const updated = await projectsApi.updateProject(editingProject.id, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
        repository_url: editRepoUrl.trim() || undefined,
      });

      setStatusMessage(`Project "${updated.name}" updated successfully.`);
      setEditingProject(null);
      loadProjects();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to update project.");
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleAnalyze = async (projectId: string) => {
    setAnalyzingId(projectId);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const analysis = await projectsApi.analyzeProject(projectId);
      setStatusMessage("Project analysis completed successfully. Demonstrated technical skills have been added to your profile.");
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
    if (!confirm("Are you sure you want to delete this project and its analyses?")) return;
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

      {/* Edit Project Modal / Section */}
      {editingProject && (
        <section className="card card-pad" style={{ marginBottom: 24, border: "2px solid var(--accent)", background: "var(--surface)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Edit Project</div>
              <h3 style={{ margin: "4px 0", fontSize: 16 }}>Update &ldquo;{editingProject.name}&rdquo;</h3>
            </div>
            <button onClick={() => setEditingProject(null)} className="icon-btn" title="Cancel edit">
              <X size={16} />
            </button>
          </div>
          <form onSubmit={handleSaveEdit}>
            <div className="grid-2">
              <div className="field">
                <label htmlFor="editPName">Project Name</label>
                <input
                  id="editPName"
                  className="input"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="editPRepo">Repository or Demo URL</label>
                <input
                  id="editPRepo"
                  className="input"
                  value={editRepoUrl}
                  onChange={(e) => setEditRepoUrl(e.target.value)}
                  placeholder="https://github.com/..."
                />
              </div>
            </div>
            <div className="field" style={{ marginTop: 12 }}>
              <label htmlFor="editPDesc">Project Description & Architecture</label>
              <textarea
                id="editPDesc"
                className="input"
                style={{ minHeight: 70, resize: "vertical" }}
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
              />
            </div>
            <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
              <button type="submit" className="btn btn-primary" disabled={updating}>
                {updating ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />} Save Changes
              </button>
              <button type="button" onClick={() => setEditingProject(null)} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Add Project Form */}
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
                  placeholder="e.g. Distributed Task Worker"
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
                placeholder="What does this project do? Mention technologies used (e.g. Python, FastAPI, Docker, PostgreSQL, React)..."
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
            const demonstratedSkills = analysis?.demonstrated_skills || [];
            const missingReqs = analysis?.missing_requirements || [];
            const recommendations = analysis?.recommendations || [];

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
                      onClick={() => handleStartEdit(p)}
                      className="icon-btn"
                      title="Edit project"
                      aria-label="Edit project"
                    >
                      <Edit2 size={13} color="var(--accent)" />
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
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span style={{ fontSize: 11, fontWeight: 700, color: "var(--teal)", display: "flex", alignItems: "center", gap: 5 }}>
                        <Sparkles size={12} /> Technical Insights & Architecture
                      </span>
                      <span className="muted" style={{ fontSize: 10 }}>Status: {analysis.status}</span>
                    </div>

                    {/* Detected Tech */}
                    {techStack.length > 0 && (
                      <div style={{ marginBottom: 10 }}>
                        <div className="muted" style={{ fontSize: 10, marginBottom: 4 }}>Detected Technologies:</div>
                        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                          {techStack.map((tech, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: 10,
                                padding: "2px 6px",
                                background: "var(--surface)",
                                borderRadius: 4,
                                border: "1px solid var(--line)",
                              }}
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Demonstrated Skills */}
                    {demonstratedSkills.length > 0 && (
                      <div style={{ marginBottom: 10 }}>
                        <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text)", display: "flex", alignItems: "center", gap: 4, marginBottom: 4 }}>
                          <Wrench size={11} color="var(--accent)" /> Demonstrated Skills ({demonstratedSkills.length}):
                        </div>
                        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                          {demonstratedSkills.map((sk, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: 10,
                                padding: "2px 6px",
                                background: "rgba(0, 209, 178, 0.08)",
                                border: "1px solid rgba(0, 209, 178, 0.2)",
                                color: "var(--teal)",
                                borderRadius: 4,
                              }}
                            >
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Architecture Summary */}
                    {analysis.architecture_summary && (
                      <p className="muted" style={{ fontSize: 11, lineHeight: 1.4, marginBottom: 8 }}>
                        {analysis.architecture_summary}
                      </p>
                    )}

                    {/* Recommendations */}
                    {recommendations.length > 0 && (
                      <div style={{ marginTop: 8, borderTop: "1px solid var(--line)", paddingTop: 8 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: "var(--accent)", display: "flex", alignItems: "center", gap: 4, marginBottom: 4 }}>
                          <Lightbulb size={11} /> Recommendations for Improvement:
                        </div>
                        <ul style={{ paddingLeft: 14, fontSize: 10, lineHeight: 1.4, margin: 0, color: "var(--muted)" }}>
                          {recommendations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Missing Requirements */}
                    {missingReqs.length > 0 && (
                      <div style={{ marginTop: 8, borderTop: "1px solid var(--line)", paddingTop: 8 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: "#ff8787", display: "flex", alignItems: "center", gap: 4, marginBottom: 4 }}>
                          <ListChecks size={11} /> Requirements to Add:
                        </div>
                        <ul style={{ paddingLeft: 14, fontSize: 10, lineHeight: 1.4, margin: 0, color: "var(--muted)" }}>
                          {missingReqs.map((req, i) => (
                            <li key={i}>{req}</li>
                          ))}
                        </ul>
                      </div>
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
