import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

type TutorType = {
  _id: string;
  courseName: string;
  // add more fields as needed
};

export default function TutorsDashboard() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [tutors, setTutors] = useState<TutorType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (!userId) {
    return <p>Error: Missing user ID in URL.</p>;
  }

  if (loading) return <p>Loading tutors...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (tutors.length === 0) return <p>No tutors found.</p>;

  return (
    <div className="container my-5">
      <h1 className="text-center mb-4">Tutors Dashboard</h1>
         <div className="text-center mb-4">
        <button
          className="btn btn-success"
          onClick={() => navigate("/")}
        >
          ➕ Add Tutor
        </button>
      </div>
      <div
        className="d-flex flex-column align-items-center"
        style={{ gap: "2rem" }}
      >
        {tutors.map((tutor) => (
          <div
            key={tutor._id}
            className="card shadow"
            style={{
              width: "100%",
              maxWidth: "80%",
              minHeight: "10rem",
            }}
          >
            <div
              className="card-body d-flex flex-column justify-content-center align-items-center"
              style={{
                padding: "2rem",
              }}
            >
              <h5 className="card-title mb-3">{tutor.course_name}</h5>
              <button
                className="btn btn-primary"
                onClick={() => navigate(`/tutor/${tutor._id}`)}
              >
                Go to Assignments
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}