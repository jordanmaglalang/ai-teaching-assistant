import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

type AssignmentType = {
  _id: string;
  assignment_name: string;
  files: string[];
  score: number;
};

export default function AssignmentsDashboard() {
  const { tutorId } = useParams<{ tutorId: string }>();
  const navigate = useNavigate(); // ✅

  const [assignments, setAssignments] = useState<AssignmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newAssignmentName, setNewAssignmentName] = useState("");
  const [newFiles, setNewFiles] = useState<FileList | null>(null);

  const [averageScore, setAverageScore] = useState<number | null>(null);
  const [numGraded, setNumGraded] = useState(0);
  const [totalAssignments, setTotalAssignments] = useState(0);

  useEffect(() => {
    if (!tutorId) return;

    async function fetchAssignments() {
      try {
        setLoading(true);
        const response = await axios.get("http://localhost:8000/assignments", {
          params: { tutorId },
        });
        setAssignments(response.data);
        setError(null);
      } catch (err) {
        setError("Failed to load assignments");
      } finally {
        setLoading(false);
      }
    }
    async function fetchCourseScore() {
    try {
      const response = await axios.get("http://localhost:8000/course_score", {
        params: { tutorId },
      });
      setAverageScore(response.data.average_score);
      setNumGraded(response.data.num_graded);
      setTotalAssignments(response.data.total);
    } catch {
      setAverageScore(null);
    }
  }


    fetchAssignments();
    fetchCourseScore();
  }, [tutorId]);

  const handleAddAssignment = async () => {
    if (!newAssignmentName || !newFiles) {
      alert("Please provide title and file(s)");
      return;
    }

    const formData = new FormData();
    formData.append("tutorId", tutorId!);
    formData.append("assignmentName", newAssignmentName);
    Array.from(newFiles).forEach((file) => formData.append("files", file));

    try {
      await axios.post("http://localhost:8000/add_assignment", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setIsModalOpen(false);
      setNewAssignmentName("");
      setNewFiles(null);

      const response = await axios.get("http://localhost:8000/assignments", {
        params: { tutorId },
      });
      setAssignments(response.data);
    } catch (err) {
      alert("Failed to add assignment");
    }
  };
  const handleDeleteAssignment = async (assignmentId: string) => {
  const confirmed = window.confirm("Are you sure you want to delete this assignment?");
  if (!confirmed) return;

    try {
      await axios.delete(`http://localhost:8000/delete_assignment`, {
        params: { assignmentId },
      });

      // Refresh the assignments list
      setAssignments((prev) => prev.filter((a) => a._id !== assignmentId));
    } catch (err) {
      alert("Failed to delete assignment");
    }
  };

  

  return (
    <div className="container my-5" style={{ position: "relative" }}>
      <h1 className="text-center mb-4">Assignments Dashboard</h1>
        {averageScore !== null && (
        <div className="alert alert-info text-center">
          <h5>📊 Course Grade Summary</h5>
          <p>
            <strong>Average Score:</strong>{" "}
            <span
              style={{
                color:
                  averageScore >= 80
                    ? "green"
                    : averageScore >= 50
                    ? "orange"
                    : "red",
              }}
            >
              {averageScore}/100
            </span>
            <br />
            ({numGraded} out of {totalAssignments} graded)
          </p>
        </div>
      )}

      <button
        className="btn btn-success mb-4"
        onClick={() => setIsModalOpen(true)}
      >
        ➕ Add Assignment
      </button>

      {assignments.map((assignment) => (
        <div
          key={assignment._id}
          className="card mb-3"
          style={{ padding: "1rem" }}
        >
          <h5>{assignment.assignment_name}</h5>
           {assignment.score !== undefined && (
            <p>
              <strong>Score:</strong>{" "}
              <span
                style={{
                  color:
                    assignment.score >= 80
                      ? "green"
                      : assignment.score >= 50
                      ? "orange"
                      : "red",
                }}
              >
                {assignment.score}/100
              </span>
            </p>
          )}
          <ul>
            {assignment.files?.map((file, index) => (
              <li key={index}>{file}</li>
            ))}
          </ul>


          <div className="d-flex gap-2">
            <button
              className="btn btn-primary"
              onClick={() =>
                navigate(`/tutor/${tutorId}/assignment/${assignment._id}`)
              }
            >
              Work on Assignment
            </button>

            <button
              className="btn btn-danger"
              onClick={() => handleDeleteAssignment(assignment._id)}
            >
               Delete
            </button>
          </div>

        </div>
      ))}

      {isModalOpen && (
        <div
          style={{
            position: "fixed",
            top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(5px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}
        >
          <div
            className="card shadow"
            style={{ maxWidth: "30rem", width: "90%", padding: "2rem" }}
          >
            <h4 className="mb-3">Add New Assignment</h4>
            <input
              type="text"
              placeholder="Assignment Title"
              value={newAssignmentName}
              onChange={(e) => setNewAssignmentName(e.target.value)}
              className="form-control mb-3"
            />
            <input
              type="file"
              multiple
              onChange={(e) => setNewFiles(e.target.files)}
              className="form-control mb-3"
            />
            <div className="d-flex justify-content-end">
              <button
                className="btn btn-secondary me-2"
                onClick={() => setIsModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleAddAssignment}
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
