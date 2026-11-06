"use client";

import { useEffect, useState } from "react";
import { BarChart3, Check, FileText, GitBranch, Loader2 } from "lucide-react";
import { workspaceApi, skillsApi } from "@/lib/api";
import { formatActivityDateTime, formatFullDateTime } from "@/lib/utils/date";
import type { ActivityResponse, UserCapabilityResponse } from "@/types";

export default function ProgressView() {
  const [activities, setActivities] = useState<ActivityResponse[]>([]);
  const [capabilities, setCapabilities] = useState<UserCapabilityResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.allSettled([workspaceApi.getActivities(50), skillsApi.listCapabilities()]).then(
      ([actRes, capRes]) => {
        if (!active) return;
        if (actRes.status === "fulfilled") setActivities(actRes.value);
        if (capRes.status === "fulfilled") setCapabilities(capRes.value);
        setLoading(false);
      }
    );

    return () => {
      active = false;
    };
  }, []);

  return (
    <div>
      <div className="section-head" style={{ marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 18, margin: 0 }}>Progress & Capability Trajectory</h2>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            A long view of how your capability is changing over time across all verified evidence sources.
          </p>
        </div>
        <BarChart3 size={20} color="var(--accent)" />
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : (
        <div className="grid-2">
          {/* Signal Breakdown */}
          <section className="card card-pad">
            <div className="card-kicker">Capability Mix</div>
            <div className="card-title" style={{ marginTop: 6, marginBottom: 16 }}>
              Current Skill Bands ({capabilities.length})
            </div>
            {capabilities.length === 0 ? (
              <p className="muted" style={{ fontSize: 12 }}>No capabilities mapped yet.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {capabilities.map((c) => (
                  <div key={c.id}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                      <span><strong>{c.skill_name || "Skill"}</strong> · <span className="muted">{c.estimated_band}</span></span>
                      <span>{c.mastery_score !== undefined && c.mastery_score !== null ? `${c.mastery_score.toFixed(1)}/10` : `${Math.round(c.score)} pts`}</span>
                    </div>
                    <div className="progress-track" style={{ height: 6 }}>
                      <div className="progress-value" style={{ width: `${Math.round(c.score)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Full Activity Audit Log */}
          <section className="card card-pad">
            <div className="card-kicker">Audit Trail</div>
            <div className="card-title" style={{ marginTop: 6, marginBottom: 16 }}>
              Full Workspace Event Log
            </div>
            {activities.length === 0 ? (
              <p className="muted" style={{ fontSize: 12 }}>No activities recorded yet.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12, maxHeight: 420, overflowY: "auto" }}>
                {activities.map((item) => (
                  <div className="activity" key={item.id}>
                    <div className="activity-icon">
                      {item.activity_type.includes("assessment") ? (
                        <Check size={14} />
                      ) : item.activity_type.includes("project") ? (
                        <GitBranch size={14} />
                      ) : (
                        <FileText size={14} />
                      )}
                    </div>
                    <div className="activity-main">
                      <div className="activity-title">
                        {item.activity_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                      </div>
                      <div className="activity-detail">
                        {typeof item.details === "object" && item.details !== null
                          ? Object.entries(item.details)
                              .map(([k, v]) => `${k}: ${v}`)
                              .join(" · ")
                          : "Recorded workspace event"}
                      </div>
                    </div>
                    <div className="activity-time" title={formatFullDateTime(item.created_at)}>
                      {formatActivityDateTime(item.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

