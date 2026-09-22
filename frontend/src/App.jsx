import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import ResumeUpload from "./pages/ResumeUpload";
import JobDescription from "./pages/JobDescription";

import ResumeAnalysis from "./pages/ResumeAnalysis";
import InterviewPreparation from "./pages/InterviewPreparation";
import PreparationProgress from "./pages/PreparationProgress";
import ResumeBuilder from "./pages/ResumeBuilder";

import ProtectedRoute from "./components/ProtectedRoute";
import SkillGapAnalysis from "./pages/SkillGapAnalysis";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                {/* Public routes */}

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />


                {/* Dashboard */}

                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />


                {/* Existing pages */}

                <Route
                    path="/resume-upload"
                    element={
                        <ProtectedRoute>
                            <ResumeUpload />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/job-description"
                    element={
                        <ProtectedRoute>
                            <JobDescription />
                        </ProtectedRoute>
                    }
                />


                {/* Stage 19 pages */}

                <Route
                    path="/resume-analysis"
                    element={
                        <ProtectedRoute>
                            <ResumeAnalysis />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/skill-gaps"
                    element={
                        <ProtectedRoute>
                            <SkillGapAnalysis />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/interview-preparation"
                    element={
                        <ProtectedRoute>
                            <InterviewPreparation />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/preparation-progress"
                    element={
                        <ProtectedRoute>
                            <PreparationProgress />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/resume-builder"
                    element={
                        <ProtectedRoute>
                            <ResumeBuilder />
                        </ProtectedRoute>
                    }
                />


                {/* Unknown route */}

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/login"
                            replace
                        />
                    }
                />

            </Routes>
        </BrowserRouter>
    );
}

export default App;