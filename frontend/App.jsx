import React, { useState } from "react";
import axios from "axios";

function ChatBubble({ sender, text }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: sender === "user" ? "flex-end" : "flex-start",
        margin: "8px 0",
      }}
    >
      <div
        style={{
          background: sender === "user" ? "#DCF8C6" : "#FFF",
          color: "#222",
          padding: "10px 16px",
          borderRadius: "18px",
          maxWidth: "70%",
          boxShadow: "0 1px 2px rgba(0,0,0,0.08)",
        }}
      >
        {text}
      </div>
    </div>
  );
}

export default function App() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setHistory([...history, userMsg]);
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: input,
        history: history.map((h) => h.text),
      });
      setHistory([
        ...history,
        userMsg,
        { sender: "agent", text: res.data.answer },
      ]);
    } catch (e) {
      setHistory([
        ...history,
        userMsg,
        { sender: "agent", text: "Error: " + e.message },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "40px auto",
        fontFamily: "sans-serif",
      }}
    >
      <h2>RAG Chat Agent</h2>
      <div
        style={{
          minHeight: 400,
          border: "1px solid #eee",
          borderRadius: 8,
          padding: 16,
          background: "#fafbfc",
        }}
      >
        {history.map((msg, i) => (
          <ChatBubble key={i} sender={msg.sender} text={msg.text} />
        ))}
        {loading && <ChatBubble sender="agent" text="..." />}
      </div>
      <div style={{ display: "flex", marginTop: 16 }}>
        <input
          style={{
            flex: 1,
            padding: 12,
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your question..."
          disabled={loading}
        />
        <button
          style={{
            marginLeft: 8,
            padding: "0 24px",
            borderRadius: 8,
          }}
          onClick={sendMessage}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
