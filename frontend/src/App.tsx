// App.tsx

import { BrowserRouter, Routes, Route } from "react-router-dom";
import CreateTutorPage from "./CreateTutorPage";
import TutorsDashboard from "./TutorsDashboard";
import AssignmentsDashboard from "./AssignmentsDashboard";
import AddAssignmentPage from "./AddAssignmentPage";
import ChatApp from "./ChatApp";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CreateTutorPage />} />
        <Route path="/tutors/:userId" element={<TutorsDashboard />} />
        <Route path="/tutor/:tutorId" element={<AssignmentsDashboard />} />
        <Route path="/tutor/:tutorId/new-assignment" element={<AddAssignmentPage />} />
        <Route path="/tutor/:tutorId/assignment/:assignmentId" element={<ChatApp />} />
      </Routes>
    </BrowserRouter>
  );
}
