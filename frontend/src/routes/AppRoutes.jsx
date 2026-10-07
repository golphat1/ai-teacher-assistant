import { Routes, Route, Navigate } from 'react-router-dom';
import TeacherDashboardPage from '../pages/TeacherDashboardPage';
import ClassAnalyticsPage from '../pages/ClassAnalyticsPage';
import StudentAssignmentPage from '../pages/StudentAssignmentPage';
import TeacherSubmissionReviewPage from '../pages/TeacherSubmissionReviewPage';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/teacher/dashboard" replace />} />
      <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
      <Route path="/teacher/classes/:classId/analytics" element={<ClassAnalyticsPage />} />
      <Route path="/teacher/submissions/:submissionId" element={<TeacherSubmissionReviewPage />} />
      <Route path="/student/assignments/:assignmentId" element={<StudentAssignmentPage />} />
    </Routes>
  );
}