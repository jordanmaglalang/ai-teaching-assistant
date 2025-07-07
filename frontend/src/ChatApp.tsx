import React, { useState, useEffect } from "react";
import axios from "axios";

interface Message {
  role: "system" | "user" | "reference";
  text: string;
}

export default function ChatApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionState, setSessionState] = useState({});
  const [questionIndex, setQuestionIndex] = useState(0);

  // Kick off first question on load
  useEffect(() => {
    handleSend(""); // send empty to get first question
  }, []);

  const handleSend = async (message: string) => {
    try {
      const res = await axios.post("http://localhost:8000/ask", {
        message,
        state: sessionState,
        index: questionIndex,
      });

      const reply = res.data.reply;
      const reference = res.data.reference;
      const newState = res.data.state;
      const newIndex = res.data.index;

      // Add user message if not empty
      if (message.trim()) {
        setMessages((prev) => [...prev, { role: "user", text: message }]);
      }

      // Add system reply and reference together
      setMessages((prev) => [
        ...prev,
        { role: "system", text: reply },
        ...(reference && reference.trim()
          ? [{ role: "reference", text: reference }as Message]
          : []),
      ]);

      setSessionState(newState);
      setQuestionIndex(newIndex);
      setInput("");
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Oops! Something went wrong." },
      ]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    handleSend(input);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-md bg-white rounded shadow p-4">
        <h1 className="text-2xl font-bold mb-4">Socratic Tutor</h1>
        <div className="h-80 overflow-y-auto mb-4 border p-2 rounded bg-gray-50">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-2 my-1 rounded ${
                msg.role === "user"
                  ? "bg-green-100 text-right"
                  : msg.role === "reference"
                  ? "bg-gray-200 text-left text-sm italic"
                  : "bg-blue-100 text-left"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="flex">
          <input
            className="flex-1 border rounded p-2 mr-2"
            type="text"
            value={input}
            placeholder="Type your answer..."
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white rounded px-4 py-2"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
