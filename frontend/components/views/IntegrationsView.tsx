"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Check, Download, ExternalLink, Github, Loader2, Target, Trash2 } from "lucide-react";
import { integrationsApi } from "@/lib/api";
import type { GitHubRepoItem } from "@/types";

export default function IntegrationsView() {
  const [repos, setRepos] = useState<GitHubRepoItem[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [importingUrl, setImportingUrl] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadRepos = () => {
    setLoadingRepos(true);
    integrationsApi
      .listGitHubRepositories()
      .then((data) => {
        setRepos(data);
        setLoadingRepos(false);
      })
      .catch((err) => {
        setErrorMessage(err.message || "Failed to load GitHub repositories.");
        setLoadingRepos(false);
      });
  };

  useEffect(() => {
    loadRepos();
  }, []);

  const handleConnectGitHub = async () => {
    setErrorMessage(null);
    try {
      const connectData = await integrationsApi.getGitHubConnectUrl();
      if (connectData.authorization_url) {
        window.location.href = connectData.authorization_url;
      }
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  const handleImportRepo = async (repo: GitHubRepoItem) => {
    setImportingUrl(repo.html_url);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await integrationsApi.importGitHubRepository({
        name: repo.name,
        description: repo.description || undefined,
        repository_url: repo.html_url,
      });

      setStatusMessage(`Repository "${repo.name}" imported into Projects.`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to import repository.");
      }
    } finally {
      setImportingUrl(null);
    }
  };

  const handleDisconnectGitHub = async () => {
    if (!confirm("Disconnect GitHub account?")) return;
    setDisconnecting(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await integrationsApi.disconnectGitHub();
      setStatusMessage("GitHub connection removed.");
      loadRepos();
    } catch (err: unknown) {
      if (err instanceof Error) setErrorMessage(err.message);
    } finally {
      setDisconnecting(false);
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

      <div className="grid-2">
        {/* GitHub Integration Card */}
        <section className="card card-pad">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <div className="avatar" style={{ background: "var(--surface-2)" }}>
                <Github size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: 16, margin: 0 }}>GitHub Integration</h3>
                <span className="muted" style={{ fontSize: 11 }}>
                  Import repositories and verify code evidence
                </span>
              </div>
            </div>
            <button onClick={handleConnectGitHub} className="btn btn-outline" style={{ fontSize: 11 }}>
              <ExternalLink size={12} /> Connect Account
            </button>
          </div>

          <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, marginTop: 14 }}>
            Connect your GitHub account to import repositories into your project evidence catalog.
          </p>

          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <button
              onClick={handleDisconnectGitHub}
              className="btn btn-ghost"
              disabled={disconnecting}
              style={{ fontSize: 11, color: "#ff8787" }}
            >
              {disconnecting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
              Disconnect GitHub
            </button>
          </div>
        </section>

        {/* LinkedIn Integration Card (Mock only notice) */}
        <section className="card card-pad" style={{ background: "var(--surface-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <div className="avatar" style={{ background: "var(--surface)" }}>
                <Target size={20} color="var(--accent)" />
              </div>
              <div>
                <h3 style={{ fontSize: 16, margin: 0 }}>LinkedIn Profile Source</h3>
                <span className="muted" style={{ fontSize: 11 }}>
                  Profile claims & career history
                </span>
              </div>
            </div>
            <span
              style={{
                fontSize: 10,
                padding: "3px 7px",
                borderRadius: 4,
                background: "rgba(255, 187, 0, 0.15)",
                color: "var(--amber)",
                fontWeight: 700,
                textTransform: "uppercase",
              }}
            >
              Mock Preview Only
            </span>
          </div>

          <p className="muted" style={{ fontSize: 12, lineHeight: 1.5, marginTop: 14 }}>
            Direct LinkedIn OAuth is not supported by the backend REST contract (`/profile-sources` was not implemented).
            Users can enter profile context manually in the Profile view.
          </p>
        </section>
      </div>

      {/* Repositories List */}
      <div style={{ marginTop: 32 }}>
        <div className="section-head">
          <div>
            <div className="eyebrow">Connected Source</div>
            <h2 style={{ margin: "6px 0 0", fontSize: 18 }}>GitHub Repositories Available for Import</h2>
          </div>
        </div>

        {loadingRepos ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 36 }}>
            <Loader2 size={22} className="animate-spin text-muted" />
          </div>
        ) : repos.length === 0 ? (
          <div className="card card-pad" style={{ textAlign: "center", padding: "36px 20px" }}>
            <Github size={32} style={{ margin: "0 auto 10px", opacity: 0.4 }} />
            <div style={{ fontSize: 14, fontWeight: 600 }}>No repositories found</div>
            <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
              Click Connect Account above to authorize GitHub and discover repositories.
            </p>
          </div>
        ) : (
          <div className="grid-2">
            {repos.map((repo) => {
              const isImporting = importingUrl === repo.html_url;
              return (
                <div className="card card-pad" key={repo.full_name}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700 }}>{repo.name}</div>
                      <a
                        href={repo.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="muted"
                        style={{ fontSize: 11, textDecoration: "underline" }}
                      >
                        {repo.full_name}
                      </a>
                    </div>
                    <button
                      onClick={() => handleImportRepo(repo)}
                      className="btn btn-primary"
                      disabled={isImporting}
                      style={{ fontSize: 11, padding: "5px 10px" }}
                    >
                      {isImporting ? (
                        <>
                          <Loader2 size={12} className="animate-spin" /> Importing...
                        </>
                      ) : (
                        <>
                          <Download size={12} /> Import to Projects
                        </>
                      )}
                    </button>
                  </div>

                  {repo.description && (
                    <p className="muted" style={{ fontSize: 12, lineHeight: 1.4, marginTop: 8 }}>
                      {repo.description}
                    </p>
                  )}

                  <div style={{ display: "flex", gap: 12, marginTop: 12, fontSize: 11, color: "var(--muted)" }}>
                    {repo.language && <span>Language: <strong>{repo.language}</strong></span>}
                    <span>★ {repo.stargazers_count}</span>
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
