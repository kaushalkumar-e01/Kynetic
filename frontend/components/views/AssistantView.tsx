"use client";

import { useEffect, useState, useRef } from "react";
import { AlertCircle, ArrowRight, Loader2, Send, Sparkles, Trash2, User } from "lucide-react";
import { assistantApi } from "@/lib/api";
import type { ConversationResponse, ConversationSummaryResponse } from "@/types";
import AssistantMarkdown from "./AssistantMarkdown";

export default function AssistantView() {
  const [conversations, setConversations] = useState<ConversationSummaryResponse[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Clean up any ongoing request on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, []);

  const loadConversations = () => {
    setLoading(true);
    assistantApi
      .listConversations()
      .then((convs) => {
        setConversations(convs);
        if (convs.length > 0) {
          assistantApi
            .getConversation(convs[0].id)
            .then((c) => setCurrentConversation(c))
            .catch(() => {});
        }
        setLoading(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load assistant conversations.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentConversation?.messages, sending]);

  const handleSendMessage = async (promptText?: string) => {
    const text = promptText || inputMessage;
    if (!text.trim() || sending) return;

    // Abort any existing in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setSending(true);
    setErrorMessage(null);
    setInputMessage("");

    try {
      const updated = await assistantApi.sendMessage(
        {
          message: text.trim(),
          conversation_id: currentConversation?.id,
        },
        controller.signal
      );

      if (!controller.signal.aborted) {
        setCurrentConversation(updated);
        assistantApi.listConversations().then((c) => setConversations(c));
      }
    } catch (err: unknown) {
      if (controller.signal.aborted) {
        return;
      }
      if (err instanceof Error) {
        if (err.name === "AbortError" || err.message.toLowerCase().includes("aborted")) {
          return;
        }
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to send message.");
      }
    } finally {
      if (abortControllerRef.current === controller) {
        setSending(false);
        abortControllerRef.current = null;
      }
    }
  };

  const handleSelectConversation = async (convId: string) => {
    if (currentConversation?.id === convId) return;

    // Cleanly cancel any in-flight request when switching conversations
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setSending(false);

    setLoading(true);
    try {
      const conv = await assistantApi.getConversation(convId);
      setCurrentConversation(conv);
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setSending(false);
    setErrorMessage(null);
    setCurrentConversation(null);
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this conversation?")) return;
    try {
      await assistantApi.deleteConversation(convId);
      if (currentConversation?.id === convId) {
        setCurrentConversation(null);
      }
      loadConversations();
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  const suggestedPrompts = [
    "What should I work on this week based on my evidence?",
    "Which roles fit my current evidence mix best?",
    "How can I turn my claimed skills into assessed proof?",
  ];

  return (
    <div>
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

      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 18 }}>
        {/* Conversations sidebar */}
        <div className="card card-pad" style={{ height: 560, display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <span style={{ fontSize: 13, fontWeight: 700 }}>Conversations</span>
            <button
              onClick={handleNewChat}
              className="btn btn-ghost"
              style={{ padding: "4px 8px", fontSize: 11 }}
            >
              + New
            </button>
          </div>

          <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
            {conversations.length === 0 ? (
              loading ? (
                <div style={{ display: "flex", alignItems: "center", gap: 6, padding: 12, color: "var(--muted)", fontSize: 11 }}>
                  <Loader2 size={12} className="animate-spin" style={{ animation: "spin 1s linear infinite", flexShrink: 0 }} />
                  <span>Loading...</span>
                </div>
              ) : (
                <p className="muted" style={{ fontSize: 11, padding: 12 }}>
                  No past conversations.
                </p>
              )
            ) : (
              conversations.map((c) => {
                const isActive = currentConversation?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => handleSelectConversation(c.id)}
                    style={{
                      padding: "8px 10px",
                      borderRadius: 6,
                      background: isActive ? "var(--accent-soft)" : "transparent",
                      border: `1px solid ${isActive ? "var(--accent)" : "transparent"}`,
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 12 }}>
                      {c.title}
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(c.id, e)}
                      style={{ background: "none", border: "none", padding: 2, cursor: "pointer", color: "var(--muted)" }}
                      title="Delete conversation"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="card card-pad" style={{ height: 560, display: "flex", flexDirection: "column" }}>
          <div
            style={{
              paddingBottom: 12,
              borderBottom: "1px solid var(--line)",
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <div className="avatar" style={{ background: "var(--accent-soft)", color: "var(--accent)" }}>
              <Sparkles size={15} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>
                {currentConversation?.title || "Kynetic Assistant"}
              </div>
              <div className="muted" style={{ fontSize: 10 }}>
                Context-aware workspace capability advisor
              </div>
            </div>
          </div>

          {/* Messages list */}
          <div style={{ flex: 1, overflowY: "auto", padding: "16px 0", display: "flex", flexDirection: "column", gap: 14 }}>
            {!currentConversation || (currentConversation.messages || []).length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px 20px" }}>
                <Sparkles size={28} color="var(--accent)" style={{ margin: "0 auto 12px" }} />
                <div style={{ fontSize: 14, fontWeight: 600 }}>Ask about your capability map</div>
                <p className="muted" style={{ fontSize: 12, marginTop: 4, maxWidth: 360, margin: "6px auto 20px" }}>
                  Kynetic connects your current goals, resume claims, and assessment history into tailored advice.
                </p>

                <div style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 440, margin: "0 auto" }}>
                  {suggestedPrompts.map((p) => (
                    <button
                      key={p}
                      onClick={() => handleSendMessage(p)}
                      className="btn btn-outline"
                      style={{ justifyContent: "space-between", textAlign: "left", fontSize: 11 }}
                    >
                      <span>{p}</span>
                      <ArrowRight size={12} />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              (currentConversation.messages || []).map((msg) => {
                const isUser = msg.role === "user";
                return (
                  <div
                    key={msg.id}
                    style={{
                      display: "flex",
                      gap: 10,
                      alignItems: "flex-start",
                      alignSelf: isUser ? "flex-end" : "flex-start",
                      maxWidth: "80%",
                    }}
                  >
                    {!isUser && (
                      <div className="avatar" style={{ background: "var(--accent-soft)", color: "var(--accent)", flexShrink: 0 }}>
                        <Sparkles size={13} />
                      </div>
                    )}
                    <div
                      style={{
                        padding: "10px 14px",
                        borderRadius: 12,
                        background: isUser ? "var(--accent)" : "var(--surface-2)",
                        color: isUser ? "#fff" : "var(--fg)",
                        fontSize: 13,
                        lineHeight: 1.5,
                      }}
                    >
                      {isUser ? (
                        msg.content
                      ) : (
                        <AssistantMarkdown content={msg.content} />
                      )}
                    </div>
                    {isUser && (
                      <div className="avatar" style={{ background: "var(--surface-2)", color: "var(--muted)", flexShrink: 0 }}>
                        <User size={13} />
                      </div>
                    )}
                  </div>
                );
              })
            )}
            {sending && (
              <div
                style={{
                  display: "flex",
                  gap: 10,
                  alignItems: "center",
                  alignSelf: "flex-start",
                  maxWidth: "80%",
                }}
              >
                <div className="avatar" style={{ background: "var(--accent-soft)", color: "var(--accent)", flexShrink: 0 }}>
                  <Sparkles size={13} />
                </div>
                <div
                  style={{
                    padding: "8px 12px",
                    borderRadius: 12,
                    background: "var(--surface-2)",
                    color: "var(--muted)",
                    fontSize: 12,
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  <Loader2
                    size={13}
                    className="animate-spin"
                    style={{ animation: "spin 1s linear infinite", flexShrink: 0 }}
                  />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Prompt input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            style={{ display: "flex", gap: 10, paddingTop: 12, borderTop: "1px solid var(--line)" }}
          >
            <input
              className="input"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about your skills, role matches, or what to learn next..."
              disabled={sending}
            />
            <button type="submit" className="btn btn-primary" disabled={!inputMessage.trim() || sending}>
              {sending ? (
                <Loader2
                  size={14}
                  className="animate-spin"
                  style={{ animation: "spin 1s linear infinite", flexShrink: 0 }}
                />
              ) : (
                <Send size={14} />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
