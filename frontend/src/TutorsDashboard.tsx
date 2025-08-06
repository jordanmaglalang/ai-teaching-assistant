import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

type TutorType = {
  _id: string;
  course_name: string;
  average_score: number | null;
  recent_assignments: {
    title: string;
    score: number | null;
    total: number;
    date: string;
  }[];
};

export default function TutorsDashboard() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [tutors, setTutors] = useState<TutorType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null);

  const getColor = (score: number | null) => {
    if (score === null) return "#9e9e9e"; // gray
    if (score >= 90) return "#4CAF50"; // green
    if (score >= 80) return "#8BC34A"; // lime
    if (score >= 70) return "#FFC107"; // amber
    if (score >= 60) return "#FF9800"; // orange
    return "#F44336"; // red
  };

  const handleDeleteTutor = async (tutorId: string, courseName: string) => {
    const isConfirmed = window.confirm(
      `Are you sure you want to delete the tutor "${courseName}"? This will also delete all associated assignments. This action cannot be undone.`
    );

    if (!isConfirmed) return;

    try {
      setDeleteLoading(tutorId);
      await axios.delete(`http://localhost:8000/delete_tutor`, {
        params: { tutorId },
      });
      
      // Remove the tutor from the local state
      setTutors(prev => prev.filter(tutor => tutor._id !== tutorId));
      
    } catch (err) {
      console.error("Failed to delete tutor:", err);
      alert("Failed to delete tutor. Please try again.");
    } finally {
      setDeleteLoading(null);
    }
  };

  useEffect(() => {
    if (!userId) return;

    async function fetchTutors() {
      try {
        setLoading(true);
        const response = await axios.get("http://localhost:8000/tutors", {
          params: { userId },
        });
        setTutors(response.data);
        setError(null);
      } catch (err) {
        setError("Failed to load tutors");
      } finally {
        setLoading(false);
      }
    }

    fetchTutors();
  }, [userId]);

  if (!userId) return <p>Error: Missing user ID in URL.</p>;
  if (loading) return <p>Loading tutors...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (tutors.length === 0) return <p>No tutors found.</p>;

  return (
    <div className="container my-5">
      <h1 className="text-center mb-4" style={{ color: "#4CAF50" }}>
        Tutors Dashboard
      </h1>

      <div className="text-center mb-4">
        <button
          className="btn"
          style={{
            backgroundColor: "#4CAF50",
            color: "#fff",
            border: "none",
            padding: "0.6rem 1.2rem",
            fontWeight: "bold",
            borderRadius: "8px",
          }}
          onClick={() => navigate("/")}
        >
          ➕ Add Tutor
        </button>
      </div>

      <div
        className="d-flex flex-column align-items-center"
        style={{ gap: "2rem" }}
      >
        {tutors.map((tutor) => {
          const scoreColor = getColor(tutor.average_score);

          return (
            <div
              key={tutor._id}
              className="card shadow"
              style={{
                width: "100%",
                maxWidth: "80%",
                backgroundColor: "#fff",
                borderRadius: "16px",
                padding: "1.5rem",
                borderLeft: `6px solid ${scoreColor}`,
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                transition: "all 0.3s ease",
              }}
            >
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="mb-0" style={{ color: "#222", fontWeight: 600 }}>
                  {tutor.course_name}
                </h4>
                <div
                  style={{
                    backgroundColor: scoreColor,
                    color: "#fff",
                    padding: "0.4rem 0.8rem",
                    borderRadius: "999px",
                    fontWeight: 500,
                    fontSize: "0.9rem",
                  }}
                >
                  {tutor.average_score != null ? `${tutor.average_score}%` : "N/A"}
                </div>
              </div>

              <div>
                <strong style={{ color: "#555" }}>Recent Assignments</strong>
                <ul className="mt-2" style={{ listStyle: "none", padding: 0 }}>
                  {tutor.recent_assignments.map((a, i) => (
                    <li
                      key={i}
                      style={{
                        padding: "0.5rem 0",
                        borderBottom: "1px solid #eee",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: "0.95rem",
                      }}
                    >
                      <span>{a.title}</span>
                      <span style={{ color: "#666" }}>
                        {a.score != null ? `${a.score}/${a.total}` : "Ungraded"}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="d-flex justify-content-end align-items-center gap-2 mt-3">
                <button
                  className="btn btn-sm"
                  style={{
                    backgroundColor: "#4CAF50",
                    color: "#fff",
                    borderRadius: "6px",
                    fontWeight: "bold",
                    border: "none",
                  }}
                  onClick={() => navigate(`/tutor/${tutor._id}`)}
                >
                  📚 View Assignments
                </button>
                
                <button
                  className="btn btn-sm"
                  style={{
                    backgroundColor: "#F44336",
                    color: "#fff",
                    borderRadius: "6px",
                    fontWeight: "bold",
                    border: "none",
                    opacity: deleteLoading === tutor._id ? 0.6 : 1,
                  }}
                  onClick={() => handleDeleteTutor(tutor._id, tutor.course_name)}
                  disabled={deleteLoading === tutor._id}
                >
                  {deleteLoading === tutor._id ? "🔄" :""} Delete
                </button>
              </div>
            </div>
          );
        })}

      </div>
    </div>
  );
}