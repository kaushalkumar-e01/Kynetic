"use client";

import { useMemo, useState } from "react";
import {
  ArrowLeft,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Circle,
  Clock,
  ExternalLink,
  Filter,
  Layers,
  ListChecks,
  RotateCcw,
  Search,
  Sparkles,
  Zap,
} from "lucide-react";
import {
  CuratedRoadmap,
  RoadmapTopic,
} from "@/data/roadmaps";
import {
  calculateRoadmapProgress,
  loadUserProgress,
  saveUserProgress,
  toggleTopicCompletion,
} from "@/lib/roadmap-progress";
import { RoadmapTopicAiModal } from "./RoadmapTopicAiModal";

interface CuratedRoadmapDetailViewProps {
  roadmap: CuratedRoadmap;
  userId?: string | null;
  onBack: () => void;
  onProgressChange?: () => void;
}

export function CuratedRoadmapDetailView({
  roadmap,
  userId,
  onBack,
  onProgressChange,
}: CuratedRoadmapDetailViewProps) {
  // Store progress locally in component state for instant rendering
  const [userProgressStore, setUserProgressStore] = useState(() => loadUserProgress(userId));
  const [topicSearch, setTopicSearch] = useState("");
  const [filterMode, setFilterMode] = useState<"all" | "essential" | "pending" | "completed">("all");

  // Track expanded phases and expanded topics
  const [expandedPhases, setExpandedPhases] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    roadmap.phases.forEach((p) => {
      init[p.id] = true; // default all phases open
    });
    return init;
  });

  const [expandedTopics, setExpandedTopics] = useState<Record<string, boolean>>({});

  // Active AI tutoring topic
  const [aiTopic, setAiTopic] = useState<RoadmapTopic | null>(null);

  const roadmapProgress = userProgressStore[roadmap.id] || {};
  const stats = useMemo(
    () => calculateRoadmapProgress(roadmap, roadmapProgress),
    [roadmap, roadmapProgress]
  );

  const handleToggleTopic = (topicId: string) => {
    const { updatedStore } = toggleTopicCompletion(userId, roadmap.id, topicId);
    setUserProgressStore(updatedStore);
    if (onProgressChange) onProgressChange();
  };

  const handleResetProgress = () => {
    if (
      !confirm(
        `Are you sure you want to reset your progress for "${roadmap.title}"? This will clear all checked topics.`
      )
    ) {
      return;
    }
    const updated = { ...userProgressStore, [roadmap.id]: {} };
    saveUserProgress(userId, updated);
    setUserProgressStore(updated);
    if (onProgressChange) onProgressChange();
  };

  const togglePhase = (phaseId: string) => {
    setExpandedPhases((prev) => ({ ...prev, [phaseId]: !prev[phaseId] }));
  };

  const toggleTopicExpand = (topicId: string) => {
    setExpandedTopics((prev) => ({ ...prev, [topicId]: !prev[topicId] }));
  };

  const handleExpandAll = (expand: boolean) => {
    const nextPhases: Record<string, boolean> = {};
    const nextTopics: Record<string, boolean> = {};
    roadmap.phases.forEach((p) => {
      nextPhases[p.id] = expand;
      p.topics.forEach((t) => {
        nextTopics[t.id] = expand;
      });
    });
    setExpandedPhases(nextPhases);
    setExpandedTopics(nextTopics);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* AI Tutoring Modal */}
      {aiTopic && (
        <RoadmapTopicAiModal
          topic={aiTopic}
          roadmapTitle={roadmap.title}
          onClose={() => setAiTopic(null)}
        />
      )}

      {/* Top Navigation Bar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <button
          onClick={onBack}
          className="btn"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            fontSize: 12,
            padding: "6px 12px",
          }}
        >
          <ArrowLeft size={14} /> Back to Learning Paths
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            onClick={() => handleExpandAll(true)}
            className="btn"
            style={{ fontSize: 11, padding: "5px 10px" }}
          >
            Expand All
          </button>
          <button
            onClick={() => handleExpandAll(false)}
            className="btn"
            style={{ fontSize: 11, padding: "5px 10px" }}
          >
            Collapse All
          </button>
          {stats.completedTopics > 0 && (
            <button
              onClick={handleResetProgress}
              className="btn"
              style={{
                fontSize: 11,
                padding: "5px 10px",
                color: "#ff8787",
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
              }}
              title="Reset progress"
            >
              <RotateCcw size={11} /> Reset Progress
            </button>
          )}
        </div>
      </div>

      {/* Roadmap Overview Hero Card */}
      <section
        className="card card-pad"
        style={{
          borderLeft: `4px solid ${roadmap.badgeColor || "var(--accent)"}`,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 8 }}>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  padding: "3px 8px",
                  borderRadius: 4,
                  background: "rgba(168, 85, 247, 0.15)",
                  color: "var(--accent)",
                  border: "1px solid rgba(168, 85, 247, 0.3)",
                }}
              >
                {roadmap.category}
              </span>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 600,
                  padding: "3px 8px",
                  borderRadius: 4,
                  background: "var(--surface-2)",
                  border: "1px solid var(--line)",
                  color: "var(--fg)",
                }}
              >
                {roadmap.difficulty}
              </span>
              <span
                style={{
                  fontSize: 10,
                  color: "var(--muted)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <Clock size={11} /> {roadmap.estimatedDuration}
              </span>
              <span
                style={{
                  fontSize: 10,
                  color: "var(--teal)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <BookOpen size={11} /> 100% Free Learning Resources
              </span>
            </div>

            <h1 style={{ fontSize: 24, fontWeight: 700, margin: "6px 0 8px" }}>{roadmap.title}</h1>
            <p style={{ fontSize: 13, color: "var(--fg)", opacity: 0.9, marginBottom: 8, lineHeight: 1.5 }}>
              {roadmap.tagline}
            </p>
            <p className="muted" style={{ fontSize: 12, lineHeight: 1.5 }}>
              {roadmap.description}
            </p>
          </div>

          {/* Progress Box */}
          <div
            style={{
              minWidth: 200,
              padding: "16px 20px",
              background: "var(--surface-2)",
              borderRadius: 10,
              border: "1px solid var(--line)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--muted)" }}>Overall Mastery</span>
              <span style={{ fontSize: 22, fontWeight: 800, color: "var(--teal)" }}>{stats.percentage}%</span>
            </div>

            <div className="progress-track" style={{ height: 8, borderRadius: 4, background: "rgba(255,255,255,0.08)" }}>
              <div
                className="progress-value"
                style={{
                  width: `${stats.percentage}%`,
                  height: "100%",
                  borderRadius: 4,
                  transition: "width 0.3s ease",
                }}
              />
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 11,
                color: "var(--muted)",
                marginTop: 8,
              }}
            >
              <span>{stats.completedTopics} of {stats.totalTopics} topics</span>
              {stats.isCompleted ? (
                <span style={{ color: "var(--teal)", fontWeight: 600, display: "flex", alignItems: "center", gap: 3 }}>
                  <Check size={12} /> Complete!
                </span>
              ) : (
                <span>{stats.totalTopics - stats.completedTopics} remaining</span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Filter and In-Roadmap Search Controls */}
      <div
        className="card card-pad"
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          padding: "12px 16px",
        }}
      >
        <div style={{ position: "relative", flex: 1, minWidth: 220 }}>
          <Search
            size={14}
            style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--muted)" }}
          />
          <input
            type="text"
            className="input"
            placeholder="Search topics, concepts, or resources..."
            value={topicSearch}
            onChange={(e) => setTopicSearch(e.target.value)}
            style={{ paddingLeft: 30, fontSize: 12 }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
          <span style={{ fontSize: 11, color: "var(--muted)", display: "flex", alignItems: "center", gap: 4, marginRight: 4 }}>
            <Filter size={12} /> Filter:
          </span>
          {(
            [
              { id: "all", label: "All Topics" },
              { id: "essential", label: "Essential Only" },
              { id: "pending", label: "Pending" },
              { id: "completed", label: "Completed" },
            ] as const
          ).map((m) => (
            <button
              key={m.id}
              onClick={() => setFilterMode(m.id)}
              style={{
                fontSize: 11,
                padding: "4px 10px",
                borderRadius: 6,
                border: "1px solid",
                borderColor: filterMode === m.id ? "var(--accent)" : "var(--line)",
                background: filterMode === m.id ? "rgba(168, 85, 247, 0.15)" : "transparent",
                color: filterMode === m.id ? "var(--accent)" : "var(--muted)",
                cursor: "pointer",
                fontWeight: filterMode === m.id ? 600 : 400,
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Curriculum Phases & Interactive Topics */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {roadmap.phases.map((phase) => {
          const phaseStat = stats.phases[phase.id] || {
            totalTopics: phase.topics.length,
            completedTopics: 0,
            percentage: 0,
          };

          // Filter topics based on search & filterMode
          const query = topicSearch.trim().toLowerCase();
          const filteredTopics = phase.topics.filter((t) => {
            const isCompleted = !!roadmapProgress[t.id]?.completed;

            if (filterMode === "essential" && !t.isEssential) return false;
            if (filterMode === "pending" && isCompleted) return false;
            if (filterMode === "completed" && !isCompleted) return false;

            if (query) {
              const inTitle = t.title.toLowerCase().includes(query);
              const inDesc = t.shortDescription.toLowerCase().includes(query);
              const inObjs = t.learningObjectives.some((o) => o.toLowerCase().includes(query));
              const inRes = t.resources.some(
                (r) => r.title.toLowerCase().includes(query) || r.publisher.toLowerCase().includes(query)
              );
              return inTitle || inDesc || inObjs || inRes;
            }

            return true;
          });

          // If searching or filtering and no topics match in this phase, hide phase
          if (filteredTopics.length === 0 && (query || filterMode !== "all")) {
            return null;
          }

          const isPhaseExpanded = expandedPhases[phase.id] ?? true;

          return (
            <div
              key={phase.id}
              className="card"
              style={{
                borderRadius: 10,
                border: "1px solid var(--line)",
                overflow: "hidden",
                background: "var(--surface)",
              }}
            >
              {/* Phase Header Accordion */}
              <div
                onClick={() => togglePhase(phase.id)}
                style={{
                  padding: "14px 18px",
                  background: "var(--surface-2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  cursor: "pointer",
                  userSelect: "none",
                  borderBottom: isPhaseExpanded ? "1px solid var(--line)" : "none",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: "50%",
                      background: phaseStat.percentage === 100 ? "rgba(0, 209, 178, 0.2)" : "rgba(168, 85, 247, 0.2)",
                      color: phaseStat.percentage === 100 ? "var(--teal)" : "var(--accent)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 12,
                      fontWeight: 700,
                      flexShrink: 0,
                    }}
                  >
                    {phaseStat.percentage === 100 ? <Check size={14} /> : phase.order}
                  </div>
                  <div>
                    <h2 style={{ fontSize: 14, fontWeight: 700, margin: 0, color: "var(--fg)" }}>{phase.title}</h2>
                    <p className="muted" style={{ fontSize: 11, margin: "2px 0 0" }}>
                      {phase.description}
                    </p>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: phaseStat.percentage === 100 ? "var(--teal)" : "var(--muted)" }}>
                      {phaseStat.completedTopics} / {phaseStat.totalTopics} Done ({phaseStat.percentage}%)
                    </div>
                    <div
                      style={{
                        width: 90,
                        height: 5,
                        background: "rgba(255,255,255,0.08)",
                        borderRadius: 3,
                        marginTop: 4,
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${phaseStat.percentage}%`,
                          height: "100%",
                          background: phaseStat.percentage === 100 ? "var(--teal)" : "var(--accent)",
                        }}
                      />
                    </div>
                  </div>

                  <span style={{ color: "var(--muted)" }}>
                    {isPhaseExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </span>
                </div>
              </div>

              {/* Phase Topics List */}
              {isPhaseExpanded && (
                <div style={{ padding: "12px 16px", display: "flex", flexDirection: "column", gap: 10 }}>
                  {filteredTopics.map((topic) => {
                    const isCompleted = !!roadmapProgress[topic.id]?.completed;
                    const isTopicExpanded = expandedTopics[topic.id] ?? false;

                    return (
                      <div
                        key={topic.id}
                        style={{
                          borderRadius: 8,
                          border: `1px solid ${isCompleted ? "rgba(0, 209, 178, 0.3)" : "var(--line)"}`,
                          background: isCompleted ? "rgba(0, 209, 178, 0.04)" : "var(--surface-2)",
                          overflow: "hidden",
                          transition: "border-color 0.2s ease",
                        }}
                      >
                        {/* Topic Main Bar */}
                        <div
                          style={{
                            padding: "12px 14px",
                            display: "flex",
                            alignItems: "center",
                            gap: 12,
                          }}
                        >
                          {/* Completion Checkbox */}
                          <button
                            onClick={() => handleToggleTopic(topic.id)}
                            style={{
                              background: "none",
                              border: "none",
                              padding: 0,
                              cursor: "pointer",
                              color: isCompleted ? "var(--teal)" : "var(--muted)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexShrink: 0,
                            }}
                            title={isCompleted ? "Mark pending" : "Mark completed"}
                            aria-label={isCompleted ? "Mark pending" : "Mark completed"}
                          >
                            {isCompleted ? <CheckCircle2 size={20} /> : <Circle size={20} />}
                          </button>

                          {/* Topic Info */}
                          <div
                            onClick={() => toggleTopicExpand(topic.id)}
                            style={{ flex: 1, cursor: "pointer", userSelect: "none" }}
                          >
                            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                              <span
                                style={{
                                  fontSize: 13,
                                  fontWeight: 600,
                                  textDecoration: isCompleted ? "line-through" : "none",
                                  color: isCompleted ? "var(--muted)" : "var(--fg)",
                                }}
                              >
                                {topic.title}
                              </span>

                              {topic.isEssential ? (
                                <span
                                  style={{
                                    fontSize: 9,
                                    fontWeight: 700,
                                    textTransform: "uppercase",
                                    padding: "2px 6px",
                                    borderRadius: 3,
                                    background: "rgba(168, 85, 247, 0.15)",
                                    color: "var(--accent)",
                                  }}
                                >
                                  Essential
                                </span>
                              ) : (
                                <span
                                  style={{
                                    fontSize: 9,
                                    padding: "2px 6px",
                                    borderRadius: 3,
                                    background: "rgba(255,255,255,0.06)",
                                    color: "var(--muted)",
                                  }}
                                >
                                  Deep Dive
                                </span>
                              )}

                              <span
                                style={{
                                  fontSize: 10,
                                  color: "var(--muted)",
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: 3,
                                }}
                              >
                                <BookOpen size={10} /> {topic.resources.length} free resources
                              </span>
                            </div>

                            <p
                              className="muted"
                              style={{
                                fontSize: 11,
                                margin: "4px 0 0",
                                lineHeight: 1.4,
                                display: "-webkit-box",
                                WebkitLineClamp: isTopicExpanded ? "unset" : 1,
                                WebkitBoxOrient: "vertical",
                                overflow: "hidden",
                              }}
                            >
                              {topic.shortDescription}
                            </p>
                          </div>

                          {/* Actions: AI Explainer & Expand Chevron */}
                          <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                            <button
                              onClick={() => setAiTopic(topic)}
                              className="btn"
                              style={{
                                fontSize: 10,
                                padding: "4px 8px",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 4,
                                color: "var(--accent)",
                                border: "1px solid rgba(168, 85, 247, 0.35)",
                                background: "rgba(168, 85, 247, 0.08)",
                              }}
                              title="Ask AI Companion to explain this concept"
                            >
                              <Sparkles size={11} /> Explain
                            </button>

                            <button
                              onClick={() => toggleTopicExpand(topic.id)}
                              style={{
                                background: "none",
                                border: "none",
                                padding: 4,
                                cursor: "pointer",
                                color: "var(--muted)",
                              }}
                              aria-label="Toggle topic details"
                            >
                              {isTopicExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>
                          </div>
                        </div>

                        {/* Expanded Topic Details Accordion */}
                        {isTopicExpanded && (
                          <div
                            style={{
                              padding: "12px 14px 14px 46px",
                              borderTop: "1px solid var(--line)",
                              background: "rgba(0,0,0,0.15)",
                              display: "flex",
                              flexDirection: "column",
                              gap: 12,
                            }}
                          >
                            {/* Prerequisites */}
                            {topic.prerequisites && topic.prerequisites.length > 0 && (
                              <div style={{ fontSize: 11, color: "var(--muted)" }}>
                                <span style={{ fontWeight: 600, color: "var(--fg)" }}>Prerequisites: </span>
                                {topic.prerequisites.join(", ")}
                              </div>
                            )}

                            {/* Learning Objectives Checklist */}
                            <div>
                              <div
                                style={{
                                  fontSize: 11,
                                  fontWeight: 700,
                                  color: "var(--fg)",
                                  marginBottom: 6,
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 6,
                                }}
                              >
                                <ListChecks size={13} color="var(--accent)" /> Learning Objectives & Key Takeaways:
                              </div>
                              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: "var(--muted)", lineHeight: 1.6 }}>
                                {topic.learningObjectives.map((obj, i) => (
                                  <li key={i}>{obj}</li>
                                ))}
                              </ul>
                            </div>

                            {/* Mandatory Verified Free Learning Resources */}
                            <div>
                              <div
                                style={{
                                  fontSize: 11,
                                  fontWeight: 700,
                                  color: "var(--teal)",
                                  marginBottom: 8,
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 6,
                                }}
                              >
                                <BookOpen size={13} /> Free Learning Resources & Official Guides:
                              </div>

                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 8 }}>
                                {topic.resources.map((res, ri) => (
                                  <a
                                    key={ri}
                                    href={res.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      display: "flex",
                                      flexDirection: "column",
                                      justifyContent: "space-between",
                                      padding: "8px 10px",
                                      borderRadius: 6,
                                      background: "var(--surface)",
                                      border: "1px solid var(--line)",
                                      textDecoration: "none",
                                      transition: "all 0.15s ease",
                                    }}
                                    className="resource-card-hover"
                                  >
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 6 }}>
                                      <span
                                        style={{
                                          fontSize: 9,
                                          fontWeight: 700,
                                          textTransform: "uppercase",
                                          padding: "1px 5px",
                                          borderRadius: 3,
                                          background: "rgba(0, 209, 178, 0.12)",
                                          color: "var(--teal)",
                                        }}
                                      >
                                        {res.publisher}
                                      </span>
                                      <span
                                        style={{
                                          fontSize: 9,
                                          color: "var(--muted)",
                                          textTransform: "capitalize",
                                        }}
                                      >
                                        {res.type}
                                      </span>
                                    </div>

                                    <div
                                      style={{
                                        fontSize: 11,
                                        fontWeight: 600,
                                        color: "var(--fg)",
                                        marginTop: 6,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "space-between",
                                        gap: 4,
                                      }}
                                    >
                                      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                        {res.title}
                                      </span>
                                      <ExternalLink size={10} color="var(--accent)" style={{ flexShrink: 0 }} />
                                    </div>
                                  </a>
                                ))}
                              </div>
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
        })}
      </div>
    </div>
  );
}
