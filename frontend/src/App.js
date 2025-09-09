import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MessageForm from "./MessageForm";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null until checked

  useEffect(() => {
    // Check if the "access_token" cookie is set
    const accessToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="));

    if (accessToken) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>; // While checking auth
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/send"
          element={
            isAuthenticated ? <MessageForm /> : <GmailLoginRedirect />
          }
        />
        {/* Redirect all unknown paths to /send */}
        <Route path="*" element={<Navigate to="/send" />} />
      </Routes>
    </BrowserRouter>
  );
}

function GmailLoginRedirect() {
  useEffect(() => {
    window.location.href = "http://localhost:8001/api/google/login/";
  }, []);

  return <div>Redirecting to Gmail Login...</div>;
}

export default App;
