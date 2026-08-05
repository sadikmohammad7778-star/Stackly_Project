import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";
import DashboardLayout from "../layouts/DashboardLayout";

/* ================= Authentication ================= */

import Login from "../pages/Login";
import Signup from "../pages/Signup";

/* ================= Dashboard ================= */

import Dashboard from "../pages/Dashboard";

/* ================= Customer Module ================= */

import Customers from "../pages/Customers";
import CustomerAnalytics from "../pages/CustomerAnalytics";
import CustomerProfile from "../pages/CustomerProfile";

/* ================= Management Modules ================= */

import Companies from "../pages/Companies";
import Categories from "../pages/Categories";
import Products from "../pages/Products";
import Sales from "../pages/Sales";
import Inventory from "../pages/Inventory";
import Employees from "../pages/Employees";
import Departments from "../pages/Departments";
import Attendance from "../pages/Attendance";
import DemandForecast from "../pages/DemandForecast";

/* ================= Reports ================= */

import Reports from "../pages/Reports";
import Analytics from "../pages/Analytics";
import AuditLogs from "../pages/AuditLogs";

/* ================= Settings ================= */

import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================= Public Routes ================= */}

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

        {/* ================= Protected Routes ================= */}

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

          {/* Companies */}

          <Route
            path="/companies"
            element={<Companies />}
          />

          {/* Categories */}

          <Route
            path="/categories"
            element={<Categories />}
          />

          {/* Products */}

          <Route
            path="/products"
            element={<Products />}
          />

          {/* Sales */}

          <Route
            path="/sales"
            element={<Sales />}
          />

          {/* Inventory */}

          <Route
            path="/inventory"
            element={<Inventory />}
          />

          {/* Demand Forecast */}

          <Route
            path="/forecast"
            element={<DemandForecast />}
          />

          {/* Customers */}

          <Route
            path="/customers"
            element={<Customers />}
          />

          {/* Customer Analytics */}

          <Route
            path="/customers/dashboard"
            element={<CustomerAnalytics />}
          />

          {/* Customer Profile */}

          <Route
            path="/customers/:id"
            element={<CustomerProfile />}
          />

          {/* Employees */}

          <Route
            path="/employees"
            element={<Employees />}
          />

          {/* Departments */}

          <Route
            path="/departments"
            element={<Departments />}
          />

          {/* Attendance */}

          <Route
            path="/attendance"
            element={<Attendance />}
          />

          {/* Reports */}

          <Route
            path="/reports"
            element={<Reports />}
          />

          {/* Analytics */}

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

          {/* Fallback */}

          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}