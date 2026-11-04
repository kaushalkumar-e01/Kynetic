"use client";

import {
  BarChart3,
  BookOpenCheck,
  ChevronRight,
  FileText,
  FolderKanban,
  Github,
  Goal,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";
import { AppShell, PageHeading } from "@/components/AppShell";
import ProfileView from "@/components/views/ProfileView";
import SettingsView from "@/components/views/SettingsView";
import ResumeView from "@/components/views/ResumeView";
import CapabilitiesView from "@/components/views/CapabilitiesView";
import AssessmentsView from "@/components/views/AssessmentsView";
import ProjectsView from "@/components/views/ProjectsView";
import GoalsView from "@/components/views/GoalsView";
import PlacementView from "@/components/views/PlacementView";
import RoadmapsView from "@/components/views/RoadmapsView";
import AssistantView from "@/components/views/AssistantView";
import IntegrationsView from "@/components/views/IntegrationsView";
import ProgressView from "@/components/views/ProgressView";

const pageMeta: Record<
  string,
  { eyebrow: string; title: string; subtitle: string; icon: typeof Zap }
> = {
  resume: {
    eyebrow: "Evidence / Claimed",
    title: "Resume evidence",
    subtitle: "See what your resume says — and where stronger proof could make it credible.",
    icon: FileText,
  },
  capabilities: {
    eyebrow: "Evidence / Capability map",
    title: "Capabilities",
    subtitle: "Your skills, separated by signal and strengthened over time.",
    icon: Zap,
  },
  assessments: {
    eyebrow: "Evidence / Assessed",
    title: "Assessments",
    subtitle: "Short, focused checks that turn knowledge into a clearer signal.",
    icon: BookOpenCheck,
  },
  projects: {
    eyebrow: "Evidence / Project-supported",
    title: "Projects",
    subtitle: "The work behind your story, with context that helps it travel.",
    icon: FolderKanban,
  },
  integrations: {
    eyebrow: "Workspace / Sources",
    title: "Integrations",
    subtitle: "Bring your profile and repositories into one personal workspace.",
    icon: Github,
  },
  goals: {
    eyebrow: "Career / Direction",
    title: "Goals",
    subtitle: "A flexible set of directions to keep your next move in view.",
    icon: Goal,
  },
  placement: {
    eyebrow: "Career / Opportunity",
    title: "Placement matches",
    subtitle: "Roles where your current evidence is already telling a strong story.",
    icon: Target,
  },
  roadmaps: {
    eyebrow: "Career / Momentum",
    title: "Roadmaps",
    subtitle: "Focused paths that connect capability gaps to practical next steps.",
    icon: ChevronRight,
  },
  progress: {
    eyebrow: "Workspace / Analytics",
    title: "Progress",
    subtitle: "A longer view of how your capability is changing, not just what is checked off.",
    icon: BarChart3,
  },
  assistant: {
    eyebrow: "Kynetic assistant",
    title: "A thoughtful next move, on demand.",
    subtitle: "Ask about your evidence, a target role, or what to work on next.",
    icon: Sparkles,
  },
  profile: {
    eyebrow: "Workspace / Identity",
    title: "Your profile",
    subtitle: "The context that helps Kynetic make your workspace feel like yours.",
    icon: Target,
  },
  settings: {
    eyebrow: "Workspace / Preferences",
    title: "Settings",
    subtitle: "Keep your workspace calm, clear and connected to how you work.",
    icon: Target,
  },
};

function DetailCard({ kind }: { kind: string }) {
  switch (kind) {
    case "profile":
      return <ProfileView />;
    case "settings":
      return <SettingsView />;
    case "resume":
      return <ResumeView />;
    case "capabilities":
      return <CapabilitiesView />;
    case "assessments":
      return <AssessmentsView />;
    case "projects":
      return <ProjectsView />;
    case "goals":
      return <GoalsView />;
    case "placement":
      return <PlacementView />;
    case "roadmaps":
      return <RoadmapsView />;
    case "assistant":
      return <AssistantView />;
    case "integrations":
      return <IntegrationsView />;
    case "progress":
      return <ProgressView />;
    default:
      return (
        <div className="card card-pad" style={{ textAlign: "center", padding: "40px 20px" }}>
          <Sparkles size={28} style={{ margin: "0 auto 10px", opacity: 0.5 }} />
          <h3>Module: {kind}</h3>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            This workspace module is active. Select an item or use the navigation sidebar.
          </p>
        </div>
      );
  }
}

export default function WorkspacePage({
  kind,
  detail,
}: {
  kind: string;
  detail?: string[];
}) {
  const meta = pageMeta[kind] ?? {
    eyebrow: "Workspace",
    title: kind[0]?.toUpperCase() + kind.slice(1),
    subtitle: "Your workspace, in motion.",
    icon: Sparkles,
  };
  const nested = detail?.length;

  return (
    <AppShell>
      <PageHeading
        eyebrow={meta.eyebrow}
        title={nested ? `${meta.title} / detail` : meta.title}
        subtitle={meta.subtitle}
      />
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          marginBottom: 18,
          color: "var(--muted)",
          fontSize: 11,
        }}
      >
        <meta.icon size={14} color="var(--accent)" />
        <span>{nested ? `Detail view · ${detail?.join(" / ")}` : "Independent workspace module"}</span>
      </div>
      <DetailCard kind={kind} />
    </AppShell>
  );
}
