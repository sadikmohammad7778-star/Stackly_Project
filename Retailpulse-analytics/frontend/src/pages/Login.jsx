import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await loginUser(
        formData.email,
        formData.password
      );

      // Save Access Token
      login(response.access_token);

      // Save Refresh Token
      localStorage.setItem(
        "refresh_token",
        response.refresh_token
      );

      // Save Logged-in User
      localStorage.setItem(
        "user",
        JSON.stringify(response.user)
      );

      // Redirect to Dashboard
      navigate("/dashboard", { replace: true });

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Invalid email or password"
      );
    }
  };

  return (
    <div className="login-container">
      <form
        className="login-card"
        onSubmit={handleSubmit}
      >
        <h2>RetailPulse Analytics</h2>

        {error && (
          <p className="error">{error}</p>
        )}

        <input
          type="email"
          name="email"
          placeholder="Enter Email"
          value={formData.email}
          onChange={handleChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Enter Password"
          value={formData.password}
          onChange={handleChange}
          required
        />

        <button type="submit">
          Login
        </button>

        <p className="signup-link">
          Don't have an account?{" "}
          <span
            onClick={() => navigate("/signup")}
          >
            Sign Up
          </span>
        </p>
      </form>
    </div>
  );
}