import React, { useState } from "react";

interface ProfileProps {
  userName: string;
  userEmail?: string;
  onLogout: () => void;
  onBack: () => void;
}

export default function Profile({ userName, userEmail, onLogout, onBack }: ProfileProps) {
  const [name, setName] = useState(userName);
  const [editing, setEditing] = useState(false);

  const purpleGrad = "linear-gradient(135deg,#7c3aed,#a78bfa,#c4b5fd)";

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
          maxWidth: 420,
          background: "#1a1630",
          border: "1px solid #2b2547",
          borderRadius: 20,
          padding: "32px",
          boxShadow: "0 10px 40px rgba(124,58,237,.25)",
        }}
      >
        <button
          onClick={onBack}
          style={{
            background: "none",
            border: "none",
            color: "#9b93b8",
            fontSize: 13,
            cursor: "pointer",
            marginBottom: 20,
            padding: 0,
          }}
        >
          ← Back to Dashboard
        </button>

        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 24 }}>
          <div
            style={{
              width: 84,
              height: 84,
              borderRadius: "50%",
              background: purpleGrad,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontSize: 30,
              fontWeight: 700,
              marginBottom: 14,
              boxShadow: "0 8px 24px rgba(124,58,237,.4)",
            }}
          >
            {name.charAt(0).toUpperCase()}
          </div>

          {editing ? (
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              onBlur={() => setEditing(false)}
              onKeyDown={(e) => e.key === "Enter" && setEditing(false)}
              autoFocus
              style={{
                background: "#161228",
                border: "1px solid #2b2547",
                borderRadius: 8,
                color: "#f1edfc",
                fontSize: 18,
                fontWeight: 600,
                textAlign: "center",
                padding: "6px 10px",
                outline: "none",
              }}
            />
          ) : (
            <h2
              onClick={() => setEditing(true)}
              style={{ color: "#f1edfc", fontSize: 20, fontWeight: 700, cursor: "pointer" }}
              title="Click to edit"
            >
              {name}
            </h2>
          )}
          {userEmail && (
            <p style={{ color: "#6b6580", fontSize: 12.5, marginTop: 4 }}>{userEmail}</p>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 24 }}>
          <div
            style={{
              background: "#161228",
              border: "1px solid #2b2547",
              borderRadius: 12,
              padding: "14px 16px",
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              color: "#9b93b8",
            }}
          >
            <span>Active Agents</span>
            <span style={{ color: "#f1edfc", fontWeight: 600 }}>3</span>
          </div>
          <div
            style={{
              background: "#161228",
              border: "1px solid #2b2547",
              borderRadius: 12,
              padding: "14px 16px",
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              color: "#9b93b8",
            }}
          >
            <span>Tasks Split Today</span>
            <span style={{ color: "#f1edfc", fontWeight: 600 }}>12</span>
          </div>
          <div
            style={{
              background: "#161228",
              border: "1px solid #2b2547",
              borderRadius: 12,
              padding: "14px 16px",
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              color: "#9b93b8",
            }}
          >
            <span>Plan</span>
            <span style={{ color: "#f1edfc", fontWeight: 600 }}>Free</span>
          </div>
        </div>

        <button
          onClick={onLogout}
          style={{
            width: "100%",
            padding: "11px 0",
            borderRadius: 10,
            border: "1px solid #ef4444",
            background: "transparent",
            color: "#ef4444",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Log Out
        </button>
      </div>
    </div>
  );
}