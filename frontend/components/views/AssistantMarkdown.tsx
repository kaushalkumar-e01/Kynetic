"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy } from "lucide-react";

interface CodeBlockProps {
  code: string;
  language?: string;
}

function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code: ", err);
    }
  };

  return (
    <div
      style={{
        margin: "8px 0",
        borderRadius: 8,
        overflow: "hidden",
        border: "1px solid var(--line)",
        background: "#12131f",
        color: "#f1f2fb",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "4px 10px",
          background: "#181a2b",
          borderBottom: "1px solid var(--line)",
          fontSize: 10,
          color: "var(--muted)",
        }}
      >
        <span
          style={{
            fontFamily: "'DM Mono', monospace",
            textTransform: "uppercase",
            fontWeight: 600,
            color: "#a5a1ff",
          }}
        >
          {language || "code"}
        </span>
        <button
          onClick={handleCopy}
          type="button"
          style={{
            background: "transparent",
            border: "none",
            color: copied ? "#4ade80" : "inherit",
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            fontSize: 10,
            padding: "2px 4px",
          }}
          title="Copy code"
        >
          {copied ? (
            <>
              <Check size={11} color="#4ade80" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={11} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <div
        style={{
          padding: "8px 10px",
          overflowX: "auto",
          fontFamily: "'DM Mono', monospace",
          fontSize: 11.5,
          lineHeight: 1.5,
        }}
      >
        <pre style={{ margin: 0, padding: 0, background: "transparent", whiteSpace: "pre" }}>
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
}

interface AssistantMarkdownProps {
  content: string;
}

export default function AssistantMarkdown({ content }: AssistantMarkdownProps) {
  return (
    <div style={{ wordBreak: "break-word" }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre: ({ children }) => <>{children}</>,
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");
            const isInline = !match && !codeString.includes("\n");

            if (isInline) {
              return (
                <code
                  style={{
                    padding: "2px 5px",
                    borderRadius: 4,
                    fontSize: 11.5,
                    fontFamily: "'DM Mono', monospace",
                    background: "rgba(0, 0, 0, 0.15)",
                    color: "var(--accent-2)",
                    border: "1px solid var(--line)",
                  }}
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <CodeBlock code={codeString} language={match ? match[1] : ""} />
            );
          },
          h1: ({ children }) => (
            <h1
              style={{
                fontSize: 15,
                fontWeight: 700,
                margin: "10px 0 6px",
                borderBottom: "1px solid var(--line)",
                paddingBottom: 3,
              }}
            >
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 style={{ fontSize: 14, fontWeight: 700, margin: "9px 0 5px" }}>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 style={{ fontSize: 13, fontWeight: 600, margin: "8px 0 4px" }}>
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 style={{ fontSize: 12, fontWeight: 600, margin: "6px 0 3px" }}>
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p style={{ margin: "5px 0" }}>
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul style={{ margin: "6px 0", paddingLeft: 18, display: "grid", gap: 3 }}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol style={{ margin: "6px 0", paddingLeft: 18, display: "grid", gap: 3 }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li style={{ margin: 0 }}>
              {children}
            </li>
          ),
          hr: () => (
            <hr style={{ margin: "8px 0", border: 0, borderTop: "1px solid var(--line)" }} />
          ),
          blockquote: ({ children }) => (
            <blockquote
              style={{
                margin: "6px 0",
                paddingLeft: 10,
                borderLeft: "2px solid var(--accent)",
                fontStyle: "italic",
                color: "var(--muted)",
              }}
            >
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div
              style={{
                overflowX: "auto",
                margin: "8px 0",
                borderRadius: 6,
                border: "1px solid var(--line)",
              }}
            >
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11.5 }}>
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead style={{ background: "var(--surface)", borderBottom: "1px solid var(--line)" }}>
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th
              style={{
                padding: "6px 8px",
                textAlign: "left",
                fontSize: 10,
                textTransform: "uppercase",
                color: "var(--muted)",
              }}
            >
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td style={{ padding: "6px 8px", borderBottom: "1px solid var(--line)" }}>
              {children}
            </td>
          ),
          strong: ({ children }) => (
            <strong style={{ fontWeight: 700 }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em style={{ fontStyle: "italic" }}>
              {children}
            </em>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--accent)", textDecoration: "underline" }}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
