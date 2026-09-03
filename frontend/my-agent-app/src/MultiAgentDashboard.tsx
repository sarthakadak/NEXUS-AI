import React, { useState } from "react";

interface MultiAgentDashboardProps {
  onProfileClick?: () => void;
  userName?: string;
}

export default function MultiAgentDashboard({ onProfileClick, userName = "there" }: MultiAgentDashboardProps) {
  const [dark, setDark] = useState(false);
  const [now, setNow] = useState(new Date());
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [problem, setProblem] = useState("");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

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
  } else if (timeDecimal >= 17 && timeDecimal < 21) {
    greeting = "Good Evening";
    isSun = false;
  } else {
    greeting = "Good Night";
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
  const chips = ["🧩 Split Task", "🧠 Assign Agent", "📊 View Report", "🔁 Workflow", "🧭 Guide Me"];
  const cards = [
    { icon: "🧠", title: "Domain Split", desc: "Breaks your problem into legal, code, finance, research and more." },
    { icon: "🤝", title: "Agent Routing", desc: "Sends each sub-task to the LLM best suited for that specialty." },
    { icon: "📈", title: "Merge Reports", desc: "Combines every agent's output into one clear final answer." },
    { icon: "⏱", title: "Schedule Runs", desc: "Automate recurring multi-agent jobs on a timer." },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
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
      `}</style>

      {/* Sidebar toggle button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          position: "fixed",
          top: 20,
          left: sidebarOpen ? 214 : 16,
          zIndex: 20,
          width: 28,
          height: 44,
          borderRadius: "0 12px 12px 0",
          border: `1px solid ${glassBorder}`,
          borderLeft: "none",
          background: dark ? "rgba(26,22,48,0.85)" : "rgba(255,255,255,0.55)",
          backdropFilter: "blur(8px)",
          color: textPrimary,
          fontSize: 14,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
          transition: "left 0.35s ease, background 0.6s ease, border-color 0.6s ease",
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" style={{ transform: sidebarOpen ? "rotate(0deg)" : "rotate(180deg)", transition: "transform 0.35s ease" }}>
          <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {/* Sidebar */}
      <aside
        style={{
          width: 230,
          padding: 16,
          borderRight: `1px solid ${glassBorder}`,
          background: "transparent",
          position: "fixed",
          top: 0,
          left: 0,
          height: "100vh",
          zIndex: 10,
          display: "flex",
          flexDirection: "column",
          transform: sidebarOpen ? "translateX(0)" : "translateX(-100%)",
          transition: "transform 0.35s ease",
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
          <span style={{ fontWeight: 700, fontSize: 15 }}>Nexus</span>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 10,
            border: `1px solid ${glassBorder}`,
            background: glassBg,
            padding: "8px 12px",
            fontSize: 12,
            color: textSecondary,
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

        {navItems.map((item) => (
          <div
            key={item.label}
            className="nexus-hover"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              borderRadius: 9,
              padding: "9px 12px",
              fontSize: 13.5,
              color: textSecondary,
              cursor: "pointer",
              transition: "transform .2s",
            }}
          >
            <span style={{ width: 16, textAlign: "center" }}>{item.icon}</span> {item.label}
          </div>
        ))}

        <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: ".06em", color: textSecondary, margin: "16px 4px 6px" }}>
          Today
        </div>
        {todayItems.map((t) => (
          <div key={t} style={{ fontSize: 13, borderRadius: 8, padding: "7px 12px", color: textSecondary, cursor: "pointer" }}>
            {t}
          </div>
        ))}

        <div style={{ marginTop: "auto" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              borderRadius: 12,
              border: `1px solid ${glassBorder}`,
              background: glassBg,
              padding: "10px 12px",
              marginBottom: 10,
            }}
          >
            <span
              className="nexus-pulse-dot"
              style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e" }}
            />
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 600 }}>Orchestrator</div>
              <div style={{ fontSize: 10.5, color: textSecondary }}>Active · routing</div>
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
              <div style={{ fontSize: 12.5, fontWeight: 600 }}>{userName}</div>
              <div style={{ fontSize: 10.5, color: textSecondary }}>Developer</div>
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
          marginLeft: sidebarOpen ? 230 : 0,
          transition: "margin-left 0.35s ease",
          minHeight: "100vh",
        }}
      >
        <svg className="wave-layer slow" viewBox="0 0 1600 200" preserveAspectRatio="none">
          <path d="M0,100 C200,180 400,20 600,100 C800,180 1000,20 1200,100 C1400,180 1600,20 1800,100 L1800,200 L0,200 Z" fill={dark ? "#1c2f3a" : "#ffffff"} opacity={dark ? 0.6 : 0.15} />
        </svg>
        <svg className="wave-layer" viewBox="0 0 1600 200" preserveAspectRatio="none">
          <path d="M0,120 C200,60 400,160 600,110 C800,60 1000,160 1200,110 C1400,60 1600,160 1800,110 L1800,200 L0,200 Z" fill={dark ? "#245B55" : "#ffffff"} opacity={dark ? 0.75 : 0.12} />
        </svg>

        <div
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

        <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 14, padding: "18px 32px", position: "relative", zIndex: 2 }}>
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

        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "10px 20px 32px", textAlign: "center", position: "relative", zIndex: 2 }}>
          <div style={{ fontSize: 12.5, color: textSecondary, marginBottom: 40, cursor: "pointer" }}>
            Orchestrator · GPT-4o / Claude / Gemini ⌄
          </div>

          <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 4, color: textPrimary }}>
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
          <p style={{ fontSize: 13.5, color: textSecondary, marginBottom: 18 }}>
            Give me a problem — I'll split it across specialist agents
          </p>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center", marginBottom: 22, maxWidth: 640 }}>
            {chips.map((c) => (
              <div
                key={c}
                className="nexus-chip"
                style={{
                  padding: "8px 14px",
                  borderRadius: 20,
                  border: `1px solid ${glassBorder}`,
                  background: glassBg,
                  fontSize: 12.5,
                  color: textSecondary,
                  cursor: "pointer",
                  transition: "all .2s",
                }}
              >
                {c}
              </div>
            ))}
          </div>

          <div
            style={{
              width: "100%",
              maxWidth: 620,
              borderRadius: 20,
              border: `1px solid ${glassBorder}`,
              background: dark ? "rgba(20,30,48,0.55)" : "rgba(255,255,255,0.5)",
              backdropFilter: "blur(6px)",
              padding: "18px 20px",
              marginBottom: 26,
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
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
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
                }}
              >
                +
              </button>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ fontSize: 12, color: textSecondary, display: "flex", alignItems: "center", gap: 5 }}>
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
                  }}
                >
                  Split it 🚀
                </button>
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 14,
              width: "100%",
              maxWidth: 960,
            }}
          >{error && (
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

{result && (
  <div
    style={{
      width: "100%",
      maxWidth: 960,
      marginBottom: 26,
      padding: 20,
      borderRadius: 16,
      background: glassBg,
      border: `1px solid ${glassBorder}`,
      backdropFilter: "blur(6px)",
      textAlign: "left",
    }}
  >
    <h3 style={{ marginBottom: 10 }}>
      🧠 Analysis Complete
    </h3>

    <p style={{ marginBottom: 8 }}>
      <strong>Final Decision:</strong>{" "}
      {result.final_decision?.overall_feasibility || "N/A"}
    </p>

    <p>
      {result.final_decision?.final_recommendation || "No recommendation available."}
    </p>
  </div>
)}
            {cards.map((c) => (
              <div
                key={c.title}
                className="nexus-hover"
                style={{
                  background: glassBg,
                  border: `1px solid ${glassBorder}`,
                  borderRadius: 16,
                  padding: 18,
                  textAlign: "left",
                  cursor: "pointer",
                  transition: "transform .25s ease, background 0.6s ease, border-color 0.6s ease",
                }}
              >
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 9,
                    background: purpleGrad,
                    color: "#fff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 15,
                    marginBottom: 12,
                  }}
                >
                  {c.icon}
                </div>
                <h4 style={{ fontSize: 14, marginBottom: 5, color: textPrimary }}>{c.title}</h4>
                <p style={{ fontSize: 11.5, color: textSecondary, lineHeight: 1.4 }}>{c.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}