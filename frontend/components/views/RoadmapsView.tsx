"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  BookOpen,
  Check,
  CheckCircle2,
  Circle,
  Clock,
  Compass,
  ExternalLink,
  Layers,
  ListChecks,
  Loader2,
  Plus,
  Search,
  Sparkles,
  Trash2,
  Wrench,
} from "lucide-react";
import { authApi, roadmapsApi } from "@/lib/api";
import type { RoadmapResponse, UserResponse } from "@/types";
import TechMultiSelect from "@/components/ui/TechMultiSelect";
import {
  ALL_CURATED_ROADMAPS,
  CuratedRoadmap,
  filterCuratedRoadmaps,
  getCuratedRoadmapById,
  getTotalTopicCount,
} from "@/data/roadmaps";
import {
  calculateRoadmapProgress,
  loadUserProgress,
  UserProgressStore,
} from "@/lib/roadmap-progress";
import { CuratedRoadmapDetailView } from "./CuratedRoadmapDetailView";

export default function RoadmapsView() {
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);

  // Tab: "curated" (Curated Learning Paths) vs "custom" (User's AI / Custom Roadmaps)
  const [activeTab, setActiveTab] = useState<"curated" | "custom">("curated");

  // Selected curated roadmap ID for detail view
  const [selectedRoadmapId, setSelectedRoadmapId] = useState<string | null>(null);

  // Filter state for curated roadmaps
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [difficultyFilter, setDifficultyFilter] = useState("all");

  // User curated progress store
  const [userProgressStore, setUserProgressStore] = useState<UserProgressStore>({});

  // Custom/AI Roadmaps state
  const [customRoadmaps, setCustomRoadmaps] = useState<RoadmapResponse[]>([]);
  const [loadingCustom, setLoadingCustom] = useState(false);
  const [showGen, setShowGen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Custom generation form
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);

  // Load authenticated user and their progress
  useEffect(() => {
    let active = true;
    authApi
      .getMe()
      .then((user) => {
        if (!active) return;
        setCurrentUser(user);
        setUserProgressStore(loadUserProgress(user?.id));
      })
      .catch(() => {
        if (!active) return;
        setUserProgressStore(loadUserProgress(null));
      });

    return () => {
      active = false;
    };
  }, []);

  // Reload progress store on demand
  const refreshProgress = () => {
    setUserProgressStore(loadUserProgress(currentUser?.id));
  };

  // Load custom roadmaps
  const loadCustomRoadmaps = () => {
    setLoadingCustom(true);
    roadmapsApi
      .listRoadmaps()
      .then((data) => {
        setCustomRoadmaps(data);
        setLoadingCustom(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load custom roadmaps.");
        setLoadingCustom(false);
      });
  };

  useEffect(() => {
    if (activeTab === "custom") {
      loadCustomRoadmaps();
    }
  }, [activeTab]);

  const handleGenerateCustom = async (e: React.FormEvent) => {
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
      loadCustomRoadmaps();
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
      loadCustomRoadmaps();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      }
    }
  };

  const handleDeleteCustomRoadmap = async (roadmapId: string) => {
    if (!confirm("Are you sure you want to delete this custom roadmap?")) return;
    try {
      await roadmapsApi.deleteRoadmap(roadmapId);
      setStatusMessage("Roadmap deleted.");
      setCustomRoadmaps((prev) => prev.filter((r) => r.id !== roadmapId));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to delete roadmap.");
      }
    }
  };

  // Filtered curated roadmaps
  const filteredCurated = useMemo(() => {
    return filterCuratedRoadmaps(ALL_CURATED_ROADMAPS, searchQuery, categoryFilter, difficultyFilter);
  }, [searchQuery, categoryFilter, difficultyFilter]);

  // Total topics completed across all curated roadmaps
  const globalCuratedStats = useMemo(() => {
    let totalTopics = 0;
    let completedTopics = 0;
    let startedCount = 0;

    ALL_CURATED_ROADMAPS.forEach((rm) => {
      const stats = calculateRoadmapProgress(rm, userProgressStore[rm.id]);
      totalTopics += stats.totalTopics;
      completedTopics += stats.completedTopics;
      if (stats.isStarted) startedCount += 1;
    });

    return { totalTopics, completedTopics, startedCount };
  }, [userProgressStore]);

  const selectedCuratedRoadmap = selectedRoadmapId ? getCuratedRoadmapById(selectedRoadmapId) : null;

  return (
    <div>
      {/* Status & Error Alerts */}
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

      {/* Detail View of a Curated Roadmap */}
      {selectedCuratedRoadmap ? (
        <CuratedRoadmapDetailView
          roadmap={selectedCuratedRoadmap}
          userId={currentUser?.id}
          onBack={() => setSelectedRoadmapId(null)}
          onProgressChange={refreshProgress}
        />
      ) : (
        <>
          {/* Main Top Header & Mode Tabs */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              flexWrap: "wrap",
              gap: 16,
              marginBottom: 20,
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Developer Learning Roadmaps</h1>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "2px 7px",
                    borderRadius: 4,
                    background: "rgba(0, 209, 178, 0.12)",
                    color: "var(--teal)",
                    border: "1px solid rgba(0, 209, 178, 0.3)",
                  }}
                >
                  ROADMAP.SH STYLE
                </span>
              </div>
              <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>
                Predefined, structured technology curriculums with interactive progress tracking and free resources.
              </p>
            </div>

            {/* Navigation Tabs */}
            <div
              style={{
                display: "flex",
                background: "var(--surface)",
                padding: 4,
                borderRadius: 10,
                border: "1px solid var(--line)",
                gap: 4,
              }}
            >
              <button
                onClick={() => setActiveTab("curated")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "8px 14px",
                  borderRadius: 7,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  border: "none",
                  background: activeTab === "curated" ? "var(--accent)" : "transparent",
                  color: activeTab === "curated" ? "#fff" : "var(--muted)",
                  transition: "all 0.15s ease",
                }}
              >
                <Compass size={14} /> Curated Paths ({ALL_CURATED_ROADMAPS.length})
              </button>
              <button
                onClick={() => setActiveTab("custom")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "8px 14px",
                  borderRadius: 7,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  border: "none",
                  background: activeTab === "custom" ? "var(--accent)" : "transparent",
                  color: activeTab === "custom" ? "#fff" : "var(--muted)",
                  transition: "all 0.15s ease",
                }}
              >
                <Wrench size={14} /> Custom & AI Roadmaps {customRoadmaps.length > 0 && `(${customRoadmaps.length})`}
              </button>
            </div>
          </div>

          {/* CURATED LEARNING PATHS DISCOVERY */}
          {activeTab === "curated" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Highlight / Summary Banner */}
              <div
                className="card card-pad"
                style={{
                  background: "linear-gradient(135deg, rgba(108,99,255,0.12) 0%, rgba(0,209,178,0.08) 100%)",
                  border: "1px solid var(--line)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: 16,
                  padding: "16px 22px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <div
                    style={{
                      width: 42,
                      height: 42,
                      borderRadius: 10,
                      background: "rgba(108,99,255,0.2)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "var(--accent)",
                    }}
                  >
                    <BookOpen size={22} />
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700 }}>Built-In, Reliable Engineering Pathways</div>
                    <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      Carefully structured sequences from foundational syntax to production mastery. Every topic includes verified free resources.
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 18, fontWeight: 800, color: "var(--teal)" }}>
                      {globalCuratedStats.completedTopics} / {globalCuratedStats.totalTopics}
                    </div>
                    <div className="muted" style={{ fontSize: 10 }}>Topics Completed</div>
                  </div>
                  <div style={{ height: 28, width: 1, background: "var(--line)" }} />
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 18, fontWeight: 800, color: "var(--accent)" }}>
                      {globalCuratedStats.startedCount} of {ALL_CURATED_ROADMAPS.length}
                    </div>
                    <div className="muted" style={{ fontSize: 10 }}>Paths In Progress</div>
                  </div>
                </div>
              </div>

              {/* Search & Filter Toolbar */}
              <div
                className="card card-pad"
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                  padding: "14px 18px",
                }}
              >
                {/* Search input */}
                <div style={{ position: "relative" }}>
                  <Search
                    size={15}
                    style={{
                      position: "absolute",
                      left: 12,
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "var(--muted)",
                    }}
                  />
                  <input
                    type="text"
                    className="input"
                    placeholder="Search roadmaps by technology, concept (e.g. C, Python, Pointers, SQL, Trees, React, Docker)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ paddingLeft: 34, fontSize: 13 }}
                  />
                </div>

                {/* Filter chips */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
                  {/* Category Chips */}
                  <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, marginRight: 2 }}>Category:</span>
                    {[
                      { id: "all", label: "All" },
                      { id: "Languages", label: "Languages" },
                      { id: "Computer Science", label: "Computer Science" },
                      { id: "Databases", label: "Databases" },
                      { id: "Web Development", label: "Web Development" },
                    ].map((cat) => (
                      <button
                        key={cat.id}
                        onClick={() => setCategoryFilter(cat.id)}
                        style={{
                          fontSize: 11,
                          padding: "4px 10px",
                          borderRadius: 6,
                          border: "1px solid",
                          borderColor: categoryFilter === cat.id ? "var(--accent)" : "var(--line)",
                          background: categoryFilter === cat.id ? "rgba(168, 85, 247, 0.15)" : "transparent",
                          color: categoryFilter === cat.id ? "var(--accent)" : "var(--muted)",
                          cursor: "pointer",
                          fontWeight: categoryFilter === cat.id ? 600 : 400,
                        }}
                      >
                        {cat.label}
                      </button>
                    ))}
                  </div>

                  {/* Difficulty Chips */}
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, marginRight: 2 }}>Difficulty:</span>
                    {[
                      { id: "all", label: "All" },
                      { id: "Beginner", label: "Beginner" },
                      { id: "Intermediate", label: "Intermediate" },
                    ].map((diff) => (
                      <button
                        key={diff.id}
                        onClick={() => setDifficultyFilter(diff.id)}
                        style={{
                          fontSize: 11,
                          padding: "4px 10px",
                          borderRadius: 6,
                          border: "1px solid",
                          borderColor: difficultyFilter === diff.id ? "var(--teal)" : "var(--line)",
                          background: difficultyFilter === diff.id ? "rgba(0, 209, 178, 0.12)" : "transparent",
                          color: difficultyFilter === diff.id ? "var(--teal)" : "var(--muted)",
                          cursor: "pointer",
                          fontWeight: difficultyFilter === diff.id ? 600 : 400,
                        }}
                      >
                        {diff.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Grid of Curated Roadmap Cards */}
              {filteredCurated.length === 0 ? (
                <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
                  <Search size={32} style={{ margin: "0 auto 12px", opacity: 0.3 }} />
                  <div style={{ fontSize: 14, fontWeight: 600 }}>No roadmaps match your criteria</div>
                  <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                    Try clearing your search query or switching categories.
                  </p>
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      setCategoryFilter("all");
                      setDifficultyFilter("all");
                    }}
                    className="btn"
                    style={{ marginTop: 12, fontSize: 11 }}
                  >
                    Reset Filters
                  </button>
                </div>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
                    gap: 16,
                  }}
                >
                  {filteredCurated.map((rm) => {
                    const stats = calculateRoadmapProgress(rm, userProgressStore[rm.id]);
                    const topicCount = getTotalTopicCount(rm);

                    return (
                      <div
                        key={rm.id}
                        className="card"
                        onClick={() => setSelectedRoadmapId(rm.id)}
                        style={{
                          borderRadius: 12,
                          border: `1px solid ${stats.isStarted ? "rgba(0, 209, 178, 0.4)" : "var(--line)"}`,
                          padding: "18px 20px",
                          display: "flex",
                          flexDirection: "column",
                          justifyContent: "space-between",
                          cursor: "pointer",
                          transition: "all 0.18s ease",
                          position: "relative",
                          background: "var(--surface)",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = "translateY(-2px)";
                          e.currentTarget.style.borderColor = "var(--accent)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = "none";
                          e.currentTarget.style.borderColor = stats.isStarted
                            ? "rgba(0, 209, 178, 0.4)"
                            : "var(--line)";
                        }}
                      >
                        <div>
                          {/* Badges row */}
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                              <span
                                style={{
                                  fontSize: 10,
                                  fontWeight: 700,
                                  textTransform: "uppercase",
                                  padding: "2px 7px",
                                  borderRadius: 4,
                                  background: "rgba(168, 85, 247, 0.12)",
                                  color: "var(--accent)",
                                }}
                              >
                                {rm.category}
                              </span>
                              <span
                                style={{
                                  fontSize: 10,
                                  fontWeight: 600,
                                  padding: "2px 6px",
                                  borderRadius: 4,
                                  background: "var(--surface-2)",
                                  border: "1px solid var(--line)",
                                  color: "var(--muted)",
                                }}
                              >
                                {rm.difficulty}
                              </span>
                            </div>

                            <span
                              style={{
                                fontSize: 10,
                                color: "var(--muted)",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 4,
                              }}
                            >
                              <Clock size={11} /> {rm.estimatedDuration}
                            </span>
                          </div>

                          {/* Title & Tagline */}
                          <h3 style={{ fontSize: 17, fontWeight: 700, margin: "0 0 6px", color: "var(--fg)" }}>
                            {rm.title}
                          </h3>
                          <p
                            className="muted"
                            style={{
                              fontSize: 12,
                              lineHeight: 1.5,
                              margin: "0 0 16px",
                              display: "-webkit-box",
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                            }}
                          >
                            {rm.tagline}
                          </p>
                        </div>

                        {/* Card Footer: Progress & Button */}
                        <div>
                          {/* Curriculum details count */}
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              fontSize: 11,
                              color: "var(--muted)",
                              marginBottom: 8,
                            }}
                          >
                            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                              <Layers size={11} /> {rm.phases.length} Phases • {topicCount} Topics
                            </span>
                            <span style={{ color: "var(--teal)", fontWeight: 600 }}>
                              {stats.isStarted ? `${stats.percentage}% Done` : "Not Started"}
                            </span>
                          </div>

                          {/* Progress track */}
                          <div
                            className="progress-track"
                            style={{
                              height: 6,
                              borderRadius: 3,
                              background: "rgba(255,255,255,0.06)",
                              marginBottom: 14,
                            }}
                          >
                            <div
                              className="progress-value"
                              style={{
                                width: `${stats.percentage}%`,
                                height: "100%",
                                borderRadius: 3,
                                transition: "width 0.3s ease",
                              }}
                            />
                          </div>

                          {/* Action Button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedRoadmapId(rm.id);
                            }}
                            className={stats.isStarted ? "btn btn-primary" : "btn"}
                            style={{
                              width: "100%",
                              justifyContent: "center",
                              fontSize: 12,
                              padding: "8px 12px",
                            }}
                          >
                            {stats.isStarted ? (
                              <>Continue Path ({stats.completedTopics}/{stats.totalTopics})</>
                            ) : (
                              <>Start Learning Path</>
                            )}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* CUSTOM & AI ROADMAPS (PRESERVING EXISTING DATA & FUNCTIONALITY) */}
          {activeTab === "custom" && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <div>
                  <h2 style={{ fontSize: 16, margin: 0 }}>Custom & Generated Milestone Roadmaps</h2>
                  <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                    Custom capability-driven paths linked to your specific career goals and targets.
                  </p>
                </div>
                <button onClick={() => setShowGen(!showGen)} className="btn btn-primary" style={{ fontSize: 12 }}>
                  <Plus size={14} /> {showGen ? "Cancel" : "Create Custom Roadmap"}
                </button>
              </div>

              {showGen && (
                <section className="card card-pad" style={{ marginBottom: 24, border: "1px solid var(--accent)" }}>
                  <div className="card-kicker">Custom Track</div>
                  <div className="card-title" style={{ marginTop: 6, marginBottom: 14 }}>
                    Generate Personalized Custom Roadmap
                  </div>
                  <form onSubmit={handleGenerateCustom}>
                    <div className="field">
                      <label htmlFor="rmTitle">Roadmap Title / Career Track</label>
                      <input
                        id="rmTitle"
                        className="input"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g. Backend Platform Engineering or Cloud Infrastructure"
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

              {loadingCustom ? (
                <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
                  <Loader2 size={24} className="animate-spin text-muted" />
                </div>
              ) : customRoadmaps.length === 0 ? (
                <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
                  <Activity size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
                  <div style={{ fontSize: 15, fontWeight: 600 }}>No custom roadmaps active</div>
                  <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
                    Generate a personalized roadmap or explore our curated learning paths above.
                  </p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  {customRoadmaps.map((r) => (
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
                            <span
                              style={{
                                fontSize: 10,
                                background: "var(--surface)",
                                border: "1px solid var(--line)",
                                color: "var(--muted)",
                                padding: "2px 6px",
                                borderRadius: 4,
                              }}
                            >
                              Custom Milestone Track
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
                            onClick={() => handleDeleteCustomRoadmap(r.id)}
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
          )}
        </>
      )}
    </div>
  );
}
