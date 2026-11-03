"use client";

import { useEffect, useState } from "react";
import { Check, Loader2, Save, UserCheck, AlertCircle } from "lucide-react";
import { profileApi } from "@/lib/api";
import type { UserProfileResponse } from "@/types";

export default function ProfileView() {
  const [profile, setProfile] = useState<UserProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Form fields matching backend UserProfileUpdate schema
  const [displayName, setDisplayName] = useState("");
  const [headline, setHeadline] = useState("");
  const [educationSummary, setEducationSummary] = useState("");
  const [experienceSummary, setExperienceSummary] = useState("");
  const [preferredDomains, setPreferredDomains] = useState("");

  useEffect(() => {
    let active = true;
    profileApi
      .getProfile()
      .then((data) => {
        if (!active) return;
        setProfile(data);
        setDisplayName(data.display_name || "");
        setHeadline(data.headline || "");
        setEducationSummary(data.education_summary || "");
        setExperienceSummary(data.experience_summary || "");
        setPreferredDomains((data.preferred_domains || []).join(", "));
        setLoading(false);
      })
      .catch((err) => {
        if (active) {
          setErrorMessage(err.message || "Failed to load profile.");
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
      const domains = preferredDomains
        .split(",")
        .map((d) => d.trim())
        .filter(Boolean);

      const updated = await profileApi.updateProfile({
        display_name: displayName.trim() || undefined,
        headline: headline.trim() || undefined,
        education_summary: educationSummary.trim() || undefined,
        experience_summary: experienceSummary.trim() || undefined,
        preferred_domains: domains.length > 0 ? domains : undefined,
      });

      setProfile(updated);
      setStatusMessage("Profile updated successfully in backend.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to update profile.");
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
            <div className="card-kicker">Identity & Direction</div>
            <div className="card-title" style={{ marginTop: 6 }}>
              Personal Profile
            </div>
          </div>
          <UserCheck size={18} color="var(--accent)" />
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
            <label htmlFor="displayName">Display Name</label>
            <input
              id="displayName"
              className="input"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Maya Chen"
            />
          </div>

          <div className="field" style={{ marginTop: 12 }}>
            <label htmlFor="headline">Professional Headline / Target Role</label>
            <input
              id="headline"
              className="input"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
              placeholder="e.g. Frontend Engineer · React & Design Systems"
            />
          </div>

          <div className="field" style={{ marginTop: 12 }}>
            <label htmlFor="education">Education Summary</label>
            <input
              id="education"
              className="input"
              value={educationSummary}
              onChange={(e) => setEducationSummary(e.target.value)}
              placeholder="e.g. B.S. in Computer Science, 2025"
            />
          </div>

          <div className="field" style={{ marginTop: 12 }}>
            <label htmlFor="experience">Experience Summary</label>
            <textarea
              id="experience"
              className="input"
              style={{ minHeight: 70, resize: "vertical" }}
              value={experienceSummary}
              onChange={(e) => setExperienceSummary(e.target.value)}
              placeholder="e.g. Summer intern building Next.js apps, open source contributor"
            />
          </div>

          <div className="field" style={{ marginTop: 12 }}>
            <label htmlFor="domains">Preferred Domains (comma-separated)</label>
            <input
              id="domains"
              className="input"
              value={preferredDomains}
              onChange={(e) => setPreferredDomains(e.target.value)}
              placeholder="e.g. Frontend Engineering, UI Systems, Distributed Systems"
            />
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
                <Save size={14} /> Save Profile Changes
              </>
            )}
          </button>
        </form>
      </section>

      <section className="card card-pad">
        <div className="card-kicker">Workspace Principles</div>
        <div className="card-title" style={{ marginTop: 6 }}>
          Evidence That Travels
        </div>
        <div style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 14 }}>
          <div className="activity">
            <div className="activity-icon">
              <Check size={14} />
            </div>
            <div className="activity-main">
              <div className="activity-title">Claims stay distinct from proof</div>
              <div className="activity-detail">
                What you claim in your profile is cataloged as self-reported until supported by quizzes or repositories.
              </div>
            </div>
          </div>
          <div className="activity">
            <div className="activity-icon">
              <Check size={14} />
            </div>
            <div className="activity-main">
              <div className="activity-title">Persistent personal space</div>
              <div className="activity-detail">
                Your goals, evidence, and roadmaps persist across logins in your private database account.
              </div>
            </div>
          </div>
          <div className="activity">
            <div className="activity-icon">
              <Check size={14} />
            </div>
            <div className="activity-main">
              <div className="activity-title">Non-linear flexibility</div>
              <div className="activity-detail">
                Access any module at any time without completing a mandatory wizard sequence.
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
