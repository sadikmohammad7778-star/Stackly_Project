import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";
import DashboardLayout from "../layouts/DashboardLayout";

// Authentication
import Login from "../pages/Login";
import Signup from "../pages/Signup";

// Dashboard
import Dashboard from "../pages/Dashboard";

// Management Modules
import Companies from "../pages/Companies";
import Categories from "../pages/Categories";
import Products from "../pages/Products";
import Sales from "../pages/Sales";
import Employees from "../pages/Employees";
import Departments from "../pages/Departments";
import Attendance from "../pages/Attendance";
import Inventory from "../pages/Inventory";

// Reports & Analytics
import Reports from "../pages/Reports";
import Analytics from "../pages/Analytics";
import AuditLogs from "../pages/AuditLogs"; // <-- ADD THIS

// Other Pages
import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Routes */}
        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        {/* Protected Routes */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          {/* Management */}
          <Route
            path="/companies"
            element={<Companies />}
          />

          <Route
            path="/categories"
            element={<Categories />}
          />

          <Route
            path="/products"
            element={<Products />}
          />

          <Route
            path="/sales"
            element={<Sales />}
          />

          <Route
            path="/inventory"
            element={<Inventory />}
          />

          <Route
            path="/employees"
            element={<Employees />}
          />

          <Route
            path="/departments"
            element={<Departments />}
          />

          <Route
            path="/attendance"
            element={<Attendance />}
          />

          {/* Reports */}
          <Route
            path="/reports"
            element={<Reports />}
          />

          <Route
            path="/analytics"
            element={<Analytics />}
          />

          {/* Audit Logs */}
          <Route
            path="/audit"
            element={<AuditLogs />}
          />

          {/* Settings */}
          <Route
            path="/settings"
            element={<Settings />}
          />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}
