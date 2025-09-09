
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Inbox() {
  const [emails, setEmails] = useState([]);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    axios.get("http://localhost:8001/api/inbox/", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setEmails(res.data))
      .catch(err => console.error("Failed to fetch inbox", err));
  }, []);

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-indigo-800">📥 Recent Emails</h2>
      {emails.length === 0 ? (
        <p>No emails found.</p>
      ) : (
        <ul>
          {emails.map((email, index) => (
            <li key={index} className="mb-4 border-b pb-2">
              <p><strong>From:</strong> {email.from}</p>
              <p><strong>Subject:</strong> {email.subject}</p>
              <p className="text-gray-600">{email.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
