import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import axios from "axios";

export default function CreateTutorPage() {
  const [courseName, setCourseName] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Example: You might get userId from auth context or props
  const userId = "64a7f9b2e4c8d81234567890"; // Replace this with real user ID

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!courseName) {
        alert("Please enter a course name");
        return;
    }
    if (!files || files.length === 0) {
        alert("Please upload at least one file");
        return;
    }

    setLoading(true);

    try {
        // ✅ Create FormData
        const formData = new FormData();
        formData.append("userId", userId);
        formData.append("courseName", courseName);

        Array.from(files).forEach((file) => {
        formData.append("files", file);
        });

        // ✅ POST FormData
        const response = await axios.post("http://localhost:8000/add_tutor", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Tutor created:", response.data);
        alert("Tutor created successfully!");

        setCourseName("");
        setFiles(null);
        (e.target as HTMLFormElement).reset();
        navigate(`/tutors/${userId}`);

    } catch (error) {
        console.error("Error creating tutor:", error);
        alert("Failed to create tutor");
    } finally {
        setLoading(false);
    }
    };


  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
      <div className="card shadow" style={{ width: "400px", maxWidth: "90%" }}>
        <div className="card-body">
          <h2 className="card-title text-center mb-4">Create Tutor</h2>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="courseName" className="form-label fw-medium">
                Course Name
              </label>
              <input
                id="courseName"
                type="text"
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
                placeholder="Enter course name"
                required
                className="form-control"
              />
            </div>

            <div className="mb-4">
              <label htmlFor="fileUpload" className="form-label fw-medium">
                Upload Course Resources (PDF, PPTX, Word)
              </label>
              <input
                id="fileUpload"
                type="file"
                accept=".pdf,.pptx,.doc,.docx"
                multiple
                onChange={handleFileChange}
                required
                className="form-control"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-100"
            >
              {loading ? "Creating Tutor..." : "Create Tutor"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
