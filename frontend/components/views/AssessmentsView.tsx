"use client";

import { useEffect, useState, useCallback } from "react";
import {
  AlertCircle,
  BookOpenCheck,
  Check,
  Code2,
  HelpCircle,
  Loader2,
  Lock,
  Play,
  Sparkles,
} from "lucide-react";
import { assessmentsApi } from "@/lib/api";
import type {
  AssessmentResponse,
  AssessmentSummaryResultsResponse,
  AssessmentTopicResponse,
} from "@/types";

export default function AssessmentsView() {
  const [topics, setTopics] = useState<AssessmentTopicResponse[]>([]);
  const [pastAssessments, setPastAssessments] = useState<AssessmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<string>("");

  // Active quiz state
  const [activeAssessment, setActiveAssessment] = useState<AssessmentResponse | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [lastFeedback, setLastFeedback] = useState<{ isCorrect: boolean; text: string; score: number } | null>(null);
  const [summaryResults, setSummaryResults] = useState<AssessmentSummaryResultsResponse | null>(null);

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

  const handleStartQuiz = async () => {
    setStarting(true);
    setErrorMessage(null);
    setLastFeedback(null);
    setSummaryResults(null);

    try {
      const assessment = await assessmentsApi.createAssessment({
        mode: "quiz",
        selected_topics: [selectedTopic],
        title: `${selectedTopic} Assessment`,
      });

      setActiveAssessment(assessment);
      setSelectedOption("");
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

  const handleSubmitAnswer = async () => {
    if (!activeAssessment || !activeAssessment.current_question || !selectedOption) return;

    setSubmittingAnswer(true);
    setErrorMessage(null);

    const questionId = activeAssessment.current_question.id;
    try {
      const attempt = await assessmentsApi.submitAnswer(activeAssessment.id, {
        question_id: questionId,
        answer: selectedOption,
      });

      setLastFeedback({
        isCorrect: attempt.is_correct ?? false,
        text: attempt.feedback || (attempt.is_correct ? "Correct answer!" : "Incorrect."),
        score: attempt.score,
      });

      // Fetch next adaptive question
      const refreshed = await assessmentsApi.getAssessment(activeAssessment.id);
      if (refreshed.current_question) {
        setActiveAssessment(refreshed);
        setSelectedOption("");
      } else {
        // No more questions -> load results
        const results = await assessmentsApi.getAssessmentResults(activeAssessment.id);
        setSummaryResults(results);
        setActiveAssessment(null);
        loadInitialData();
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to submit answer.");
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
      loadInitialData();
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
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

      {/* Active Quiz Session View */}
      {activeAssessment && activeAssessment.current_question && (
        <section
          className="card card-pad"
          style={{ marginBottom: 32, border: "2px solid var(--accent)", background: "var(--surface)" }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div>
              <span className="card-kicker">Live Adaptive Quiz</span>
              <h2 style={{ fontSize: 18, margin: "4px 0" }}>{activeAssessment.title}</h2>
            </div>
            <button onClick={handleFinishEarly} className="btn btn-outline" style={{ fontSize: 11 }}>
              Complete & View Results
            </button>
          </div>

          {/* Feedback banner from previous question if any */}
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
                background: lastFeedback.isCorrect ? "rgba(0, 209, 178, 0.12)" : "rgba(255, 107, 107, 0.12)",
                border: `1px solid ${lastFeedback.isCorrect ? "rgba(0, 209, 178, 0.35)" : "rgba(255, 107, 107, 0.35)"}`,
                color: lastFeedback.isCorrect ? "var(--teal)" : "#ff8787",
              }}
            >
              <Check size={14} />
              <span>
                <strong>{lastFeedback.isCorrect ? "Correct!" : "Note:"}</strong> {lastFeedback.text}
              </span>
            </div>
          )}

          <div style={{ padding: "16px 0", borderTop: "1px solid var(--line)", borderBottom: "1px solid var(--line)" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10 }}>
              <span
                style={{
                  fontSize: 10,
                  textTransform: "uppercase",
                  fontWeight: 700,
                  padding: "3px 7px",
                  borderRadius: 4,
                  background: "var(--accent-soft)",
                  color: "var(--accent)",
                }}
              >
                Difficulty: {activeAssessment.current_question.difficulty}
              </span>
            </div>
            <h3 style={{ fontSize: 15, lineHeight: 1.5, margin: "8px 0 16px" }}>
              {activeAssessment.current_question.prompt}
            </h3>

            {/* Options */}
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {(activeAssessment.current_question.options || []).map((opt, idx) => {
                const optText = typeof opt === "string" ? opt : (opt as { text: string }).text;
                const isSelected = selectedOption === optText;
                return (
                  <label
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      padding: "12px 14px",
                      borderRadius: 8,
                      background: isSelected ? "var(--accent-soft)" : "var(--surface-2)",
                      border: `1px solid ${isSelected ? "var(--accent)" : "var(--line)"}`,
                      cursor: "pointer",
                      fontSize: 13,
                    }}
                  >
                    <input
                      type="radio"
                      name="quiz-option"
                      checked={isSelected}
                      onChange={() => setSelectedOption(optText)}
                      style={{ accentColor: "var(--accent)" }}
                    />
                    <span>{optText}</span>
                  </label>
                );
              })}
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 18 }}>
            <button
              onClick={handleSubmitAnswer}
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
        </section>
      )}

      {/* Summary Results Card if quiz just finished */}
      {summaryResults && (
        <section
          className="card card-pad"
          style={{ marginBottom: 32, border: "2px solid var(--teal)", background: "var(--surface)" }}
        >
          <div className="section-head">
            <div>
              <div className="card-kicker">Assessment Complete</div>
              <h2 style={{ fontSize: 18, margin: "4px 0" }}>{summaryResults.title} Results</h2>
            </div>
            <div className="score-ring" style={{ width: 60, height: 60 }}>
              <strong>{Math.round(summaryResults.average_score)}</strong>
              <small>%</small>
            </div>
          </div>

          <p className="muted" style={{ fontSize: 13, marginTop: 10 }}>
            You answered {summaryResults.correct_answers} of {summaryResults.total_questions} questions correctly.
            Your capability score and evidence records have been updated in your profile.
          </p>
        </section>
      )}

      {/* Start New Assessment Controls */}
      <div className="grid-2">
        <section className="card card-pad">
          <div className="section-head" style={{ marginBottom: 12 }}>
            <div>
              <div className="card-kicker">Signal Verification</div>
              <div className="card-title" style={{ marginTop: 6 }}>
                Start Adaptive Knowledge Check
              </div>
            </div>
            <BookOpenCheck size={18} color="var(--accent)" />
          </div>

          <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, marginBottom: 16 }}>
            Multiple-choice adaptive checks test your knowledge progression (Easy, Medium, Hard). Verified answers
            upgrade claimed skills to <span style={{ color: "var(--teal)", fontWeight: 600 }}>Assessed</span> capability.
          </p>

          <div className="field">
            <label htmlFor="topicSelect">Select Topic Area</label>
            <select
              id="topicSelect"
              className="input"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
            >
              {topics.map((t) => (
                <option key={t.id} value={t.name}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleStartQuiz}
            className="btn btn-primary"
            style={{ marginTop: 18, width: "100%", justifyContent: "center" }}
            disabled={starting || !selectedTopic}
          >
            {starting ? (
              <>
                <Loader2 size={13} className="animate-spin" /> Preparing Questions...
              </>
            ) : (
              <>
                <Play size={13} /> Start Assessment
              </>
            )}
          </button>
        </section>

        {/* Coding Sandbox Coming Soon Notice per Security Rule */}
        <section className="card card-pad" style={{ background: "var(--surface-2)" }}>
          <div className="section-head" style={{ marginBottom: 8 }}>
            <div>
              <div className="card-kicker">Coding Challenges</div>
              <div className="card-title" style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 8 }}>
                <span>Code Execution Sandbox</span>
                <span
                  style={{
                    fontSize: 10,
                    padding: "3px 7px",
                    borderRadius: 4,
                    background: "rgba(255, 187, 0, 0.15)",
                    color: "var(--amber)",
                    textTransform: "uppercase",
                    fontWeight: 700,
                  }}
                >
                  Coming Soon
                </span>
              </div>
            </div>
            <Lock size={18} color="var(--amber)" />
          </div>

          <p className="muted" style={{ fontSize: 12, lineHeight: 1.6 }}>
            User code execution is currently disabled against the live backend server per platform security policies.
            Subprocess execution on the host server with static AST filtering is pending isolated microVM runner
            deployment with resource and network isolation.
          </p>

          <div
            style={{
              marginTop: 18,
              padding: "10px 14px",
              borderRadius: 8,
              background: "var(--surface)",
              border: "1px solid var(--line)",
              fontSize: 11,
              color: "var(--muted)",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Code2 size={14} color="var(--amber)" />
            <span>Interactive sandbox preview is available in mock design review mode only.</span>
          </div>
        </section>
      </div>

      {/* Past Assessments History */}
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
              Start your first knowledge check above to turn knowledge into a verified signal.
            </p>
          </div>
        ) : (
          <div className="grid-2">
            {pastAssessments.map((a) => {
              const res = (a.summary_result || {}) as Record<string, unknown>;
              const avg = typeof res.average_score === "number" ? res.average_score : 0;
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
                          background: a.status === "completed" ? "rgba(0, 209, 178, 0.12)" : "rgba(255, 187, 0, 0.15)",
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
                    {a.status === "completed" && (
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 18, fontWeight: 700, color: "var(--teal)" }}>
                          {Math.round(avg)}%
                        </div>
                        <div className="muted" style={{ fontSize: 10 }}>Score</div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
