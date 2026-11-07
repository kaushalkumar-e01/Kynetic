"use client";

import { useEffect, useState } from "react";
import { X, Sparkles, Loader2, BookOpen, AlertCircle, RefreshCw } from "lucide-react";
import { assistantApi } from "@/lib/api";
import { RoadmapTopic } from "@/data/roadmaps";
import AssistantMarkdown from "./AssistantMarkdown";

interface RoadmapTopicAiModalProps {
  topic: RoadmapTopic | null;
  roadmapTitle: string;
  onClose: () => void;
}

export function RoadmapTopicAiModal({ topic, roadmapTitle, onClose }: RoadmapTopicAiModalProps) {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"explain" | "quiz">("explain");

  const fetchAiTutoring = async (requestMode: "explain" | "quiz") => {
    if (!topic) return;
    setLoading(true);
    setError(null);

    const prompt =
      requestMode === "explain"
        ? `Act as an expert computer science tutor. Provide a clear, intuitive, and practical explanation of the topic "${topic.title}" from the ${roadmapTitle} curriculum.\n\nContext & Objectives:\n${topic.learningObjectives.map((o) => `- ${o}`).join("\n")}\n\nPlease include:\n1. Core concept intuition (in plain English)\n2. Key mechanics with a concise, well-annotated code example\n3. Common beginner mistakes and traps to avoid\n4. Real-world engineering application.`
        : `Generate a hands-on practice challenge and 2 conceptual quiz questions to test mastery of "${topic.title}" from ${roadmapTitle}.\n\nContext & Objectives:\n${topic.learningObjectives.map((o) => `- ${o}`).join("\n")}\n\nInclude questions, hints, and expected answers/explanations hidden below.`;

    try {
      const res = await assistantApi.sendMessage({ message: prompt });
      const lastMsg = res.messages && res.messages[res.messages.length - 1];
      if (lastMsg && lastMsg.content) {
        setResponse(lastMsg.content);
      } else {
        setResponse("No response received from AI tutor.");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || "Failed to reach AI tutor.");
      } else {
        setError("Failed to reach AI tutor.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (topic) {
      setResponse(null);
      setError(null);
      fetchAiTutoring(mode);
    }
  }, [topic, mode]);

  if (!topic) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(4px)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: 780,
          maxHeight: "88vh",
          display: "flex",
          flexDirection: "column",
          borderRadius: 14,
          border: "1px solid var(--accent)",
          boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
          overflow: "hidden",
          background: "var(--surface)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "16px 20px",
            borderBottom: "1px solid var(--line)",
            background: "rgba(168, 85, 247, 0.08)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: "rgba(168, 85, 247, 0.2)",
                color: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Sparkles size={18} />
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, color: "var(--accent)", fontWeight: 700 }}>
                AI Topic Companion • {roadmapTitle}
              </div>
              <h3 style={{ fontSize: 16, margin: "2px 0 0", fontWeight: 700 }}>{topic.title}</h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="icon-btn"
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 6,
              color: "var(--muted)",
              borderRadius: 6,
            }}
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Mode Selector */}
        <div
          style={{
            display: "flex",
            gap: 8,
            padding: "10px 20px",
            borderBottom: "1px solid var(--line)",
            background: "var(--surface-2)",
          }}
        >
          <button
            onClick={() => {
              if (mode !== "explain") setMode("explain");
            }}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              border: "1px solid",
              borderColor: mode === "explain" ? "var(--accent)" : "var(--line)",
              background: mode === "explain" ? "rgba(168, 85, 247, 0.15)" : "transparent",
              color: mode === "explain" ? "var(--accent)" : "var(--muted)",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <BookOpen size={13} /> Deep-Dive Explanation
          </button>
          <button
            onClick={() => {
              if (mode !== "quiz") setMode("quiz");
            }}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              border: "1px solid",
              borderColor: mode === "quiz" ? "var(--accent)" : "var(--line)",
              background: mode === "quiz" ? "rgba(168, 85, 247, 0.15)" : "transparent",
              color: mode === "quiz" ? "var(--accent)" : "var(--muted)",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <Sparkles size={13} /> Practice Challenge & Quiz
          </button>

          <button
            onClick={() => fetchAiTutoring(mode)}
            disabled={loading}
            style={{
              marginLeft: "auto",
              padding: "6px 10px",
              borderRadius: 6,
              fontSize: 11,
              cursor: "pointer",
              background: "transparent",
              border: "1px solid var(--line)",
              color: "var(--muted)",
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
            title="Regenerate explanation"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} /> Refresh
          </button>
        </div>

        {/* Content Body */}
        <div
          style={{
            padding: "20px",
            overflowY: "auto",
            flex: 1,
            lineHeight: 1.6,
          }}
        >
          {loading ? (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                minHeight: 220,
                gap: 12,
                color: "var(--muted)",
              }}
            >
              <Loader2 size={28} className="animate-spin text-accent" />
              <div style={{ fontSize: 13 }}>
                Generating structured explanation for <strong style={{ color: "var(--fg)" }}>{topic.title}</strong>...
              </div>
            </div>
          ) : error ? (
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 10,
                padding: "14px 16px",
                borderRadius: 8,
                background: "rgba(255, 107, 107, 0.1)",
                border: "1px solid rgba(255, 107, 107, 0.3)",
                color: "#ff8787",
                fontSize: 13,
              }}
            >
              <AlertCircle size={18} style={{ marginTop: 2, flexShrink: 0 }} />
              <div>
                <div style={{ fontWeight: 600 }}>Tutor request failed</div>
                <div style={{ fontSize: 12, marginTop: 2 }}>{error}</div>
                <button
                  onClick={() => fetchAiTutoring(mode)}
                  className="btn"
                  style={{ marginTop: 10, fontSize: 11, padding: "4px 10px" }}
                >
                  Try Again
                </button>
              </div>
            </div>
          ) : response ? (
            <AssistantMarkdown content={response} />
          ) : null}
        </div>

        {/* Footer Note */}
        <div
          style={{
            padding: "10px 20px",
            borderTop: "1px solid var(--line)",
            background: "var(--surface-2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: 11,
            color: "var(--muted)",
          }}
        >
          <span>Curriculum and verified learning resources remain immutable. AI provides on-demand conceptual tutoring.</span>
          <button onClick={onClose} className="btn" style={{ fontSize: 11, padding: "4px 12px" }}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
