"use client";

import { useEffect, useState, useRef } from "react";
import {
  AlertCircle,
  Briefcase,
  Check,
  FileText,
  FolderGit2,
  GraduationCap,
  Layers,
  Loader2,
  Mail,
  Sparkles,
  Trash2,
  UploadCloud,
} from "lucide-react";
import { resumesApi } from "@/lib/api";
import type { ResumeResponse } from "@/types";
import { EvidenceBadge } from "@/components/AppShell";

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB limit

export default function ResumeView() {
  const [resumes, setResumes] = useState<ResumeResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadResumes = () => {
    setLoading(true);
    resumesApi
      .listResumes()
      .then((data) => {
        setResumes(data);
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load resumes.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Only PDF documents are supported for resume extraction.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setErrorMessage("File exceeds the maximum 10MB limit.");
      return;
    }

    setUploading(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await resumesApi.uploadResume(file);
      setStatusMessage(`Resume "${file.name}" uploaded successfully. You can now analyze it to extract capability signals.`);
      loadResumes();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Upload failed.");
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleAnalyze = async (resumeId: string) => {
    setAnalyzingId(resumeId);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const result = await resumesApi.analyzeResume(resumeId);
      setStatusMessage("AI resume analysis completed successfully. Extracted skills have been added to your Capability Profile as claimed signals.");
      // Update local state with latest analysis
      setResumes((prev) =>
        prev.map((r) => (r.id === resumeId ? { ...r, status: "analyzed", analysis: result } : r))
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

  const handleDelete = async (resumeId: string) => {
    if (!confirm("Are you sure you want to delete this resume and its analysis?")) return;
    try {
      await resumesApi.deleteResume(resumeId);
      setStatusMessage("Resume deleted.");
      setResumes((prev) => prev.filter((r) => r.id !== resumeId));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to delete resume.");
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

      <div className="grid-2">
        {/* Upload Box */}
        <section className="card card-pad">
          <div className="section-head" style={{ marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Resume Intelligence</div>
              <div className="card-title" style={{ marginTop: 6 }}>
                Upload PDF Resume
              </div>
            </div>
            <FileText size={18} color="var(--accent)" />
          </div>
          <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, marginBottom: 20 }}>
            Upload your resume in PDF format (up to 10MB). Kynetic parses education, experience, and claimed skills,
            distinguishing claims from verified evidence.
          </p>

          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: "2px dashed var(--line)",
              borderRadius: 12,
              padding: "36px 20px",
              textAlign: "center",
              cursor: uploading ? "not-allowed" : "pointer",
              background: "var(--surface-2)",
              transition: "border-color 0.2s ease",
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,application/pdf"
              style={{ display: "none" }}
              disabled={uploading}
            />
            {uploading ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
                <Loader2 size={24} className="animate-spin text-muted" />
                <span style={{ fontSize: 13, color: "var(--muted)" }}>Uploading and storing privately...</span>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
                <UploadCloud size={30} color="var(--accent)" />
                <strong style={{ fontSize: 14 }}>Click to select PDF resume</strong>
                <span className="muted" style={{ fontSize: 11 }}>
                  Maximum file size: 10MB · PDF documents only
                </span>
              </div>
            )}
          </div>
        </section>

        {/* Claimed Evidence Principle */}
        <section className="card card-pad">
          <div className="card-kicker">Signal Distinction</div>
          <div className="card-title" style={{ marginTop: 6 }}>
            What Happens to Extracted Skills?
          </div>
          <div style={{ marginTop: 14, fontSize: 12, lineHeight: 1.6, color: "var(--muted)" }}>
            <p>
              When a resume is analyzed, extracted skills are categorized as <EvidenceBadge kind="claimed" /> signals.
            </p>
            <p style={{ marginTop: 10 }}>
              Kynetic does not elevate a self-written resume bullet point to verified capability until you:
            </p>
            <ul style={{ paddingLeft: 18, marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
              <li>Complete a focused quiz or conceptual check in <strong>Assessments</strong>.</li>
              <li>Connect an active GitHub repository or project link in <strong>Projects</strong>.</li>
            </ul>
          </div>
        </section>
      </div>

      {/* Uploaded Resumes and Analyses */}
      <div style={{ marginTop: 32 }}>
        <div className="section-head">
          <div>
            <div className="eyebrow">Stored Documents</div>
            <h2 style={{ margin: "6px 0 0", fontSize: 18 }}>Uploaded Resumes & AI Analysis Reports</h2>
          </div>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 36 }}>
            <Loader2 size={22} className="animate-spin text-muted" />
          </div>
        ) : resumes.length === 0 ? (
          <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
            <FileText size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
            <div style={{ fontSize: 15, fontWeight: 600 }}>No resumes uploaded yet</div>
            <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
              Upload your PDF resume above to extract capability claims and receive tailored AI feedback.
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {resumes.map((resume) => {
              const isAnalyzing = analyzingId === resume.id;
              const hasAnalysis = !!resume.analysis;
              const extracted = (resume.analysis?.extracted_profile || {}) as Record<string, unknown>;
              const claimedSkills = (extracted.claimed_skills as Array<{ name: string; category?: string }>) || [];
              const education = (extracted.education as string[]) || [];
              const experience = (extracted.experience as string[]) || [];
              const projects = (extracted.projects as string[]) || [];
              const candidateEmail = extracted.candidate_email as string | undefined;
              const candidateName = extracted.candidate_name as string | undefined;

              return (
                <div className="card card-pad" key={resume.id}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                      <div className="evidence-mark mark-claimed" style={{ width: 40, height: 40 }}>
                        <FileText size={18} />
                      </div>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700 }}>{resume.original_filename}</div>
                        <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>
                          {(resume.file_size / 1024).toFixed(1)} KB · Uploaded on{" "}
                          {new Date(resume.created_at).toLocaleDateString()} · Status: <span style={{ textTransform: "capitalize" }}>{resume.status}</span>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        onClick={() => handleAnalyze(resume.id)}
                        className="btn btn-primary"
                        disabled={isAnalyzing}
                        style={{ fontSize: 12, padding: "7px 12px" }}
                      >
                        {isAnalyzing ? (
                          <>
                            <Loader2 size={13} className="animate-spin" /> Analyzing...
                          </>
                        ) : hasAnalysis ? (
                          <>
                            <Sparkles size={13} /> Re-analyze
                          </>
                        ) : (
                          <>
                            <Sparkles size={13} /> Analyze with AI
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(resume.id)}
                        className="icon-btn"
                        title="Delete resume"
                        aria-label="Delete resume"
                      >
                        <Trash2 size={14} color="#ff8787" />
                      </button>
                    </div>
                  </div>

                  {hasAnalysis && (
                    <div
                      style={{
                        marginTop: 18,
                        padding: 16,
                        background: "var(--surface-2)",
                        borderRadius: 10,
                        border: "1px solid var(--line)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                        <span style={{ fontSize: 13, fontWeight: 700, display: "flex", alignItems: "center", gap: 6 }}>
                          <Sparkles size={14} color="var(--accent)" /> Extracted Resume Intelligence
                        </span>
                        <span className="muted" style={{ fontSize: 11 }}>
                          Completed: {resume.analysis?.completed_at ? new Date(resume.analysis.completed_at).toLocaleTimeString() : "Ready"}
                        </span>
                      </div>

                      {/* Candidate info if detected */}
                      {(candidateName || candidateEmail) && (
                        <div style={{ display: "flex", gap: 16, marginBottom: 12, fontSize: 12, color: "var(--muted)" }}>
                          {candidateName && <span><strong>Name:</strong> {candidateName}</span>}
                          {candidateEmail && (
                            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                              <Mail size={12} /> {candidateEmail}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Extracted Skills */}
                      {claimedSkills.length > 0 && (
                        <div style={{ marginBottom: 16 }}>
                          <div style={{ fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                            <Layers size={13} color="var(--accent)" />
                            Extracted Claimed Competencies ({claimedSkills.length}):
                          </div>
                          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                            {claimedSkills.map((s, idx) => (
                              <span
                                key={idx}
                                style={{
                                  fontSize: 11,
                                  padding: "4px 8px",
                                  background: "var(--surface)",
                                  borderRadius: 5,
                                  border: "1px solid var(--line)",
                                }}
                              >
                                {s.name} <span className="muted">· {s.category || "claimed"}</span>
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Education & Experience in 2 columns */}
                      <div className="grid-2" style={{ gap: 16, marginBottom: 16 }}>
                        {/* Education */}
                        {education.length > 0 && (
                          <div style={{ background: "var(--surface)", padding: 12, borderRadius: 8, border: "1px solid var(--line)" }}>
                            <div style={{ fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "var(--teal)" }}>
                              <GraduationCap size={14} /> Education Details
                            </div>
                            <ul style={{ paddingLeft: 16, fontSize: 11, lineHeight: 1.5, margin: 0, color: "var(--muted)" }}>
                              {education.map((edu, idx) => (
                                <li key={idx} style={{ marginBottom: 4 }}>{edu}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Experience */}
                        {experience.length > 0 && (
                          <div style={{ background: "var(--surface)", padding: 12, borderRadius: 8, border: "1px solid var(--line)" }}>
                            <div style={{ fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "var(--accent)" }}>
                              <Briefcase size={14} /> Experience & History
                            </div>
                            <ul style={{ paddingLeft: 16, fontSize: 11, lineHeight: 1.5, margin: 0, color: "var(--muted)" }}>
                              {experience.map((exp, idx) => (
                                <li key={idx} style={{ marginBottom: 4 }}>{exp}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {/* Projects Section */}
                      {projects.length > 0 && (
                        <div style={{ background: "var(--surface)", padding: 12, borderRadius: 8, border: "1px solid var(--line)", marginBottom: 16 }}>
                          <div style={{ fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "var(--accent-2)" }}>
                            <FolderGit2 size={14} /> Projects Mentioned
                          </div>
                          <ul style={{ paddingLeft: 16, fontSize: 11, lineHeight: 1.5, margin: 0, color: "var(--muted)" }}>
                            {projects.map((proj, idx) => (
                              <li key={idx} style={{ marginBottom: 4 }}>{proj}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Strengths */}
                      {resume.analysis?.strengths && resume.analysis.strengths.length > 0 && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--teal)", marginBottom: 4 }}>
                            Strengths Identified:
                          </div>
                          <ul style={{ paddingLeft: 18, fontSize: 11, lineHeight: 1.5, color: "var(--muted)" }}>
                            {resume.analysis.strengths.map((str, i) => (
                              <li key={i}>{str}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommendations */}
                      {resume.analysis?.suggestions && resume.analysis.suggestions.length > 0 && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--accent)", marginBottom: 4 }}>
                            Recommendations to Make Claims Believable:
                          </div>
                          <ul style={{ paddingLeft: 18, fontSize: 11, lineHeight: 1.5, color: "var(--muted)" }}>
                            {resume.analysis.suggestions.map((sug, i) => (
                              <li key={i}>{sug}</li>
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
    </div>
  );
}
