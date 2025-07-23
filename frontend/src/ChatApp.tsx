import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

import "./ChatApp.css"; // ✅ Make sure to include your CSS animations!

interface Message {
  role: "system" | "user" | "reference" | "loading";
  text: string;
}

export default function ChatApp() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const [assignmentName, setAssignmentName] = useState("Socratic Tutor");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionState, setSessionState] = useState({});
  const [questionIndex, setQuestionIndex] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [headerTextType, setHeaderTextType] = useState<"question" | "label">(
    "question"
  );

  useEffect(() => {
    if (!assignmentId) return;

    axios
      .get(`http://localhost:8000/assignments/${assignmentId}`)
      .then((res) => {
        setAssignmentName(res.data.assignment_name);
      })
      .catch((err) => {
        console.error("Failed to fetch assignment", err);
        setAssignmentName("Socratic Tutor");
      });
  }, [assignmentId]);

  useEffect(() => {
    if (assignmentId) {
      handleSend("");
    }
  }, [assignmentId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    const interval = setInterval(() => {
      setHeaderTextType((prev) =>
        prev === "question" ? "label" : "question"
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleSend = async (message: string) => {
    if (!assignmentId) {
      console.error("No assignmentId!");
      return;
    }

    // Add user message immediately if there's any
    if (message.trim()) {
      setMessages((prev) => [...prev, { role: "user", text: message }]);
    }

    // ✅ Add the loader bubble
    setMessages((prev) => [...prev, { role: "loading", text: "" }]);

    try {
      const res = await axios.post("http://localhost:8000/ask", {
        assignmentId,
        message,
        state: sessionState,
        index: questionIndex,
      });

      const reply = res.data.reply;
      const reference = res.data.reference;
      const newState = res.data.state;
      const newIndex = res.data.index;

      // ✅ Remove the loader bubble
      setMessages((prev) => {
        const trimmed = [...prev];
        if (trimmed[trimmed.length - 1].role === "loading") {
          trimmed.pop();
        }
        return trimmed;
      });

      // ✅ Add the real system reply & reference if any
      setMessages((prev) => [
        ...prev,
        { role: "system", text: reply },
        ...(reference && reference.trim()
          ? [{ role: "reference", text: reference } as Message]
          : []),
      ]);

      setSessionState(newState);
      setQuestionIndex(newIndex);
      setInput("");
    } catch (err) {
      console.error(err);

      // Remove the loader bubble if error
      setMessages((prev) => {
        const trimmed = [...prev];
        if (trimmed[trimmed.length - 1].role === "loading") {
          trimmed.pop();
        }
        return trimmed;
      });

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

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="container-fluid vh-100 d-flex flex-column bg-light">
      {/* Header */}
      <div
        className="p-3 text-center"
        style={{
          backgroundColor: "#ffffff",
          color: "#4CAF50",
        }}
      >
        <h2 className="mb-0 position-relative" style={{ height: "40px" }}>
          <span
            className={`fade-text ${
              headerTextType === "question" ? "visible" : ""
            }`}
          >
            {`Question ${questionIndex + 1}`}
          </span>
          <span
            className={`fade-text ${
              headerTextType === "label" ? "visible" : ""
            }`}
          >
            {assignmentName}
          </span>
        </h2>
      </div>

      {/* Messages Container */}
      <div
        className="flex-grow-1 overflow-auto p-3"
        style={{ maxHeight: "calc(100vh - 140px)" }}
      >
        <div className="d-flex flex-column gap-3">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`d-flex ${
                msg.role === "user"
                  ? "justify-content-end"
                  : "justify-content-start"
              }`}
            >
              <FadeInBubble msg={msg} />
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-top p-3 d-flex justify-content-center">
        <div className="w-100 position-relative" style={{ maxWidth: "720px" }}>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              className="form-control rounded-pill px-4 py-3 shadow-none"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your answer..."
              style={{
                fontSize: "16px",
                backgroundColor: "#f7f7f8",
                border: "1px solid #ccc",
                paddingRight: "60px",
                height: "80px",
              }}
            />
            <button
              type="submit"
              className="btn btn-primary rounded-circle send-btn"
              disabled={!input.trim()}
              style={{
                position: "absolute",
                right: "10px",
                top: "50%",
                transform: "translateY(-50%)",
                padding: "0",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <i className="bi bi-send-fill"></i>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

/* ✅ Updated Bubble component with loader support */
function FadeInBubble({ msg }: { msg: Message }) {
  const [visible, setVisible] = React.useState(msg.role === "user");
  const [displayedText, setDisplayedText] = React.useState("");
  const [dots, setDots] = React.useState(".");

  React.useEffect(() => {
    if (msg.role === "loading") {
      setVisible(true);
      const interval = setInterval(() => {
        setDots((prev) => {
          if (prev === ".") return "..";
          if (prev === "..") return "...";
          return ".";
        });
      }, 500);
      return () => clearInterval(interval);
    }

    if (msg.role === "user" || msg.role === "reference") {
      setVisible(true);
      return;
    }

    setDisplayedText("");
    setVisible(true);

    const characters = Array.from(msg.text);
    let currentIndex = 0;

    const interval = setInterval(() => {
      if (currentIndex < characters.length) {
        setDisplayedText(characters.slice(0, currentIndex + 1).join(""));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 25);

    return () => clearInterval(interval);
  }, [msg]);

  const baseStyle = {
    maxWidth: "70%",
    wordWrap: "break-word",
  };

  if (msg.role === "user") {
    return (
      <div
        className={`p-3 rounded-4 bg-primary text-white ${
          visible ? "appear" : ""
        }`}
        style={{
          ...baseStyle,
          borderBottomRightRadius: "0.375rem",
        }}
      >
        {msg.text}
      </div>
    );
  }

  if (msg.role === "system") {
    return (
      <div
        className={`fade-in ${visible ? "appear" : ""}`}
        style={{
          ...baseStyle,
          backgroundColor: "white",
          color: "black",
          padding: "12px 15px",
          borderRadius: 0,
          border: "none",
          fontSize: "1rem",
          fontWeight: "normal",
        }}
      >
        {displayedText}
      </div>
    );
  }

  if (msg.role === "reference") {
    return (
      <div
        className={`p-3 rounded-4 bg-light text-dark border-start border-warning border-4 fade-in ${
          visible ? "appear" : ""
        }`}
        style={{
          ...baseStyle,
          borderBottomLeftRadius: "0.375rem",
        }}
      >
        <div className="small text-muted fw-bold mb-1">📚 Reference:</div>
        <div>{msg.text}</div>
      </div>
    );
  }

  if (msg.role === "loading") {
    return (
      <div
        className={`fade-in appear`}
        style={{
          ...baseStyle,
          backgroundColor: "#f0f0f0",
          color: "#888",
          padding: "12px 15px",
          borderRadius: "1rem",
          fontStyle: "italic",
          fontSize: "1rem",
        }}
      >
        {dots}
      </div>
    );
  }

  return null;
}
