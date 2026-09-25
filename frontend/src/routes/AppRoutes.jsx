import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";
import AdminRoute from "./AdminRoute";
import DashboardLayout from "../layouts/DashboardLayout";

import Login from "../pages/Login";
import Signup from "../pages/Signup";

import Dashboard from "../pages/Dashboard";

import Customers from "../pages/Customers";
import CustomerAnalytics from "../pages/CustomerAnalytics";
import CustomerProfile from "../pages/CustomerProfile";

import Companies from "../pages/Companies";
import Categories from "../pages/Categories";
import Products from "../pages/Products";
import Sales from "../pages/Sales";
import Inventory from "../pages/Inventory";
import Employees from "../pages/Employees";
import Departments from "../pages/Departments";
import Attendance from "../pages/Attendance";
import DemandForecast from "../pages/DemandForecast";
import InventoryForecast from "../pages/InventoryForecast";
import DataImport from "../pages/DataImport";
import DataQuality from "../pages/DataQuality";

import Reports from "../pages/Reports";
import Analytics from "../pages/Analytics";
import AuditLogs from "../pages/AuditLogs";
import ScheduledReports from "../pages/ScheduledReports";

import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
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

        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

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
            path="/data-import"
            element={<DataImport />}
          />

          <Route
            path="/data-quality"
            element={<DataQuality />}
          />

          <Route
            path="/forecast"
            element={<DemandForecast />}
          />

          <Route
            path="/inventory/forecast"
            element={<InventoryForecast />}
          />

          <Route
            path="/customers"
            element={<Customers />}
          />

          <Route
            path="/customers/dashboard"
            element={<CustomerAnalytics />}
          />

          <Route
            path="/customers/:id"
            element={<CustomerProfile />}
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

          <Route
            path="/reports"
            element={<Reports />}
          />

          <Route
            path="/scheduled-reports"
            element={<ScheduledReports />}
          />

          <Route
            path="/analytics"
            element={<Analytics />}
          />

          <Route
            path="/audit"
            element={
              <AdminRoute>
                <AuditLogs />
              </AdminRoute>
            }
          />

          <Route
            path="/settings"
            element={<Settings />}
          />

          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}