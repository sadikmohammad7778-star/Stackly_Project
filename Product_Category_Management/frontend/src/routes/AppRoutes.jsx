import { Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/Login/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import Categories from "../pages/Category/Categories";
import Products from "../pages/Products/Products";
import Reports from "../pages/Reports/Reports";
import Settings from "../pages/Settings/Settings";

import MainLayout from "../layouts/MainLayout/MainLayout";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" />} />

      <Route path="/login" element={<Login />} />

      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/products" element={<Products />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default AppRoutes;