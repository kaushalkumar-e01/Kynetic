"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowUpRight, Check, FileText, GitBranch, Plus, ShieldCheck, Loader2 } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { workspaceApi, skillsApi } from "@/lib/api";
import type { ActivityResponse, UserCapabilityResponse, WorkspaceSummaryResponse } from "@/types";
import { AppShell, PageHeading } from "@/components/AppShell";

const defaultSeries = [
  { week: "W1", score: 50 },
  { week: "W2", score: 55 },
  { week: "W3", score: 60 },
  { week: "W4", score: 65 },
  { week: "W5", score: 70 },
  { week: "W6", score: 74 },
];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<WorkspaceSummaryResponse | null>(null);
  const [capabilities, setCapabilities] = useState<UserCapabilityResponse[]>([]);
  const [activities, setActivities] = useState<ActivityResponse[]>([]);

  useEffect(() => {
    let active = true;
    Promise.allSettled([
      workspaceApi.getWorkspaceSummary(),
      skillsApi.listCapabilities(),
      workspaceApi.getActivities(6),
    ]).then(([sumRes, capRes, actRes]) => {
      if (!active) return;
      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (capRes.status === "fulfilled") setCapabilities(capRes.value);
      if (actRes.status === "fulfilled") setActivities(actRes.value);
      setLoading(false);
    });

    return () => {
      active = false;
    };
  }, []);

  const userName = summary?.profile?.display_name || summary?.user.email.split("@")[0] || "there";
  const targetHeadline = summary?.profile?.headline || "Software Engineering";

  // Calculate evidence mix percentages
  const claimedCount = capabilities.filter((c) => c.estimated_band === "claimed").length;
  const assessedCount = capabilities.filter((c) => c.estimated_band === "proficient" || c.estimated_band === "advanced").length;
  const projectCount = capabilities.filter((c) => c.estimated_band === "foundational").length;
  const totalSignals = capabilities.length || 1;

  const readinessScore = Math.min(
    95,
    Math.round(
      capabilities.reduce((acc, c) => acc + (c.score || 50), 0) / (capabilities.length || 1)
    )
  );

  return (
    <AppShell>
      <PageHeading
        eyebrow="Personalized Workspace"
        title={`Good day, ${userName}.`}
        subtitle="A clear view of the capability you're building — and the persistent proof behind it."
        action={
          <Link href="/progress" className="btn btn-outline">
            View progress <ArrowUpRight size={14} />
          </Link>
        }
      />

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 280 }}>
          <Loader2 size={24} className="animate-spin text-muted" />
        </div>
      ) : (
        <>
          <div className="dashboard-hero">
            <section className="card welcome-panel">
              <div className="welcome-label">Pick up where you left off</div>
              <h2>Your next proof point is closer than you think.</h2>
              <p>
                {summary?.active_roadmap
                  ? `Active roadmap: "${summary.active_roadmap.title}". Continue working on your current milestones.`
                  : "You have persistent evidence stored in your workspace. Connect a project or complete an assessment to strengthen your profile."}
              </p>
              <div style={{ display: "flex", gap: 9, marginTop: 23 }}>
                <Link href="/projects/new" className="btn btn-light">
                  <Plus size={14} /> Add project evidence
                </Link>
                <Link href="/roadmaps" className="btn" style={{ color: "#d2d0ff" }}>
                  View roadmaps <ArrowUpRight size={14} />
                </Link>
              </div>
            </section>
            <section className="card readiness">
              <div className="readiness-top">
                <div>
                  <div className="card-kicker">Capability readiness</div>
                  <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 9 }}>
                    for {targetHeadline}
                  </div>
                </div>
                <div className="score-ring">
                  <strong>{readinessScore}</strong>
                  <small>%</small>
                </div>
              </div>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 8 }}>
                  <span className="muted">Based on verified signals</span>
                  <span style={{ color: "var(--teal)", fontWeight: 700 }}>
                    {summary?.assessments_count || 0} checks completed
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-value" style={{ width: `${readinessScore}%` }} />
                </div>
              </div>
            </section>
          </div>

          <div className="grid-2">
            <section className="card card-pad">
              <div className="section-head" style={{ marginBottom: 0 }}>
                <div>
                  <div className="card-kicker">Evidence mix</div>
                  <div className="card-title" style={{ marginTop: 6 }}>
                    Signal distribution
                  </div>
                </div>
                <Link className="icon-btn" href="/capabilities" aria-label="View capabilities">
                  <ArrowUpRight size={16} />
                </Link>
              </div>
              <div className="evidence-list">
                <div className="evidence-row">
                  <span className="evidence-dot dot-claimed" />
                  <div style={{ width: 92, fontSize: 12 }}>
                    Claimed <span className="muted">{claimedCount}</span>
                  </div>
                  <div className="bar">
                    <span
                      className="bar-claimed"
                      style={{ width: `${Math.round((claimedCount / totalSignals) * 100)}%` }}
                    />
                  </div>
                  <span className="muted" style={{ fontSize: 11 }}>
                    {Math.round((claimedCount / totalSignals) * 100)}%
                  </span>
                </div>
                <div className="evidence-row">
                  <span className="evidence-dot dot-assessed" />
                  <div style={{ width: 92, fontSize: 12 }}>
                    Assessed <span className="muted">{assessedCount}</span>
                  </div>
                  <div className="bar">
                    <span
                      className="bar-assessed"
                      style={{ width: `${Math.round((assessedCount / totalSignals) * 100)}%` }}
                    />
                  </div>
                  <span className="muted" style={{ fontSize: 11 }}>
                    {Math.round((assessedCount / totalSignals) * 100)}%
                  </span>
                </div>
                <div className="evidence-row">
                  <span className="evidence-dot dot-project" />
                  <div style={{ width: 92, fontSize: 12 }}>
                    Projects <span className="muted">{projectCount}</span>
                  </div>
                  <div className="bar">
                    <span
                      className="bar-project"
                      style={{ width: `${Math.round((projectCount / totalSignals) * 100)}%` }}
                    />
                  </div>
                  <span className="muted" style={{ fontSize: 11 }}>
                    {Math.round((projectCount / totalSignals) * 100)}%
                  </span>
                </div>
              </div>
              <div className="stat-row">
                <div className="stat-chip">
                  <span className="number">{summary?.projects_count || 0}</span>
                  <span className="label">projects</span>
                </div>
                <div className="stat-chip">
                  <span className="number">{summary?.resumes_count || 0}</span>
                  <span className="label">resumes</span>
                </div>
                <div className="stat-chip">
                  <span className="number">{summary?.goals_count || 0}</span>
                  <span className="label">goals active</span>
                </div>
              </div>
            </section>

            <section className="card card-pad">
              <div className="section-head" style={{ marginBottom: 0 }}>
                <div>
                  <div className="card-kicker">Recent activity</div>
                  <div className="card-title" style={{ marginTop: 6 }}>
                    Workspace events
                  </div>
                </div>
                <Link className="muted" href="/progress" style={{ fontSize: 11 }}>
                  See all
                </Link>
              </div>
              <div className="activity-list">
                {activities.length === 0 ? (
                  <p className="muted" style={{ fontSize: 12, padding: "24px 0" }}>
                    No activities recorded yet. Start by uploading a resume or starting an assessment!
                  </p>
                ) : (
                  activities.map((item) => (
                    <div className="activity" key={item.id}>
                      <div className="activity-icon">
                        {item.activity_type.includes("assessment") ? (
                          <Check size={15} />
                        ) : item.activity_type.includes("project") ? (
                          <GitBranch size={15} />
                        ) : (
                          <FileText size={15} />
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
                      <div className="activity-time">
                        {new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>

          <div style={{ marginTop: 34 }}>
            <div className="section-head">
              <div>
                <div className="eyebrow">Momentum map</div>
                <h2 style={{ margin: "7px 0 0", fontSize: 20, letterSpacing: "-.04em" }}>
                  Keep building signal
                </h2>
              </div>
              <Link href="/roadmaps" className="btn btn-ghost">
                Open roadmaps <ArrowUpRight size={14} />
              </Link>
            </div>
            <div className="grid-3">
              <Link href="/resumes" className="card move-card tone-violet">
                <div className="move-label">Resume Intelligence</div>
                <div className="move-title">Extract and verify claims</div>
                <div className="move-detail">Upload PDF · instant AI capability parsing</div>
                <ArrowUpRight size={15} style={{ position: "absolute", right: 17, top: 18, color: "var(--muted)" }} />
              </Link>
              <Link href="/assessments" className="card move-card tone-teal">
                <div className="move-label">Assessments</div>
                <div className="move-title">Test your knowledge</div>
                <div className="move-detail">Adaptive quizzes · demonstrate real capability</div>
                <ArrowUpRight size={15} style={{ position: "absolute", right: 17, top: 18, color: "var(--muted)" }} />
              </Link>
              <Link href="/placement" className="card move-card tone-amber">
                <div className="move-label">Career Signal</div>
                <div className="move-title">Match with placement roles</div>
                <div className="move-detail">Explainable skill gaps · find role alignment</div>
                <ArrowUpRight size={15} style={{ position: "absolute", right: 17, top: 18, color: "var(--muted)" }} />
              </Link>
            </div>
          </div>

          <div className="grid-2" style={{ marginTop: 34 }}>
            <section className="card card-pad">
              <div className="section-head" style={{ marginBottom: 5 }}>
                <div>
                  <div className="card-kicker">Readiness trajectory</div>
                  <div className="card-title" style={{ marginTop: 6 }}>
                    Evidence progression
                  </div>
                </div>
                <span style={{ color: "var(--teal)", fontSize: 12, fontWeight: 700 }}>Active</span>
              </div>
              <div style={{ height: 210, margin: "20px -10px -8px -16px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={defaultSeries}>
                    <defs>
                      <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6c63ff" stopOpacity={0.28} />
                        <stop offset="100%" stopColor="#6c63ff" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="week" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: "#85899b" }} />
                    <YAxis hide domain={[40, 90]} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--surface)",
                        border: "1px solid var(--line)",
                        borderRadius: 8,
                        fontSize: 11,
                      }}
                    />
                    <Area type="monotone" dataKey="score" stroke="#6c63ff" fill="url(#scoreFill)" strokeWidth={2.5} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="card card-pad">
              <div className="section-head" style={{ marginBottom: 0 }}>
                <div>
                  <div className="card-kicker">Capability focus</div>
                  <div className="card-title" style={{ marginTop: 6 }}>
                    Demonstrated capabilities
                  </div>
                </div>
                <ShieldCheck size={17} color="var(--teal)" />
              </div>
              <div className="skill-grid" style={{ marginTop: 15 }}>
                {capabilities.length === 0 ? (
                  <p className="muted" style={{ fontSize: 12, padding: "24px 0" }}>
                    No capabilities recorded yet. Take an assessment or add evidence to build your map.
                  </p>
                ) : (
                  capabilities.slice(0, 4).map((skill) => (
                    <Link
                      href={`/capabilities/${skill.skill_id}`}
                      className="skill-card"
                      style={{ padding: "13px 0", borderBottom: "1px solid var(--line)" }}
                      key={skill.id}
                    >
                      <div className="skill-head">
                        <div>
                          <div className="skill-name" style={{ fontSize: 12 }}>
                            {skill.skill_name || "Skill"}
                          </div>
                          <div className="skill-category">
                            {skill.category || "Technical"} · {skill.estimated_band}
                          </div>
                        </div>
                        <div className="skill-score" style={{ fontSize: 17 }}>
                          {Math.round(skill.score)}
                        </div>
                      </div>
                      <div className="progress-track" style={{ marginTop: 10, height: 6 }}>
                        <div className="progress-value" style={{ width: `${Math.round(skill.score)}%` }} />
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </section>
          </div>
        </>
      )}
    </AppShell>
  );
}
