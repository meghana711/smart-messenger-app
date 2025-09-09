// src/MessageForm.js
import React, { useState } from "react";
import axios from "axios";
import "./MessageForm.css";

export default function MessageForm() {
  const [msg, setMsg] = useState("");
  const [image, setImage] = useState(null);
  const [toEmail, setToEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [pdfLink, setPdfLink] = useState("");

  // ✅ Get access_token from cookies
  const getAccessTokenFromCookie = () => {
    const match = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="));
    return match ? match.split("=")[1] : null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!msg || !toEmail || !image) {
      alert("Please fill all fields.");
      return;
    }

    // ✅ Get the token and print it
    const token = getAccessTokenFromCookie();
    console.log("📦 Token from cookie:", token); // ← ADD THIS LINE

    if (!token) {
      alert("❌ Not authenticated. Please log in with Gmail.");
      window.location.href = "http://localhost:8001/api/google/login/";
      return;
    }

    const fd = new FormData();
    fd.append("message", msg);
    fd.append("recipient_email", toEmail);
    fd.append("image", image);

    try {
      const res = await axios.post("http://localhost:8001/api/send-email/", fd, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
        withCredentials: true,
      });

      setSubject(res.data.subject);
      setPdfLink(`http://localhost:8001/media/${res.data.pdf_id}.pdf`);
      alert("✅ Email sent successfully!");
    } catch (err) {
      console.error("❌ Error sending email:", err.response?.data || err.message);
      alert("❌ Failed to send email. Please check the console.");
    }
  };

  return (
    <div className="form-wrapper">
      <form className="email-form" onSubmit={handleSubmit}>
        <h2>📤 Smart Email Sender</h2>

        <textarea
          placeholder="Enter your message"
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          required
        ></textarea>

        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
          required
        />

        <input
          type="email"
          placeholder="Recipient Email"
          value={toEmail}
          onChange={(e) => setToEmail(e.target.value)}
          required
        />

        <button type="submit">Send Email</button>

        {subject && <p className="subject-line">📌 Subject: {subject}</p>}
       

        {pdfLink && (
          <a
            className="pdf-link"
            href={pdfLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            📎 Download PDF
          </a>
        )}
      </form>
    </div>
  );
}
