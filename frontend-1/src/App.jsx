import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./components/Auth/LoginForm";
import Signup from "./components/Auth/SignupForm";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import Departments from "./pages/Departments";
import Attendance from "./pages/Attendance";
import Settings from "./pages/Settings";

import Layout from "./components/Layout";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Authentication */}
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Dashboard Layout */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/departments" element={<Departments />} />
          <Route path="/attendance" element={<Attendance />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;