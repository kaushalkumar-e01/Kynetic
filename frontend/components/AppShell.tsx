"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Bell,
  BookOpenCheck,
  ChevronDown,
  FileText,
  FolderKanban,
  Github,
  Goal,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Search,
  Settings,
  Sparkles,
  Sun,
  Target,
  X,
  Zap,
} from "lucide-react";
import { authApi, profileApi } from "@/lib/api";
import type { UserProfileResponse, UserResponse } from "@/types";

export type EvidenceKind = "claimed" | "assessed" | "project";

export const navGroups = [
  {
    label: "Workspace",
    items: [
      { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { label: "Progress", href: "/progress", icon: BarChart3 },
    ],
  },
  {
    label: "Evidence",
    items: [
      { label: "Resume", href: "/resume", icon: FileText },
      { label: "Assessments", href: "/assessments", icon: BookOpenCheck },
      { label: "Projects", href: "/projects", icon: FolderKanban },
      { label: "Capabilities", href: "/capabilities", icon: Zap },
    ],
  },
  {
    label: "Career",
    items: [
      { label: "Goals", href: "/goals", icon: Goal },
      { label: "Placement", href: "/placement", icon: Target },
      { label: "Roadmaps", href: "/roadmaps", icon: Activity },
    ],
  },
];

export function EvidenceBadge({ kind, label }: { kind: EvidenceKind; label?: string }) {
  const names = { claimed: "Claimed", assessed: "Assessed", project: "Project-supported" };
  return (
    <span className={`evidence-badge badge-${kind}`}>
      <span className={`evidence-dot dot-${kind}`} />
      {label ?? names[kind]}
    </span>
  );
}

function isActive(pathname: string, href: string) {
  return pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`));
}

export function AppShell({ children }: { children: React.ReactNode; title?: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [dark, setDark] = useState(false);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [profile, setProfile] = useState<UserProfileResponse | null>(null);

  useEffect(() => {
    let active = true;
    authApi
      .getMe()
      .then((userData) => {
        if (active) setUser(userData);
      })
      .catch(() => {
        // Not authenticated
      });

    profileApi
      .getProfile()
      .then((profData) => {
        if (active) setProfile(profData);
      })
      .catch(() => {
        // Profile might not exist yet
      });

    return () => {
      active = false;
    };
  }, []);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore
    }
    router.push("/login");
    router.refresh();
  };

  const displayName = profile?.display_name || user?.email?.split("@")[0] || "Workspace";
  const initials = displayName
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const headline = profile?.headline || user?.email || "Early-career builder";

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="logo">
          <div className="logo-mark">
            <span>K</span>
          </div>
          <span>Kynetic</span>
        </div>
        <nav aria-label="Primary navigation">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-label">{group.label}</div>
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    className={`nav-item ${isActive(pathname, item.href) ? "active" : ""}`}
                    href={item.href}
                    key={item.href}
                    onClick={() => setOpen(false)}
                  >
                    <span className="nav-icon">
                      <Icon size={16} strokeWidth={1.8} />
                    </span>
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ))}
          <div className="nav-group">
            <div className="nav-label">Workspace</div>
            <Link
              className={`nav-item ${isActive(pathname, "/assistant") ? "active" : ""}`}
              href="/assistant"
              onClick={() => setOpen(false)}
            >
              <span className="nav-icon">
                <Sparkles size={16} strokeWidth={1.8} />
              </span>
              Assistant
            </Link>
            <Link
              className={`nav-item ${isActive(pathname, "/integrations") ? "active" : ""}`}
              href="/integrations"
              onClick={() => setOpen(false)}
            >
              <span className="nav-icon">
                <Github size={16} strokeWidth={1.8} />
              </span>
              Integrations
            </Link>
            <Link
              className={`nav-item ${isActive(pathname, "/settings") ? "active" : ""}`}
              href="/settings"
              onClick={() => setOpen(false)}
            >
              <span className="nav-icon">
                <Settings size={16} strokeWidth={1.8} />
              </span>
              Settings
            </Link>
          </div>
        </nav>
        <div className="sidebar-footer">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <Link href="/profile" className="user-mini" style={{ flex: 1, textDecoration: "none" }}>
              <div className="avatar">{initials}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 700, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {displayName}
                </div>
                <div className="muted" style={{ fontSize: 10, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {headline}
                </div>
              </div>
            </Link>
            <button
              onClick={handleLogout}
              className="icon-btn"
              title="Log out"
              aria-label="Log out"
              style={{ marginLeft: 4 }}
            >
              <LogOut size={14} />
            </button>
          </div>
          <div className="muted" style={{ fontSize: 10, padding: "9px 10px 0", lineHeight: 1.5 }}>
            Kynetic is your workspace. No forced sequence.
          </div>
        </div>
      </aside>
      <main className="main-with-sidebar">
        <header className="topbar">
          <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
            <button className="icon-btn mobile-menu" aria-label="Open navigation" onClick={() => setOpen(!open)}>
              {open ? <X size={18} /> : <Menu size={18} />}
            </button>
            <div className="searchbox">
              <Search size={15} />
              <span>Search workspace</span>
              <kbd>⌘ K</kbd>
            </div>
          </div>
          <div className="top-actions">
            <button className="icon-btn" aria-label="Toggle theme" onClick={toggleTheme}>
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <button className="icon-btn" aria-label="Notifications">
              <Bell size={16} />
            </button>
            <Link href="/assistant" className="btn btn-primary" style={{ padding: "9px 12px" }}>
              <Sparkles size={14} /> Ask Kynetic
            </Link>
          </div>
        </header>
        <div className="page-content">{children}</div>
        <Link href="/assistant" className="assistant-fab" aria-label="Open Kynetic assistant">
          <Sparkles size={19} />
        </Link>
      </main>
    </div>
  );
}

export function PageHeading({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="section-head">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1 className="page-title">{title}</h1>
        <p className="page-subtitle">{subtitle}</p>
      </div>
      {action}
    </div>
  );
}
