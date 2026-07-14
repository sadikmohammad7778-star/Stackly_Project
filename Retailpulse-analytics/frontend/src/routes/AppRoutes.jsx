import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import Dashboard from "../pages/Dashboard";
import Companies from "../pages/Companies";
import Employees from "../pages/Employees";
import Departments from "../pages/Departments";
import Attendance from "../pages/Attendance";
import Analytics from "../pages/Analytics";
import Reports from "../pages/Reports";
import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="companies" element={<Companies />} />
        <Route path="employees" element={<Employees />} />
        <Route path="departments" element={<Departments />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
        

        {/* Dashboard Layout */}
        <Route path="/" element={<DashboardLayout />}>
          <Route path="dashboard" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}