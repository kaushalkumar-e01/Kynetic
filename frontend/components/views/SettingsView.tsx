"use client";

import { useEffect, useState } from "react";
import { Check, Loader2, Save, Settings, AlertCircle } from "lucide-react";
import { workspaceApi } from "@/lib/api";
import type { UserSettingsResponse } from "@/types";

export default function SettingsView() {
  const [settings, setSettings] = useState<UserSettingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [themePref, setThemePref] = useState("dark");
  const [emailDigest, setEmailDigest] = useState(true);
  const [difficultyPref, setDifficultyPref] = useState("adaptive");

  useEffect(() => {
    let active = true;
    workspaceApi
      .getSettings()
      .then((data) => {
        if (!active) return;
        setSettings(data);
        const prefs = (data.learning_preferences || {}) as Record<string, unknown>;
        if (typeof prefs.theme === "string") setThemePref(prefs.theme);
        if (typeof prefs.email_digest === "boolean") setEmailDigest(prefs.email_digest);
        if (typeof prefs.difficulty === "string") setDifficultyPref(prefs.difficulty);
        setLoading(false);
      })
      .catch((err) => {
        if (active) {
          setErrorMessage(err.message || "Failed to load settings.");
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatusMessage(null);
    setErrorMessage(null);

    try {
      const updated = await workspaceApi.updateSettings({
        learning_preferences: {
          theme: themePref,
          email_digest: emailDigest,
          difficulty: difficultyPref,
        },
      });
      setSettings(updated);
      setStatusMessage("Settings updated successfully.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to update settings.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
        <Loader2 size={24} className="animate-spin text-muted" />
      </div>
    );
  }

  return (
    <div className="grid-2">
      <section className="card card-pad">
        <div className="section-head" style={{ marginBottom: 16 }}>
          <div>
            <div className="card-kicker">Workspace Preferences</div>
            <div className="card-title" style={{ marginTop: 6 }}>
              Account & Environment
            </div>
          </div>
          <Settings size={18} color="var(--accent)" />
        </div>

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

        <form onSubmit={handleSave}>
          <div className="field">
            <label>Registered Account Email</label>
            <input className="input" value={settings?.email || ""} disabled style={{ opacity: 0.7 }} />
            <span className="muted" style={{ fontSize: 10, marginTop: 4 }}>
              Account Status: {settings?.account_status || "active"}
            </span>
          </div>

          <div className="field" style={{ marginTop: 14 }}>
            <label htmlFor="themePref">Workspace Theme Mode</label>
            <select
              id="themePref"
              className="input"
              value={themePref}
              onChange={(e) => setThemePref(e.target.value)}
            >
              <option value="dark">Dark Ink (Soft-Neon)</option>
              <option value="light">Light Mist</option>
            </select>
          </div>

          <div className="field" style={{ marginTop: 14 }}>
            <label htmlFor="difficultyPref">Assessment Difficulty Mode</label>
            <select
              id="difficultyPref"
              className="input"
              value={difficultyPref}
              onChange={(e) => setDifficultyPref(e.target.value)}
            >
              <option value="adaptive">Adaptive (Progresses based on answers)</option>
              <option value="standard">Standard Practice</option>
            </select>
          </div>

          <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 10 }}>
            <input
              type="checkbox"
              id="emailDigest"
              checked={emailDigest}
              onChange={(e) => setEmailDigest(e.target.checked)}
              style={{ width: 16, height: 16, accentColor: "var(--accent)" }}
            />
            <label htmlFor="emailDigest" style={{ fontSize: 13, cursor: "pointer" }}>
              Enable weekly progress & roadmap notification digests
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ marginTop: 22, width: "100%", justifyContent: "center" }}
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2 size={14} className="animate-spin" /> Saving...
              </>
            ) : (
              <>
                <Save size={14} /> Update Preferences
              </>
            )}
          </button>
        </form>
      </section>

      <section className="card card-pad">
        <div className="card-kicker">Security & Privacy</div>
        <div className="card-title" style={{ marginTop: 6 }}>
          Data Policy
        </div>
        <div style={{ marginTop: 16, fontSize: 12, lineHeight: 1.6, color: "var(--muted)" }}>
          <p>
            Kynetic sessions use secure HttpOnly cookies. Your credentials and tokens are never stored in browser
            localStorage or exposed to client JavaScript.
          </p>
          <p style={{ marginTop: 12 }}>
            Resume documents and private repository links are isolated to your private user ID and verified
            server-side with role and ownership checks.
          </p>
        </div>
      </section>
    </div>
  );
}

