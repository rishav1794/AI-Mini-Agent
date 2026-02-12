import { useState } from "react";

type Msg = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", content: "Hi! I’m the Invictus Mini Agent. Ask me something." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Request failed");

      setMessages((m) => [...m, { role: "assistant", content: data.response }]);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "unknown";
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 820, margin: "0 auto", padding: 16, fontFamily: "system-ui" }}>
      <h2>Invictus Mini Agent</h2>

      <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12, height: 520, overflowY: "auto" }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, opacity: 0.7 }}>{m.role.toUpperCase()}</div>
            <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.4 }}>{m.content}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => (e.key === "Enter" ? send() : null)}
          placeholder='Try: "Create a todo: review demo" or "Explain RAG" or "12*(3+4)"'
          style={{ flex: 1, padding: "12px 12px", borderRadius: 10, border: "1px solid #ddd" }}
        />
        <button
          onClick={send}
          disabled={loading}
          style={{ padding: "12px 16px", borderRadius: 10, border: "1px solid #ddd", cursor: "pointer" }}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>

      <div style={{ marginTop: 10, fontSize: 12, opacity: 0.7 }}>
        Session: {sessionId}
      </div>
    </div>
  );
}
