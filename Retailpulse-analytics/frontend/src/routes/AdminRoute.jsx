import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AdminRoute({ children }) {
  const { isAuthenticated } = useAuth();

  const user = JSON.parse(localStorage.getItem("user"));

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== "Company Admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}