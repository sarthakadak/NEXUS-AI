import React, { useState } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Login from "./Login";
import MultiAgentDashboard from "./MultiAgentDashboard";
import Profile from "./Profile";

const GOOGLE_CLIENT_ID = "591855603162-qsie11el4ddpj7hrq0rk7mk7rm3g8q54.apps.googleusercontent.com";

type View = "dashboard" | "profile";

function App() {
  const [user, setUser] = useState<string | null>(() => localStorage.getItem("nexus_user"));
  const [view, setView] = useState<View>("dashboard");

  const handleLogin = (name: string) => {
    localStorage.setItem("nexus_user", name);
    setUser(name);
  };

  const handleLogout = () => {
    localStorage.removeItem("nexus_user");
    setUser(null);
    setView("dashboard");
  };

  if (!user) {
    return (
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <Login onLogin={handleLogin} />
      </GoogleOAuthProvider>
    );
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      {view === "profile" ? (
        <Profile userName={user} onLogout={handleLogout} onBack={() => setView("dashboard")} />
      ) : (
        <MultiAgentDashboard onProfileClick={() => setView("profile")} userName={user} />
      )}
    </GoogleOAuthProvider>
  );
}

export default App;