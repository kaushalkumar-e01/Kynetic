export type EvidenceKind = "claimed" | "assessed" | "project";

export type EvidenceItem = {
  kind: EvidenceKind;
  label: string;
  detail: string;
  score?: number;
};

export type Capability = {
  id: string;
  name: string;
  category: string;
  score: number;
  delta: string;
  evidence: EvidenceItem[];
  color: string;
};

export type Activity = {
  title: string;
  detail: string;
  time: string;
  kind: EvidenceKind;
  icon: string;
};

export type Project = {
  id: string;
  name: string;
  description: string;
  stack: string[];
  completeness: number;
  evidence: EvidenceKind;
};

export const currentUser = {
  name: "Maya Chen",
  firstName: "Maya",
  role: "Computer science · final year",
  initials: "MC",
  readiness: 74,
  target: "Frontend engineering",
};

export const capabilities: Capability[] = [
  {
    id: "frontend",
    name: "Frontend engineering",
    category: "Technical",
    score: 82,
    delta: "+8 this month",
    color: "indigo",
    evidence: [
      { kind: "assessed", label: "Assessed", detail: "React patterns · 86%", score: 86 },
      { kind: "project", label: "Project-supported", detail: "2 repositories" },
      { kind: "claimed", label: "Claimed", detail: "Resume · 3 years" },
    ],
  },
  {
    id: "data-structures",
    name: "Data structures",
    category: "Technical",
    score: 68,
    delta: "+4 this month",
    color: "teal",
    evidence: [
      { kind: "assessed", label: "Assessed", detail: "Arrays & graphs · 72%", score: 72 },
      { kind: "claimed", label: "Claimed", detail: "Resume · intermediate" },
    ],
  },
  {
    id: "communication",
    name: "Technical communication",
    category: "Human",
    score: 76,
    delta: "+11 this month",
    color: "violet",
    evidence: [
      { kind: "project", label: "Project-supported", detail: "Case study · strong" },
      { kind: "claimed", label: "Claimed", detail: "Resume · advanced" },
    ],
  },
  {
    id: "systems",
    name: "Systems thinking",
    category: "Technical",
    score: 54,
    delta: "Needs evidence",
    color: "amber",
    evidence: [
      { kind: "claimed", label: "Claimed", detail: "Resume · familiar" },
    ],
  },
];

export const activities: Activity[] = [
  { title: "React patterns assessment completed", detail: "Result: 86% · Frontend engineering", time: "Today, 10:24", kind: "assessed", icon: "check" },
  { title: "Portfolio repository connected", detail: "github.com/mayachen/kinetic-ui", time: "Yesterday", kind: "project", icon: "git" },
  { title: "Resume refreshed", detail: "3 claims added · 1 needs evidence", time: "Mon, 4:12 PM", kind: "claimed", icon: "file" },
];

export const projects: Project[] = [
  { id: "kinetic-ui", name: "Kinetic UI", description: "A motion-first component system for accessible product surfaces.", stack: ["React", "TypeScript", "Framer Motion"], completeness: 88, evidence: "project" },
  { id: "campus-circles", name: "Campus Circles", description: "Peer study groups with lightweight matching and progress loops.", stack: ["Next.js", "Postgres", "Tailwind"], completeness: 64, evidence: "project" },
  { id: "algo-notes", name: "Algo Notes", description: "A personal learning log for data structures and algorithms.", stack: ["JavaScript", "MDX"], completeness: 42, evidence: "claimed" },
];

export const chartData = [
  { week: "Sep 2", score: 52 }, { week: "Sep 9", score: 56 }, { week: "Sep 16", score: 58 },
  { week: "Sep 23", score: 63 }, { week: "Sep 30", score: 65 }, { week: "Oct 7", score: 69 },
  { week: "Oct 14", score: 74 },
];

export const nextMoves = [
  { label: "Add evidence", title: "Tell us about your systems project", detail: "12 min · strengthen one capability", route: "/projects/new", tone: "violet" },
  { label: "Keep going", title: "Complete the data structures check", detail: "20 min · unlock a stronger score", route: "/assessments/new", tone: "teal" },
  { label: "Career signal", title: "Review your top placement match", detail: "3 roles · 82% average fit", route: "/placement", tone: "amber" },
];
