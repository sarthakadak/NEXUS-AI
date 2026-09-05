import React, { useState } from "react";

interface MultiAgentDashboardProps {
  onProfileClick?: () => void;
  userName?: string;
}

export default function MultiAgentDashboard({ onProfileClick, userName = "there" }: MultiAgentDashboardProps) {
  const [dark, setDark] = useState(false);
  const [now, setNow] = useState(new Date());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [problem, setProblem] = useState("");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [openAgents, setOpenAgents] = useState<Record<string, boolean>>({});
  const [todayOpen, setTodayOpen] = useState(true);
  const [navOpen, setNavOpen] = useState(true);

  const toggleAgent = (key: string) =>
    setOpenAgents((prev) => ({ ...prev, [key]: !prev[key] }));

  const renderAgentValue = (value: any): React.ReactNode => {
    if (value === null || value === undefined || value === "") {
      return <span style={{ opacity: 0.6 }}>—</span>;
    }
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      return <span>{String(value)}</span>;
    }
    if (Array.isArray(value)) {
      return (
        <ul style={{ margin: "4px 0 0 18px", padding: 0 }}>
          {value.map((item, i) => (
            <li key={i} style={{ marginBottom: 4 }}>
              {renderAgentValue(item)}
            </li>
          ))}
        </ul>
      );
    }
    if (typeof value === "object") {
      return (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 4 }}>
          {Object.entries(value).map(([k, v]) => (
            <div key={k} style={{ fontSize: 13.5 }}>
              <span style={{ fontWeight: 600, textTransform: "capitalize" }}>
                {k.replace(/_/g, " ")}:{" "}
              </span>
              {renderAgentValue(v)}
            </div>
          ))}
        </div>
      );
    }
    return <span>{String(value)}</span>;
  };

  const handleAnalyze = async () => {
  if (!problem.trim()) {
    setError("Please enter a problem statement.");
    return;
  }

  setLoading(true);
  setError("");
  setResult(null);

  try {
    const response = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        problem: problem,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Analysis failed.");
    }

    setResult(data.result);
  }  catch (err: any) {
  console.error("ANALYSIS ERROR:", err);

  setError(
    err?.message ||
      "Unable to connect to the AI backend. Make sure the Python API is running."
  );
} finally {
    setLoading(false);
  }
};


  React.useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const hasResult = loading || !!result || !!error;
  const hasContent = !!result || !!error;

  const hour = now.getHours();
  const minute = now.getMinutes();
  const timeDecimal = hour + minute / 60;

  let greeting = "Good Morning";
  let isSun = true;
  if (timeDecimal >= 5 && timeDecimal < 12) {
    greeting = "Good Morning";
    isSun = true;
  } else if (timeDecimal >= 12 && timeDecimal < 17) {
    greeting = "Good Afternoon";
    isSun = true;
  } else if (timeDecimal >= 17 && timeDecimal < 22) {
    greeting = "Good Evening";
    isSun = false;
  } else {
    greeting = "Late night work?";
    isSun = false;
  }

  let progress;
  if (isSun) {
    progress = (timeDecimal - 6) / 12;
  } else {
    let nightTime = timeDecimal >= 18 ? timeDecimal - 18 : timeDecimal + 6;
    progress = nightTime / 12;
  }
  progress = Math.max(0, Math.min(1, progress));

  const arcWidth = 560;
  const arcStartX = 40;
  const celestialX = arcStartX + progress * arcWidth;
  const celestialY = 160 - Math.sin(progress * Math.PI) * 130;

  const pageGradient = dark
    ? "linear-gradient(180deg, #141E30 0%, #245B55 100%)"
    : "linear-gradient(120deg, #6b4c6e 0%, #d98b9e 22%, #f0d9a8 45%, #cfe0b0 62%, #8fc3c0 80%, #6f9bc4 100%)";

  const textPrimary = dark ? "#f1edfc" : "#1e1b2e";
  const textSecondary = dark ? "#cfd8dc" : "#3a3550";
  const glassBorder = dark ? "rgba(255,255,255,0.15)" : "rgba(30,27,46,0.15)";
  const glassBg = dark ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.35)";

  const purpleGrad = "linear-gradient(135deg,#7c3aed,#a78bfa,#c4b5fd)";

  const navItems = [
    { icon: "▦", label: "Dashboard" },
    { icon: "🤖", label: "Agents" },
    { icon: "🌐", label: "Domains" },
  ];
  const todayItems = ["Split legal + finance query", "Route to Code agent", "Summarize research task"];

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        maxWidth: "100vw",
        overflowX: "hidden",
        fontFamily: "'Segoe UI', system-ui, sans-serif",
        color: textPrimary,
        background: pageGradient,
        transition: "background 0.6s ease, color 0.6s ease",
        position: "relative",
      }}
    >
      <style>{`
        @keyframes waveMove {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes celestialFloat {
          0%,100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        @keyframes glowPulse {
          0%,100% { opacity: .55; }
          50% { opacity: .85; }
        }
        @keyframes pulseDot {
          0%{box-shadow:0 0 0 0 rgba(34,197,94,.5)}
          70%{box-shadow:0 0 0 8px rgba(34,197,94,0)}
          100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}
        }
        .hero-bg {
          position: relative;
          overflow: hidden;
        }
        .wave-layer {
          position: absolute;
          left: 0; bottom: -10px;
          width: 200%; height: 160px;
          animation: waveMove 14s linear infinite;
        }
        .wave-layer.slow { animation-duration: 22s; opacity: .5; bottom: -20px; }
        .celestial-inner {
          animation: celestialFloat 6s ease-in-out infinite;
        }
        .celestial-glow {
          animation: glowPulse 4s ease-in-out infinite;
        }
        .nexus-hover:hover { transform: translateY(-3px); }
        .nexus-chip:hover { color: #7c3aed !important; border-color:#a78bfa !important; }
        .nexus-pulse-dot { animation: pulseDot 2s infinite; }

        @media (max-width: 640px) {
          .nexus-header-row {
            padding: 14px 16px !important;
            gap: 8px !important;
          }
          .nexus-hero-wrap {
            padding: 60px 14px 24px !important;
          }
          .nexus-greeting {
            font-size: 21px !important;
          }
          .nexus-sidebar {
            width: calc(100vw - 24px) !important;
            max-width: 320px !important;
            left: 12px !important;
            top: 12px !important;
          }
          .nexus-result-card {
            padding: 16px !important;
            border-radius: 14px !important;
          }
          .nexus-input-box {
            padding: 14px !important;
            border-radius: 16px !important;
          }
          .nexus-input-controls {
            flex-wrap: wrap;
            row-gap: 10px;
          }
          .nexus-recommended-label {
            display: none !important;
          }
          .nexus-celestial {
            width: 54px !important;
            height: 54px !important;
            opacity: 0.6;
          }
        }

        @media (max-width: 420px) {
          .nexus-greeting {
            font-size: 18px !important;
          }
        }
      `}</style>

      {/* Sidebar toggle button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          position: "fixed",
          top: 20,
          left: 16,
          zIndex: 20,
          width: 36,
          height: 36,
          borderRadius: 10,
          border: `1px solid ${glassBorder}`,
          background: dark ? "rgba(26,22,48,0.85)" : "rgba(255,255,255,0.55)",
          backdropFilter: "blur(8px)",
          color: textPrimary,
          fontSize: 14,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
          transition: "background 0.6s ease, border-color 0.6s ease",
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </button>
      {/* Backdrop for the dropdown sidebar */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "transparent",
            zIndex: 9,
          }}
        />
      )}
      {/* Sidebar as a dropdown */}
      <aside
        className="nexus-sidebar"
        style={{
          width: 260,
          maxHeight: "calc(100vh - 32px)",
          padding: 16,
          borderRadius: 16,
          border: dark ? "1px solid rgba(255,255,255,0.12)" : "1px solid rgba(0,0,0,0.08)",
          background: dark ? "rgba(24,24,28,0.6)" : "rgba(255,255,255,0.65)",
          backdropFilter: "blur(14px)",
          WebkitBackdropFilter: "blur(14px)",
          boxShadow: "0 12px 40px rgba(0,0,0,0.25)",
          position: "fixed",
          top: 16,
          left: 16,
          zIndex: 10,
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
          transformOrigin: "top left",
          transform: sidebarOpen ? "scale(1) translateY(0)" : "scale(0.92) translateY(-10px)",
          opacity: sidebarOpen ? 1 : 0,
          pointerEvents: sidebarOpen ? "auto" : "none",
          transition: sidebarOpen
            ? "transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease, background 0.4s ease, border-color 0.4s ease"
            : "transform 0.16s ease, opacity 0.16s ease, background 0.4s ease, border-color 0.4s ease",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, paddingBottom: 16 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 9,
              background: purpleGrad,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 700,
              fontSize: 14,
              boxShadow: "0 2px 10px rgba(124,58,237,.4)",
            }}
          >
            N
          </div>
          <span style={{ fontWeight: 700, fontSize: 15, color: (dark ? "#f1f1f3" : "#22232a") }}>Nexus</span>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 10,
            border: (dark ? "1px solid rgba(255,255,255,0.1)" : "1px solid rgba(0,0,0,0.08)"),
            background: (dark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.035)"),
            padding: "8px 12px",
            fontSize: 12,
            color: (dark ? "#9a9aa2" : "#6b6b74"),
            marginBottom: 16,
          }}
        >
          🔍 Search…
        </div>

        <button
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 9,
            padding: "9px 12px",
            fontSize: 13.5,
            fontWeight: 600,
            color: "#fff",
            background: purpleGrad,
            border: "none",
            marginBottom: 4,
            cursor: "pointer",
            boxShadow: "0 3px 12px rgba(124,58,237,.35)",
          }}
        >
          <span>✎</span> New Task
        </button>

        <button
          onClick={() => setNavOpen((v) => !v)}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
            margin: "16px 0 4px",
            padding: "4px 4px",
            background: "transparent",
            border: "none",
            cursor: "pointer",
          }}
        >
          <span style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: ".06em", color: (dark ? "#77777f" : "#8a8a92") }}>
            Pinned
          </span>
          <span
            style={{
              color: (dark ? "#77777f" : "#8a8a92"),
              fontSize: 12,
              transform: navOpen ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.25s ease",
            }}
          >
            ⌄
          </span>
        </button>
        {navOpen && navItems.map((item) => (
          <div
            key={item.label}
            className="nexus-hover"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              borderRadius: 9,
              padding: "8px 10px",
              fontSize: 13.5,
              color: (dark ? "#d4d4d8" : "#3a3a42"),
              cursor: "pointer",
              transition: "background .15s",
              background: "transparent",
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                border: "1.5px solid #7c8b99",
                flexShrink: 0,
              }}
            />
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.label}</span>
          </div>
        ))}

        <button
          onClick={() => setTodayOpen((v) => !v)}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
            margin: "18px 0 4px",
            padding: "4px 4px",
            background: "transparent",
            border: "none",
            cursor: "pointer",
          }}
        >
          <span style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: ".06em", color: (dark ? "#77777f" : "#8a8a92") }}>
            Chats
          </span>
          <span
            style={{
              color: (dark ? "#77777f" : "#8a8a92"),
              fontSize: 12,
              transform: todayOpen ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.25s ease",
            }}
          >
            ⌄
          </span>
        </button>
        {todayOpen && (
          <div style={{ background: "transparent" }}>
            {todayItems.map((t, i) => (
              <div
                key={t}
                className="nexus-hover"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  fontSize: 13,
                  borderRadius: 8,
                  padding: "8px 10px",
                  color: i === 0 ? (dark ? "#f1f1f3" : "#22232a") : (dark ? "#a4a4ac" : "#5a5a62"),
                  cursor: "pointer",
                  background: i === 0 ? (dark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.045)") : "transparent",
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    border: "1.5px solid #7c8b99",
                    flexShrink: 0,
                  }}
                />
                <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t}</span>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: "auto" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              borderRadius: 12,
              border: (dark ? "1px solid rgba(255,255,255,0.08)" : "1px solid rgba(0,0,0,0.06)"),
              background: (dark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.035)"),
              padding: "10px 12px",
              marginBottom: 10,
            }}
          >
            <span
              className="nexus-pulse-dot"
              style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e" }}
            />
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 600, color: (dark ? "#f1f1f3" : "#22232a") }}>Orchestrator</div>
              <div style={{ fontSize: 10.5, color: (dark ? "#9a9aa2" : "#6b6b74") }}>Active · routing</div>
            </div>
          </div>
          <div
            onClick={onProfileClick}
            style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 4px", cursor: "pointer" }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: purpleGrad,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 13,
                fontWeight: 600,
              }}
            >
              {userName.charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 600, color: (dark ? "#f1f1f3" : "#22232a") }}>{userName}</div>
              <div style={{ fontSize: 10.5, color: (dark ? "#9a9aa2" : "#6b6b74") }}>Developer</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div
        className="hero-bg"
        style={{
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          width: "100%",
          marginLeft: 0,
          transition: "margin-left 0.35s ease, width 0.35s ease",
          minHeight: "100vh",
          overflowX: "hidden",
          boxSizing: "border-box",
        }}
      >
        <svg className="wave-layer slow" viewBox="0 0 1600 200" preserveAspectRatio="none">
          <path d="M0,100 C200,180 400,20 600,100 C800,180 1000,20 1200,100 C1400,180 1600,20 1800,100 L1800,200 L0,200 Z" fill={dark ? "#1c2f3a" : "#ffffff"} opacity={dark ? 0.6 : 0.15} />
        </svg>
        <svg className="wave-layer" viewBox="0 0 1600 200" preserveAspectRatio="none">
          <path d="M0,120 C200,60 400,160 600,110 C800,60 1000,160 1200,110 C1400,60 1600,160 1800,110 L1800,200 L0,200 Z" fill={dark ? "#245B55" : "#ffffff"} opacity={dark ? 0.75 : 0.12} />
        </svg>

        <div
          className="nexus-celestial"
          style={{
            position: "absolute",
            top: celestialY,
            left: celestialX,
            width: 90,
            height: 90,
            transition: "top 1s linear, left 1s linear",
            zIndex: 1,
          }}
        >
          <div className="celestial-inner" style={{ position: "relative", width: "100%", height: "100%" }}>
            <div
              className="celestial-glow"
              style={{
                position: "absolute",
                inset: -20,
                borderRadius: "50%",
                background: isSun
                  ? "radial-gradient(circle, rgba(250,200,110,0.55) 0%, rgba(250,200,110,0) 70%)"
                  : "radial-gradient(circle, rgba(180,200,230,0.35) 0%, rgba(180,200,230,0) 70%)",
              }}
            />
            {isSun ? (
              <div
                style={{
                  position: "relative",
                  width: "100%",
                  height: "100%",
                  borderRadius: "50%",
                  background: "radial-gradient(circle at 35% 30%, #FFE9B0, #F5B94A 60%, #E08F2A)",
                  boxShadow: "0 0 40px rgba(250,200,110,0.5)",
                }}
              />
            ) : (
              <svg width="90" height="90" viewBox="0 0 90 90" style={{ filter: "drop-shadow(0 0 14px rgba(200,210,230,0.45))" }}>
                <defs>
                  <mask id="moonMask">
                    <rect width="90" height="90" fill="white" />
                    <circle cx="56" cy="38" r="30" fill="black" />
                  </mask>
                </defs>
                <circle cx="45" cy="45" r="34" fill="#DCE3ED" mask="url(#moonMask)" />
                <circle cx="30" cy="34" r="2" fill="#B8C2D6" opacity="0.6" />
                <circle cx="34" cy="52" r="1.4" fill="#B8C2D6" opacity="0.5" />
                <circle cx="22" cy="48" r="1.6" fill="#B8C2D6" opacity="0.4" />
              </svg>
            )}
          </div>
        </div>

        <div className="nexus-header-row" style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 14, padding: "18px 32px", position: "relative", zIndex: 2 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              border: `1px solid ${glassBorder}`,
              background: glassBg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: textSecondary,
            }}
          >
            ✉
          </div>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              border: `1px solid ${glassBorder}`,
              background: glassBg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: textSecondary,
            }}
          >
            🔔
          </div>

          <button
            onClick={() => setDark(!dark)}
            style={{
              width: 64,
              height: 34,
              borderRadius: 20,
              border: `1px solid ${glassBorder}`,
              background: glassBg,
              display: "flex",
              alignItems: "center",
              padding: 4,
              cursor: "pointer",
              transition: "background 0.6s ease, border-color 0.6s ease",
            }}
          >
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: "50%",
                background: purpleGrad,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 13,
                transform: dark ? "translateX(30px)" : "translateX(0)",
                transition: "transform .35s cubic-bezier(.4,1.6,.6,1)",
              }}
            >
              {dark ? "🌙" : "☀"}
            </div>
          </button>

          <div
            onClick={onProfileClick}
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: purpleGrad,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {userName.charAt(0).toUpperCase()}
          </div>
        </div>

        <div className="nexus-hero-wrap" style={{ display: "flex", flexDirection: "column", alignItems: hasResult ? "flex-start" : "center", padding: "10px 20px 32px", textAlign: hasResult ? "left" : "center", position: "relative", zIndex: 2, flex: 1, transition: "align-items 0.4s ease" }}>
          <h1
            className="nexus-greeting"
            style={{
              fontSize: hasResult ? 16 : 26,
              fontWeight: 700,
              marginBottom: hasResult ? 2 : 4,
              color: textPrimary,
              transition: "font-size 0.4s ease, margin-bottom 0.4s ease",
            }}
          >
            {greeting},{" "}
            <span
              style={{
                background: purpleGrad,
                WebkitBackgroundClip: "text",
                backgroundClip: "text",
                color: "transparent",
              }}
            >
              {userName}
            </span>
          </h1>
          <p
            style={{
              fontSize: hasResult ? 11.5 : 13.5,
              color: textSecondary,
              marginBottom: hasResult ? 14 : 18,
              transition: "font-size 0.4s ease, margin-bottom 0.4s ease",
              opacity: hasResult ? 0.75 : 1,
            }}
          >
            Give me a problem — I'll split it across specialist agents
          </p>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              width: "100%",
              maxWidth: 960,
              gap: 14,
              flex: 1,
              minHeight: 0,
              justifyContent: hasContent ? "flex-start" : "space-between",
            }}
          >
            <div>
              {loading && !hasContent && (
                <div
                  style={{
                    width: "100%",
                    maxWidth: 620,
                    marginBottom: 20,
                    padding: "16px 18px",
                    borderRadius: 14,
                    background: glassBg,
                    border: `1px solid ${glassBorder}`,
                    color: textSecondary,
                    fontSize: 13,
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <span
                    className="nexus-pulse-dot"
                    style={{ width: 8, height: 8, borderRadius: "50%", background: "#7c3aed" }}
                  />
                  Analyzing across Finance, Technical &amp; Market agents…
                </div>
              )}
              {error && (
  <div
    style={{
      width: "100%",
      maxWidth: 620,
      marginBottom: 20,
      padding: "12px 16px",
      borderRadius: 12,
      background: "rgba(220, 38, 38, 0.12)",
      border: "1px solid rgba(220, 38, 38, 0.3)",
      color: textPrimary,
      fontSize: 13,
    }}
  >
    {error}
  </div>
)}

{result && (() => {
  const feasibility: string = result.final_decision?.overall_feasibility || "N/A";
  const f = feasibility.toLowerCase();
  let badgeBg = "rgba(148,163,184,0.18)";
  let badgeBorder = "rgba(148,163,184,0.4)";
  let badgeColor = textPrimary;
  let badgeIcon = "❓";
  if (f.includes("not") || f.includes("infeasible") || f.includes("un")) {
    badgeBg = "rgba(220,38,38,0.14)";
    badgeBorder = "rgba(220,38,38,0.35)";
    badgeColor = "#dc2626";
    badgeIcon = "⚠️";
  } else if (f.includes("conditional")) {
    badgeBg = "rgba(217,119,6,0.14)";
    badgeBorder = "rgba(217,119,6,0.35)";
    badgeColor = "#d97706";
    badgeIcon = "🟡";
  } else if (f.includes("feasible")) {
    badgeBg = "rgba(22,163,74,0.14)";
    badgeBorder = "rgba(22,163,74,0.35)";
    badgeColor = "#16a34a";
    badgeIcon = "✅";
  }

  return (
    <div
      className="nexus-result-card"
      style={{
        width: "100%",
        maxWidth: 960,
        marginBottom: 26,
        padding: 24,
        borderRadius: 18,
        background: glassBg,
        border: `1px solid ${glassBorder}`,
        backdropFilter: "blur(6px)",
        textAlign: "left",
        boxShadow: "0 6px 24px rgba(0,0,0,0.12)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
          marginBottom: 18,
          paddingBottom: 16,
          borderBottom: `1px solid ${glassBorder}`,
        }}
      >
        <h3 style={{ margin: 0, fontSize: 17, fontWeight: 700, color: textPrimary }}>
          🧠 Analysis Complete
        </h3>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 7,
            padding: "6px 14px",
            borderRadius: 20,
            background: badgeBg,
            border: `1px solid ${badgeBorder}`,
            color: badgeColor,
            fontSize: 13,
            fontWeight: 700,
            letterSpacing: 0.2,
          }}
        >
          <span>{badgeIcon}</span>
          <span>{feasibility}</span>
        </div>
      </div>

      <div
        style={{
          fontSize: 11.5,
          fontWeight: 700,
          letterSpacing: 0.6,
          textTransform: "uppercase",
          color: textSecondary,
          marginBottom: 8,
        }}
      >
        🎯 Recommendation
      </div>
      <p
        style={{
          margin: 0,
          fontSize: 14.5,
          lineHeight: 1.65,
          color: textPrimary,
        }}
      >
        {result.final_decision?.final_recommendation || "No recommendation available."}
      </p>

      {(() => {
        const agents = [
          {
            key: "finance",
            icon: "💰",
            label: "Finance Agent",
            data:
              result.finance_agent ?? result.finance ?? result.agents?.finance ??
              result.financial_agent ?? null,
          },
          {
            key: "technical",
            icon: "⚙️",
            label: "Technical Agent",
            data:
              result.technical_agent ?? result.technical ?? result.agents?.technical ?? null,
          },
          {
            key: "market",
            icon: "📊",
            label: "Market Agent",
            data:
              result.market_agent ?? result.market ?? result.agents?.market ?? null,
          },
        ];

        const extraDecisionKeys = Object.entries(result.final_decision || {}).filter(
          ([k]) => !["overall_feasibility", "final_recommendation"].includes(k)
        );

        return (
          <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 10 }}>
            {agents.map((a) => {
              const isOpen = !!openAgents[a.key];
              return (
                <div
                  key={a.key}
                  style={{
                    borderRadius: 12,
                    border: `1px solid ${glassBorder}`,
                    background: dark ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.35)",
                    overflow: "hidden",
                  }}
                >
                  <button
                    onClick={() => toggleAgent(a.key)}
                    style={{
                      width: "100%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "12px 16px",
                      background: "transparent",
                      border: "none",
                      cursor: "pointer",
                      color: textPrimary,
                      fontSize: 13.5,
                      fontWeight: 600,
                    }}
                  >
                    <span>
                      {a.icon} {a.label}
                    </span>
                    <span
                      style={{
                        transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                        transition: "transform 0.25s ease",
                        color: textSecondary,
                      }}
                    >
                      ⌄
                    </span>
                  </button>
                  {isOpen && (
                    <div
                      style={{
                        padding: "0 16px 16px 16px",
                        fontSize: 13.5,
                        lineHeight: 1.6,
                        color: textPrimary,
                        borderTop: `1px solid ${glassBorder}`,
                        paddingTop: 12,
                      }}
                    >
                      {a.data ? renderAgentValue(a.data) : (
                        <span style={{ opacity: 0.6 }}>No data returned by this agent.</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            {extraDecisionKeys.length > 0 && (
              <div
                style={{
                  borderRadius: 12,
                  border: `1px solid ${glassBorder}`,
                  background: dark ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.35)",
                  overflow: "hidden",
                }}
              >
                <button
                  onClick={() => toggleAgent("decision_extra")}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: textPrimary,
                    fontSize: 13.5,
                    fontWeight: 600,
                  }}
                >
                  <span>📋 Additional Decision Details</span>
                  <span
                    style={{
                      transform: openAgents["decision_extra"] ? "rotate(180deg)" : "rotate(0deg)",
                      transition: "transform 0.25s ease",
                      color: textSecondary,
                    }}
                  >
                    ⌄
                  </span>
                </button>
                {openAgents["decision_extra"] && (
                  <div
                    style={{
                      padding: "0 16px 16px 16px",
                      fontSize: 13.5,
                      lineHeight: 1.6,
                      color: textPrimary,
                      borderTop: `1px solid ${glassBorder}`,
                      paddingTop: 12,
                    }}
                  >
                    {extraDecisionKeys.map(([k, v]) => (
                      <div key={k} style={{ marginBottom: 8 }}>
                        <span style={{ fontWeight: 600, textTransform: "capitalize" }}>
                          {k.replace(/_/g, " ")}:{" "}
                        </span>
                        {renderAgentValue(v)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })()}
    </div>
  );
})()}
            </div>

            <div
              className="nexus-input-box"
              style={{
                width: "100%",
                borderRadius: 20,
                border: `1px solid ${glassBorder}`,
                background: dark ? "rgba(20,30,48,0.55)" : "rgba(255,255,255,0.5)",
                backdropFilter: "blur(6px)",
                padding: "18px 20px",
                marginTop: hasContent ? 24 : 0,
                boxShadow: "0 4px 24px rgba(0,0,0,0.15)",
                transition: "background 0.6s ease, border-color 0.6s ease",
              }}
            >
              <input
                type="text"
                placeholder="Describe a problem — e.g. 'Plan a product launch'"
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                style={{
                  width: "100%",
                  border: "none",
                  outline: "none",
                  background: "transparent",
                  color: textPrimary,
                  fontSize: 14.5,
                  marginBottom: 26,
                }}
              />
              <div className="nexus-input-controls" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <button
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 10,
                    border: `1px solid ${glassBorder}`,
                    background: glassBg,
                    color: textSecondary,
                    fontSize: 16,
                    cursor: "pointer",
                    flexShrink: 0,
                  }}
                >
                  +
                </button>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <div className="nexus-recommended-label" style={{ fontSize: 12, color: textSecondary, display: "flex", alignItems: "center", gap: 5 }}>
                    ⭐ Recommended ⌄
                  </div>
                  <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    style={{
                      background: purpleGrad,
                      border: "none",
                      color: "#fff",
                      padding: "9px 18px",
                      borderRadius: 12,
                      fontSize: 13,
                      fontWeight: 600,
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      cursor: "pointer",
                      boxShadow: "0 4px 14px rgba(124,58,237,.4)",
                      flexShrink: 0,
                      whiteSpace: "nowrap",
                    }}
                  >
                    Split it 🚀
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}