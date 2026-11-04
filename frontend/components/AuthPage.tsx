"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import { authApi } from "@/lib/api";

export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const register = mode === "register";

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (register) {
        await authApi.register({
          email: email.trim(),
          password,
          display_name: name.trim() || undefined,
        });
      } else {
        await authApi.login({
          email: email.trim(),
          password,
        });
      }
      router.push("/dashboard");
      router.refresh();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Authentication failed. Please check your credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-visual">
        <Link href="/" className="logo">
          <div className="logo-mark">
            <span>K</span>
          </div>
          <span>Kynetic</span>
        </Link>
        <div>
          <div className="eyebrow" style={{ color: "#aaa5ff" }}>
            Knowledge in motion
          </div>
          <h1>
            {register
              ? "Build the proof behind your next move."
              : "Welcome back to your capability workspace."}
          </h1>
          <p>Kynetic keeps your ambition connected to the evidence that makes it real.</p>
        </div>
        <div style={{ color: "#7f849d", fontSize: 11 }}>
          Your workspace is yours. No forced sequence.
        </div>
      </section>

      <section className="auth-form">
        <div className="form-card">
          <div className="eyebrow">{register ? "Create your workspace" : "Sign in"}</div>
          <h2>{register ? "Start with what you know." : "Pick up where you left off."}</h2>
          <p className="page-subtitle">
            {register
              ? "A clearer path to capability starts with your current signals."
              : "Your evidence map is ready when you are."}
          </p>

          {error && (
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
                marginTop: 14,
                marginBottom: 8,
              }}
            >
              <AlertCircle size={15} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="field">
              {register && (
                <>
                  <label htmlFor="name">Full name</label>
                  <input
                    className="input"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Maya Chen"
                    required
                  />
                </>
              )}
              <label htmlFor="email">Email address</label>
              <input
                className="input"
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
              <label htmlFor="password">Password</label>
              <input
                className="input"
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>
            <button
              className="btn btn-primary"
              style={{ width: "100%", justifyContent: "center", marginTop: 22 }}
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  {register ? "Creating workspace..." : "Signing in..."}
                </>
              ) : (
                <>
                  {register ? "Create my workspace" : "Continue to Kynetic"}
                  <ArrowRight size={14} />
                </>
              )}
            </button>
          </form>

          <div className="form-foot">
            {register ? (
              <>
                Already have an account? <Link href="/login">Sign in</Link>
              </>
            ) : (
              <>
                New to Kynetic? <Link href="/register">Create an account</Link>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
