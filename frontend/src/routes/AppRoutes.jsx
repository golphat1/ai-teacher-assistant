import { Routes, Route, Navigate } from 'react-router-dom';
import TeacherDashboardPage from '../pages/TeacherDashboardPage';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/teacher/dashboard" replace />} />
      <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
    </Routes>
  );
}