// src/GmailLogin.js
import React from "react";
import "./GmailLogin.css";

export default function GmailLogin() {
  return (
    <div className="login-container">
      <h2>Welcome to Smart Messenger</h2>
      <button
        className="gmail-btn"
        onClick={() => {
          window.location.href = "http://localhost:8001/api/google/login/";
        }}
      >
        Sign In with Gmail
      </button>
    </div>
  );
}
