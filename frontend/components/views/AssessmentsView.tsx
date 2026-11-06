"use client";

import { useEffect, useState, useCallback } from "react";
import {
  AlertCircle,
  Award,
  BookOpenCheck,
  Check,
  CheckCircle2,
  Code2,
  Database,
  HelpCircle,
  Layers,
  Loader2,
  Play,
  RotateCcw,
  Sparkles,
  Terminal,
  TrendingDown,
  TrendingUp,
  XCircle,
  Bug,
  Brain,
  ListChecks,
} from "lucide-react";
import { assessmentsApi } from "@/lib/api";
import type {
  AssessmentResponse,
  AssessmentSummaryResultsResponse,
  AssessmentTopicResponse,
  QuestionPublicResponse,
} from "@/types";

interface ParsedQuestionLayout {
  title: string;
  description: string;
  codeSnippet?: string;
  codeLanguage?: string;
  questionTask?: string;
}

function parseQuestionLayout(q: QuestionPublicResponse): ParsedQuestionLayout {
  let title = (q.title || "").replace(/^###\s*/, "").trim();
  let rawPrompt = (q.prompt || "").trim();

  if (!title && rawPrompt.startsWith("### ")) {
    const lines = rawPrompt.split("\n");
    title = lines[0].replace(/^###\s*/, "").trim();
    rawPrompt = lines.slice(1).join("\n").trim();
  } else if (rawPrompt.startsWith("### ")) {
    rawPrompt = rawPrompt.replace(/^###\s*[^\n]+\n*/, "").trim();
  }

  let codeSnippet = q.starter_code?.trim() || "";
  let codeLanguage = q.programming_language && q.programming_language !== "none" ? q.programming_language : "";

  const codeBlockMatch = rawPrompt.match(/```(\w+)?\n([\s\S]*?)```/);
  if (codeBlockMatch) {
    if (!codeSnippet) {
      codeLanguage = codeBlockMatch[1] || codeLanguage;
      codeSnippet = codeBlockMatch[2].trim();
    }
    rawPrompt = rawPrompt.replace(/```(\w+)?\n([\s\S]*?)```/, "").trim();
  }

  let description = rawPrompt;
  let questionTask = "";

  const taskRegex = /(what is (?:the )?(?:output|result|defect|time complexity|functional difference)[\s\S]*\?|which (?:of the following|statement)[\s\S]*\?|identify the [\s\S]*\?|in [\w\s]+, what [\s\S]*\?|analyze [\s\S]*\?|how does [\s\S]*\?|why does [\s\S]*\?)/i;
  const match = rawPrompt.match(taskRegex);
  if (match) {
    const taskIdx = rawPrompt.indexOf(match[0]);
    if (taskIdx > 0) {
      description = rawPrompt.substring(0, taskIdx).trim();
      questionTask = rawPrompt.substring(taskIdx).trim();
    } else {
      questionTask = rawPrompt;
      description = "";
    }
  }

  description = description.replace(/^#+\s+/gm, "").replace(/\*\*/g, "");
  questionTask = questionTask.replace(/^#+\s+/gm, "").replace(/\*\*/g, "");

  return {
    title: title || "Assessment Challenge",
    description,
    codeSnippet,
    codeLanguage,
    questionTask: questionTask || description,
  };
}

export default function AssessmentsView() {
  const [topics, setTopics] = useState<AssessmentTopicResponse[]>([]);
  const [pastAssessments, setPastAssessments] = useState<AssessmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [selectedMode, setSelectedMode] = useState<"mixed" | "coding" | "quiz" | "sql">("mixed");

  // Active assessment session state
  const [activeAssessment, setActiveAssessment] = useState<AssessmentResponse | null>(null);
  const [currentQ, setCurrentQ] = useState<QuestionPublicResponse | null>(null);

  // Per-question response states
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [codeValue, setCodeValue] = useState<string>("");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("python");
  const [activeTestTab, setActiveTestTab] = useState<number>(0);
  const [sqlValue, setSqlValue] = useState<string>("");
  const [outputGuess, setOutputGuess] = useState<string>("");
  const [conceptualText, setConceptualText] = useState<string>("");

  // Sandbox run state
  const [runningTests, setRunningTests] = useState(false);
  const [testOutput, setTestOutput] = useState<{
    status: string;
    passed_tests: number;
    total_tests: number;
    test_results?: Array<{ inputs?: unknown[]; expected?: unknown; actual?: unknown; passed?: boolean; error?: string; duration_ms?: number }>;
    error_message?: string;
    quality_metrics?: {
      estimated_time_complexity?: string;
      estimated_space_complexity?: string;
      quality_score?: number;
      max_loop_depth?: number;
    };
    integrity_flags?: string[];
  } | null>(null);

  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [lastFeedback, setLastFeedback] = useState<{ isCorrect: boolean; text: string; score: number } | null>(null);
  const [summaryResults, setSummaryResults] = useState<AssessmentSummaryResultsResponse | null>(null);
  const [loadingPastResultId, setLoadingPastResultId] = useState<string | null>(null);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const loadInitialData = useCallback(() => {
    setLoading(true);
    Promise.allSettled([assessmentsApi.listTopics(), assessmentsApi.listAssessments()]).then(
      ([topRes, assRes]) => {
        if (topRes.status === "fulfilled") {
          setTopics(topRes.value);
          if (topRes.value.length > 0 && !selectedTopic) {
            setSelectedTopic(topRes.value[0].name);
          }
        }
        if (assRes.status === "fulfilled") {
          setPastAssessments(assRes.value);
        }
        setLoading(false);
      }
    );
  }, [selectedTopic]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Sync question state whenever current_question changes
  const applyQuestionState = useCallback((q: QuestionPublicResponse | null) => {
    setCurrentQ(q);
    setSelectedOption("");
    setOutputGuess("");
    setConceptualText("");
    setTestOutput(null);
    setActiveTestTab(0);
    if (q) {
      const initialLang = (q.programming_language && ["python", "javascript", "typescript", "c", "cpp", "java"].includes(q.programming_language.toLowerCase()))
        ? q.programming_language.toLowerCase()
        : "python";
      setSelectedLanguage(initialLang);
      if (q.starter_codes && q.starter_codes[initialLang]) {
        setCodeValue(q.starter_codes[initialLang]);
      } else {
        setCodeValue(q.starter_code || "");
      }
      setSqlValue("");
    } else {
      setCodeValue("");
      setSqlValue("");
    }
  }, []);

  const handleLanguageChange = (lang: string) => {
    setSelectedLanguage(lang);
    if (currentQ?.starter_codes && currentQ.starter_codes[lang]) {
      setCodeValue(currentQ.starter_codes[lang]);
    } else if (lang === (currentQ?.programming_language || "").toLowerCase()) {
      setCodeValue(currentQ?.starter_code || "");
    }
  };

  const handleEditorKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const val = target.value;
      const newVal = val.substring(0, start) + "    " + val.substring(end);
      setCodeValue(newVal);
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      });
    }
  };

  const handleStartAssessment = async () => {
    setStarting(true);
    setErrorMessage(null);
    setLastFeedback(null);
    setSummaryResults(null);

    const modeLabels: Record<string, string> = {
      mixed: "Mixed Mastery",
      coding: "Coding Sandbox",
      quiz: "Technical Quiz",
      sql: "SQL Mastery",
    };

    try {
      const assessment = await assessmentsApi.createAssessment({
        mode: selectedMode,
        selected_topics: selectedTopic ? [selectedTopic] : [],
        title: `${selectedTopic || "Technical"} ${modeLabels[selectedMode] || "Assessment"}`,
      });

      setActiveAssessment(assessment);
      applyQuestionState(assessment.current_question || null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to start assessment.");
      }
    } finally {
      setStarting(false);
    }
  };

  const handleAdvanceToNextQuestion = async (assessmentId: string) => {
    try {
      const refreshed = await assessmentsApi.getAssessment(assessmentId);
      if (refreshed.current_question) {
        setActiveAssessment(refreshed);
        applyQuestionState(refreshed.current_question);
      } else {
        const results = await assessmentsApi.getAssessmentResults(assessmentId);
        setSummaryResults(results);
        setActiveAssessment(null);
        applyQuestionState(null);
        loadInitialData();
      }
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  // Submit Answer for MCQ, Output Prediction, Debugging, SQL, and Conceptual questions
  const handleSubmitGenericAnswer = async (answerPayload: string) => {
    if (!activeAssessment || !currentQ || !answerPayload.trim()) return;

    setSubmittingAnswer(true);
    setErrorMessage(null);

    try {
      const attempt = await assessmentsApi.submitAnswer(activeAssessment.id, {
        question_id: currentQ.id,
        answer: answerPayload,
      });

      setLastFeedback({
        isCorrect: attempt.is_correct ?? false,
        text: attempt.feedback || (attempt.is_correct ? "Correct answer!" : "Incorrect."),
        score: attempt.score,
      });

      await handleAdvanceToNextQuestion(activeAssessment.id);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to submit response.");
      }
    } finally {
      setSubmittingAnswer(false);
    }
  };

  // Run candidate code against public/sample test cases only
  const handleRunCodeTests = async () => {
    if (!activeAssessment || !currentQ || !codeValue.trim()) return;

    setRunningTests(true);
    setErrorMessage(null);

    try {
      const result = await assessmentsApi.runCode(activeAssessment.id, {
        question_id: currentQ.id,
        code: codeValue,
      });
      setTestOutput(result as typeof testOutput);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Sandbox execution failed.");
      }
    } finally {
      setRunningTests(false);
    }
  };

  // Final code submission evaluated in sandbox against complete test suite
  const handleSubmitCodeSolution = async () => {
    if (!activeAssessment || !currentQ || !codeValue.trim()) return;

    setSubmittingAnswer(true);
    setErrorMessage(null);

    try {
      const attempt = await assessmentsApi.submitCode(activeAssessment.id, {
        question_id: currentQ.id,
        code: codeValue,
      });

      setLastFeedback({
        isCorrect: attempt.is_correct ?? false,
        text: attempt.feedback || (attempt.is_correct ? "All unit tests passed!" : "Test failures detected."),
        score: attempt.score,
      });

      await handleAdvanceToNextQuestion(activeAssessment.id);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to submit code solution.");
      }
    } finally {
      setSubmittingAnswer(false);
    }
  };

  const handleFinishEarly = async () => {
    if (!activeAssessment) return;
    try {
      const results = await assessmentsApi.getAssessmentResults(activeAssessment.id);
      setSummaryResults(results);
      setActiveAssessment(null);
      applyQuestionState(null);
      loadInitialData();
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  const handleViewPastResults = async (assessmentId: string) => {
    setLoadingPastResultId(assessmentId);
    setErrorMessage(null);
    try {
      const results = await assessmentsApi.getAssessmentResults(assessmentId);
      setSummaryResults(results);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    } finally {
      setLoadingPastResultId(null);
    }
  };

  // Helpers for difficulty pill coloring
  const getDifficultyPill = (level?: number, label?: string) => {
    const lvl = level || 2;
    const colors: Record<number, { bg: string; text: string; name: string }> = {
      1: { bg: "rgba(38, 169, 154, 0.14)", text: "var(--teal)", name: "Level 1 • Very Easy" },
      2: { bg: "rgba(38, 169, 154, 0.2)", text: "var(--teal)", name: "Level 2 • Easy" },
      3: { bg: "rgba(108, 99, 255, 0.15)", text: "var(--accent)", name: "Level 3 • Medium" },
      4: { bg: "rgba(239, 174, 75, 0.15)", text: "var(--amber)", name: "Level 4 • Hard" },
      5: { bg: "rgba(255, 120, 60, 0.15)", text: "#ff783c", name: "Level 5 • Very Hard" },
      6: { bg: "rgba(230, 109, 118, 0.18)", text: "var(--danger)", name: "Level 6 • Expert" },
    };
    const conf = colors[lvl] || colors[2];
    return (
      <span
        style={{
          fontSize: 10,
          textTransform: "uppercase",
          fontWeight: 700,
          padding: "3px 8px",
          borderRadius: 4,
          background: conf.bg,
          color: conf.text,
          letterSpacing: "0.06em",
        }}
      >
        {label || conf.name}
      </span>
    );
  };

  const getQuestionTypeIcon = (type?: string) => {
    switch (type) {
      case "coding":
        return <Code2 size={15} color="var(--accent)" />;
      case "sql":
        return <Database size={15} color="var(--teal)" />;
      case "output_prediction":
        return <Terminal size={15} color="var(--amber)" />;
      case "debugging":
        return <Bug size={15} color="var(--danger)" />;
      case "conceptual":
        return <Brain size={15} color="var(--violet)" />;
      default:
        return <ListChecks size={15} color="var(--accent)" />;
    }
  };

  const correctAttempts = summaryResults?.attempts?.filter((a) => a.is_correct) || [];
  const incorrectAttempts = summaryResults?.attempts?.filter((a) => !a.is_correct) || [];

  return (
    <div>
      {statusMessage && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            background: "rgba(38, 169, 154, 0.12)",
            border: "1px solid rgba(38, 169, 154, 0.35)",
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
            background: "rgba(230, 109, 118, 0.12)",
            border: "1px solid rgba(230, 109, 118, 0.35)",
            borderRadius: 8,
            color: "var(--danger)",
            fontSize: 12,
            marginBottom: 16,
          }}
        >
          <AlertCircle size={15} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* =====================================================================
          ACTIVE ASSESSMENT SESSION: Multi-Interface Dynamic Engine
      ===================================================================== */}
      {activeAssessment && currentQ && (
        <section
          className="card card-pad"
          style={{
            marginBottom: 32,
            border: "2px solid var(--accent)",
            background: "var(--surface)",
            boxShadow: "0 18px 45px rgba(108, 99, 255, 0.12)",
          }}
        >
          {/* Header Bar */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 14,
              flexWrap: "wrap",
              gap: 12,
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="card-kicker">
                  {activeAssessment.mode === "coding"
                    ? "Live Code Execution Sandbox"
                    : activeAssessment.mode === "sql"
                    ? "Interactive SQL Engine"
                    : "Live Adaptive Skill Assessment"}
                </span>
                <span
                  style={{
                    fontSize: 10,
                    textTransform: "uppercase",
                    padding: "2px 6px",
                    borderRadius: 4,
                    background: "var(--surface-2)",
                    color: "var(--muted)",
                    fontWeight: 700,
                  }}
                >
                  Mode: {activeAssessment.mode}
                </span>
              </div>
              <h2 style={{ fontSize: 19, margin: "4px 0" }}>{activeAssessment.title}</h2>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <button onClick={handleFinishEarly} className="btn btn-outline" style={{ fontSize: 11 }}>
                Complete & View Results
              </button>
            </div>
          </div>

          {/* Feedback from previous question attempt */}
          {lastFeedback && (
            <div
              style={{
                padding: "10px 14px",
                borderRadius: 8,
                marginBottom: 16,
                fontSize: 12,
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: lastFeedback.isCorrect ? "rgba(38, 169, 154, 0.12)" : "rgba(230, 109, 118, 0.12)",
                border: `1px solid ${
                  lastFeedback.isCorrect ? "rgba(38, 169, 154, 0.35)" : "rgba(230, 109, 118, 0.35)"
                }`,
                color: lastFeedback.isCorrect ? "var(--teal)" : "var(--danger)",
              }}
            >
              {lastFeedback.isCorrect ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
              <span>
                <strong>{lastFeedback.isCorrect ? "Correct!" : "Feedback:"}</strong> {lastFeedback.text} (Score:{" "}
                {Math.round(lastFeedback.score)}%)
              </span>
            </div>
          )}

          {/* Question Metadata Bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              paddingBottom: 14,
              borderBottom: "1px solid var(--line)",
              marginBottom: 16,
              flexWrap: "wrap",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              {getQuestionTypeIcon(currentQ.question_type)}
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--text)" }}>
                {currentQ.question_type.replace("_", " ")}
              </span>
            </div>

            {getDifficultyPill(currentQ.difficulty_level, `Tier: ${currentQ.difficulty}`)}

            {currentQ.category && (
              <span
                style={{
                  fontSize: 10,
                  textTransform: "uppercase",
                  fontWeight: 600,
                  padding: "3px 7px",
                  borderRadius: 4,
                  background: "var(--surface-2)",
                  color: "var(--muted)",
                }}
              >
                {currentQ.category.replace("_", " ")}
              </span>
            )}

            {currentQ.programming_language && currentQ.programming_language !== "none" && (
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  padding: "3px 7px",
                  borderRadius: 4,
                  background: "var(--accent-soft)",
                  color: "var(--accent)",
                }}
              >
                {currentQ.programming_language}
              </span>
            )}
          </div>

          {/* =================================================================
              INTERFACE 1: CODING CHALLENGE (LeetCode / HackerRank Style)
          ================================================================= */}
          {currentQ.question_type === "coding" && (
            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1.3fr", gap: 20 }}>
              {/* Left Column: Problem Prompt & Specs */}
              <div
                style={{
                  background: "var(--surface-2)",
                  padding: 20,
                  borderRadius: 10,
                  border: "1px solid var(--line)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 16,
                  maxHeight: "820px",
                  overflowY: "auto",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
                    {getDifficultyPill(currentQ.difficulty_level, currentQ.difficulty)}
                    {currentQ.subtopic && (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 600,
                          padding: "2px 8px",
                          borderRadius: 4,
                          background: "var(--surface)",
                          border: "1px solid var(--line)",
                          color: "var(--text)",
                        }}
                      >
                        {currentQ.subtopic}
                      </span>
                    )}
                  </div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, margin: "4px 0 12px", color: "var(--text)" }}>
                    {currentQ.title || "Coding Challenge"}
                  </h2>
                  <div
                    style={{
                      fontSize: 13,
                      lineHeight: 1.7,
                      color: "var(--text)",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {currentQ.prompt.replace(/^###\s+[^\n]+\n+/, "")}
                  </div>
                </div>

                {/* Formatted Examples */}
                {currentQ.examples && currentQ.examples.length > 0 ? (
                  <div>
                    <div
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        color: "var(--muted)",
                        marginBottom: 8,
                        letterSpacing: "0.05em",
                      }}
                    >
                      Examples
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      {currentQ.examples.map((ex, idx) => (
                        <div
                          key={idx}
                          style={{
                            background: "var(--surface)",
                            border: "1px solid var(--line)",
                            padding: "10px 14px",
                            borderRadius: 6,
                            fontSize: 12,
                          }}
                        >
                          <div
                            style={{
                              color: "var(--accent)",
                              fontSize: 11,
                              textTransform: "uppercase",
                              fontWeight: 700,
                              marginBottom: 6,
                            }}
                          >
                            Example {idx + 1}
                          </div>
                          <div style={{ marginBottom: 4 }}>
                            <strong style={{ color: "var(--muted)" }}>Input: </strong>
                            <code className="mono" style={{ color: "var(--text)" }}>{ex.input}</code>
                          </div>
                          <div style={{ marginBottom: ex.explanation ? 4 : 0 }}>
                            <strong style={{ color: "var(--muted)" }}>Output: </strong>
                            <code className="mono" style={{ color: "var(--teal)", fontWeight: 700 }}>{ex.output}</code>
                          </div>
                          {ex.explanation && (
                            <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>
                              <strong>Explanation: </strong>{ex.explanation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : currentQ.sample_test_cases && currentQ.sample_test_cases.length > 0 ? (
                  <div>
                    <div
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        color: "var(--muted)",
                        marginBottom: 8,
                        letterSpacing: "0.05em",
                      }}
                    >
                      Examples
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      {currentQ.sample_test_cases.map((tc, idx) => (
                        <div
                          key={idx}
                          style={{
                            background: "var(--surface)",
                            border: "1px solid var(--line)",
                            padding: "10px 14px",
                            borderRadius: 6,
                            fontSize: 12,
                          }}
                        >
                          <div
                            style={{
                              color: "var(--accent)",
                              fontSize: 11,
                              textTransform: "uppercase",
                              fontWeight: 700,
                              marginBottom: 6,
                            }}
                          >
                            Example {idx + 1}
                          </div>
                          <div style={{ marginBottom: 4 }}>
                            <strong style={{ color: "var(--muted)" }}>Input: </strong>
                            <code className="mono">{JSON.stringify(tc.inputs)}</code>
                          </div>
                          <div>
                            <strong style={{ color: "var(--muted)" }}>Output: </strong>
                            <code className="mono" style={{ color: "var(--teal)", fontWeight: 700 }}>
                              {JSON.stringify(tc.expected)}
                            </code>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {/* Constraints */}
                {currentQ.constraints && currentQ.constraints.length > 0 && (
                  <div>
                    <div
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        color: "var(--muted)",
                        marginBottom: 8,
                        letterSpacing: "0.05em",
                      }}
                    >
                      Constraints
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.8, color: "var(--text)" }}>
                      {currentQ.constraints.map((c, idx) => (
                        <li key={idx} className="mono">
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Column: Code Editor & Execution Sandbox */}
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {/* Editor Header: Language Selector & Reset */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    background: "var(--surface-2)",
                    padding: "8px 12px",
                    borderRadius: 8,
                    border: "1px solid var(--line)",
                    flexWrap: "wrap",
                    gap: 8,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Code2 size={16} color="var(--accent)" />
                    <span style={{ fontSize: 12, fontWeight: 700 }}>Language:</span>
                    <div style={{ display: "flex", gap: 4 }}>
                      {[
                        { key: "python", label: "Python 3" },
                        { key: "javascript", label: "JavaScript" },
                        { key: "typescript", label: "TypeScript" },
                        { key: "c", label: "C" },
                        { key: "cpp", label: "C++" },
                        { key: "java", label: "Java" },
                      ].map((l) => (
                        <button
                          key={l.key}
                          type="button"
                          onClick={() => handleLanguageChange(l.key)}
                          style={{
                            fontSize: 11,
                            padding: "3px 8px",
                            borderRadius: 4,
                            border: selectedLanguage === l.key ? "1px solid var(--accent)" : "1px solid var(--line)",
                            background: selectedLanguage === l.key ? "var(--accent)" : "var(--surface)",
                            color: selectedLanguage === l.key ? "#fff" : "var(--muted)",
                            fontWeight: selectedLanguage === l.key ? 700 : 500,
                            cursor: "pointer",
                          }}
                        >
                          {l.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      if (currentQ.starter_codes && currentQ.starter_codes[selectedLanguage]) {
                        setCodeValue(currentQ.starter_codes[selectedLanguage]);
                      } else {
                        setCodeValue(currentQ.starter_code || "");
                      }
                    }}
                    className="btn btn-outline"
                    style={{ fontSize: 11, padding: "3px 8px" }}
                    title="Reset to starter code"
                  >
                    <RotateCcw size={12} /> Reset Code
                  </button>
                </div>

                {/* Code Textarea Editor */}
                <div style={{ position: "relative" }}>
                  <textarea
                    value={codeValue}
                    onChange={(e) => setCodeValue(e.target.value)}
                    onKeyDown={handleEditorKeyDown}
                    rows={15}
                    spellCheck={false}
                    className="mono"
                    placeholder="// Write your clean solution here..."
                    style={{
                      width: "100%",
                      padding: 16,
                      borderRadius: 8,
                      background: "var(--surface-2)",
                      color: "var(--text)",
                      border: "1px solid var(--line)",
                      fontSize: 13,
                      lineHeight: 1.6,
                      resize: "vertical",
                      outline: "none",
                      fontFamily: "var(--font-mono, 'Courier New', monospace)",
                    }}
                  />
                  <div
                    style={{
                      position: "absolute",
                      bottom: 10,
                      right: 14,
                      fontSize: 10,
                      color: "var(--muted)",
                      pointerEvents: "none",
                    }}
                  >
                    Tab key indents by 4 spaces
                  </div>
                </div>

                {/* Interactive Tabbed Test Case Runner */}
                <div
                  style={{
                    background: "var(--surface-2)",
                    border: "1px solid var(--line)",
                    borderRadius: 8,
                    overflow: "hidden",
                  }}
                >
                  {/* Tab Headers */}
                  <div
                    style={{
                      display: "flex",
                      background: "var(--surface)",
                      borderBottom: "1px solid var(--line)",
                      padding: "0 8px",
                      gap: 4,
                    }}
                  >
                    {(currentQ.sample_test_cases && currentQ.sample_test_cases.length > 0
                      ? currentQ.sample_test_cases
                      : [{ inputs: [], expected: null }]
                    ).map((tc, idx) => {
                      const res = testOutput?.test_results?.[idx];
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setActiveTestTab(idx)}
                          style={{
                            padding: "8px 14px",
                            fontSize: 12,
                            fontWeight: 600,
                            border: "none",
                            borderBottom: activeTestTab === idx ? "2px solid var(--accent)" : "2px solid transparent",
                            background: "transparent",
                            color: activeTestTab === idx ? "var(--text)" : "var(--muted)",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                          }}
                        >
                          <span>Case {idx + 1}</span>
                          {res && (
                            <span
                              style={{
                                color: res.passed ? "var(--teal)" : "var(--danger)",
                                fontSize: 12,
                                fontWeight: 700,
                              }}
                            >
                              {res.passed ? "✓" : "✗"}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Active Tab Content */}
                  <div style={{ padding: 14 }}>
                    {(() => {
                      const tc = (currentQ.sample_test_cases || [])[activeTestTab];
                      const res = testOutput?.test_results?.[activeTestTab];
                      if (!tc) return <div style={{ fontSize: 12, color: "var(--muted)" }}>No sample test cases provided.</div>;

                      return (
                        <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: 12 }}>
                          <div>
                            <div style={{ color: "var(--muted)", fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
                              INPUT:
                            </div>
                            <pre
                              className="mono"
                              style={{
                                background: "var(--surface)",
                                border: "1px solid var(--line)",
                                padding: "8px 12px",
                                borderRadius: 6,
                                margin: 0,
                                color: "var(--text)",
                              }}
                            >
                              {JSON.stringify(tc.inputs, null, 2)}
                            </pre>
                          </div>

                          <div>
                            <div style={{ color: "var(--muted)", fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
                              EXPECTED OUTPUT:
                            </div>
                            <pre
                              className="mono"
                              style={{
                                background: "var(--surface)",
                                border: "1px solid var(--line)",
                                padding: "8px 12px",
                                borderRadius: 6,
                                margin: 0,
                                color: "var(--teal)",
                                fontWeight: 700,
                              }}
                            >
                              {JSON.stringify(tc.expected, null, 2)}
                            </pre>
                          </div>

                          {res && (
                            <div>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                  marginBottom: 4,
                                }}
                              >
                                <span style={{ color: "var(--muted)", fontSize: 11, fontWeight: 700 }}>
                                  ACTUAL RUNTIME OUTPUT:
                                </span>
                                {res.duration_ms !== undefined && (
                                  <span style={{ fontSize: 10, color: "var(--muted)" }}>
                                    Duration: {res.duration_ms} ms
                                  </span>
                                )}
                              </div>
                              <pre
                                className="mono"
                                style={{
                                  background: "var(--surface)",
                                  border: `1px solid ${res.passed ? "var(--teal)" : "var(--danger)"}`,
                                  padding: "8px 12px",
                                  borderRadius: 6,
                                  margin: 0,
                                  color: res.passed ? "var(--teal)" : "var(--danger)",
                                  fontWeight: 700,
                                }}
                              >
                                {res.actual !== undefined ? JSON.stringify(res.actual, null, 2) : res.error || "No output returned"}
                              </pre>
                            </div>
                          )}
                        </div>
                      );
                    })()}

                    {/* Overall Sandbox Execution Summary (Complexity, Anti-Cheating) */}
                    {testOutput && (
                      <div
                        style={{
                          marginTop: 12,
                          paddingTop: 10,
                          borderTop: "1px solid var(--line)",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          flexWrap: "wrap",
                          gap: 8,
                        }}
                      >
                        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                          <span
                            style={{
                              fontSize: 10,
                              fontWeight: 700,
                              textTransform: "uppercase",
                              padding: "2px 6px",
                              borderRadius: 4,
                              background: testOutput.status === "passed" ? "rgba(38, 169, 154, 0.15)" : "rgba(230, 109, 118, 0.15)",
                              color: testOutput.status === "passed" ? "var(--teal)" : "var(--danger)",
                            }}
                          >
                            Status: {testOutput.status} ({testOutput.passed_tests}/{testOutput.total_tests} passed)
                          </span>
                          {testOutput.quality_metrics && (
                            <>
                              <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 4, background: "var(--accent-soft)", color: "var(--accent)" }}>
                                Time: {testOutput.quality_metrics.estimated_time_complexity || "O(n)"}
                              </span>
                              <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 4, background: "var(--surface)", border: "1px solid var(--line)" }}>
                                Space: {testOutput.quality_metrics.estimated_space_complexity || "O(1)"}
                              </span>
                            </>
                          )}
                        </div>
                        {testOutput.error_message && (
                          <div style={{ fontSize: 11, color: "var(--danger)", width: "100%", marginTop: 4 }}>
                            {testOutput.error_message}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Bar */}
                <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 4 }}>
                  <button
                    onClick={handleRunCodeTests}
                    className="btn btn-outline"
                    disabled={runningTests || submittingAnswer || !codeValue.trim()}
                  >
                    {runningTests ? (
                      <>
                        <Loader2 size={13} className="animate-spin" /> Running Tests...
                      </>
                    ) : (
                      <>
                        <Play size={13} /> Run Sample Tests
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleSubmitCodeSolution}
                    className="btn btn-primary"
                    disabled={submittingAnswer || !codeValue.trim()}
                  >
                    {submittingAnswer ? (
                      <>
                        <Loader2 size={13} className="animate-spin" /> Evaluating Sandbox...
                      </>
                    ) : (
                      <>
                        <Sparkles size={13} /> Submit Solution
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* =================================================================
              INTERFACE 2: SQL QUERY CHALLENGE
          ================================================================= */}
          {currentQ.question_type === "sql" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ background: "var(--surface-2)", padding: 16, borderRadius: 8, border: "1px solid var(--line)" }}>
                <div className="card-kicker">Query Goal</div>
                <h3 style={{ fontSize: 16, margin: "6px 0 12px" }}>{currentQ.prompt}</h3>

                {currentQ.schema_ddl && (
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)", marginBottom: 6 }}>
                      Database Schema DDL & Sample Data
                    </div>
                    <pre
                      className="mono"
                      style={{
                        background: "var(--surface)",
                        border: "1px solid var(--line)",
                        padding: 12,
                        borderRadius: 6,
                        fontSize: 11,
                        overflowX: "auto",
                        color: "var(--text)",
                      }}
                    >
                      {currentQ.schema_ddl.trim()}
                    </pre>
                  </div>
                )}
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <label style={{ fontSize: 12, fontWeight: 700 }}>Write SQL Query</label>
                  {/* Quick SQL Tokens */}
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "JOIN", "LIMIT"].map((token) => (
                      <button
                        key={token}
                        type="button"
                        onClick={() => setSqlValue((prev) => (prev ? `${prev} ${token} ` : `${token} `))}
                        style={{
                          fontSize: 10,
                          padding: "2px 6px",
                          borderRadius: 4,
                          background: "var(--surface-2)",
                          border: "1px solid var(--line)",
                          color: "var(--accent)",
                          fontWeight: 700,
                          cursor: "pointer",
                        }}
                      >
                        {token}
                      </button>
                    ))}
                  </div>
                </div>

                <textarea
                  value={sqlValue}
                  onChange={(e) => setSqlValue(e.target.value)}
                  rows={6}
                  className="mono"
                  placeholder="SELECT * FROM table_name WHERE ..."
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 8,
                    background: "var(--surface-2)",
                    color: "var(--text)",
                    border: "1px solid var(--line)",
                    fontSize: 13,
                    resize: "vertical",
                    outline: "none",
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => handleSubmitGenericAnswer(sqlValue)}
                  className="btn btn-primary"
                  disabled={submittingAnswer || !sqlValue.trim()}
                >
                  {submittingAnswer ? (
                    <>
                      <Loader2 size={13} className="animate-spin" /> Executing Query...
                    </>
                  ) : (
                    <>
                      <Play size={13} /> Execute & Submit SQL
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* =================================================================
              INTERFACE 3: OUTPUT PREDICTION CHALLENGE
          ================================================================= */}
          {currentQ.question_type === "output_prediction" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {(() => {
                const parsed = parseQuestionLayout(currentQ);
                return (
                  <div style={{ background: "var(--surface-2)", padding: 20, borderRadius: 10, border: "1px solid var(--line)" }}>
                    <div className="card-kicker">Execution Prediction</div>
                    <h2 style={{ fontSize: 18, fontWeight: 700, margin: "6px 0 10px", color: "var(--text)" }}>
                      {parsed.title}
                    </h2>
                    {parsed.description && (
                      <div style={{ fontSize: 13, lineHeight: 1.7, color: "var(--muted)", marginBottom: 12 }}>
                        {parsed.description}
                      </div>
                    )}
                    {parsed.codeSnippet && (
                      <div style={{ margin: "14px 0", borderRadius: 8, border: "1px solid var(--line)", overflow: "hidden", background: "var(--surface)" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 14px", background: "var(--surface-2)", borderBottom: "1px solid var(--line)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>
                          <span>{parsed.codeLanguage || currentQ.programming_language || "Program Code"}</span>
                          <span>Execution Target</span>
                        </div>
                        <pre className="mono" style={{ padding: 14, margin: 0, fontSize: 13, lineHeight: 1.6, overflowX: "auto", color: "var(--text)", whiteSpace: "pre", fontFamily: "var(--font-mono, monospace)" }}>
                          {parsed.codeSnippet}
                        </pre>
                      </div>
                    )}
                    <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginTop: 12 }}>
                      {parsed.questionTask || "What is the expected stdout output of the program?"}
                    </div>
                  </div>
                );
              })()}

              {currentQ.options && currentQ.options.length > 0 ? (
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Select Predicted Output:
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {currentQ.options.map((opt, idx) => {
                      const optText = typeof opt === "string" ? opt : (opt as { text: string }).text;
                      const isSelected = selectedOption === optText;
                      const letter = ["A", "B", "C", "D", "E", "F"][idx] || String(idx + 1);
                      return (
                        <label
                          key={idx}
                          onClick={() => setSelectedOption(optText)}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 14,
                            padding: "12px 18px",
                            borderRadius: 8,
                            background: isSelected ? "var(--accent-soft)" : "var(--surface-2)",
                            border: `1.5px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                            cursor: "pointer",
                            transition: "all 0.15s ease",
                          }}
                        >
                          <div
                            style={{
                              width: 28,
                              height: 28,
                              minWidth: 28,
                              borderRadius: "50%",
                              background: isSelected ? "var(--accent)" : "var(--surface)",
                              color: isSelected ? "#ffffff" : "var(--text)",
                              border: `1px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: 12,
                              fontWeight: 700,
                            }}
                          >
                            {letter}
                          </div>
                          <span className="mono" style={{ fontSize: 13, color: "var(--text)", fontWeight: isSelected ? 600 : 400 }}>{optText}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div>
                  <label style={{ fontSize: 12, fontWeight: 700, display: "block", marginBottom: 6 }}>
                    Enter Exact Stdout Output
                  </label>
                  <input
                    type="text"
                    value={outputGuess}
                    onChange={(e) => setOutputGuess(e.target.value)}
                    className="mono"
                    placeholder="e.g. 42 or False"
                    style={{
                      width: "100%",
                      padding: "10px 14px",
                      borderRadius: 8,
                      background: "var(--surface-2)",
                      color: "var(--text)",
                      border: "1px solid var(--line)",
                      fontSize: 13,
                    }}
                  />
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => handleSubmitGenericAnswer(selectedOption || outputGuess)}
                  className="btn btn-primary"
                  disabled={submittingAnswer || (!selectedOption && !outputGuess.trim())}
                >
                  {submittingAnswer ? (
                    <>
                      <Loader2 size={13} className="animate-spin" /> Checking Output...
                    </>
                  ) : (
                    <>
                      <Play size={13} /> Submit Prediction
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* =================================================================
              INTERFACE 4: DEBUGGING CHALLENGE
          ================================================================= */}
          {currentQ.question_type === "debugging" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {(() => {
                const parsed = parseQuestionLayout(currentQ);
                return (
                  <div style={{ background: "var(--surface-2)", padding: 20, borderRadius: 10, border: "1px solid var(--line)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                      <Bug size={16} color="var(--danger)" />
                      <span className="card-kicker" style={{ color: "var(--danger)" }}>
                        Defective Logic Inspection
                      </span>
                    </div>
                    <h2 style={{ fontSize: 18, fontWeight: 700, margin: "6px 0 10px", color: "var(--text)" }}>
                      {parsed.title}
                    </h2>
                    {parsed.description && (
                      <div style={{ fontSize: 13, lineHeight: 1.7, color: "var(--muted)", marginBottom: 12 }}>
                        {parsed.description}
                      </div>
                    )}
                    {parsed.codeSnippet && (
                      <div style={{ margin: "14px 0", borderRadius: 8, border: "1px solid rgba(230, 109, 118, 0.4)", overflow: "hidden", background: "var(--surface)" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 14px", background: "rgba(230, 109, 118, 0.12)", borderBottom: "1px solid rgba(230, 109, 118, 0.25)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--danger)" }}>
                          <span>{parsed.codeLanguage || currentQ.programming_language || "Code Under Test"}</span>
                          <span>Contains Defect</span>
                        </div>
                        <pre className="mono" style={{ padding: 14, margin: 0, fontSize: 13, lineHeight: 1.6, overflowX: "auto", color: "var(--text)", whiteSpace: "pre", fontFamily: "var(--font-mono, monospace)" }}>
                          {parsed.codeSnippet}
                        </pre>
                      </div>
                    )}
                    <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginTop: 12 }}>
                      {parsed.questionTask || "Identify the defect and required resolution:"}
                    </div>
                  </div>
                );
              })()}

              {currentQ.options && currentQ.options.length > 0 ? (
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Select Correct Defect Diagnosis / Fix:
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {currentQ.options.map((opt, idx) => {
                      const optText = typeof opt === "string" ? opt : (opt as { text: string }).text;
                      const isSelected = selectedOption === optText;
                      const letter = ["A", "B", "C", "D", "E", "F"][idx] || String(idx + 1);
                      return (
                        <label
                          key={idx}
                          onClick={() => setSelectedOption(optText)}
                          style={{
                            display: "flex",
                            alignItems: "flex-start",
                            gap: 14,
                            padding: "14px 18px",
                            borderRadius: 8,
                            background: isSelected ? "var(--accent-soft)" : "var(--surface-2)",
                            border: `1.5px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                            cursor: "pointer",
                            transition: "all 0.15s ease",
                          }}
                        >
                          <div
                            style={{
                              width: 28,
                              height: 28,
                              minWidth: 28,
                              borderRadius: "50%",
                              background: isSelected ? "var(--accent)" : "var(--surface)",
                              color: isSelected ? "#ffffff" : "var(--text)",
                              border: `1px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: 12,
                              fontWeight: 700,
                              marginTop: 1,
                            }}
                          >
                            {letter}
                          </div>
                          <span style={{ fontSize: 13, lineHeight: 1.6, color: "var(--text)" }}>{optText}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div>
                  <label style={{ fontSize: 12, fontWeight: 700, display: "block", marginBottom: 6 }}>
                    Describe the bug and corrected patch:
                  </label>
                  <textarea
                    value={conceptualText}
                    onChange={(e) => setConceptualText(e.target.value)}
                    rows={4}
                    placeholder="Explain the defect and the required code modification..."
                    style={{
                      width: "100%",
                      padding: 12,
                      borderRadius: 8,
                      background: "var(--surface-2)",
                      color: "var(--text)",
                      border: "1px solid var(--line)",
                      fontSize: 13,
                    }}
                  />
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => handleSubmitGenericAnswer(selectedOption || conceptualText)}
                  className="btn btn-primary"
                  disabled={submittingAnswer || (!selectedOption && !conceptualText.trim())}
                >
                  {submittingAnswer ? (
                    <>
                      <Loader2 size={13} className="animate-spin" /> Verifying Fix...
                    </>
                  ) : (
                    <>
                      <Play size={13} /> Submit Diagnosis
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* =================================================================
              INTERFACE 5: CONCEPTUAL & ARCHITECTURAL REASONING
          ================================================================= */}
          {currentQ.question_type === "conceptual" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {(() => {
                const parsed = parseQuestionLayout(currentQ);
                return (
                  <div style={{ background: "var(--surface-2)", padding: 20, borderRadius: 10, border: "1px solid var(--line)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                      <Brain size={16} color="var(--violet)" />
                      <span className="card-kicker" style={{ color: "var(--violet)" }}>
                        Deep Technical Reasoning
                      </span>
                    </div>
                    <h2 style={{ fontSize: 18, fontWeight: 700, margin: "6px 0 10px", color: "var(--text)" }}>
                      {parsed.title}
                    </h2>
                    {parsed.description && (
                      <div style={{ fontSize: 13, lineHeight: 1.7, color: "var(--muted)", marginBottom: 12 }}>
                        {parsed.description}
                      </div>
                    )}
                    <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", margin: "8px 0 14px", lineHeight: 1.5 }}>
                      {parsed.questionTask}
                    </div>

                    {currentQ.constraints && currentQ.constraints.length > 0 && (
                      <div>
                        <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)", marginBottom: 6 }}>
                          Rubric Criteria Focus (address these key concepts):
                        </div>
                        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                          {currentQ.constraints.map((conc, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: 11,
                                padding: "3px 8px",
                                borderRadius: 4,
                                background: "var(--violet-soft)",
                                color: "var(--violet)",
                                fontWeight: 600,
                              }}
                            >
                              {conc}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <label style={{ fontSize: 12, fontWeight: 700 }}>Candidate Explanation & Trade-Off Analysis</label>
                  <span className="muted" style={{ fontSize: 11 }}>
                    {conceptualText.trim().split(/\s+/).filter(Boolean).length} words
                  </span>
                </div>
                <textarea
                  value={conceptualText}
                  onChange={(e) => setConceptualText(e.target.value)}
                  rows={8}
                  placeholder="Provide your in-depth technical analysis, comparing trade-offs, edge conditions, memory locality, and algorithmic complexity..."
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 8,
                    background: "var(--surface-2)",
                    color: "var(--text)",
                    border: "1px solid var(--line)",
                    fontSize: 13,
                    lineHeight: 1.6,
                    resize: "vertical",
                    outline: "none",
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => handleSubmitGenericAnswer(conceptualText)}
                  className="btn btn-primary"
                  disabled={submittingAnswer || !conceptualText.trim()}
                >
                  {submittingAnswer ? (
                    <>
                      <Loader2 size={13} className="animate-spin" /> Evaluating Rubric...
                    </>
                  ) : (
                    <>
                      <Sparkles size={13} /> Submit Reasoning Analysis
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* =================================================================
              INTERFACE 6: MULTIPLE CHOICE QUESTION (Standard MCQ)
          ================================================================= */}
          {currentQ.question_type === "multiple_choice" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {(() => {
                const parsed = parseQuestionLayout(currentQ);
                return (
                  <div style={{ background: "var(--surface-2)", padding: 20, borderRadius: 10, border: "1px solid var(--line)" }}>
                    <div className="card-kicker">Technical Knowledge Quiz</div>
                    <h2 style={{ fontSize: 18, fontWeight: 700, margin: "6px 0 10px", color: "var(--text)" }}>
                      {parsed.title}
                    </h2>
                    {parsed.description && (
                      <div style={{ fontSize: 13, lineHeight: 1.7, color: "var(--muted)", marginBottom: 12 }}>
                        {parsed.description}
                      </div>
                    )}
                    {parsed.codeSnippet && (
                      <div style={{ margin: "14px 0", borderRadius: 8, border: "1px solid var(--line)", overflow: "hidden", background: "var(--surface)" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 14px", background: "var(--surface-2)", borderBottom: "1px solid var(--line)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>
                          <span>{parsed.codeLanguage || currentQ.programming_language || "Code"}</span>
                          <span>Reference Snippet</span>
                        </div>
                        <pre className="mono" style={{ padding: 14, margin: 0, fontSize: 13, lineHeight: 1.6, overflowX: "auto", color: "var(--text)", whiteSpace: "pre", fontFamily: "var(--font-mono, monospace)" }}>
                          {parsed.codeSnippet}
                        </pre>
                      </div>
                    )}
                    <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginTop: 8, lineHeight: 1.5 }}>
                      {parsed.questionTask}
                    </div>
                  </div>
                );
              })()}

              <div>
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Select the Correct Answer:
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {(currentQ.options || []).map((opt, idx) => {
                    const optText = typeof opt === "string" ? opt : (opt as { text: string }).text;
                    const isSelected = selectedOption === optText;
                    const letter = ["A", "B", "C", "D", "E", "F"][idx] || String(idx + 1);
                    return (
                      <label
                        key={idx}
                        onClick={() => setSelectedOption(optText)}
                        style={{
                          display: "flex",
                          alignItems: "flex-start",
                          gap: 14,
                          padding: "14px 18px",
                          borderRadius: 8,
                          background: isSelected ? "var(--accent-soft)" : "var(--surface-2)",
                          border: `1.5px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                        }}
                      >
                        <div
                          style={{
                            width: 28,
                            height: 28,
                            minWidth: 28,
                            borderRadius: "50%",
                            background: isSelected ? "var(--accent)" : "var(--surface)",
                            color: isSelected ? "#ffffff" : "var(--text)",
                            border: `1px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 12,
                            fontWeight: 700,
                            marginTop: 1,
                          }}
                        >
                          {letter}
                        </div>
                        <span style={{ fontSize: 13, lineHeight: 1.6, color: "var(--text)", flex: 1 }}>
                          {optText}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
                <button
                  onClick={() => handleSubmitGenericAnswer(selectedOption)}
                  className="btn btn-primary"
                  disabled={!selectedOption || submittingAnswer}
                >
                  {submittingAnswer ? (
                    <>
                      <Loader2 size={13} className="animate-spin" /> Evaluating...
                    </>
                  ) : (
                    <>
                      Submit Answer <Play size={13} />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      {/* =====================================================================
          SUMMARY RESULTS CARD: Shown after finishing assessment
      ===================================================================== */}
      {summaryResults && (
        <section
          className="card card-pad"
          style={{ marginBottom: 32, border: "2px solid var(--teal)", background: "var(--surface)" }}
        >
          <div className="section-head">
            <div>
              <div className="card-kicker">Performance Summary</div>
              <h2 style={{ fontSize: 18, margin: "4px 0" }}>{summaryResults.title} Results</h2>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              {typeof summaryResults.mastery_score === "number" && (
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: "var(--accent)" }}>
                    {summaryResults.mastery_score.toFixed(1)} <span style={{ fontSize: 13 }}>/ 10</span>
                  </div>
                  <div style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "var(--accent)" }}>
                    {summaryResults.mastery_band || "Calibrated Mastery"}
                  </div>
                </div>
              )}
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: "50%",
                  border: "4px solid var(--teal)",
                  display: "grid",
                  placeItems: "center",
                  fontWeight: 700,
                  fontSize: 16,
                  color: "var(--teal)",
                }}
              >
                <span>{Math.round(summaryResults.average_score)}%</span>
              </div>
              <button
                onClick={() => setSummaryResults(null)}
                className="btn btn-outline"
                style={{ fontSize: 11, padding: "5px 10px" }}
              >
                Close Summary
              </button>
            </div>
          </div>

          <p className="muted" style={{ fontSize: 13, marginTop: 10, lineHeight: 1.5 }}>
            You answered <strong>{summaryResults.correct_answers}</strong> of <strong>{summaryResults.total_questions}</strong> challenges correctly ({Math.round(summaryResults.average_score)}% overall accuracy).
            {summaryResults.highest_tier_passed && summaryResults.highest_tier_passed !== "None" && (
              <span> Highest Tier Conquered: <strong style={{ color: "var(--text)", textTransform: "uppercase" }}>{summaryResults.highest_tier_passed.replace("_", " ")}</strong>. </span>
            )}
            Calibrated technical mastery evaluated at <strong>{summaryResults.mastery_score !== undefined ? `${summaryResults.mastery_score.toFixed(1)} / 10.0` : `${Math.round(summaryResults.average_score)}%`}</strong> ({summaryResults.mastery_band || "Verified"}).
          </p>

          {/* Strengths & Weaknesses Breakdown */}
          <div className="grid-2" style={{ gap: 16, marginTop: 18 }}>
            <div style={{ background: "var(--surface-2)", padding: 14, borderRadius: 8, border: "1px solid var(--line)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 700, color: "var(--teal)", marginBottom: 8 }}>
                <TrendingUp size={15} /> Strengths Demonstrated ({correctAttempts.length})
              </div>
              {correctAttempts.length === 0 ? (
                <p className="muted" style={{ fontSize: 11 }}>No correct answers in this session. Review the explanations below.</p>
              ) : (
                <ul style={{ paddingLeft: 18, fontSize: 11, lineHeight: 1.5, margin: 0, color: "var(--muted)" }}>
                  {correctAttempts.map((a, i) => (
                    <li key={i} style={{ marginBottom: 6 }}>
                      {a.feedback || "Question answered accurately."}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div style={{ background: "var(--surface-2)", padding: 14, borderRadius: 8, border: "1px solid var(--line)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 700, color: "var(--danger)", marginBottom: 8 }}>
                <TrendingDown size={15} /> Areas for Review ({incorrectAttempts.length})
              </div>
              {incorrectAttempts.length === 0 ? (
                <p className="muted" style={{ fontSize: 11 }}>Perfect run! No incorrect challenges recorded.</p>
              ) : (
                <ul style={{ paddingLeft: 18, fontSize: 11, lineHeight: 1.5, margin: 0, color: "var(--muted)" }}>
                  {incorrectAttempts.map((a, i) => (
                    <li key={i} style={{ marginBottom: 6 }}>
                      {a.feedback || "Incorrect response. Review core topic documentation."}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Question Details List */}
          {summaryResults.attempts && summaryResults.attempts.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 10, color: "var(--text)" }}>
                Question-by-Question Evaluation Breakdown:
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {summaryResults.attempts.map((att, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "10px 14px",
                      borderRadius: 6,
                      background: att.is_correct ? "rgba(38, 169, 154, 0.08)" : "rgba(230, 109, 118, 0.08)",
                      border: `1px solid ${att.is_correct ? "rgba(38, 169, 154, 0.25)" : "rgba(230, 109, 118, 0.25)"}`,
                      fontSize: 12,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      {att.is_correct ? <CheckCircle2 size={15} color="var(--teal)" /> : <XCircle size={15} color="var(--danger)" />}
                      <span>
                        <strong>Q{idx + 1}:</strong> {att.feedback}
                      </span>
                    </div>
                    <span style={{ fontSize: 11, fontWeight: 700, color: att.is_correct ? "var(--teal)" : "var(--danger)" }}>
                      {Math.round(att.score)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* =====================================================================
          START NEW ASSESSMENT: Topic & Mode Selection
      ===================================================================== */}
      <div className="grid-2">
        <section className="card card-pad">
          <div className="section-head" style={{ marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Technical Skill Assessment</div>
              <div className="card-title" style={{ marginTop: 6 }}>
                Launch Adaptive Evaluation
              </div>
            </div>
            <BookOpenCheck size={18} color="var(--accent)" />
          </div>

          <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, marginBottom: 16 }}>
            Select your target technology domain and assessment mode. Questions dynamically adapt in difficulty (Level 1 to 6)
            based on real-time execution performance.
          </p>

          {/* Mode Selector */}
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)", display: "block", marginBottom: 6 }}>
              Assessment Mode
            </label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {[
                { id: "mixed", label: "Mixed Mastery", icon: <Layers size={13} /> },
                { id: "coding", label: "Coding Sandbox", icon: <Code2 size={13} /> },
                { id: "sql", label: "SQL Engine", icon: <Database size={13} /> },
                { id: "quiz", label: "Knowledge Quiz", icon: <ListChecks size={13} /> },
              ].map((m) => {
                const isSel = selectedMode === m.id;
                return (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setSelectedMode(m.id as typeof selectedMode)}
                    style={{
                      padding: "8px 10px",
                      borderRadius: 8,
                      border: `1px solid ${isSel ? "var(--accent)" : "var(--line)"}`,
                      background: isSel ? "var(--accent-soft)" : "var(--surface)",
                      color: isSel ? "var(--accent)" : "var(--text)",
                      fontSize: 12,
                      fontWeight: 600,
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      cursor: "pointer",
                    }}
                  >
                    {m.icon}
                    <span>{m.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Topic Selector */}
          <div className="field">
            <label htmlFor="topicSelect">Target Technical Domain</label>
            <select
              id="topicSelect"
              className="input"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              style={{
                width: "100%",
                padding: "9px 12px",
                borderRadius: 8,
                background: "var(--surface)",
                border: "1px solid var(--line)",
                fontSize: 13,
                color: "var(--text)",
              }}
            >
              {topics.map((t) => (
                <option key={t.id} value={t.name}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleStartAssessment}
            className="btn btn-primary"
            style={{ marginTop: 18, width: "100%", justifyContent: "center" }}
            disabled={starting || !selectedTopic}
          >
            {starting ? (
              <>
                <Loader2 size={13} className="animate-spin" /> Preparing Assessment Engine...
              </>
            ) : (
              <>
                <Play size={13} /> Start Assessment
              </>
            )}
          </button>
        </section>

        {/* Engine Capabilities & Question Bank Architecture */}
        <section className="card card-pad" style={{ background: "var(--surface-2)" }}>
          <div className="section-head" style={{ marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Validated Assessment Engine</div>
              <div className="card-title" style={{ marginTop: 6 }}>
                Real-Time Verification Architecture
              </div>
            </div>
            <Sparkles size={18} color="var(--accent)" />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: 12, lineHeight: 1.5, color: "var(--muted)" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <Code2 size={16} color="var(--accent)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ color: "var(--text)" }}>Isolated Subprocess Execution:</strong> Python candidate solutions are evaluated inside restricted process sandboxes with AST security analysis and execution timeouts.
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <Database size={16} color="var(--teal)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ color: "var(--text)" }}>In-Memory SQL Runner:</strong> Relational queries execute in isolated ephemeral SQLite databases populated with live DDL schemas and tested against reference queries.
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <Layers size={16} color="var(--amber)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ color: "var(--text)" }}>2,000+ Validated Question Bank:</strong> 6 difficulty tiers (Very Easy to Expert) spanning Algorithms, Programming Languages, Web Dev, Databases, and Systems.
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <Award size={16} color="var(--teal)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ color: "var(--text)" }}>Verified Capability Ledger:</strong> Successful completions automatically update demonstrated evidence and calibrate skill bands in your profile.
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* =====================================================================
          PAST ASSESSMENTS HISTORY
      ===================================================================== */}
      <div style={{ marginTop: 34 }}>
        <div className="section-head">
          <div>
            <div className="eyebrow">Demonstrated History</div>
            <h2 style={{ margin: "6px 0 0", fontSize: 18 }}>Past Assessment Attempts</h2>
          </div>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 36 }}>
            <Loader2 size={22} className="animate-spin text-muted" />
          </div>
        ) : pastAssessments.length === 0 ? (
          <div className="card card-pad" style={{ textAlign: "center", padding: "36px 20px" }}>
            <HelpCircle size={32} style={{ margin: "0 auto 10px", opacity: 0.4 }} />
            <div style={{ fontSize: 14, fontWeight: 600 }}>No past assessments recorded</div>
            <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
              Start your first assessment above to turn your skills into verified capability signals.
            </p>
          </div>
        ) : (
          <div className="grid-2">
            {pastAssessments.map((a) => {
              const res = (a.summary_result || {}) as Record<string, unknown>;
              const avg = typeof res.average_score === "number" ? res.average_score : 0;
              const isViewing = loadingPastResultId === a.id;

              return (
                <div className="card card-pad" key={a.id}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          textTransform: "uppercase",
                          padding: "3px 6px",
                          borderRadius: 4,
                          background: a.status === "completed" ? "rgba(38, 169, 154, 0.12)" : "rgba(239, 174, 75, 0.15)",
                          color: a.status === "completed" ? "var(--teal)" : "var(--amber)",
                        }}
                      >
                        {a.status}
                      </span>
                      <h3 style={{ fontSize: 15, margin: "8px 0 4px" }}>{a.title}</h3>
                      <div className="muted" style={{ fontSize: 11 }}>
                        Started {new Date(a.started_at).toLocaleDateString()}
                      </div>
                    </div>
                    {a.status === "completed" ? (
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 18, fontWeight: 700, color: "var(--teal)" }}>
                          {typeof res.mastery_score === "number" ? `${res.mastery_score.toFixed(1)}/10` : `${Math.round(avg)}%`}
                        </div>
                        <div className="muted" style={{ fontSize: 10 }}>
                          {typeof res.mastery_band === "string" ? res.mastery_band : "Score"}
                        </div>
                      </div>
                    ) : (
                      <span className="muted" style={{ fontSize: 11 }}>In Progress</span>
                    )}
                  </div>

                  {a.status === "completed" && (
                    <div style={{ marginTop: 14, display: "flex", justifyContent: "flex-end" }}>
                      <button
                        onClick={() => handleViewPastResults(a.id)}
                        className="btn btn-outline"
                        style={{ fontSize: 11, padding: "5px 10px" }}
                        disabled={isViewing}
                      >
                        {isViewing ? <Loader2 size={12} className="animate-spin" /> : <Award size={12} />}
                        View Breakdown
                      </button>
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
