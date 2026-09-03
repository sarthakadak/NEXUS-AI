import React, { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";
interface LoginProps {
    onLogin: (name: string) => void;
}

export default function Login({ onLogin }: LoginProps) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const purpleGrad = "linear-gradient(135deg,#7c3aed,#a78bfa,#c4b5fd)";

    const handleGoogleSuccess = (credentialResponse: CredentialResponse) => {
        if (!credentialResponse.credential) return;
        const payload = JSON.parse(atob(credentialResponse.credential.split(".")[1]));
        onLogin(payload.name || payload.email || "User");
    };

    const handleEmailLogin = (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return;
        onLogin(email.split("@")[0]);
    };

    return (
        <div
            style={{
                minHeight: "100vh",
                width: "100vw",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "#131022",
                fontFamily: "'Segoe UI', system-ui, sans-serif",
            }}
        >
            <div
                style={{
                    width: "100%",
                    maxWidth: 380,
                    background: "#1a1630",
                    border: "1px solid #2b2547",
                    borderRadius: 20,
                    padding: "36px 32px",
                    boxShadow: "0 10px 40px rgba(124,58,237,.25)",
                }}
            >
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
                    <div
                        style={{
                            width: 100,
                            height: 100,
                            borderRadius: "50%",
                            background: "conic-gradient(from 180deg, #7c3aed, #c4b5fd, #a78bfa, #7c3aed)",
                            boxShadow: "0 10px 40px rgba(124,58,237,.45)",
                            animation: "loginFloat 4s ease-in-out infinite",
                        }}
                    />
                    <style>{`
            @keyframes loginFloat {
              0%,100%{transform:translateY(0)}
              50%{transform:translateY(-8px)}
            }
          `}</style>
                </div>

                <h1 style={{ color: "#f1edfc", fontSize: 22, fontWeight: 700, textAlign: "center", marginBottom: 4 }}>
                    Welcome to Nexus
                </h1>
                <p style={{ color: "#9b93b8", fontSize: 13, textAlign: "center", marginBottom: 24 }}>
                    Sign in to route your first task
                </p>

                <div style={{ display: "flex", justifyContent: "center", marginBottom: 18 }}>
                    {<GoogleLogin onSuccess={handleGoogleSuccess} onError={() => console.log("Google login failed")} theme="filled_black" shape="pill" />}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "18px 0", color: "#6b6580", fontSize: 12 }}>
                    <div style={{ flex: 1, height: 1, background: "#2b2547" }} />
                    or
                    <div style={{ flex: 1, height: 1, background: "#2b2547" }} />
                </div>

                <form onSubmit={handleEmailLogin}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "11px 14px",
                            borderRadius: 10,
                            border: "1px solid #2b2547",
                            background: "#161228",
                            color: "#f1edfc",
                            fontSize: 13.5,
                            marginBottom: 10,
                            outline: "none",
                            boxSizing: "border-box",
                        }}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "11px 14px",
                            borderRadius: 10,
                            border: "1px solid #2b2547",
                            background: "#161228",
                            color: "#f1edfc",
                            fontSize: 13.5,
                            marginBottom: 18,
                            outline: "none",
                            boxSizing: "border-box",
                        }}
                    />
                    <button
                        type="submit"
                        style={{
                            width: "100%",
                            padding: "11px 0",
                            borderRadius: 10,
                            border: "none",
                            background: purpleGrad,
                            color: "#fff",
                            fontSize: 14,
                            fontWeight: 600,
                            cursor: "pointer",
                            boxShadow: "0 4px 14px rgba(124,58,237,.4)",
                        }}
                    >
                        Sign In
                    </button>
                </form>

                <p style={{ color: "#6b6580", fontSize: 12, textAlign: "center", marginTop: 18 }}>
                    No account needed — just enter any email to continue
                </p>
            </div>
        </div>
    );
}